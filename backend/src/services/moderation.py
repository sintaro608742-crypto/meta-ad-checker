"""
============================================
メタ広告審査チェッカー - OpenAI Moderation API連携
============================================

OpenAI Moderation APIを使った補助的な有害コンテンツ検出
"""

import os
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


# --------------------------------------------
# OpenAI Moderation Service
# --------------------------------------------

class ModerationService:
    """OpenAI Moderation APIサービスクラス（オプション）"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: OpenAI APIキー（未指定の場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. Moderation API will be unavailable.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("ModerationService initialized")

    def is_available(self) -> bool:
        """Moderation APIが利用可能かチェック"""
        return self.client is not None

    async def check_content(self, text: str) -> Optional[Dict[str, Any]]:
        """
        テキストコンテンツの有害性をチェック

        Args:
            text: チェック対象のテキスト

        Returns:
            Optional[Dict[str, Any]]: モデレーション結果、またはNone（APIが利用不可の場合）

        モデレーション結果の例:
        {
            "flagged": True,
            "categories": {
                "sexual": False,
                "hate": False,
                "harassment": False,
                "self-harm": False,
                "sexual/minors": False,
                "hate/threatening": False,
                "violence/graphic": False,
                "self-harm/intent": False,
                "self-harm/instructions": False,
                "harassment/threatening": True,
                "violence": False
            },
            "category_scores": {
                "sexual": 0.0001,
                "hate": 0.0002,
                ...
            }
        }
        """
        if not self.is_available():
            logger.debug("Moderation API not available, skipping check")
            return None

        try:
            logger.debug(f"Checking content with Moderation API: {len(text)} characters")

            response = await self.client.moderations.create(
                model="omni-moderation-latest",
                input=text
            )

            result = response.results[0]

            moderation_result = {
                "flagged": result.flagged,
                "categories": result.categories.model_dump(),
                "category_scores": result.category_scores.model_dump(),
            }

            logger.debug(f"Moderation result: flagged={result.flagged}")

            return moderation_result

        except Exception as e:
            logger.warning(f"Moderation API error (non-critical): {str(e)}")
            return None

    def extract_flagged_categories(self, moderation_result: Optional[Dict[str, Any]]) -> list[str]:
        """
        フラグが立ったカテゴリのリストを抽出

        Args:
            moderation_result: check_content()の返り値

        Returns:
            list[str]: フラグが立ったカテゴリ名のリスト
        """
        if not moderation_result or not moderation_result.get("flagged"):
            return []

        flagged_categories = []
        categories = moderation_result.get("categories", {})

        for category, is_flagged in categories.items():
            if is_flagged:
                flagged_categories.append(category)

        return flagged_categories

    def is_nsfw_detected(self, moderation_result: Optional[Dict[str, Any]]) -> bool:
        """
        NSFW（性的・暴力的）コンテンツが検出されたかチェック

        Args:
            moderation_result: check_content()の返り値

        Returns:
            bool: NSFWコンテンツが検出された場合True
        """
        if not moderation_result:
            return False

        categories = moderation_result.get("categories", {})

        # NSFW関連カテゴリ
        nsfw_categories = [
            "sexual",
            "sexual/minors",
            "violence",
            "violence/graphic",
        ]

        return any(categories.get(cat, False) for cat in nsfw_categories)
