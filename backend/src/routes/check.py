"""
============================================
メタ広告審査チェッカー - 広告審査エンドポイント
============================================

POST /api/check - 広告テキスト+画像の総合審査
"""

import logging
from typing import Optional
from fastapi import APIRouter, Request

from ..types import (
    AdCheckRequest,
    AdCheckResponse,
    AdStatus,
    Violation,
    Recommendation,
    ViolationCategory,
    ViolationSeverity,
    ViolationLocation,
)
from ..utils.errors import validate_request_has_content
from ..utils.image import process_and_validate_image, encode_image_to_base64
from ..utils.url_fetcher import fetch_page_data
from ..services import GeminiService, ModerationService, build_meta_ad_review_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ad-check"])


# --------------------------------------------
# POST /api/check - 広告審査AI判定
# --------------------------------------------

@router.post("/check", response_model=AdCheckResponse)
async def check_advertisement(request: AdCheckRequest) -> AdCheckResponse:
    """
    広告テキスト+画像を総合的にチェックし、Meta広告審査の合否予測と改善提案を返却

    ## 処理フロー:
    1. リクエストバリデーション
    2. 画像の前処理（Base64エンコード検証）
    3. Gemini APIへのリクエスト送信
    4. AI応答の解析
    5. スコア計算とステータス判定
    6. レスポンス整形

    ## エラー:
    - 400: バリデーションエラー
    - 413: 画像サイズ超過
    - 415: 非対応形式
    - 429: レート制限超過
    - 500: サーバーエラー
    - 503: タイムアウト
    """
    logger.info("Starting ad check")

    # --------------------------------------------
    # 1. リクエストバリデーション
    # --------------------------------------------
    validate_request_has_content(request)

    # --------------------------------------------
    # 2. 画像の前処理（画像がある場合）
    # --------------------------------------------
    image_data: Optional[bytes] = None
    image_format: Optional[str] = None

    if request.image:
        logger.info("Processing image...")
        image_data, image_format = process_and_validate_image(request.image)
        logger.info(f"Image validated: format={image_format}, size={len(image_data)/1024:.2f}KB")

    # --------------------------------------------
    # 2.5. URL審査の場合、ページデータを取得
    # --------------------------------------------
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    page_text: Optional[str] = None

    if request.page_url:
        logger.info(f"Fetching page data from URL: {request.page_url}")
        page_data = await fetch_page_data(request.page_url)

        page_title = page_data.title
        page_description = page_data.description
        page_text = page_data.page_text

        # OGP画像がある場合、画像として使用（既存画像がない場合のみ）
        if page_data.og_image_data and not image_data:
            logger.info(f"Using OGP image: {len(page_data.og_image_data)/1024:.2f}KB")
            image_data = page_data.og_image_data

        logger.info(f"Page data fetched: title={page_title}, has_og_image={image_data is not None}")

    # --------------------------------------------
    # 3. Gemini APIへのリクエスト送信
    # --------------------------------------------
    logger.info("Building prompt for Gemini API...")
    prompt = build_meta_ad_review_prompt(
        headline=request.headline,
        description=request.description,
        cta=request.cta,
        has_image=image_data is not None,
        page_url=request.page_url,
        page_title=page_title,
        page_description=page_description,
        page_text=page_text,
    )

    logger.info("Calling Gemini API...")
    gemini_service = GeminiService()
    ai_response_text = await gemini_service.generate_content_with_retry(
        prompt=prompt,
        image_data=image_data,
        temperature=0.3,
    )

    # --------------------------------------------
    # 4. AI応答の解析
    # --------------------------------------------
    logger.info("Parsing AI response...")
    ai_response = gemini_service.parse_json_response(ai_response_text)

    # --------------------------------------------
    # 5. 補助チェック（OpenAI Moderation API - オプション）
    # --------------------------------------------
    moderation_result = None
    text_to_check = [request.headline, request.description, request.cta]
    # URL審査の場合、ページテキストも含める
    if page_text:
        text_to_check.append(page_text[:2000])  # Moderation用に2000文字に制限

    if any(text_to_check):
        logger.info("Running optional moderation check...")
        moderation_service = ModerationService()
        if moderation_service.is_available():
            # 全テキストを結合
            all_text = " ".join(filter(None, text_to_check))
            moderation_result = await moderation_service.check_content(all_text)

    # --------------------------------------------
    # 6. スコア計算とステータス判定
    # --------------------------------------------
    logger.info("Calculating score and status...")
    response = _build_response_from_ai_result(ai_response, moderation_result)

    logger.info(f"Ad check completed: score={response.overall_score}, status={response.status}")
    return response


# --------------------------------------------
# Helper Functions
# --------------------------------------------

def _build_response_from_ai_result(
    ai_result: dict,
    moderation_result: Optional[dict] = None
) -> AdCheckResponse:
    """
    AIの応答からAdCheckResponseを構築

    Args:
        ai_result: Gemini APIから返されたJSONオブジェクト
        moderation_result: OpenAI Moderation APIの結果（オプション）

    Returns:
        AdCheckResponse: 構造化されたレスポンス
    """
    # Violationsの構築
    violations = []
    # カテゴリのマッピング（AIが返す値 → enum値）
    category_mapping = {
        "misleading_claims": "misleading",
        "misleading_claim": "misleading",
        "false_claims": "misleading",
        "exaggerated_claims": "misleading",
        "prohibited": "prohibited_content",
        "sexual": "nsfw",
        "adult": "nsfw",
    }
    for v in ai_result.get("violations", []):
        raw_category = v.get("category", "misleading")
        # マッピングがあれば変換、なければそのまま使用
        mapped_category = category_mapping.get(raw_category, raw_category)
        # それでも無効な場合はデフォルト値を使用
        try:
            category = ViolationCategory(mapped_category)
        except ValueError:
            logger.warning(f"Unknown violation category: {raw_category}, using 'misleading'")
            category = ViolationCategory.MISLEADING

        try:
            severity = ViolationSeverity(v.get("severity", "medium"))
        except ValueError:
            severity = ViolationSeverity.MEDIUM

        try:
            location = ViolationLocation(v.get("location", "text"))
        except ValueError:
            location = ViolationLocation.TEXT

        violations.append(
            Violation(
                category=category,
                severity=severity,
                description=v.get("description", ""),
                location=location,
            )
        )

    # Recommendationsの構築
    recommendations = []
    for r in ai_result.get("recommendations", []):
        recommendations.append(
            Recommendation(
                before=r.get("before", ""),
                after=r.get("after", ""),
                reason=r.get("reason", ""),
            )
        )

    # 禁止コンテンツのリスト
    prohibited_content = ai_result.get("prohibited_content", [])

    # Moderation APIの結果をマージ（オプション）
    nsfw_detected = ai_result.get("nsfw_detected", False)
    if moderation_result:
        from ..services import ModerationService
        moderation_service = ModerationService()

        # Moderationでフラグされたカテゴリを追加
        flagged_categories = moderation_service.extract_flagged_categories(moderation_result)
        if flagged_categories:
            logger.info(f"Moderation flagged categories: {flagged_categories}")
            # prohibited_contentに追加（重複回避）
            for category in flagged_categories:
                category_name = f"moderation:{category}"
                if category_name not in prohibited_content:
                    prohibited_content.append(category_name)

        # NSFWの検出をマージ
        if moderation_service.is_nsfw_detected(moderation_result):
            nsfw_detected = True
            # NSFWが検出された場合、違反として追加
            if not any(v.get("category") == "nsfw" for v in ai_result.get("violations", [])):
                violations.append(
                    Violation(
                        category=ViolationCategory.NSFW,
                        severity=ViolationSeverity.HIGH,
                        description="不適切なコンテンツが検出されました（OpenAI Moderation API）。",
                        location=ViolationLocation.TEXT,
                    )
                )

    # スコアとステータスの検証
    overall_score = max(0, min(100, ai_result.get("overall_score", 50)))
    status_str = ai_result.get("status", "needs_review")

    # ステータスの妥当性チェック（スコアと整合性を取る）
    if status_str == "approved" and overall_score < 70:
        status_str = "needs_review"
    elif status_str == "rejected" and overall_score > 49:
        status_str = "needs_review"

    try:
        status = AdStatus(status_str)
    except ValueError:
        logger.warning(f"Unknown status: {status_str}, using 'needs_review'")
        status = AdStatus.NEEDS_REVIEW

    # 信頼度の検証
    confidence = max(0.0, min(1.0, ai_result.get("confidence", 0.8)))

    # レスポンス作成
    return AdCheckResponse.create_with_timestamp(
        overall_score=overall_score,
        status=status,
        confidence=confidence,
        violations=violations,
        recommendations=recommendations,
        text_overlay_percentage=ai_result.get("text_overlay_percentage"),
        nsfw_detected=nsfw_detected,
        prohibited_content=prohibited_content,
        api_used="gemini-2.0-flash-exp",
    )
