"""
============================================
メタ広告審査チェッカー - pytest設定
============================================
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    return TestClient(app)


@pytest.fixture
def sample_ad_text_only():
    """サンプルリクエスト（テキストのみ）"""
    return {
        "headline": "お得なキャンペーン実施中",
        "description": "高品質な商品を提供しています。今すぐお問い合わせください。",
        "cta": "詳細を見る"
    }


@pytest.fixture
def sample_ad_with_violations():
    """サンプルリクエスト（違反含む）"""
    return {
        "headline": "この薬を飲めば病気が治ります",
        "description": "100%保証！業界最安値で提供します。",
        "cta": "今すぐ購入"
    }


@pytest.fixture
def sample_base64_image():
    """サンプルBase64画像（1x1 PNGピクセル）"""
    # 1x1の透明PNGピクセル
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
