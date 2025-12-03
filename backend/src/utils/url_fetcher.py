"""
============================================
メタ広告審査チェッカー - URL取得ユーティリティ
============================================

URLからOGP情報、ページテキスト、画像を取得
"""

import logging
import httpx
import re
import json
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from .errors import ValidationError

logger = logging.getLogger(__name__)

# --------------------------------------------
# Data Classes
# --------------------------------------------

@dataclass
class PageImage:
    """ページから取得した画像"""
    url: str
    data: bytes
    source: str  # 'ogp', 'hero', 'main'

@dataclass
class PageData:
    """ページから取得したデータ"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    og_image_url: Optional[str] = None
    og_image_data: Optional[bytes] = None
    page_text: Optional[str] = None
    # 主要画像リスト（OGP画像を含む）
    images: Optional[List[PageImage]] = None


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

            # 画像リストを初期化
            page_data.images = []

            # OGP画像を取得
            if page_data.og_image_url:
                page_data.og_image_data = await _fetch_image(client, page_data.og_image_url)
                if page_data.og_image_data:
                    page_data.images.append(PageImage(
                        url=page_data.og_image_url,
                        data=page_data.og_image_data,
                        source='ogp'
                    ))

            # LP内の主要画像を取得（最大2枚追加）
            # htmlを渡してVue.js等のJSON埋め込み画像も抽出
            # サイズ制限で失敗する画像があるため、多めに候補を取得
            main_image_urls = _extract_main_images(soup, url, max_images=10, html=html)
            for img_url in main_image_urls:
                # OGP画像と重複しない場合のみ取得
                if img_url != page_data.og_image_url:
                    img_data = await _fetch_image(client, img_url)
                    if img_data:
                        page_data.images.append(PageImage(
                            url=img_url,
                            data=img_data,
                            source='main'
                        ))
                        if len(page_data.images) >= 3:  # 合計3枚まで
                            break

            logger.info(f"Page data fetched successfully: title={page_data.title}, images={len(page_data.images)}")

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


def _extract_images_from_json_data(html: str, base_url: str) -> List[str]:
    """
    Vue.js/React等のJSON埋め込みデータから画像URLを抽出

    Args:
        html: 生のHTML文字列
        base_url: ベースURL（相対パス解決用）

    Returns:
        List[str]: 画像URLのリスト
    """
    image_urls = []

    # v-bind:data='...' や data='...' 内のJSONを探す
    # UTAGE等のSPA/Vue.jsサイトで使用されるパターン
    json_patterns = [
        r'v-bind:data=\'([^\']+)\'',
        r':data=\'([^\']+)\'',
        r'data-elements=\'([^\']+)\'',
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            try:
                # HTMLエンティティをデコード
                decoded = match.replace('&quot;', '"').replace('&#039;', "'")
                data = json.loads(decoded)

                # 再帰的に画像URLを探す
                def find_images(obj, urls):
                    if isinstance(obj, dict):
                        # "type": "image" と "img_src" のパターン
                        if obj.get('type') == 'image' and obj.get('img_src'):
                            img_url = obj['img_src'].replace('\\/', '/')
                            if _is_valid_image_url(img_url):
                                full_url = urljoin(base_url, img_url)
                                if full_url not in urls:
                                    urls.append(full_url)
                        # "image-text" タイプも対応（プロフィール画像等）
                        elif obj.get('type') == 'image-text' and obj.get('img_src'):
                            img_url = obj['img_src'].replace('\\/', '/')
                            if _is_valid_image_url(img_url):
                                full_url = urljoin(base_url, img_url)
                                if full_url not in urls:
                                    urls.append(full_url)
                        # 子要素を再帰的に探索
                        for key, value in obj.items():
                            find_images(value, urls)
                    elif isinstance(obj, list):
                        for item in obj:
                            find_images(item, urls)

                find_images(data, image_urls)
            except (json.JSONDecodeError, TypeError) as e:
                logger.debug(f"Failed to parse JSON data: {e}")
                continue

    logger.info(f"Extracted {len(image_urls)} images from JSON data")
    return image_urls


def _extract_main_images(soup: BeautifulSoup, base_url: str, max_images: int = 2, html: str = None) -> List[str]:
    """
    LP内の主要画像URLを抽出

    Args:
        soup: BeautifulSoupオブジェクト
        base_url: ベースURL（相対パス解決用）
        max_images: 取得する最大画像数
        html: 生のHTML文字列（JSON埋め込み画像抽出用）

    Returns:
        List[str]: 画像URLのリスト
    """
    image_urls = []

    # 0. Vue.js/React等のJSON埋め込み画像を優先的に抽出
    if html:
        json_images = _extract_images_from_json_data(html, base_url)
        for img_url in json_images[:max_images]:
            if img_url not in image_urls:
                image_urls.append(img_url)
                if len(image_urls) >= max_images:
                    logger.info(f"Found {len(image_urls)} images from JSON data")
                    return image_urls

    # 1. hero/mainセクション内の画像を優先
    hero_selectors = [
        'header img',
        'section img',
        '.hero img',
        '.main-visual img',
        '.mv img',
        '.kv img',
        '.top img',
        '.banner img',
        '[class*="hero"] img',
        '[class*="main"] img',
        '[class*="visual"] img',
    ]

    for selector in hero_selectors:
        try:
            for img in soup.select(selector)[:3]:
                src = img.get('src') or img.get('data-src')
                if src and _is_valid_image_url(src):
                    full_url = urljoin(base_url, src)
                    if full_url not in image_urls:
                        image_urls.append(full_url)
                        if len(image_urls) >= max_images:
                            return image_urls
        except Exception:
            continue

    # 2. 大きな画像を探す（width/height属性がある場合）
    for img in soup.find_all('img')[:20]:
        src = img.get('src') or img.get('data-src')
        if not src or not _is_valid_image_url(src):
            continue

        # サイズ属性をチェック
        width = img.get('width', '')
        height = img.get('height', '')
        try:
            w = int(str(width).replace('px', ''))
            h = int(str(height).replace('px', ''))
            if w >= 300 or h >= 200:  # 比較的大きな画像
                full_url = urljoin(base_url, src)
                if full_url not in image_urls:
                    image_urls.append(full_url)
                    if len(image_urls) >= max_images:
                        return image_urls
        except (ValueError, TypeError):
            pass

    # 3. それでも見つからない場合、最初の数枚の画像を取得
    for img in soup.find_all('img')[:10]:
        src = img.get('src') or img.get('data-src')
        if src and _is_valid_image_url(src):
            full_url = urljoin(base_url, src)
            if full_url not in image_urls:
                image_urls.append(full_url)
                if len(image_urls) >= max_images:
                    return image_urls

    return image_urls


def _is_valid_image_url(url: str) -> bool:
    """画像URLとして有効かチェック"""
    if not url:
        return False
    # data:URLやsvgは除外
    if url.startswith('data:'):
        return False
    # 小さなアイコン系を除外
    lower_url = url.lower()
    exclude_patterns = ['icon', 'logo', 'favicon', 'sprite', 'loading', 'placeholder', '.svg', '.gif']
    return not any(pattern in lower_url for pattern in exclude_patterns)


def _extract_page_text(soup: BeautifulSoup, max_length: int = 5000) -> str:
    """
    HTMLから本文テキストを抽出（見出しタグを優先）

    Args:
        soup: BeautifulSoupオブジェクト
        max_length: 最大文字数

    Returns:
        str: 抽出したテキスト（構造化）
    """
    # soup のコピーを作成（元のsoupを変更しないため）
    from copy import copy
    soup_copy = copy(soup)

    # 完全に不要な要素のみを削除（script, style, noscript）
    for element in soup_copy(['script', 'style', 'noscript']):
        element.decompose()

    extracted_parts = []

    # 1. 見出しタグを優先的に抽出（h1 > h2 > h3）
    for tag in ['h1', 'h2', 'h3']:
        for element in soup_copy.find_all(tag):
            text = element.get_text(strip=True)
            if text and len(text) > 2:  # 2文字以上のみ
                extracted_parts.append(f"【{tag.upper()}】{text}")

    # 2. headerやhero内のキャッチコピー（重要な広告文言が多い）
    hero_sections = soup_copy.find_all(['header', 'section'], class_=lambda x: x and any(
        keyword in str(x).lower() for keyword in ['hero', 'main-visual', 'mv', 'kv', 'top', 'first']
    ))
    for section in hero_sections[:3]:  # 最大3セクション
        for p in section.find_all(['p', 'span', 'div'], recursive=True):
            text = p.get_text(strip=True)
            if text and 5 < len(text) < 200:  # 短すぎず長すぎないテキスト
                if text not in ' '.join(extracted_parts):  # 重複チェック
                    extracted_parts.append(f"【ヒーロー】{text}")

    # 3. 強調テキスト（strong, b, em）
    for element in soup_copy.find_all(['strong', 'b', 'em'])[:20]:
        text = element.get_text(strip=True)
        if text and 3 < len(text) < 100:
            if text not in ' '.join(extracted_parts):
                extracted_parts.append(f"【強調】{text}")

    # 4. メインコンテンツの段落テキスト
    main_content = soup_copy.find('main') or soup_copy.find('article') or soup_copy.find('body')
    if main_content:
        # nav, footer, aside内のテキストは除外
        for unwanted in main_content.find_all(['nav', 'footer', 'aside']):
            unwanted.decompose()

        for p in main_content.find_all('p')[:30]:  # 最大30段落
            text = p.get_text(strip=True)
            if text and len(text) > 10:
                if text not in ' '.join(extracted_parts):
                    extracted_parts.append(text)

    # 5. リスト項目（特徴や利点が書かれていることが多い）
    for li in soup_copy.find_all('li')[:20]:
        text = li.get_text(strip=True)
        if text and 5 < len(text) < 200:
            if text not in ' '.join(extracted_parts):
                extracted_parts.append(f"・{text}")

    # 結合
    full_text = '\n'.join(extracted_parts)

    # 連続する空白を1つに
    full_text = ' '.join(full_text.split())

    # 最大文字数で切り詰め
    if len(full_text) > max_length:
        full_text = full_text[:max_length] + '...'

    logger.info(f"Extracted page text: {len(full_text)} chars, {len(extracted_parts)} parts")

    return full_text


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
