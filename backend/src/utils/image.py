"""
============================================
メタ広告審査チェッカー - 画像処理ユーティリティ
============================================

Base64エンコード/デコード、形式検証、サイズ制限を提供
"""

import base64
import io
import logging
from typing import Optional, Tuple
from PIL import Image

from .errors import ValidationError, FileSizeExceededError, UnsupportedMediaTypeError

logger = logging.getLogger(__name__)


# --------------------------------------------
# Constants
# --------------------------------------------

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 20MB

SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}
SUPPORTED_MIME_TYPES = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP"
}


# --------------------------------------------
# Base64 Helpers
# --------------------------------------------

def decode_base64_image(base64_string: str) -> bytes:
    """
    Base64エンコードされた画像をデコード

    Args:
        base64_string: Base64エンコードされた画像文字列（data:image/...;base64,を含む場合は自動削除）

    Returns:
        bytes: デコードされた画像データ

    Raises:
        ValidationError: Base64デコードに失敗した場合
    """
    try:
        # data:image/...;base64, プレフィックスを削除
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]

        # Base64デコード
        image_data = base64.b64decode(base64_string)
        return image_data

    except Exception as e:
        logger.error(f"Base64 decode error: {str(e)}")
        raise ValidationError(
            message="画像データのデコードに失敗しました。正しい形式のBase64文字列を送信してください。",
            details={"error": str(e)}
        )


def encode_image_to_base64(image_data: bytes) -> str:
    """
    画像データをBase64エンコード

    Args:
        image_data: 画像のバイナリデータ

    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(image_data).decode("utf-8")


# --------------------------------------------
# Image Validation
# --------------------------------------------

def validate_image_size(image_data: bytes) -> None:
    """
    画像サイズを検証（20MB制限）

    Args:
        image_data: 画像のバイナリデータ

    Raises:
        FileSizeExceededError: ファイルサイズが20MBを超えている場合
    """
    size_mb = len(image_data) / (1024 * 1024)

    if len(image_data) > MAX_FILE_SIZE_BYTES:
        raise FileSizeExceededError(
            message=f"ファイルサイズが{MAX_FILE_SIZE_MB}MBを超えています（{size_mb:.2f}MB）。画像を圧縮してください。",
            details={
                "current_size_mb": round(size_mb, 2),
                "max_size_mb": MAX_FILE_SIZE_MB
            }
        )


def validate_image_format(image_data: bytes) -> str:
    """
    画像形式を検証（JPEG/PNG/WebPのみ許可）

    Args:
        image_data: 画像のバイナリデータ

    Returns:
        str: 画像フォーマット名（"JPEG", "PNG", "WEBP"）

    Raises:
        UnsupportedMediaTypeError: 非対応の画像形式の場合
        ValidationError: 画像ファイルが破損している場合
    """
    try:
        # PILで画像を開いてフォーマット検証
        image = Image.open(io.BytesIO(image_data))
        image_format = image.format

        if image_format not in SUPPORTED_FORMATS:
            raise UnsupportedMediaTypeError(
                message=f"対応していない画像形式です（{image_format}）。JPEG、PNG、WebPのいずれかを使用してください。",
                details={
                    "detected_format": image_format,
                    "supported_formats": list(SUPPORTED_FORMATS)
                }
            )

        return image_format

    except UnsupportedMediaTypeError:
        raise

    except Exception as e:
        logger.error(f"Image format validation error: {str(e)}")
        raise ValidationError(
            message="画像ファイルが破損しているか、正しい形式ではありません。",
            details={"error": str(e)}
        )


def get_image_dimensions(image_data: bytes) -> Tuple[int, int]:
    """
    画像の寸法を取得

    Args:
        image_data: 画像のバイナリデータ

    Returns:
        Tuple[int, int]: (width, height)
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        return image.size
    except Exception as e:
        logger.error(f"Failed to get image dimensions: {str(e)}")
        return (0, 0)


# --------------------------------------------
# Comprehensive Image Processing
# --------------------------------------------

def process_and_validate_image(base64_string: str) -> Tuple[bytes, str]:
    """
    Base64画像を総合的に処理・検証

    Args:
        base64_string: Base64エンコードされた画像文字列

    Returns:
        Tuple[bytes, str]: (画像データ, フォーマット名)

    Raises:
        ValidationError: デコードまたは画像の破損
        FileSizeExceededError: サイズ超過
        UnsupportedMediaTypeError: 非対応形式
    """
    # 1. Base64デコード
    image_data = decode_base64_image(base64_string)

    # 2. サイズ検証
    validate_image_size(image_data)

    # 3. 形式検証
    image_format = validate_image_format(image_data)

    logger.info(f"Image validated successfully: format={image_format}, size={len(image_data)/1024:.2f}KB")

    return image_data, image_format


def extract_mime_type_from_base64(base64_string: str) -> Optional[str]:
    """
    Base64文字列からMIMEタイプを抽出

    Args:
        base64_string: Base64エンコードされた画像文字列（data:image/...;base64,を含む場合）

    Returns:
        Optional[str]: MIMEタイプ（例: "image/jpeg"）、プレフィックスがない場合はNone
    """
    if not base64_string.startswith("data:"):
        return None

    try:
        # data:image/jpeg;base64,... から image/jpeg を抽出
        mime_type = base64_string.split(";")[0].split(":")[1]
        return mime_type
    except (IndexError, ValueError):
        return None


# --------------------------------------------
# Image Optimization (Optional)
# --------------------------------------------

def optimize_image_for_ai(image_data: bytes, max_dimension: int = 2048) -> bytes:
    """
    AI処理用に画像を最適化（必要に応じてリサイズ）

    Args:
        image_data: 画像のバイナリデータ
        max_dimension: 最大寸法（デフォルト: 2048px）

    Returns:
        bytes: 最適化された画像データ
    """
    try:
        image = Image.open(io.BytesIO(image_data))

        # 画像が大きすぎる場合はリサイズ
        width, height = image.size
        if width > max_dimension or height > max_dimension:
            # アスペクト比を維持してリサイズ
            ratio = min(max_dimension / width, max_dimension / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            logger.info(f"Image resized: {width}x{height} -> {new_size[0]}x{new_size[1]}")

        # 最適化された画像をバイトに変換
        output = io.BytesIO()
        image_format = image.format or "PNG"
        image.save(output, format=image_format, optimize=True, quality=85)
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Image optimization failed, using original: {str(e)}")
        return image_data
