"""
============================================
メタ広告審査チェッカー - エラーハンドリングユーティリティ
============================================

統一されたエラーレスポンスフォーマットとカスタムHTTP例外を提供
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

from ..types import ApiError

logger = logging.getLogger(__name__)


# --------------------------------------------
# Custom HTTP Exceptions
# --------------------------------------------

class ValidationError(HTTPException):
    """バリデーションエラー（400）"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_detail("validation_error", message, details)
        )


class FileSizeExceededError(HTTPException):
    """ファイルサイズ超過エラー（413）"""
    def __init__(self, message: str = "ファイルサイズが20MBを超えています。画像を圧縮してください。", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=create_error_detail("file_size_exceeded", message, details)
        )


class UnsupportedMediaTypeError(HTTPException):
    """非対応形式エラー（415）"""
    def __init__(self, message: str = "対応していない画像形式です。JPEG、PNG、WebPのいずれかを使用してください。", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=create_error_detail("unsupported_media_type", message, details)
        )


class RateLimitExceededError(HTTPException):
    """レート制限超過エラー（429）"""
    def __init__(self, message: str = "リクエスト制限を超えました。しばらく待ってから再試行してください。", retry_after: Optional[int] = None):
        details = {"retry_after_seconds": retry_after} if retry_after else None
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=create_error_detail("rate_limit_exceeded", message, details)
        )


class ExternalAPIError(HTTPException):
    """外部APIエラー（500）"""
    def __init__(self, message: str = "外部サービスとの通信でエラーが発生しました。", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_detail("external_api_error", message, details)
        )


class ServiceUnavailableError(HTTPException):
    """サービス利用不可エラー（503）"""
    def __init__(self, message: str = "サービスが一時的に利用できません。時間を置いて再試行してください。", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=create_error_detail("service_unavailable", message, details)
        )


# --------------------------------------------
# Error Response Helpers
# --------------------------------------------

def create_error_detail(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """エラーレスポンスの詳細を作成"""
    error_detail = {
        "error": error_type,
        "message": message
    }
    if details:
        error_detail["details"] = details
    return error_detail


def create_error_response(error_type: str, message: str, status_code: int, details: Optional[Dict[str, Any]] = None) -> JSONResponse:
    """エラーレスポンスを作成"""
    error = ApiError(
        error=error_type,
        message=message,
        details=details
    )
    return JSONResponse(
        status_code=status_code,
        content=error.model_dump()
    )


# --------------------------------------------
# Exception Handlers
# --------------------------------------------

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTPExceptionのハンドラー"""
    # カスタムHTTPExceptionの場合は詳細情報を保持
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    # 通常のHTTPExceptionの場合は標準フォーマットに変換
    return create_error_response(
        error_type="http_error",
        message=str(exc.detail),
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """一般的な例外のハンドラー"""
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True)

    return create_error_response(
        error_type="internal_server_error",
        message="予期しないエラーが発生しました。",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"error_type": type(exc).__name__}
    )


# --------------------------------------------
# Validation Helpers
# --------------------------------------------

def validate_request_has_content(request) -> None:
    """リクエストにコンテンツが存在するか検証"""
    if not request.has_content():
        raise ValidationError(
            message="テキストまたは画像のいずれかを入力してください。",
            details={
                "fields": ["headline", "description", "cta", "image", "image_url"]
            }
        )
