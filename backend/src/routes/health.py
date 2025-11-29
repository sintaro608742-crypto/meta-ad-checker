"""
============================================
メタ広告審査チェッカー - ヘルスチェックエンドポイント
============================================

スライス1-A: ヘルスチェック実装
"""

from fastapi import APIRouter
from ..types import HealthCheckResponse
from ..utils import get_logger

logger = get_logger(__name__)

# ルーター作成
router = APIRouter(
    prefix="/api",
    tags=["health"]
)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    ヘルスチェックエンドポイント

    システムの稼働状態を確認するためのエンドポイント。
    デプロイ環境（Cloud Run等）のヘルスチェックやモニタリングに使用。

    Returns:
        HealthCheckResponse: システムステータスとタイムスタンプ
    """
    logger.info("Health check requested")
    return HealthCheckResponse.create_healthy()
