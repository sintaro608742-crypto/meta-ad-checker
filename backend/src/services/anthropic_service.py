"""
============================================
メタ広告審査チェッカー - Anthropic APIクライアント
============================================

Anthropic Claude APIとの連携、リトライロジック、タイムアウト処理、レート制限を提供
"""

import os
import json
import asyncio
import time
import base64
import logging
from typing import Optional, Dict, Any, List
from collections import deque

import anthropic

from ..utils.errors import (
    ExternalAPIError,
    RateLimitExceededError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)


# --------------------------------------------
# Configuration
# --------------------------------------------

CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_TIMEOUT = 60
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1

# レート制限: 1時間あたり最大10リクエスト
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 3600  # 1時間


# --------------------------------------------
# Global Rate Limiter
# --------------------------------------------

class RateLimiter:
    """シンプルなスライディングウィンドウレート制限"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: deque = deque()

    def is_allowed(self) -> bool:
        """リクエストが許可されるかチェック"""
        now = time.time()
        # ウィンドウ外のタイムスタンプを削除
        while self._timestamps and self._timestamps[0] < now - self.window_seconds:
            self._timestamps.popleft()
        return len(self._timestamps) < self.max_requests

    def record(self):
        """リクエストを記録"""
        self._timestamps.append(time.time())

    def remaining(self) -> int:
        """残りリクエスト数"""
        now = time.time()
        while self._timestamps and self._timestamps[0] < now - self.window_seconds:
            self._timestamps.popleft()
        return max(0, self.max_requests - len(self._timestamps))

    def retry_after(self) -> int:
        """次にリクエスト可能になるまでの秒数"""
        if self.is_allowed():
            return 0
        now = time.time()
        oldest = self._timestamps[0]
        return int(oldest + self.window_seconds - now) + 1


# グローバルレートリミッター
_rate_limiter = RateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)


# --------------------------------------------
# Anthropic Service
# --------------------------------------------

class AnthropicService:
    """Anthropic Claude API サービスクラス"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")

        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        logger.info(f"AnthropicService initialized with model: {CLAUDE_MODEL}")

    async def generate_content_with_retry(
        self,
        prompt: str,
        image_data: Optional[bytes] = None,
        images: Optional[List[bytes]] = None,
        temperature: float = 0.3,
    ) -> str:
        """Claude APIにリクエスト送信（レート制限+リトライ付き）"""

        # レート制限チェック
        if not _rate_limiter.is_allowed():
            retry_after = _rate_limiter.retry_after()
            logger.warning(f"Rate limit exceeded. Retry after {retry_after}s. Remaining: {_rate_limiter.remaining()}")
            raise RateLimitExceededError(
                message=f"リクエスト制限に達しました（1時間あたり{RATE_LIMIT_MAX_REQUESTS}回まで）。あと{retry_after}秒後に再試行してください。",
                retry_after=retry_after,
            )

        # 画像統合
        all_images = images or []
        if image_data and image_data not in all_images:
            all_images = [image_data] + all_images

        for attempt in range(MAX_RETRIES):
            try:
                result = await asyncio.wait_for(
                    self._call_claude_api(prompt, all_images, temperature),
                    timeout=CLAUDE_TIMEOUT,
                )
                # 成功時にレートリミッターに記録
                _rate_limiter.record()
                return result

            except asyncio.TimeoutError:
                logger.warning(f"Claude API timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt == MAX_RETRIES - 1:
                    raise ServiceUnavailableError(
                        message="AI審査がタイムアウトしました。時間を置いて再試行してください。",
                        details={"timeout_seconds": CLAUDE_TIMEOUT},
                    )
                await self._exponential_backoff(attempt)

            except RateLimitExceededError:
                raise  # レート制限はそのまま上に投げる

            except Exception as e:
                error_message = str(e).lower()

                if "rate" in error_message or "429" in error_message:
                    logger.warning(f"Claude API rate limit (attempt {attempt + 1}/{MAX_RETRIES})")
                    if attempt == MAX_RETRIES - 1:
                        raise RateLimitExceededError(retry_after=60)
                    await self._exponential_backoff(attempt)
                    continue

                if "500" in error_message or "503" in error_message or "overloaded" in error_message:
                    logger.warning(f"Claude API server error (attempt {attempt + 1}/{MAX_RETRIES}): {error_message}")
                    if attempt == MAX_RETRIES - 1:
                        raise ExternalAPIError(
                            message="AI審査サービスでエラーが発生しました。",
                            details={"error": str(e)},
                        )
                    await self._exponential_backoff(attempt)
                    continue

                logger.error(f"Claude API error: {str(e)}")
                raise ExternalAPIError(
                    message="AI審査の実行中にエラーが発生しました。",
                    details={"error": str(e)},
                )

        raise ExternalAPIError(message="AI審査に失敗しました。")

    async def _call_claude_api(
        self,
        prompt: str,
        images: Optional[List[bytes]] = None,
        temperature: float = 0.3,
    ) -> str:
        """Claude APIの実際の呼び出し"""

        # メッセージコンテンツ構築
        content = []

        # 画像追加（最大3枚）
        if images:
            for idx, img_data in enumerate(images[:3]):
                try:
                    # 画像のメディアタイプを推定
                    media_type = self._detect_media_type(img_data)
                    b64_data = base64.b64encode(img_data).decode("utf-8")
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_data,
                        },
                    })
                    logger.info(f"Added image {idx + 1} to content ({media_type})")
                except Exception as e:
                    logger.warning(f"Failed to process image {idx + 1}: {str(e)}")

        # テキストプロンプト追加
        content.append({"type": "text", "text": prompt})

        # 非同期APIで直接呼び出し
        response = await self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8192,
            temperature=temperature,
            messages=[{"role": "user", "content": content}],
        )

        # レスポンスからテキスト抽出
        if response.content and len(response.content) > 0:
            result_text = response.content[0].text
            logger.debug(f"Claude API response received: {len(result_text)} characters")
            return result_text

        raise ExternalAPIError(
            message="AI審査の結果が空でした。",
            details={"stop_reason": response.stop_reason},
        )

    def _detect_media_type(self, image_data: bytes) -> str:
        """画像バイナリからメディアタイプを推定"""
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        if image_data[:2] == b'\xff\xd8':
            return "image/jpeg"
        if image_data[:4] == b'GIF8':
            return "image/gif"
        if image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            return "image/webp"
        return "image/jpeg"  # デフォルト

    async def _exponential_backoff(self, attempt: int) -> None:
        delay = INITIAL_RETRY_DELAY * (2 ** attempt)
        logger.info(f"Retrying after {delay} seconds...")
        await asyncio.sleep(delay)

    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """AIの応答からJSON部分を抽出・解析"""
        try:
            json_text = response_text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()

            parsed = json.loads(json_text)
            logger.debug("JSON response parsed successfully")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text[:500]}")
            raise ExternalAPIError(
                message="AI審査の結果を解析できませんでした。",
                details={"error": str(e), "response_preview": response_text[:200]},
            )


def get_rate_limiter() -> RateLimiter:
    """グローバルレートリミッターを取得"""
    return _rate_limiter
