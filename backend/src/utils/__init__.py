"""
メタ広告審査チェッカー - ユーティリティモジュール
"""

from .errors import (
    ValidationError,
    FileSizeExceededError,
    UnsupportedMediaTypeError,
    RateLimitExceededError,
    ExternalAPIError,
    ServiceUnavailableError,
    create_error_response,
    validate_request_has_content,
    http_exception_handler,
    general_exception_handler,
)

from .image import (
    decode_base64_image,
    encode_image_to_base64,
    validate_image_size,
    validate_image_format,
    process_and_validate_image,
    extract_mime_type_from_base64,
    optimize_image_for_ai,
)

from .logger import setup_logging, get_logger

__all__ = [
    # Error handling
    "ValidationError",
    "FileSizeExceededError",
    "UnsupportedMediaTypeError",
    "RateLimitExceededError",
    "ExternalAPIError",
    "ServiceUnavailableError",
    "create_error_response",
    "validate_request_has_content",
    "http_exception_handler",
    "general_exception_handler",
    # Image processing
    "decode_base64_image",
    "encode_image_to_base64",
    "validate_image_size",
    "validate_image_format",
    "process_and_validate_image",
    "extract_mime_type_from_base64",
    "optimize_image_for_ai",
    # Logging
    "setup_logging",
    "get_logger",
]
