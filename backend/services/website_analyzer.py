"""
网站爬取和分析模块
支持 JavaScript 渲染、反爬虫处理、并发控制和缓存机制
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, urljoin
import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta
import random

# 用户代理池（反爬虫）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# 缓存配置
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
CACHE_EXPIRY_HOURS = 24

# 并发控制
SEMAPHORE = asyncio.Semaphore(5)  # 最多 5 个并发请求

# 请求延迟配置（反爬虫）
REQUEST_DELAY_MIN = 1.0  # 秒
REQUEST_DELAY_MAX = 3.0  # 秒


def _get_cache_key(url: str) -> str:
    """生成 URL 的缓存键"""
    return hashlib.md5(url.encode()).hexdigest()


def _load_from_cache(url: str) -> Optional[Dict]:
    """从缓存加载数据"""
    cache_file = os.path.join(CACHE_DIR, f"{_get_cache_key(url)}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get('_cached_at', ''))
                if datetime.now() - cached_time < timedelta(hours=CACHE_EXPIRY_HOURS):
                    return data
        except Exception as e:
            print(f"缓存读取失败：{e}")
    return None


def _save_to_cache(url: str, data: Dict):
    """保存数据到缓存"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{_get_cache_key(url)}.json")
    data['_cached_at'] = datetime.now().isoformat()
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"缓存写入失败：{e}")


def _get_random_user_agent() -> str:
    """随机选择一个用户代理"""
    return random.choice(USER_AGENTS)


async def _random_delay():
    """随机延迟（反爬虫）"""
    delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
    await asyncio.sleep(delay)


async def analyze(url: str, use_playwright: bool = False) -> Optional[Dict]:
    """
    分析网站并返回结构化数据
    
    Args:
        url: 网站 URL
        use_playwright: 是否使用 Playwright 渲染 JavaScript（默认 False）
    
    Returns:
        网站分析数据字典，失败返回 None
    """
    async with SEMAPHORE:
        # 检查缓存
        cached_data = _load_from_cache(url)
        if cached_data:
            print(f"使用缓存数据：{url}")
            return cached_data
        
        await _random_delay()
        
        try:
            # 获取网页内容
            if use_playwright:
                html = await _fetch_with_playwright(url)
            else:
                html = await _fetch_with_httpx(url)
            
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取基本信息
            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_description': get_meta_description(soup),
                'meta_keywords': get_meta_keywords(soup),
                'content_length': len(html),
                'word_count': count_words(soup),
                'has_privacy_policy': await check_privacy_policy(url),
                'has_about_page': await check_about_page(url),
                'has_contact_page': await check_contact_page(url),
                'images': extract_images(soup, url),
                'images_count': len(extract_images(soup, url)),
                'internal_links': extract_internal_links(soup, url),
                'external_links': extract_external_links(soup, url),
                'links_count': len(soup.find_all('a')),
                'headings': extract_headings(soup),
                'is_https': url.startswith('https://'),
                'load_time': 0,  # Playwright 模式下不精确
                'language': get_language(soup),
                'has_favicon': await check_favicon(url),
                'has_sitemap': await check_sitemap(url),
                'has_robots_txt': await check_robots_txt(url),
            }
            
            # 保存到缓存
            _save_to_cache(url, data)
            
            return data
            
        except Exception as e:
            print(f"分析失败：{url} - {e}")
            return None


async def _fetch_with_httpx(url: str) -> Optional[str]:
    """使用 httpx 获取网页内容"""
    try:
        headers = {
            'User-Agent': _get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"HTTPX 请求失败：{e}")
        return None


async def _fetch_with_playwright(url: str) -> Optional[str]:
    """使用 Playwright 获取渲染后的网页内容（支持 JavaScript）"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                user_agent=_get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080},
            )
            page = await context.new_page()
            
            # 设置请求拦截器（可选：阻止图片等资源加快加载）
            # await page.route('**/*.{png,jpg,jpeg,gif,svg,ico,webp}', lambda route: route.abort())
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待页面完全加载
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # 额外等待动态内容加载
            
            html = await page.content()
            await browser.close()
            return html
            
    except ImportError:
        print("Playwright 未安装，回退到 httpx")
        return await _fetch_with_httpx(url)
    except Exception as e:
        print(f"Playwright 请求失败：{e}")
        return await _fetch_with_httpx(url)


def get_meta_description(soup: BeautifulSoup) -> str:
    """获取 meta description"""
    meta = soup.find('meta', attrs={'name': 'description'})
    if not meta:
        meta = soup.find('meta', attrs={'property': 'og:description'})
    return meta.get('content', '') if meta else ''


def get_meta_keywords(soup: BeautifulSoup) -> str:
    """获取 meta keywords"""
    meta = soup.find('meta', attrs={'name': 'keywords'})
    return meta.get('content', '') if meta else ''


def count_words(soup: BeautifulSoup) -> int:
    """统计页面文字数量"""
    # 移除 script 和 style 标签
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text()
    # 移除多余空白
    lines = (line.strip() for line in text.splitlines())
    text = ' '.join(line for line in lines if line)
    return len(text.split())


def extract_headings(soup: BeautifulSoup) -> Dict:
    """提取标题结构"""
    return {
        'h1': [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
        'h2': [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
        'h3': [h3.get_text(strip=True) for h3 in soup.find_all('h3')],
        'h4': [h4.get_text(strip=True) for h4 in soup.find_all('h4')],
        'h1_count': len(soup.find_all('h1')),
        'h2_count': len(soup.find_all('h2')),
        'h3_count': len(soup.find_all('h3')),
    }


def extract_images(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """提取图片信息"""
    images = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src', '')
        if src:
            full_url = urljoin(base_url, src)
            images.append({
                'url': full_url,
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
            })
    return images[:20]  # 最多返回 20 张图片


def extract_internal_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """提取内部链接"""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    internal_links = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # 检查是否为内部链接
        if parsed.netloc == base_domain or parsed.netloc == '':
            if full_url not in internal_links:
                internal_links.add(full_url)
    
    return list(internal_links)[:50]  # 最多返回 50 个内部链接


def extract_external_links(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """提取外部链接"""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    external_links = []
    seen = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # 检查是否为外部链接
        if parsed.netloc and parsed.netloc != base_domain:
            if full_url not in seen:
                seen.add(full_url)
                external_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True),
                    'domain': parsed.netloc,
                })
    
    return external_links[:50]  # 最多返回 50 个外部链接


def get_language(soup: BeautifulSoup) -> str:
    """检测网站语言"""
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        return html_tag['lang']
    
    # 通过内容简单判断
    text = soup.get_text()[:500]
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if chinese_chars > len(text) * 0.3:
        return 'zh'
    return 'en'


async def check_favicon(url: str) -> bool:
    """检查是否有 favicon"""
    try:
        parsed = urlparse(url)
        favicon_url = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.head(favicon_url)
            return response.status_code == 200
    except:
        return False


async def check_sitemap(url: str) -> bool:
    """检查是否有 sitemap"""
    try:
        parsed = urlparse(url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(sitemap_url)
            return response.status_code == 200 and 'xml' in response.headers.get('content-type', '')
    except:
        return False


async def check_robots_txt(url: str) -> bool:
    """检查是否有 robots.txt"""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(robots_url)
            return response.status_code == 200
    except:
        return False


async def check_privacy_policy(url: str) -> bool:
    """检查是否有隐私政策页面"""
    paths = ['/privacy', '/privacy-policy', '/privacy.html', '/privacy-policy.html', '/privacy-policy/', '/privacy/']
    return await _check_page_exists(url, paths)


async def check_about_page(url: str) -> bool:
    """检查是否有关于我们页面"""
    paths = ['/about', '/about-us', '/about.html', '/about-us.html', '/about/', '/about-us/', '/about-us.html']
    return await _check_page_exists(url, paths)


async def check_contact_page(url: str) -> bool:
    """检查是否有联系我们页面"""
    paths = ['/contact', '/contact-us', '/contact.html', '/contact-us.html', '/contact/', '/contact-us/']
    return await _check_page_exists(url, paths)


async def _check_page_exists(base_url: str, paths: List[str]) -> bool:
    """检查页面是否存在"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        headers = {'User-Agent': _get_random_user_agent()}
        for path in paths:
            try:
                response = await client.get(
                    base_url.rstrip('/') + path,
                    headers=headers,
                    follow_redirects=True
                )
                if response.status_code == 200:
                    return True
            except:
                continue
    return False


async def batch_analyze(urls: List[str], use_playwright: bool = False) -> List[Optional[Dict]]:
    """
    批量分析多个网站
    
    Args:
        urls: URL 列表
        use_playwright: 是否使用 Playwright
    
    Returns:
        分析结果列表
    """
    tasks = [analyze(url, use_playwright) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [
        result if not isinstance(result, Exception) else None
        for result in results
    ]
