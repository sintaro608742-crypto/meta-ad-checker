"""
============================================
メタ広告審査チェッカー - URL取得ユーティリティ
============================================

URLからOGP情報、ページテキスト、画像を取得
"""

import logging
import httpx
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from .errors import ValidationError

logger = logging.getLogger(__name__)

# --------------------------------------------
# Data Classes
# --------------------------------------------

@dataclass
class PageData:
    """ページから取得したデータ"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    og_image_url: Optional[str] = None
    og_image_data: Optional[bytes] = None
    page_text: Optional[str] = None


# --------------------------------------------
# URL Validation
# --------------------------------------------

def validate_url(url: str) -> str:
    """
    URLを検証し、正規化する

    Args:
        url: 検証するURL

    Returns:
        str: 正規化されたURL

    Raises:
        ValidationError: 不正なURLの場合
    """
    if not url:
        raise ValidationError(
            message="URLを入力してください",
            details={"error": "URL is empty"}
        )

    # スキームがない場合はhttpsを追加
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValidationError(
                message="有効なURLを入力してください",
                details={"error": "Invalid URL format", "url": url}
            )
        return url
    except Exception as e:
        raise ValidationError(
            message="URLの解析に失敗しました",
            details={"error": str(e), "url": url}
        )


# --------------------------------------------
# Page Fetching
# --------------------------------------------

async def fetch_page_data(url: str, timeout: float = 15.0) -> PageData:
    """
    URLからページデータを取得

    Args:
        url: 取得するURL
        timeout: タイムアウト秒数

    Returns:
        PageData: 取得したページデータ

    Raises:
        ValidationError: 取得に失敗した場合
    """
    url = validate_url(url)

    logger.info(f"Fetching page data from: {url}")

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; MetaAdChecker/1.0)'
            }
        ) as client:
            # ページHTMLを取得
            response = await client.get(url)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, 'lxml')

            # OGPとメタデータを抽出
            page_data = _extract_metadata(soup, url)

            # ページテキストを抽出
            page_data.page_text = _extract_page_text(soup)

            # OGP画像を取得
            if page_data.og_image_url:
                page_data.og_image_data = await _fetch_image(client, page_data.og_image_url)

            logger.info(f"Page data fetched successfully: title={page_data.title}, has_og_image={page_data.og_image_data is not None}")

            return page_data

    except httpx.TimeoutException:
        raise ValidationError(
            message="ページの取得がタイムアウトしました。URLを確認してください。",
            details={"error": "timeout", "url": url}
        )
    except httpx.HTTPStatusError as e:
        raise ValidationError(
            message=f"ページの取得に失敗しました（HTTPステータス: {e.response.status_code}）",
            details={"error": "http_error", "status_code": e.response.status_code, "url": url}
        )
    except Exception as e:
        logger.error(f"Failed to fetch page: {str(e)}")
        raise ValidationError(
            message="ページの取得に失敗しました。URLを確認してください。",
            details={"error": str(e), "url": url}
        )


# --------------------------------------------
# Metadata Extraction
# --------------------------------------------

def _extract_metadata(soup: BeautifulSoup, base_url: str) -> PageData:
    """
    HTMLからメタデータを抽出

    Args:
        soup: BeautifulSoupオブジェクト
        base_url: ベースURL（相対パス解決用）

    Returns:
        PageData: 抽出したメタデータ
    """
    page_data = PageData(url=base_url)

    # タイトル取得（優先順位: og:title > title tag）
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        page_data.title = og_title['content']
    else:
        title_tag = soup.find('title')
        if title_tag:
            page_data.title = title_tag.get_text(strip=True)

    # 説明文取得（優先順位: og:description > meta description）
    og_desc = soup.find('meta', property='og:description')
    if og_desc and og_desc.get('content'):
        page_data.description = og_desc['content']
    else:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            page_data.description = meta_desc['content']

    # OGP画像URL取得
    og_image = soup.find('meta', property='og:image')
    if og_image and og_image.get('content'):
        image_url = og_image['content']
        # 相対パスの場合は絶対パスに変換
        page_data.og_image_url = urljoin(base_url, image_url)

    return page_data


def _extract_page_text(soup: BeautifulSoup, max_length: int = 3000) -> str:
    """
    HTMLから本文テキストを抽出

    Args:
        soup: BeautifulSoupオブジェクト
        max_length: 最大文字数

    Returns:
        str: 抽出したテキスト
    """
    # 不要な要素を削除
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
        element.decompose()

    # メインコンテンツを優先的に取得
    main_content = soup.find('main') or soup.find('article') or soup.find('body')

    if main_content:
        # テキストを取得（空白を正規化）
        text = main_content.get_text(separator=' ', strip=True)
        # 連続する空白を1つに
        text = ' '.join(text.split())
        # 最大文字数で切り詰め
        if len(text) > max_length:
            text = text[:max_length] + '...'
        return text

    return ""


# --------------------------------------------
# Image Fetching
# --------------------------------------------

async def _fetch_image(client: httpx.AsyncClient, image_url: str, max_size: int = 10 * 1024 * 1024) -> Optional[bytes]:
    """
    画像URLから画像データを取得

    Args:
        client: HTTPクライアント
        image_url: 画像URL
        max_size: 最大サイズ（バイト）

    Returns:
        Optional[bytes]: 画像データ、取得失敗時はNone
    """
    try:
        response = await client.get(image_url)
        response.raise_for_status()

        # サイズチェック
        if len(response.content) > max_size:
            logger.warning(f"Image too large: {len(response.content)} bytes")
            return None

        # Content-Typeチェック
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"Not an image: {content_type}")
            return None

        logger.info(f"Image fetched: {len(response.content)} bytes")
        return response.content

    except Exception as e:
        logger.warning(f"Failed to fetch image: {str(e)}")
        return None
