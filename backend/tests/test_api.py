"""
API 测试脚本
测试评估 API 的各项功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import website_analyzer, scoring_engine
from ai import content_analyzer


async def test_website_analyzer():
    """测试网站分析模块"""
    print("\n=== 测试网站分析模块 ===")
    
    # 测试简单网站
    url = "https://www.example.com"
    print(f"\n分析网站：{url}")
    
    data = await website_analyzer.analyze(url, use_playwright=False)
    
    if data:
        print(f"✓ 标题：{data.get('title', 'N/A')}")
        print(f"✓ 字数：{data.get('word_count', 0)}")
        print(f"✓ HTTPS: {data.get('is_https', False)}")
        print(f"✓ 隐私政策：{data.get('has_privacy_policy', False)}")
        print(f"✓ 图片数：{data.get('images_count', 0)}")
        print(f"✓ 内部链接：{len(data.get('internal_links', []))}")
        print(f"✓ 外部链接：{len(data.get('external_links', []))}")
    else:
        print("✗ 分析失败")
    
    return data


async def test_scoring_engine(website_data):
    """测试评分系统"""
    print("\n=== 测试评分系统 ===")
    
    if not website_data:
        print("✗ 缺少网站数据，跳过测试")
        return
    
    scores = scoring_engine.calculate_scores(website_data)
    total = sum(scores.values())
    
    print(f"\n各维度得分:")
    print(f"  内容质量：{scores.get('content_quality', 0)}/35")
    print(f"  网站结构：{scores.get('site_structure', 0)}/20")
    print(f"  流量来源：{scores.get('traffic_source', 0)}/15")
    print(f"  技术合规：{scores.get('technical_compliance', 0)}/20")
    print(f"  政策遵守：{scores.get('policy_compliance', 0)}/10")
    print(f"  总分：{total}/100")
    
    # 等级评定
    _, rating_code, rating_desc = scoring_engine.calculate_overall_score(scores)
    print(f"\n等级：{rating_desc}")
    
    # 识别问题
    issues = scoring_engine.identify_issues(website_data, scores)
    print(f"\n发现问题：{len(issues)} 个")
    
    high_priority = sum(1 for i in issues if i['priority'] == 'high')
    medium_priority = sum(1 for i in issues if i['priority'] == 'medium')
    low_priority = sum(1 for i in issues if i['priority'] == 'low')
    
    print(f"  高优先级：{high_priority}")
    print(f"  中优先级：{medium_priority}")
    print(f"  低优先级：{low_priority}")
    
    if issues:
        print("\n前 3 个问题:")
        for i, issue in enumerate(issues[:3], 1):
            print(f"  {i}. [{issue['priority']}] {issue['title']}")
    
    return scores, issues


async def test_ai_analyzer(website_data, scores, issues):
    """测试 AI 分析模块"""
    print("\n=== 测试 AI 分析模块 ===")
    
    if not website_data or not scores or not issues:
        print("✗ 缺少数据，跳过测试")
        return
    
    # 检查是否有 API 密钥
    api_key = os.getenv('LLM_API_KEY', '')
    if not api_key:
        print("⚠ 未设置 LLM_API_KEY，使用模拟模式")
    
    suggestions = await content_analyzer.analyze_and_suggest(website_data, scores, issues)
    
    print(f"\nAI 建议数量：{len(suggestions)}")
    
    if suggestions:
        print("\n前 3 条建议:")
        for i, sug in enumerate(suggestions[:3], 1):
            print(f"  {i}. [{sug.get('priority', 'medium')}] {sug.get('title', 'N/A')}")
            if sug.get('expected_impact'):
                print(f"     预期影响：{sug['expected_impact']}")
    
    return suggestions


async def main():
    """主测试函数"""
    print("=" * 60)
    print("AdSense Evaluator API 测试")
    print("=" * 60)
    
    try:
        # 1. 测试网站分析
        website_data = await test_website_analyzer()
        
        # 2. 测试评分系统
        scores_and_issues = await test_scoring_engine(website_data)
        
        if scores_and_issues:
            scores, issues = scores_and_issues
            
            # 3. 测试 AI 分析
            await test_ai_analyzer(website_data, scores, issues)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
