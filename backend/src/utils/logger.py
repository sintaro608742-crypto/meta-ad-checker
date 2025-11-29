"""
============================================
メタ広告審査チェッカー - ロギング設定
============================================

統一されたログフォーマットと設定を提供
"""

import logging
import sys
from typing import Optional


# --------------------------------------------
# Logging Configuration
# --------------------------------------------

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    ロギングを設定

    Args:
        level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: ログファイルのパス（Noneの場合は標準出力のみ）
    """
    # ログレベルの変換
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # ログフォーマット
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # ハンドラーのリスト
    handlers = [logging.StreamHandler(sys.stdout)]

    # ファイルハンドラーの追加（指定された場合）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)

    # 基本設定
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )

    # サードパーティライブラリのログレベルを調整
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={level}")


def get_logger(name: str) -> logging.Logger:
    """
    指定された名前のロガーを取得

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        logging.Logger: ロガーインスタンス
    """
    return logging.getLogger(name)
