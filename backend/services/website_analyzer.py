"""
网站爬取和分析模块
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urlparse
import asyncio

async def analyze(url: str) -> Optional[Dict]:
    """
    分析网站并返回结构化数据
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 获取网页内容
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取基本信息
            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_description': get_meta_description(soup),
                'content_length': len(html),
                'word_count': count_words(soup),
                'has_privacy_policy': await check_privacy_policy(client, url),
                'has_about_page': await check_about_page(client, url),
                'has_contact_page': await check_contact_page(client, url),
                'images_count': len(soup.find_all('img')),
                'links_count': len(soup.find_all('a')),
                'headings': extract_headings(soup),
                'is_https': url.startswith('https://'),
                'load_time': response.elapsed.total_seconds(),
            }
            
            return data
            
    except Exception as e:
        print(f"分析失败：{e}")
        return None

def get_meta_description(soup: BeautifulSoup) -> str:
    """获取 meta description"""
    meta = soup.find('meta', attrs={'name': 'description'})
    return meta.get('content', '') if meta else ''

def count_words(soup: BeautifulSoup) -> int:
    """统计页面文字数量"""
    text = soup.get_text()
    return len(text.split())

def extract_headings(soup: BeautifulSoup) -> Dict:
    """提取标题结构"""
    return {
        'h1': len(soup.find_all('h1')),
        'h2': len(soup.find_all('h2')),
        'h3': len(soup.find_all('h3')),
    }

async def check_privacy_policy(client: httpx.AsyncClient, base_url: str) -> bool:
    """检查是否有隐私政策页面"""
    paths = ['/privacy', '/privacy-policy', '/privacy.html', '/privacy-policy.html']
    for path in paths:
        try:
            response = await client.get(base_url.rstrip('/') + path, timeout=5.0)
            if response.status_code == 200:
                return True
        except:
            continue
    return False

async def check_about_page(client: httpx.AsyncClient, base_url: str) -> bool:
    """检查是否有关于我们页面"""
    paths = ['/about', '/about-us', '/about.html', '/about-us.html']
    for path in paths:
        try:
            response = await client.get(base_url.rstrip('/') + path, timeout=5.0)
            if response.status_code == 200:
                return True
        except:
            continue
    return False

async def check_contact_page(client: httpx.AsyncClient, base_url: str) -> bool:
    """检查是否有联系我们页面"""
    paths = ['/contact', '/contact-us', '/contact.html', '/contact-us.html']
    for path in paths:
        try:
            response = await client.get(base_url.rstrip('/') + path, timeout=5.0)
            if response.status_code == 200:
                return True
        except:
            continue
    return False
