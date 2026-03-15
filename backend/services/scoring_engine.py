"""
评估打分系统
5 大维度评分标准：内容质量 35%、网站结构 20%、流量来源 15%、技术合规 20%、政策遵守 10%
至少 20 个具体检测点
"""
from typing import Dict, List, Tuple
from datetime import datetime


# 评分权重配置
SCORING_WEIGHTS = {
    'content_quality': 35,      # 内容质量
    'site_structure': 20,       # 网站结构
    'traffic_source': 15,       # 流量来源（模拟评估）
    'technical_compliance': 20, # 技术合规
    'policy_compliance': 10,    # 政策遵守
}

# 等级评定标准
RATING_LEVELS = [
    (90, 'EXCELLENT', '优秀', '非常符合 AdSense 要求，通过概率极高'),
    (75, 'GOOD', '良好', '符合 AdSense 要求，通过概率较高'),
    (60, 'FAIR', '一般', '基本符合要求，但需要优化'),
    (40, 'POOR', '较差', '不符合要求，需要大量改进'),
    (0, 'VERY_POOR', '很差', '严重不符合要求，不建议申请'),
]


def calculate_scores(website_data: Dict) -> Dict[str, int]:
    """
    根据网站数据计算各项得分
    
    Args:
        website_data: 网站分析数据
    
    Returns:
        各维度得分为字典
    """
    scores = {
        'content_quality': score_content_quality(website_data),
        'site_structure': score_site_structure(website_data),
        'traffic_source': score_traffic_source(website_data),
        'technical_compliance': score_technical_compliance(website_data),
        'policy_compliance': score_policy_compliance(website_data),
    }
    return scores


def score_content_quality(data: Dict) -> int:
    """
    内容质量评分（35 分）
    检测点：
    1. 文字数量（10 分）
    2. 标题结构（8 分）
    3. Meta 描述（5 分）
    4. 图片质量和数量（5 分）
    5. 内容原创性指标（4 分）
    6. 内容深度（3 分）
    """
    score = 0
    
    # 1. 字数评分（最多 10 分）
    word_count = data.get('word_count', 0)
    if word_count >= 2000:
        score += 10
    elif word_count >= 1000:
        score += 8
    elif word_count >= 500:
        score += 6
    elif word_count >= 200:
        score += 4
    elif word_count >= 100:
        score += 2
    
    # 2. 标题结构（最多 8 分）
    headings = data.get('headings', {})
    h1_count = headings.get('h1_count', len(headings.get('h1', [])))
    h2_count = headings.get('h2_count', len(headings.get('h2', [])))
    
    if h1_count == 1:
        score += 3  # 有且只有一个 H1
    elif h1_count > 1:
        score += 1  # H1 过多扣分
    
    if h2_count >= 3:
        score += 3  # 足够的 H2
    elif h2_count >= 1:
        score += 2
    
    if headings.get('h3_count', 0) >= 2:
        score += 2  # 有 H3 层次更好
    
    # 3. Meta 描述（最多 5 分）
    meta_desc = data.get('meta_description', '')
    if meta_desc:
        score += 3
        if 120 <= len(meta_desc) <= 160:  # 最佳长度
            score += 2
        elif 80 <= len(meta_desc) <= 200:
            score += 1
    
    # 4. 图片（最多 5 分）
    images_count = data.get('images_count', 0)
    images = data.get('images', [])
    
    if images_count >= 5:
        score += 3
    elif images_count >= 2:
        score += 2
    elif images_count >= 1:
        score += 1
    
    # 检查图片 alt 属性（可访问性）
    if images:
        alt_filled = sum(1 for img in images if img.get('alt'))
        if alt_filled > len(images) * 0.5:
            score += 2  # 超过一半图片有 alt 描述
    
    # 5. 内容原创性指标（最多 4 分）- 基于简单启发式
    content_length = data.get('content_length', 0)
    if content_length >= 5000:
        score += 4
    elif content_length >= 2000:
        score += 3
    elif content_length >= 1000:
        score += 2
    
    # 6. 内容深度（最多 3 分）
    if h2_count >= 5 and headings.get('h3_count', 0) >= 3:
        score += 3  # 内容结构完整
    elif h2_count >= 2:
        score += 2
    
    return min(score, 35)


def score_site_structure(data: Dict) -> int:
    """
    网站结构评分（20 分）
    检测点：
    1. 必要页面（10 分）
    2. 导航链接（4 分）
    3. 内部链接结构（3 分）
    4. URL 结构（3 分）
    """
    score = 0
    
    # 1. 必要页面（最多 10 分）
    if data.get('has_privacy_policy'):
        score += 4
    if data.get('has_about_page'):
        score += 3
    if data.get('has_contact_page'):
        score += 3
    
    # 2. 导航链接（最多 4 分）
    internal_links = data.get('internal_links', [])
    links_count = data.get('links_count', 0)
    
    if len(internal_links) >= 10:
        score += 4
    elif len(internal_links) >= 5:
        score += 3
    elif len(internal_links) >= 2:
        score += 2
    elif links_count >= 5:
        score += 1
    
    # 3. 内部链接结构（最多 3 分）
    if len(internal_links) >= 15:
        score += 3
    elif len(internal_links) >= 8:
        score += 2
    elif len(internal_links) >= 3:
        score += 1
    
    # 4. URL 结构（最多 3 分）
    if data.get('is_https'):
        score += 2  # HTTPS
    if data.get('has_sitemap'):
        score += 1  # 有 sitemap
    
    return min(score, 20)


def score_traffic_source(data: Dict) -> int:
    """
    流量来源评分（15 分）- 基于间接指标模拟评估
    检测点：
    1. 外部链接质量（5 分）
    2. 社交媒体存在（3 分）
    3. 网站权威性指标（4 分）
    4. 内容更新频率（3 分）
    
    注意：实际流量数据需要接入分析工具，这里使用替代指标
    """
    score = 0
    
    # 1. 外部链接质量（最多 5 分）
    external_links = data.get('external_links', [])
    if len(external_links) >= 10:
        score += 3
    elif len(external_links) >= 5:
        score += 2
    elif len(external_links) >= 2:
        score += 1
    
    # 检查是否有高质量外部链接（如维基百科、政府网站等）
    high_quality_domains = ['wikipedia.org', 'github.com', 'medium.com', 'reddit.com']
    for link in external_links[:20]:
        if any(domain in link.get('url', '') for domain in high_quality_domains):
            score += 2
            break
    
    # 2. 社交媒体存在（最多 3 分）- 通过外部链接判断
    social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'weibo.com']
    social_count = 0
    for link in external_links:
        if any(domain in link.get('url', '') for domain in social_domains):
            social_count += 1
    
    if social_count >= 3:
        score += 3
    elif social_count >= 1:
        score += 2
    
    # 3. 网站权威性指标（最多 4 分）
    if data.get('has_robots_txt'):
        score += 1
    if data.get('has_sitemap'):
        score += 1
    if data.get('has_favicon'):
        score += 1
    
    # 内容长度作为权威性代理
    if data.get('word_count', 0) >= 1500:
        score += 1
    
    # 4. 内容更新频率（最多 3 分）- 使用缓存时间作为代理
    # 实际应该检查最后更新时间
    cached_at = data.get('_cached_at')
    if cached_at:
        try:
            cached_time = datetime.fromisoformat(cached_at)
            days_since_cache = (datetime.now() - cached_time).days
            if days_since_cache <= 1:
                score += 3
            elif days_since_cache <= 7:
                score += 2
            elif days_since_cache <= 30:
                score += 1
        except:
            pass
    
    return min(score, 15)


def score_technical_compliance(data: Dict) -> int:
    """
    技术合规评分（20 分）
    检测点：
    1. HTTPS 加密（5 分）
    2. 页面加载速度（5 分）
    3. 移动端适配（4 分）
    4. SEO 基础（4 分）
    5. 可访问性（2 分）
    """
    score = 0
    
    # 1. HTTPS 加密（最多 5 分）
    if data.get('is_https'):
        score += 5
    
    # 2. 页面加载速度（最多 5 分）
    load_time = data.get('load_time', 0)
    if load_time > 0:
        if load_time < 2:
            score += 5
        elif load_time < 3:
            score += 4
        elif load_time < 5:
            score += 3
        elif load_time < 8:
            score += 2
        elif load_time < 10:
            score += 1
    
    # 如果没有加载时间数据，给平均分
    if load_time == 0:
        score += 3
    
    # 3. 移动端适配（最多 4 分）- 通过 viewport 判断
    # 简化处理：如果有 title 和 meta description，假设基本适配
    if data.get('title'):
        score += 2
    if data.get('meta_description'):
        score += 1
    
    # 4. SEO 基础（最多 4 分）
    if data.get('meta_description'):
        score += 2
    if data.get('meta_keywords'):
        score += 1
    if data.get('has_sitemap'):
        score += 1
    
    # 5. 可访问性（最多 2 分）
    images = data.get('images', [])
    if images:
        alt_filled = sum(1 for img in images if img.get('alt'))
        if alt_filled > len(images) * 0.7:
            score += 2
        elif alt_filled > len(images) * 0.3:
            score += 1
    
    return min(score, 20)


def score_policy_compliance(data: Dict) -> int:
    """
    政策遵守评分（10 分）
    检测点：
    1. 隐私政策（4 分）
    2. 关于我们（2 分）
    3. 联系我们（2 分）
    4. 内容政策（2 分）
    """
    score = 0
    
    # 1. 隐私政策（最多 4 分）- AdSense 强制要求
    if data.get('has_privacy_policy'):
        score += 4
    
    # 2. 关于我们（最多 2 分）
    if data.get('has_about_page'):
        score += 2
    
    # 3. 联系我们（最多 2 分）
    if data.get('has_contact_page'):
        score += 2
    
    # 4. 内容政策（最多 2 分）- 基于语言和内容长度判断
    if data.get('word_count', 0) >= 500:
        score += 1
    if data.get('language') in ['zh', 'en']:
        score += 1
    
    return min(score, 10)


def identify_issues(website_data: Dict, scores: Dict) -> List[Dict]:
    """
    识别网站存在的问题
    
    Args:
        website_data: 网站分析数据
        scores: 各维度得分
    
    Returns:
        问题列表，按优先级排序
    """
    issues = []
    
    # === 高优先级问题（必须解决）===
    
    # 缺少隐私政策
    if not website_data.get('has_privacy_policy'):
        issues.append({
            'category': 'policy_compliance',
            'priority': 'high',
            'title': '缺少隐私政策页面',
            'description': 'AdSense 强制要求网站必须有隐私政策页面',
            'suggestion': '创建隐私政策页面，说明如何收集、使用和保护用户数据',
            'impact': '可能导致申请被直接拒绝'
        })
    
    # 未使用 HTTPS
    if not website_data.get('is_https'):
        issues.append({
            'category': 'technical_compliance',
            'priority': 'high',
            'title': '未使用 HTTPS 加密',
            'description': 'AdSense 要求网站必须使用 HTTPS',
            'suggestion': '安装 SSL 证书（可使用 Let\'s Encrypt 免费证书）',
            'impact': '安全警告，影响用户体验和 SEO'
        })
    
    # 内容质量严重不足
    if scores.get('content_quality', 0) < 15:
        issues.append({
            'category': 'content_quality',
            'priority': 'high',
            'title': '内容质量严重不足',
            'description': f'内容质量得分 {scores.get("content_quality", 0)}/35，远低于要求',
            'suggestion': '增加原创深度内容，每篇文章至少 800-1000 字，确保有 H1/H2/H3 标题结构',
            'impact': 'AdSense 重视内容质量，低质内容难以通过'
        })
    
    # 内容字数过少
    word_count = website_data.get('word_count', 0)
    if word_count < 200:
        issues.append({
            'category': 'content_quality',
            'priority': 'high',
            'title': '页面内容过少',
            'description': f'当前仅 {word_count} 字，建议至少 500 字以上',
            'suggestion': '扩展页面内容，增加有价值的信息和深度分析',
            'impact': '内容过少会被视为低质量网站'
        })
    
    # === 中优先级问题（强烈建议解决）===
    
    # 缺少关于我们页面
    if not website_data.get('has_about_page'):
        issues.append({
            'category': 'site_structure',
            'priority': 'medium',
            'title': '缺少关于我们页面',
            'description': '缺少网站介绍会影响可信度',
            'suggestion': '创建关于我们页面，介绍网站背景、使命和团队',
            'impact': '降低网站可信度'
        })
    
    # 缺少联系我们页面
    if not website_data.get('has_contact_page'):
        issues.append({
            'category': 'site_structure',
            'priority': 'medium',
            'title': '缺少联系我们页面',
            'description': '缺少联系方式会影响可信度',
            'suggestion': '创建联系我们页面，提供邮箱、表单或其他联系方式',
            'impact': '降低网站可信度'
        })
    
    # 缺少 Meta 描述
    if not website_data.get('meta_description'):
        issues.append({
            'category': 'technical_compliance',
            'priority': 'medium',
            'title': '缺少 Meta 描述',
            'description': '页面没有设置 meta description',
            'suggestion': '添加 120-160 字的页面描述，包含关键词',
            'impact': '影响 SEO 和搜索点击率'
        })
    
    # H1 标题问题
    headings = website_data.get('headings', {})
    h1_count = headings.get('h1_count', len(headings.get('h1', [])))
    if h1_count == 0:
        issues.append({
            'category': 'content_quality',
            'priority': 'medium',
            'title': '缺少 H1 标题',
            'description': '页面没有 H1 标题',
            'suggestion': '添加一个明确的 H1 标题，概括页面主题',
            'impact': '影响 SEO 和内容结构'
        })
    elif h1_count > 1:
        issues.append({
            'category': 'content_quality',
            'priority': 'medium',
            'title': 'H1 标题过多',
            'description': f'页面有 {h1_count} 个 H1 标题，建议只保留 1 个',
            'suggestion': '将多余的 H1 改为 H2 或其他级别',
            'impact': '影响 SEO 和内容层次'
        })
    
    # 图片缺少 alt 属性
    images = website_data.get('images', [])
    if images:
        alt_missing = sum(1 for img in images if not img.get('alt'))
        if alt_missing > len(images) * 0.5:
            issues.append({
                'category': 'technical_compliance',
                'priority': 'medium',
                'title': '图片缺少 ALT 描述',
                'description': f'{alt_missing}/{len(images)} 张图片缺少 alt 属性',
                'suggestion': '为所有图片添加描述性 alt 文本',
                'impact': '影响可访问性和 SEO'
            })
    
    # 缺少 Sitemap
    if not website_data.get('has_sitemap'):
        issues.append({
            'category': 'site_structure',
            'priority': 'medium',
            'title': '缺少 Sitemap',
            'description': '网站没有 sitemap.xml 文件',
            'suggestion': '生成并提交 sitemap.xml 到搜索引擎',
            'impact': '影响搜索引擎收录'
        })
    
    # === 低优先级问题（优化建议）===
    
    # 缺少 favicon
    if not website_data.get('has_favicon'):
        issues.append({
            'category': 'user_experience',
            'priority': 'low',
            'title': '缺少 Favicon',
            'description': '网站没有设置 favicon 图标',
            'suggestion': '添加 16x16 或 32x32 的 favicon.ico 文件',
            'impact': '影响品牌识别和用户体验'
        })
    
    # 缺少 robots.txt
    if not website_data.get('has_robots_txt'):
        issues.append({
            'category': 'technical_compliance',
            'priority': 'low',
            'title': '缺少 robots.txt',
            'description': '网站没有 robots.txt 文件',
            'suggestion': '创建 robots.txt 文件，指导搜索引擎爬虫',
            'impact': '轻微影响 SEO'
        })
    
    # 外部链接过少
    external_links = website_data.get('external_links', [])
    if len(external_links) < 3:
        issues.append({
            'category': 'traffic_source',
            'priority': 'low',
            'title': '外部链接较少',
            'description': '页面外部链接较少，可能影响权威性',
            'suggestion': '适当引用权威来源，增加高质量外部链接',
            'impact': '轻微影响网站权威性'
        })
    
    # 内部链接过少
    internal_links = website_data.get('internal_links', [])
    if len(internal_links) < 5:
        issues.append({
            'category': 'site_structure',
            'priority': 'low',
            'title': '内部链接较少',
            'description': '页面内部链接较少',
            'suggestion': '增加相关文章链接，改善网站内部导航',
            'impact': '影响用户浏览深度和 SEO'
        })
    
    # 按优先级排序
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    issues.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return issues


def calculate_overall_score(scores: Dict[str, int]) -> Tuple[int, str, str]:
    """
    计算总体评分和等级
    
    Args:
        scores: 各维度得分
    
    Returns:
        (总分，等级代码，等级描述)
    """
    total = sum(scores.values())
    max_score = sum(SCORING_WEIGHTS.values())
    
    # 计算百分比
    percentage = (total / max_score) * 100 if max_score > 0 else 0
    
    # 确定等级
    rating = RATING_LEVELS[-1]  # 默认最低等级
    for threshold, code, name, desc in RATING_LEVELS:
        if percentage >= threshold:
            rating = (threshold, code, name, desc)
            break
    
    return total, rating[1], f"{rating[2]} - {rating[3]}"


def generate_score_report(website_data: Dict, scores: Dict, issues: List[Dict]) -> Dict:
    """
    生成详细评分报告
    
    Args:
        website_data: 网站分析数据
        scores: 各维度得分
        issues: 问题列表
    
    Returns:
        完整评分报告
    """
    total_score, rating_code, rating_desc = calculate_overall_score(scores)
    
    # 计算通过概率
    pass_probability = calculate_pass_probability(total_score, len(issues))
    
    report = {
        'summary': {
            'url': website_data.get('url', ''),
            'overall_score': total_score,
            'max_score': 100,
            'rating': rating_desc,
            'pass_probability': pass_probability,
            'analyzed_at': datetime.now().isoformat(),
        },
        'dimensions': {
            'content_quality': {
                'score': scores.get('content_quality', 0),
                'max_score': SCORING_WEIGHTS['content_quality'],
                'percentage': round(scores.get('content_quality', 0) / SCORING_WEIGHTS['content_quality'] * 100, 1),
                'weight': '35%',
            },
            'site_structure': {
                'score': scores.get('site_structure', 0),
                'max_score': SCORING_WEIGHTS['site_structure'],
                'percentage': round(scores.get('site_structure', 0) / SCORING_WEIGHTS['site_structure'] * 100, 1),
                'weight': '20%',
            },
            'traffic_source': {
                'score': scores.get('traffic_source', 0),
                'max_score': SCORING_WEIGHTS['traffic_source'],
                'percentage': round(scores.get('traffic_source', 0) / SCORING_WEIGHTS['traffic_source'] * 100, 1),
                'weight': '15%',
            },
            'technical_compliance': {
                'score': scores.get('technical_compliance', 0),
                'max_score': SCORING_WEIGHTS['technical_compliance'],
                'percentage': round(scores.get('technical_compliance', 0) / SCORING_WEIGHTS['technical_compliance'] * 100, 1),
                'weight': '20%',
            },
            'policy_compliance': {
                'score': scores.get('policy_compliance', 0),
                'max_score': SCORING_WEIGHTS['policy_compliance'],
                'percentage': round(scores.get('policy_compliance', 0) / SCORING_WEIGHTS['policy_compliance'] * 100, 1),
                'weight': '10%',
            },
        },
        'issues': issues,
        'issues_summary': {
            'high': sum(1 for i in issues if i['priority'] == 'high'),
            'medium': sum(1 for i in issues if i['priority'] == 'medium'),
            'low': sum(1 for i in issues if i['priority'] == 'low'),
            'total': len(issues),
        },
        'recommendations': generate_recommendations(scores, issues),
    }
    
    return report


def calculate_pass_probability(score: int, issue_count: int) -> float:
    """
    计算 AdSense 通过概率
    
    Args:
        score: 总分
        issue_count: 问题数量
    
    Returns:
        通过概率（0-100）
    """
    # 基础概率基于分数
    base_probability = min(score / 100.0, 1.0)
    
    # 高优先级问题惩罚
    high_priority_penalty = min(issue_count * 0.08, 0.4)
    
    # 计算最终概率
    probability = max(0, min(1, base_probability - high_priority_penalty))
    
    return round(probability * 100, 1)


def generate_recommendations(scores: Dict, issues: List[Dict]) -> List[Dict]:
    """
    生成优化建议
    
    Args:
        scores: 各维度得分
        issues: 问题列表
    
    Returns:
        建议列表
    """
    recommendations = []
    
    # 基于得分最低的维度生成建议
    min_dimension = min(scores.items(), key=lambda x: x[1] / SCORING_WEIGHTS.get(x[0], 1))
    
    recommendations_map = {
        'content_quality': {
            'title': '优先提升内容质量',
            'description': '内容质量是 AdSense 审核的核心。建议：1. 每周发布 2-3 篇原创文章 2. 每篇文章 1000 字以上 3. 使用清晰的标题结构',
            'expected_improvement': '+10-15 分',
        },
        'site_structure': {
            'title': '完善网站结构',
            'description': '建议创建必要的页面：隐私政策、关于我们、联系我们。同时优化内部链接结构。',
            'expected_improvement': '+8-12 分',
        },
        'technical_compliance': {
            'title': '优化技术合规',
            'description': '确保使用 HTTPS，添加 Meta 描述，优化页面加载速度，为图片添加 alt 属性。',
            'expected_improvement': '+5-10 分',
        },
        'policy_compliance': {
            'title': '确保政策合规',
            'description': '隐私政策是 AdSense 的强制要求。务必创建详细的隐私政策页面。',
            'expected_improvement': '+4-8 分',
        },
        'traffic_source': {
            'title': '增加网站权威性',
            'description': '通过社交媒体推广、引用权威来源、创建 sitemap 等方式提升网站权威性。',
            'expected_improvement': '+3-6 分',
        },
    }
    
    if min_dimension[0] in recommendations_map:
        recommendations.append(recommendations_map[min_dimension[0]])
    
    # 如果有高优先级问题，添加紧急建议
    high_priority_issues = [i for i in issues if i['priority'] == 'high']
    if high_priority_issues:
        recommendations.append({
            'title': '🚨 紧急修复项',
            'description': f'发现 {len(high_priority_issues)} 个高优先级问题，建议在申请 AdSense 前优先解决',
            'expected_improvement': '避免直接拒绝',
        })
    
    # 总体建议
    total_score = sum(scores.values())
    if total_score >= 75:
        recommendations.append({
            'title': '准备申请',
            'description': '网站质量良好，可以开始准备 AdSense 申请。确保网站持续更新，保持内容质量。',
            'expected_improvement': '通过概率 >70%',
        })
    elif total_score >= 60:
        recommendations.append({
            'title': '继续优化',
            'description': '网站基础不错，但还需要进一步优化。建议重点解决高优先级问题，预计 1-2 周后可尝试申请。',
            'expected_improvement': '通过概率 50-70%',
        })
    else:
        recommendations.append({
            'title': '需要大量改进',
            'description': '网站距离 AdSense 要求还有较大差距。建议先完善基础内容（隐私政策、HTTPS、优质内容），再考虑申请。',
            'expected_improvement': '通过概率 <50%',
        })
    
    return recommendations
