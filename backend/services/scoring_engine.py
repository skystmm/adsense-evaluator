"""
评估打分系统
"""
from typing import Dict, List

def calculate_scores(website_data: Dict) -> Dict[str, int]:
    """
    根据网站数据计算各项得分
    """
    scores = {
        'content_quality': score_content_quality(website_data),
        'site_structure': score_site_structure(website_data),
        'user_experience': score_user_experience(website_data),
        'technical_compliance': score_technical_compliance(website_data),
    }
    return scores

def score_content_quality(data: Dict) -> int:
    """
    内容质量评分（30 分）
    """
    score = 0
    
    # 字数评分（最多 10 分）
    word_count = data.get('word_count', 0)
    if word_count >= 1000:
        score += 10
    elif word_count >= 500:
        score += 7
    elif word_count >= 200:
        score += 4
    
    # 标题结构（最多 10 分）
    headings = data.get('headings', {})
    if headings.get('h1', 0) >= 1:
        score += 5
    if headings.get('h2', 0) >= 2:
        score += 5
    
    # Meta 描述（最多 5 分）
    if data.get('meta_description'):
        score += 5
    
    # 图片（最多 5 分）
    if data.get('images_count', 0) >= 3:
        score += 5
    
    return min(score, 30)

def score_site_structure(data: Dict) -> int:
    """
    网站结构评分（25 分）
    """
    score = 0
    
    # 必要页面（最多 15 分）
    if data.get('has_privacy_policy'):
        score += 5
    if data.get('has_about_page'):
        score += 5
    if data.get('has_contact_page'):
        score += 5
    
    # 链接数量（最多 5 分）
    links_count = data.get('links_count', 0)
    if links_count >= 10:
        score += 5
    elif links_count >= 5:
        score += 3
    
    # 标题层次（最多 5 分）
    headings = data.get('headings', {})
    if headings.get('h1', 0) == 1 and headings.get('h2', 0) >= 1:
        score += 5
    
    return min(score, 25)

def score_user_experience(data: Dict) -> int:
    """
    用户体验评分（25 分）
    """
    score = 0
    
    # 加载速度（最多 10 分）
    load_time = data.get('load_time', 999)
    if load_time < 2:
        score += 10
    elif load_time < 3:
        score += 7
    elif load_time < 5:
        score += 4
    
    # 内容长度（最多 10 分）
    content_length = data.get('content_length', 0)
    if content_length >= 10000:
        score += 10
    elif content_length >= 5000:
        score += 7
    elif content_length >= 2000:
        score += 4
    
    # 图片数量（最多 5 分）
    images = data.get('images_count', 0)
    if images >= 5:
        score += 5
    elif images >= 2:
        score += 3
    
    return min(score, 25)

def score_technical_compliance(data: Dict) -> int:
    """
    技术合规评分（20 分）
    """
    score = 0
    
    # HTTPS（最多 10 分）
    if data.get('is_https'):
        score += 10
    
    # 标题（最多 5 分）
    if data.get('title'):
        score += 5
    
    # Meta 描述（最多 5 分）
    if data.get('meta_description'):
        score += 5
    
    return min(score, 20)

def identify_issues(website_data: Dict, scores: Dict) -> List[Dict]:
    """
    识别网站存在的问题
    """
    issues = []
    
    # 内容质量问题
    if scores.get('content_quality', 0) < 15:
        issues.append({
            'category': 'content_quality',
            'priority': 'high',
            'title': '内容质量不足',
            'description': '网站内容数量或质量可能不符合 AdSense 要求',
            'suggestion': '增加原创深度内容，确保每篇文章至少 500 字'
        })
    
    # 缺少必要页面
    if not website_data.get('has_privacy_policy'):
        issues.append({
            'category': 'site_structure',
            'priority': 'high',
            'title': '缺少隐私政策页面',
            'description': 'AdSense 要求网站必须有隐私政策',
            'suggestion': '创建隐私政策页面，说明如何收集和使用用户数据'
        })
    
    if not website_data.get('has_about_page'):
        issues.append({
            'category': 'site_structure',
            'priority': 'medium',
            'title': '缺少关于我们页面',
            'description': '缺少网站介绍会影响可信度',
            'suggestion': '创建关于我们页面，介绍网站背景和团队'
        })
    
    if not website_data.get('has_contact_page'):
        issues.append({
            'category': 'site_structure',
            'priority': 'medium',
            'title': '缺少联系我们页面',
            'description': '缺少联系方式会影响可信度',
            'suggestion': '创建联系我们页面，提供有效的联系方式'
        })
    
    # 技术问题
    if not website_data.get('is_https'):
        issues.append({
            'category': 'technical',
            'priority': 'high',
            'title': '未使用 HTTPS',
            'description': 'AdSense 要求网站必须使用 HTTPS',
            'suggestion': '安装 SSL 证书，启用 HTTPS'
        })
    
    # 加载速度
    if website_data.get('load_time', 0) > 3:
        issues.append({
            'category': 'user_experience',
            'priority': 'medium',
            'title': '加载速度较慢',
            'description': f'页面加载时间 {website_data.get("load_time", 0):.2f} 秒，建议优化到 3 秒以内',
            'suggestion': '优化图片大小、启用缓存、使用 CDN'
        })
    
    return issues
