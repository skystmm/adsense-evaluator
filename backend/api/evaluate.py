from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from services import website_analyzer, scoring_engine
from ai import content_analyzer
import asyncio

router = APIRouter()

class EvaluateRequest(BaseModel):
    url: str
    include_ai_analysis: bool = True

class EvaluateResponse(BaseModel):
    success: bool
    url: str
    overall_score: int
    pass_probability: float
    metrics: dict
    issues: list
    ai_suggestions: Optional[list] = None
    report_id: Optional[str] = None

@router.post("/", response_model=EvaluateResponse)
async def evaluate_website(request: EvaluateRequest):
    """
    评估网站是否符合 AdSense 要求
    """
    try:
        # 1. 爬取和分析网站
        website_data = await website_analyzer.analyze(request.url)
        
        if not website_data:
            raise HTTPException(status_code=400, detail="无法访问目标网站")
        
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
        
        # 5. 计算通过概率
        pass_probability = calculate_pass_probability(overall_score, len(issues))
        
        # 6. 生成报告 ID
        report_id = f"rpt_{asyncio.get_event_loop().time()}"
        
        return EvaluateResponse(
            success=True,
            url=request.url,
            overall_score=overall_score,
            pass_probability=pass_probability,
            metrics=scores,
            issues=issues,
            ai_suggestions=ai_suggestions,
            report_id=report_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估失败：{str(e)}")

def calculate_pass_probability(score: int, issue_count: int) -> float:
    """
    根据评分和问题数量计算通过概率
    """
    base_probability = score / 100.0
    issue_penalty = min(issue_count * 0.05, 0.3)
    probability = max(0, min(1, base_probability - issue_penalty))
    return round(probability * 100, 1)
