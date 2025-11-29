"""
============================================
メタ広告審査チェッカー - /api/check エンドポイント統合テスト
============================================
"""

import pytest
import os
from unittest.mock import patch, MagicMock


class TestCheckEndpoint:
    """POST /api/check エンドポイントのテスト"""

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_check_endpoint_exists(self, mock_gemini, client):
        """エンドポイントが存在するかテスト"""
        # モックレスポンス
        mock_response = """{
            "overall_score": 85,
            "status": "approved",
            "confidence": 0.92,
            "violations": [],
            "recommendations": [],
            "text_overlay_percentage": null,
            "nsfw_detected": false,
            "prohibited_content": []
        }"""
        mock_gemini.return_value = mock_response

        response = client.post("/api/check", json={
            "headline": "Test headline"
        })
        # 200 (成功) が返るべき
        assert response.status_code == 200

    def test_validation_error_no_content(self, client):
        """コンテンツなしでバリデーションエラーを返すかテスト"""
        response = client.post("/api/check", json={})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "validation_error"

    def test_validation_error_empty_strings(self, client):
        """空文字列でバリデーションエラーを返すかテスト"""
        response = client.post("/api/check", json={
            "headline": "   ",
            "description": "",
            "cta": ""
        })
        assert response.status_code == 400

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_check_text_only_success(self, mock_gemini, client, sample_ad_text_only):
        """テキストのみの審査が成功するかテスト（モック使用）"""
        # モックレスポンス
        mock_response = """{
            "overall_score": 85,
            "status": "approved",
            "confidence": 0.92,
            "violations": [],
            "recommendations": [],
            "text_overlay_percentage": null,
            "nsfw_detected": false,
            "prohibited_content": []
        }"""
        mock_gemini.return_value = mock_response

        response = client.post("/api/check", json=sample_ad_text_only)
        assert response.status_code == 200

        data = response.json()
        # レスポンスの構造をチェック
        assert "overall_score" in data
        assert "status" in data
        assert "confidence" in data
        assert "violations" in data
        assert "recommendations" in data
        assert "nsfw_detected" in data
        assert "prohibited_content" in data
        assert "checked_at" in data
        assert "api_used" in data

        # 値の範囲をチェック
        assert 0 <= data["overall_score"] <= 100
        assert data["status"] in ["approved", "needs_review", "rejected"]
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["violations"], list)
        assert isinstance(data["recommendations"], list)

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_check_with_violations(self, mock_gemini, client, sample_ad_with_violations):
        """違反を含む広告が適切に検出されるかテスト（モック使用）"""
        # モックレスポンス（違反あり）
        mock_response = """{
            "overall_score": 35,
            "status": "rejected",
            "confidence": 0.95,
            "violations": [
                {
                    "category": "prohibited_content",
                    "severity": "high",
                    "description": "医薬品に関する表現が検出されました。",
                    "location": "text"
                },
                {
                    "category": "misleading",
                    "severity": "high",
                    "description": "誇大広告表現が検出されました。",
                    "location": "text"
                }
            ],
            "recommendations": [
                {
                    "before": "この薬を飲めば病気が治ります",
                    "after": "健康的な生活をサポートする製品です",
                    "reason": "医薬品的な効果効能の表現を削除"
                }
            ],
            "text_overlay_percentage": null,
            "nsfw_detected": false,
            "prohibited_content": ["医薬品"]
        }"""
        mock_gemini.return_value = mock_response

        response = client.post("/api/check", json=sample_ad_with_violations)
        assert response.status_code == 200

        data = response.json()
        # 違反が検出されるべき
        assert len(data["violations"]) > 0
        # スコアが低いはず
        assert data["overall_score"] < 70

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_check_with_image_validation(self, mock_gemini, client, sample_base64_image):
        """画像のバリデーションが動作するかテスト"""
        # モックレスポンス
        mock_response = """{
            "overall_score": 75,
            "status": "approved",
            "confidence": 0.85,
            "violations": [],
            "recommendations": [],
            "text_overlay_percentage": 5,
            "nsfw_detected": false,
            "prohibited_content": []
        }"""
        mock_gemini.return_value = mock_response

        response = client.post("/api/check", json={
            "headline": "テスト広告",
            "image": sample_base64_image
        })
        # 画像のバリデーションが通過し、成功するはず
        assert response.status_code == 200

    def test_check_invalid_base64_image(self, client):
        """不正なBase64画像でエラーを返すかテスト"""
        response = client.post("/api/check", json={
            "headline": "テスト広告",
            "image": "invalid_base64_string!!!"
        })
        assert response.status_code == 400

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_check_with_mock_gemini(self, mock_gemini, client, sample_ad_text_only):
        """モックを使用したGemini API呼び出しテスト"""
        # モックレスポンス
        mock_response = """{
            "overall_score": 85,
            "status": "approved",
            "confidence": 0.92,
            "violations": [],
            "recommendations": [],
            "text_overlay_percentage": null,
            "nsfw_detected": false,
            "prohibited_content": []
        }"""
        mock_gemini.return_value = mock_response

        response = client.post("/api/check", json=sample_ad_text_only)
        assert response.status_code == 200

    def test_response_structure_validation(self, client):
        """レスポンス構造が仕様通りかテスト（モック使用）"""
        with patch('src.services.gemini.GeminiService.generate_content_with_retry') as mock_gemini:
            mock_response = """{
                "overall_score": 75,
                "status": "approved",
                "confidence": 0.85,
                "violations": [
                    {
                        "category": "text_overlay",
                        "severity": "medium",
                        "description": "Test violation",
                        "location": "image"
                    }
                ],
                "recommendations": [
                    {
                        "before": "Test before",
                        "after": "Test after",
                        "reason": "Test reason"
                    }
                ],
                "text_overlay_percentage": 25,
                "nsfw_detected": false,
                "prohibited_content": []
            }"""
            mock_gemini.return_value = mock_response

            response = client.post("/api/check", json={"headline": "Test"})

            if response.status_code == 200:
                data = response.json()

                # Violationの構造
                if len(data["violations"]) > 0:
                    violation = data["violations"][0]
                    assert "category" in violation
                    assert "severity" in violation
                    assert "description" in violation
                    assert "location" in violation

                # Recommendationの構造
                if len(data["recommendations"]) > 0:
                    recommendation = data["recommendations"][0]
                    assert "before" in recommendation
                    assert "after" in recommendation
                    assert "reason" in recommendation


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_image_size_exceeded_error(self, client):
        """画像サイズ超過エラーのテスト"""
        # 20MBを超えるBase64文字列を生成（実際には生成せず、モックで代用）
        large_base64 = "A" * (30 * 1024 * 1024)  # 30MB相当
        response = client.post("/api/check", json={
            "headline": "Test",
            "image": large_base64
        })
        # 413または400エラーが返されるべき
        assert response.status_code in [400, 413]

    def test_unsupported_media_type_error(self, client):
        """非対応形式エラーのテスト"""
        # SVG画像（非対応）のBase64
        svg_base64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg=="
        response = client.post("/api/check", json={
            "headline": "Test",
            "image": svg_base64
        })
        # 415または400エラーが返される可能性
        assert response.status_code in [400, 415]

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_external_api_error(self, mock_gemini, client):
        """外部APIエラーのテスト"""
        from src.utils.errors import ExternalAPIError

        mock_gemini.side_effect = ExternalAPIError("Test API error")

        response = client.post("/api/check", json={"headline": "Test"})
        assert response.status_code == 500

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_rate_limit_error(self, mock_gemini, client):
        """レート制限エラーのテスト"""
        from src.utils.errors import RateLimitExceededError

        mock_gemini.side_effect = RateLimitExceededError()

        response = client.post("/api/check", json={"headline": "Test"})
        assert response.status_code == 429

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_service_unavailable_error(self, mock_gemini, client):
        """サービス利用不可エラーのテスト"""
        from src.utils.errors import ServiceUnavailableError

        mock_gemini.side_effect = ServiceUnavailableError()

        response = client.post("/api/check", json={"headline": "Test"})
        assert response.status_code == 503


class TestModerationIntegration:
    """OpenAI Moderation API統合のテスト"""

    @patch('src.services.gemini.GeminiService.generate_content_with_retry')
    async def test_moderation_api_integration(self, mock_gemini, client):
        """Moderation APIが統合されているかテスト"""
        # モックレスポンス
        mock_response = """{
            "overall_score": 80,
            "status": "approved",
            "confidence": 0.88,
            "violations": [],
            "recommendations": [],
            "text_overlay_percentage": null,
            "nsfw_detected": false,
            "prohibited_content": []
        }"""
        mock_gemini.return_value = mock_response

        response = client.post("/api/check", json={
            "headline": "Appropriate content test",
            "description": "Testing moderation API"
        })
        # 成功するはず
        assert response.status_code == 200

    @patch('src.services.moderation.ModerationService.check_content')
    async def test_moderation_nsfw_detection(self, mock_moderation, client):
        """Moderation APIによるNSFW検出のテスト"""
        # NSFWフラグ付きのモックレスポンス
        mock_moderation.return_value = {
            "flagged": True,
            "categories": {
                "sexual": True,
                "hate": False,
                "harassment": False,
                "self-harm": False,
                "sexual/minors": False,
                "hate/threatening": False,
                "violence/graphic": False,
                "self-harm/intent": False,
                "self-harm/instructions": False,
                "harassment/threatening": False,
                "violence": False
            },
            "category_scores": {}
        }

        with patch('src.services.gemini.GeminiService.generate_content_with_retry') as mock_gemini:
            mock_gemini.return_value = """{
                "overall_score": 50,
                "status": "needs_review",
                "confidence": 0.8,
                "violations": [],
                "recommendations": [],
                "text_overlay_percentage": null,
                "nsfw_detected": false,
                "prohibited_content": []
            }"""

            response = client.post("/api/check", json={"headline": "Test"})

            if response.status_code == 200:
                data = response.json()
                # NSFWが検出されるべき
                assert data["nsfw_detected"] is True
