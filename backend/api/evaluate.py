from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from services import website_analyzer, scoring_engine
from ai import content_analyzer
import asyncio
import uuid
from datetime import datetime
import json
import os

router = APIRouter()

# 报告存储目录
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)


class EvaluateRequest(BaseModel):
    url: str
    include_ai_analysis: bool = True
    use_playwright: bool = False  # 是否使用 Playwright 渲染 JavaScript


class EvaluateResponse(BaseModel):
    success: bool
    url: str
    overall_score: int
    pass_probability: float
    metrics: dict
    issues: list
    ai_suggestions: Optional[list] = None
    report_id: str
    rating: str
    created_at: str


@router.post("/", response_model=EvaluateResponse)
async def evaluate_website(request: EvaluateRequest):
    """
    评估网站是否符合 AdSense 要求
    
    Args:
        request: 评估请求，包含 URL 和选项
    
    Returns:
        评估报告
    
    Examples:
        POST /api/evaluate/
        {
            "url": "https://example.com",
            "include_ai_analysis": true,
            "use_playwright": false
        }
    """
    try:
        # 1. 爬取和分析网站
        website_data = await website_analyzer.analyze(
            request.url,
            use_playwright=request.use_playwright
        )
        
        if not website_data:
            raise HTTPException(status_code=400, detail="无法访问目标网站，请检查 URL 是否正确")
        
        # 2. 计算评分
        scores = scoring_engine.calculate_scores(website_data)
        overall_score = sum(scores.values())
        
        # 3. 识别问题
        issues = scoring_engine.identify_issues(website_data, scores)
        
        # 4. AI 分析（可选）
        ai_suggestions = None
        if request.include_ai_analysis:
            ai_suggestions = await content_analyzer.analyze_and_suggest(
                website_data,
                scores,
                issues
            )
        
        # 5. 计算通过概率和等级
        pass_probability = scoring_engine.calculate_pass_probability(overall_score, len(issues))
        _, rating_code, rating_desc = scoring_engine.calculate_overall_score(scores)
        
        # 6. 生成报告 ID 并保存
        report_id = f"rpt_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now().isoformat()
        
        # 保存完整报告
        report_data = {
            'report_id': report_id,
            'url': request.url,
            'overall_score': overall_score,
            'pass_probability': pass_probability,
            'metrics': scores,
            'issues': issues,
            'ai_suggestions': ai_suggestions,
            'rating': rating_desc,
            'created_at': created_at,
            'website_data': website_data,
        }
        
        _save_report(report_id, report_data)
        
        return EvaluateResponse(
            success=True,
            url=request.url,
            overall_score=overall_score,
            pass_probability=pass_probability,
            metrics=scores,
            issues=issues,
            ai_suggestions=ai_suggestions,
            report_id=report_id,
            rating=rating_desc,
            created_at=created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估失败：{str(e)}")


@router.post("/batch", response_model=List[EvaluateResponse])
async def batch_evaluate(requests: List[EvaluateRequest]):
    """
    批量评估多个网站
    
    Args:
        requests: 评估请求列表
    
    Returns:
        评估报告列表
    """
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="单次最多评估 10 个网站")
    
    tasks = [evaluate_website(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    responses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            responses.append({
                'success': False,
                'url': requests[i].url,
                'error': str(result),
            })
        else:
            responses.append(result)
    
    return responses


def _save_report(report_id: str, report_data: dict):
    """保存报告到文件"""
    report_file = os.path.join(REPORTS_DIR, f"{report_id}.json")
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存报告失败：{e}")


def _load_report(report_id: str) -> Optional[dict]:
    """从文件加载报告"""
    report_file = os.path.join(REPORTS_DIR, f"{report_id}.json")
    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载报告失败：{e}")
    return None


def _list_reports(limit: int = 50) -> List[dict]:
    """列出所有报告"""
    reports = []
    try:
        files = sorted(
            os.listdir(REPORTS_DIR),
            key=lambda f: os.path.getmtime(os.path.join(REPORTS_DIR, f)),
            reverse=True
        )
        
        for filename in files[:limit]:
            if filename.endswith('.json'):
                report_id = filename[:-5]
                report_data = _load_report(report_id)
                if report_data:
                    reports.append({
                        'report_id': report_id,
                        'url': report_data.get('url', ''),
                        'overall_score': report_data.get('overall_score', 0),
                        'pass_probability': report_data.get('pass_probability', 0),
                        'rating': report_data.get('rating', ''),
                        'created_at': report_data.get('created_at', ''),
                    })
    except Exception as e:
        print(f"列出报告失败：{e}")
    
    return reports
