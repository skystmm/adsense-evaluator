"""
AI 内容分析模块
使用 LLM API 进行深度内容分析和建议生成
支持 OpenAI、Claude 等主流 LLM
"""
from typing import Dict, List, Optional
import os
import json
from datetime import datetime
import httpx

# API 配置
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_API_BASE = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')


class ContentAnalyzer:
    """AI 内容分析器"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or LLM_API_KEY
        self.api_base = api_base or LLM_API_BASE
        self.model = model or LLM_MODEL
        self.use_mock = not self.api_key  # 没有 API 密钥时使用模拟模式
    
    async def analyze_and_suggest(
        self,
        website_data: Dict,
        scores: Dict,
        issues: List[Dict]
    ) -> List[Dict]:
        """
        使用 AI 分析网站内容并生成个性化建议
        
        Args:
            website_data: 网站分析数据
            scores: 各维度得分
            issues: 问题列表
        
        Returns:
            AI 建议列表
        """
        if self.use_mock:
            return self._mock_analyze(website_data, scores, issues)
        
        try:
            return await self._llm_analyze(website_data, scores, issues)
        except Exception as e:
            print(f"AI 分析失败，使用模拟模式：{e}")
            return self._mock_analyze(website_data, scores, issues)
    
    async def _llm_analyze(
        self,
        website_data: Dict,
        scores: Dict,
        issues: List[Dict]
    ) -> List[Dict]:
        """调用 LLM API 进行分析"""
        
        # 构建分析提示
        prompt = self._build_analysis_prompt(website_data, scores, issues)
        
        # 调用 API
        response_data = await self._call_llm_api(prompt)
        
        if not response_data:
            return self._mock_analyze(website_data, scores, issues)
        
        # 解析响应
        suggestions = self._parse_llm_response(response_data, website_data, scores)
        
        return suggestions
    
    def _build_analysis_prompt(
        self,
        website_data: Dict,
        scores: Dict,
        issues: List[Dict]
    ) -> str:
        """构建分析提示词"""
        
        prompt = f"""你是一位 Google AdSense 审核专家。请分析以下网站数据，并提供专业的评估建议。

## 网站基本信息
- URL: {website_data.get('url', 'N/A')}
- 标题：{website_data.get('title', 'N/A')}
- 语言：{website_data.get('language', 'N/A')}
- 内容字数：{website_data.get('word_count', 0)}
- HTTPS: {'是' if website_data.get('is_https') else '否'}

## 必要页面检查
- 隐私政策：{'有' if website_data.get('has_privacy_policy') else '无'}
- 关于我们：{'有' if website_data.get('has_about_page') else '无'}
- 联系我们：{'有' if website_data.get('has_contact_page') else '无'}

## 内容结构
- H1 标题数：{website_data.get('headings', {}).get('h1_count', 0)}
- H2 标题数：{website_data.get('headings', {}).get('h2_count', 0)}
- 图片数：{website_data.get('images_count', 0)}
- 内部链接：{len(website_data.get('internal_links', []))}
- 外部链接：{len(website_data.get('external_links', []))}

## 各维度得分
- 内容质量：{scores.get('content_quality', 0)}/35
- 网站结构：{scores.get('site_structure', 0)}/20
- 流量来源：{scores.get('traffic_source', 0)}/15
- 技术合规：{scores.get('technical_compliance', 0)}/20
- 政策遵守：{scores.get('policy_compliance', 0)}/10
- 总分：{sum(scores.values())}/100

## 已识别问题
{json.dumps(issues, ensure_ascii=False, indent=2)}

请基于以上信息，提供：
1. 整体评估（100 字以内）
2. 3-5 条最关键的改进建议（按优先级排序）
3. 预估 AdSense 通过概率
4. 预计需要多少时间的优化

请以 JSON 格式返回，格式如下：
{{
    "overall_assessment": "整体评估文字",
    "key_recommendations": [
        {{
            "priority": "high|medium|low",
            "title": "建议标题",
            "description": "详细描述",
            "action_items": ["具体行动 1", "具体行动 2"],
            "expected_impact": "预期提升分数"
        }}
    ],
    "pass_probability": 75,
    "estimated_optimization_weeks": 2
}}
"""
        return prompt
    
    async def _call_llm_api(self, prompt: str) -> Optional[Dict]:
        """调用 LLM API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一位专业的 Google AdSense 审核专家，擅长网站质量评估和优化建议。请提供专业、具体、可执行的建议。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 1500,
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f'{self.api_base}/chat/completions',
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 尝试解析 JSON
                try:
                    # 清理可能的 markdown 标记
                    content = content.replace('```json', '').replace('```', '').strip()
                    return json.loads(content)
                except:
                    print("无法解析 LLM 响应为 JSON")
                    return None
                    
        except Exception as e:
            print(f"LLM API 调用失败：{e}")
            return None
    
    def _parse_llm_response(
        self,
        response: Dict,
        website_data: Dict,
        scores: Dict
    ) -> List[Dict]:
        """解析 LLM 响应为建议列表"""
        suggestions = []
        
        # 整体评估
        overall = response.get('overall_assessment', '')
        if overall:
            suggestions.append({
                'type': 'ai_overall_assessment',
                'priority': 'high',
                'title': 'AI 整体评估',
                'description': overall,
                'ai_generated': True,
            })
        
        # 关键建议
        recommendations = response.get('key_recommendations', [])
        for rec in recommendations:
            suggestions.append({
                'type': 'ai_recommendation',
                'priority': rec.get('priority', 'medium'),
                'title': rec.get('title', ''),
                'description': rec.get('description', ''),
                'action_items': rec.get('action_items', []),
                'expected_impact': rec.get('expected_impact', ''),
                'ai_generated': True,
            })
        
        # 通过概率
        pass_prob = response.get('pass_probability')
        if pass_prob is not None:
            suggestions.append({
                'type': 'ai_pass_probability',
                'priority': 'high',
                'title': 'AI 预估通过概率',
                'description': f'根据当前网站质量，预估 AdSense 通过概率为 {pass_prob}%',
                'probability': pass_prob,
                'ai_generated': True,
            })
        
        # 优化时间预估
        opt_weeks = response.get('estimated_optimization_weeks')
        if opt_weeks is not None:
            suggestions.append({
                'type': 'ai_timeline',
                'priority': 'medium',
                'title': '预计优化时间',
                'description': f'预计需要 {opt_weeks} 周的持续优化才能达到 AdSense 要求',
                'weeks': opt_weeks,
                'ai_generated': True,
            })
        
        return suggestions
    
    def _mock_analyze(
        self,
        website_data: Dict,
        scores: Dict,
        issues: List[Dict]
    ) -> List[Dict]:
        """模拟 AI 分析（无 API 密钥时使用）"""
        suggestions = []
        
        total_score = sum(scores.values())
        
        # 基于分数生成建议
        if scores.get('content_quality', 0) < 20:
            suggestions.append({
                'type': 'content_improvement',
                'priority': 'high',
                'title': '提升内容质量',
                'description': f'当前内容质量得分 {scores.get("content_quality", 0)}/35',
                'action_items': [
                    '每周发布 2-3 篇原创文章',
                    '每篇文章至少 1000 字',
                    '使用 H1/H2/H3 构建清晰的内容结构',
                    '添加相关图片和视频丰富内容',
                ],
                'expected_impact': '+10-15 分',
                'ai_generated': False,
            })
        
        if scores.get('site_structure', 0) < 15:
            suggestions.append({
                'type': 'structure_improvement',
                'priority': 'high',
                'title': '优化网站结构',
                'description': f'当前网站结构得分 {scores.get("site_structure", 0)}/20',
                'action_items': [
                    '创建隐私政策页面（必须）',
                    '添加关于我们页面',
                    '完善联系我们页面',
                    '优化网站导航和内部链接',
                ],
                'expected_impact': '+8-12 分',
                'ai_generated': False,
            })
        
        if scores.get('technical_compliance', 0) < 15:
            suggestions.append({
                'type': 'technical_improvement',
                'priority': 'medium',
                'title': '改善技术合规',
                'description': f'当前技术合规得分 {scores.get("technical_compliance", 0)}/20',
                'action_items': [
                    '安装 SSL 证书启用 HTTPS',
                    '添加 Meta 描述（120-160 字）',
                    '为图片添加 alt 属性',
                    '创建 sitemap.xml 并提交到搜索引擎',
                ],
                'expected_impact': '+5-10 分',
                'ai_generated': False,
            })
        
        # 总体建议
        if total_score < 60:
            suggestions.append({
                'type': 'overall',
                'priority': 'high',
                'title': '整体优化建议',
                'description': f'当前总分 {total_score}/100，距离 AdSense 要求还有较大差距',
                'action_items': [
                    '优先解决高优先级问题（隐私政策、HTTPS、内容质量）',
                    '制定内容发布计划，保持每周更新',
                    '参考竞争对手网站，学习优秀实践',
                ],
                'expected_impact': '+20-30 分',
                'estimated_weeks': 3,
                'ai_generated': False,
            })
        elif total_score < 75:
            suggestions.append({
                'type': 'overall',
                'priority': 'medium',
                'title': '冲刺建议',
                'description': f'当前总分 {total_score}/100，接近 AdSense 要求',
                'action_items': [
                    '重点优化内容质量和用户体验',
                    '增加原创深度文章到 15 篇以上',
                    '优化页面加载速度',
                ],
                'expected_impact': '+10-15 分',
                'estimated_weeks': 2,
                'ai_generated': False,
            })
        elif total_score < 90:
            suggestions.append({
                'type': 'overall',
                'priority': 'low',
                'title': '准备申请',
                'description': f'当前总分 {total_score}/100，已符合 AdSense 基本要求',
                'action_items': [
                    '可以开始准备 AdSense 申请',
                    '确保网站持续更新',
                    '准备好所有必要页面',
                ],
                'expected_impact': '通过概率 >70%',
                'estimated_weeks': 1,
                'ai_generated': False,
            })
        else:
            suggestions.append({
                'type': 'overall',
                'priority': 'low',
                'title': '优秀网站',
                'description': f'当前总分 {total_score}/100，网站质量优秀',
                'action_items': [
                    '可以直接申请 AdSense',
                    '保持内容更新频率',
                    '持续监控网站性能',
                ],
                'expected_impact': '通过概率 >85%',
                'estimated_weeks': 0,
                'ai_generated': False,
            })
        
        # 同类网站对比（模拟）
        suggestions.append({
            'type': 'benchmark',
            'priority': 'medium',
            'title': '同类网站对比',
            'description': f'您的网站得分超过了约 {min(total_score + 10, 95)}% 的申请者',
            'benchmark_data': {
                'average_score': 65,
                'passing_score': 75,
                'excellent_score': 90,
                'your_score': total_score,
            },
            'ai_generated': False,
        })
        
        return suggestions


# 全局分析器实例
_analyzer: Optional[ContentAnalyzer] = None


def get_analyzer() -> ContentAnalyzer:
    """获取分析器实例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ContentAnalyzer()
    return _analyzer


async def analyze_and_suggest(
    website_data: Dict,
    scores: Dict,
    issues: List[Dict]
) -> List[Dict]:
    """
    使用 AI 分析网站内容并生成个性化建议（便捷函数）
    
    Args:
        website_data: 网站分析数据
        scores: 各维度得分
        issues: 问题列表
    
    Returns:
        AI 建议列表
    """
    analyzer = get_analyzer()
    return await analyzer.analyze_and_suggest(website_data, scores, issues)


async def compare_websites(websites: List[Dict]) -> Dict:
    """
    同类网站对比分析
    
    Args:
        websites: 多个网站的数据列表
    
    Returns:
        对比分析结果
    """
    if not websites:
        return {'error': '没有网站数据'}
    
    comparison = {
        'total_websites': len(websites),
        'average_score': 0,
        'best_website': None,
        'worst_website': None,
        'websites': [],
    }
    
    total_score = 0
    max_score = -1
    min_score = 101
    
    for site in websites:
        scores = site.get('scores', {})
        site_total = sum(scores.values())
        total_score += site_total
        
        if site_total > max_score:
            max_score = site_total
            comparison['best_website'] = site.get('url', 'N/A')
        
        if site_total < min_score:
            min_score = site_total
            comparison['worst_website'] = site.get('url', 'N/A')
        
        comparison['websites'].append({
            'url': site.get('url', 'N/A'),
            'score': site_total,
            'strengths': site.get('strengths', []),
            'weaknesses': site.get('weaknesses', []),
        })
    
    comparison['average_score'] = round(total_score / len(websites), 1) if websites else 0
    
    return comparison
