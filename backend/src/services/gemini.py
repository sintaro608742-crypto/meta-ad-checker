"""
============================================
メタ広告審査チェッカー - Gemini APIクライアント
============================================

Google Gemini APIとの連携、リトライロジック、タイムアウト処理を提供
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from ..utils.errors import (
    ExternalAPIError,
    RateLimitExceededError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)


# --------------------------------------------
# Configuration
# --------------------------------------------

GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_TIMEOUT = 30  # 30秒
MAX_RETRIES = 3  # 最大リトライ回数
INITIAL_RETRY_DELAY = 1  # 初回リトライ待機時間（秒）


# --------------------------------------------
# Gemini Service
# --------------------------------------------

class GeminiService:
    """Gemini API サービスクラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Gemini APIキー（未指定の場合は環境変数から取得）

        Raises:
            ValueError: APIキーが設定されていない場合
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        # Gemini APIの設定
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

        logger.info(f"GeminiService initialized with model: {GEMINI_MODEL}")

    async def generate_content_with_retry(
        self,
        prompt: str,
        image_data: Optional[bytes] = None,
        temperature: float = 0.3,
    ) -> str:
        """
        Gemini APIにリクエストを送信（リトライロジック付き）

        Args:
            prompt: プロンプト文字列
            image_data: 画像のバイナリデータ（オプション）
            temperature: 生成温度（0.0-1.0、デフォルト: 0.3）

        Returns:
            str: AIの生成結果（JSON文字列）

        Raises:
            RateLimitExceededError: レート制限超過
            ServiceUnavailableError: タイムアウト
            ExternalAPIError: その他のAPIエラー
        """
        for attempt in range(MAX_RETRIES):
            try:
                # タイムアウト付きでAPI呼び出し
                result = await asyncio.wait_for(
                    self._call_gemini_api(prompt, image_data, temperature),
                    timeout=GEMINI_TIMEOUT
                )
                return result

            except asyncio.TimeoutError:
                logger.warning(f"Gemini API timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt == MAX_RETRIES - 1:
                    raise ServiceUnavailableError(
                        message="AI審査がタイムアウトしました。時間を置いて再試行してください。",
                        details={"timeout_seconds": GEMINI_TIMEOUT}
                    )
                await self._exponential_backoff(attempt)

            except Exception as e:
                error_message = str(e).lower()

                # レート制限エラー（429）
                if "quota" in error_message or "rate limit" in error_message or "429" in error_message:
                    logger.warning(f"Gemini API rate limit exceeded (attempt {attempt + 1}/{MAX_RETRIES})")
                    if attempt == MAX_RETRIES - 1:
                        raise RateLimitExceededError(retry_after=60)
                    await self._exponential_backoff(attempt)
                    continue

                # サーバーエラー（500系）- リトライ
                if "500" in error_message or "503" in error_message or "internal error" in error_message:
                    logger.warning(f"Gemini API server error (attempt {attempt + 1}/{MAX_RETRIES}): {error_message}")
                    if attempt == MAX_RETRIES - 1:
                        raise ExternalAPIError(
                            message="AI審査サービスでエラーが発生しました。",
                            details={"error": str(e)}
                        )
                    await self._exponential_backoff(attempt)
                    continue

                # その他のエラー - 即座に失敗
                logger.error(f"Gemini API error: {str(e)}")
                raise ExternalAPIError(
                    message="AI審査の実行中にエラーが発生しました。",
                    details={"error": str(e)}
                )

        # 到達しないはずだが、念のため
        raise ExternalAPIError(message="AI審査に失敗しました。")

    async def _call_gemini_api(
        self,
        prompt: str,
        image_data: Optional[bytes] = None,
        temperature: float = 0.3,
    ) -> str:
        """
        Gemini APIの実際の呼び出し（非同期）

        Args:
            prompt: プロンプト文字列
            image_data: 画像のバイナリデータ（オプション）
            temperature: 生成温度（0.0-1.0）

        Returns:
            str: AIの生成結果（JSON文字列）
        """
        # 生成設定
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )

        # コンテンツの準備
        contents = []

        # 画像がある場合は追加
        if image_data:
            # PILで画像を開く
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            contents.append(image)

        # プロンプトを追加
        contents.append(prompt)

        # 同期APIを非同期実行
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                contents,
                generation_config=generation_config,
            )
        )

        # レスポンスのテキストを取得
        result_text = response.text

        logger.debug(f"Gemini API response received: {len(result_text)} characters")

        return result_text

    async def _exponential_backoff(self, attempt: int) -> None:
        """
        指数バックオフで待機

        Args:
            attempt: 試行回数（0から開始）
        """
        delay = INITIAL_RETRY_DELAY * (2 ** attempt)
        logger.info(f"Retrying after {delay} seconds...")
        await asyncio.sleep(delay)

    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        AIの応答からJSON部分を抽出・解析

        Args:
            response_text: AIの生成結果テキスト

        Returns:
            Dict[str, Any]: 解析されたJSONオブジェクト

        Raises:
            ExternalAPIError: JSON解析に失敗した場合
        """
        try:
            # JSONブロックを抽出（```json ... ``` または {...} 形式）
            json_text = response_text.strip()

            # マークダウンのコードブロックを除去
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]

            json_text = json_text.strip()

            # JSONをパース
            parsed = json.loads(json_text)
            logger.debug("JSON response parsed successfully")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text[:500]}")
            raise ExternalAPIError(
                message="AI審査の結果を解析できませんでした。",
                details={"error": str(e), "response_preview": response_text[:200]}
            )
