"""
============================================
メタ広告審査チェッカー - 広告審査エンドポイント
============================================

POST /api/check - URL審査（LP・広告ページのURL審査専用）
"""

import logging
from typing import Optional
from fastapi import APIRouter

from ..types import (
    AdCheckRequest,
    AdCheckResponse,
    AdStatus,
    Violation,
    ViolationCategory,
    ViolationSeverity,
    ViolationLocation,
    RecommendationPriority,
    RecommendationActionType,
    RecommendationTarget,
    Recommendation,
    ImageImprovement,
    ImageImprovementTextOverlay,
    ImageImprovementContentIssue,
)
from ..utils.url_fetcher import fetch_page_data
from ..services import GeminiService, ModerationService, build_meta_ad_review_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ad-check"])


# --------------------------------------------
# POST /api/check - URL審査AI判定
# --------------------------------------------

@router.post("/check", response_model=AdCheckResponse)
async def check_advertisement(request: AdCheckRequest) -> AdCheckResponse:
    """
    LP・広告ページのURLを審査し、Meta広告審査の合否予測と改善提案を返却

    ## 処理フロー:
    1. URLからページデータを取得
    2. Gemini APIへのリクエスト送信
    3. AI応答の解析
    4. スコア計算とステータス判定
    5. レスポンス整形

    ## エラー:
    - 400: バリデーションエラー
    - 429: レート制限超過
    - 500: サーバーエラー
    - 503: タイムアウト
    """
    logger.info(f"Starting URL ad check: {request.page_url}")

    # --------------------------------------------
    # 1. URLからページデータを取得
    # --------------------------------------------
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    page_text: Optional[str] = None
    page_images: list = []

    logger.info(f"Fetching page data from URL: {request.page_url}")
    page_data = await fetch_page_data(request.page_url)

    page_title = page_data.title
    page_description = page_data.description
    page_text = page_data.page_text

    # LP内の画像を取得（OGP画像 + 主要画像）
    if page_data.images:
        page_images = [img.data for img in page_data.images]
        logger.info(f"Found {len(page_images)} images from LP")

    logger.info(f"Page data fetched: title={page_title}, images={len(page_images)}")
    if page_text:
        logger.debug(f"Page text preview (first 500 chars): {page_text[:500]}")

    # --------------------------------------------
    # 2. Gemini APIへのリクエスト送信
    # --------------------------------------------
    has_images = len(page_images) > 0

    logger.info("Building prompt for Gemini API...")
    prompt = build_meta_ad_review_prompt(
        headline=None,
        description=None,
        cta=None,
        has_image=has_images,
        page_url=request.page_url,
        page_title=page_title,
        page_description=page_description,
        page_text=page_text,
        image_count=len(page_images),
    )

    logger.info(f"Calling Gemini API with {len(page_images)} images...")
    gemini_service = GeminiService()
    ai_response_text = await gemini_service.generate_content_with_retry(
        prompt=prompt,
        images=page_images if page_images else None,
        temperature=0.3,
    )

    # --------------------------------------------
    # 3. AI応答の解析
    # --------------------------------------------
    logger.info("Parsing AI response...")
    ai_response = gemini_service.parse_json_response(ai_response_text)

    # --------------------------------------------
    # 4. 補助チェック（OpenAI Moderation API - オプション）
    # --------------------------------------------
    moderation_result = None
    if page_text:
        logger.info("Running optional moderation check...")
        moderation_service = ModerationService()
        if moderation_service.is_available():
            # ページテキストをModeration APIでチェック（2000文字に制限）
            moderation_result = await moderation_service.check_content(page_text[:2000])

    # --------------------------------------------
    # 5. スコア計算とステータス判定
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
    # Violationsの構築（nullチェック）
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
    violations_raw = ai_result.get("violations")
    violations_list = violations_raw if isinstance(violations_raw, list) else []
    for v in violations_list:
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

    # Recommendationsの構築（新形式対応、nullチェック）
    recommendations = []
    # アクションタイプのマッピング
    action_type_mapping = {
        "change": "replace",
        "modify": "rephrase",
        "delete": "remove",
        "move": "relocate",
    }
    # 優先度のマッピング
    priority_mapping = {
        "high": "must",
        "medium": "recommended",
        "low": "optional",
        "critical": "must",
    }

    recommendations_raw = ai_result.get("recommendations")
    recommendations_list = recommendations_raw if isinstance(recommendations_raw, list) else []
    for r in recommendations_list:
        # 新形式の場合
        if "target" in r and "suggestions" in r:
            # target の安全な変換
            raw_target = r.get("target", "text")
            try:
                target = RecommendationTarget(raw_target)
            except ValueError:
                logger.warning(f"Unknown target: {raw_target}, using 'text'")
                target = RecommendationTarget.TEXT

            # action_type の安全な変換
            raw_action_type = r.get("action_type", "replace")
            mapped_action_type = action_type_mapping.get(raw_action_type, raw_action_type)
            try:
                action_type = RecommendationActionType(mapped_action_type)
            except ValueError:
                logger.warning(f"Unknown action_type: {raw_action_type}, using 'replace'")
                action_type = RecommendationActionType.REPLACE

            # priority の安全な変換
            raw_priority = r.get("priority", "recommended")
            mapped_priority = priority_mapping.get(raw_priority, raw_priority)
            try:
                priority = RecommendationPriority(mapped_priority)
            except ValueError:
                logger.warning(f"Unknown priority: {raw_priority}, using 'recommended'")
                priority = RecommendationPriority.RECOMMENDED

            # suggestionsがnullの場合に空リストにフォールバック
            suggestions_raw = r.get("suggestions")
            suggestions_list = suggestions_raw if isinstance(suggestions_raw, list) else []

            recommendations.append(
                Recommendation(
                    target=target,
                    target_field=r.get("target_field"),
                    related_violation_category=r.get("related_violation_category"),
                    action_type=action_type,
                    priority=priority,
                    estimated_score_impact=max(0, min(100, r.get("estimated_score_impact") or 10)),
                    title=r.get("title") or "改善提案",
                    before=r.get("before") or "",
                    suggestions=suggestions_list,
                    reason=r.get("reason") or "",
                )
            )
        else:
            # 旧形式からの変換（後方互換性）
            after_text = r.get("after")
            suggestions_from_old = [after_text] if after_text else []

            recommendations.append(
                Recommendation(
                    target=RecommendationTarget.TEXT,
                    target_field=None,
                    related_violation_category=None,
                    action_type=RecommendationActionType.REPLACE,
                    priority=RecommendationPriority.RECOMMENDED,
                    estimated_score_impact=10,
                    title="改善提案",
                    before=r.get("before") or "",
                    suggestions=suggestions_from_old,
                    reason=r.get("reason") or "",
                )
            )

    # ImageImprovementの構築
    image_improvement = None
    img_imp = ai_result.get("image_improvement")
    if img_imp and isinstance(img_imp, dict):
        text_overlay = None
        content_issues = []

        to = img_imp.get("text_overlay")
        if to and isinstance(to, dict):
            # リストフィールドのnullチェック
            problematic_areas_raw = to.get("problematic_areas")
            problematic_areas = problematic_areas_raw if isinstance(problematic_areas_raw, list) else []
            removal_suggestions_raw = to.get("removal_suggestions")
            removal_suggestions = removal_suggestions_raw if isinstance(removal_suggestions_raw, list) else []

            text_overlay = ImageImprovementTextOverlay(
                current_percentage=to.get("current_percentage") or 0,
                target_percentage=to.get("target_percentage") or 15,
                problematic_areas=problematic_areas,
                removal_suggestions=removal_suggestions,
            )

        ci_list = img_imp.get("content_issues")
        if ci_list and isinstance(ci_list, list):
            for ci in ci_list:
                if isinstance(ci, dict):
                    alternatives_raw = ci.get("alternatives")
                    alternatives = alternatives_raw if isinstance(alternatives_raw, list) else []
                    content_issues.append(
                        ImageImprovementContentIssue(
                            issue=ci.get("issue") or "",
                            location=ci.get("location") or "",
                            alternatives=alternatives,
                        )
                    )

        image_improvement = ImageImprovement(
            text_overlay=text_overlay,
            content_issues=content_issues,
        )

    # 禁止コンテンツのリスト（nullチェック）
    prohibited_content_raw = ai_result.get("prohibited_content")
    prohibited_content = prohibited_content_raw if isinstance(prohibited_content_raw, list) else []

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
        api_used="gemini-2.0-flash",
        image_improvement=image_improvement,
    )
