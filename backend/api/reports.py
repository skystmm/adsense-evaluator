from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List

router = APIRouter()

class Report(BaseModel):
    report_id: str
    url: str
    overall_score: int
    created_at: str
    metrics: Dict
    issues: List
    ai_suggestions: Optional[List] = None

# 临时存储（实际实现会用数据库）
reports_db = {}

@router.get("/{report_id}", response_model=Report)
async def get_report(report_id: str):
    """
    获取评估报告详情
    """
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return reports_db[report_id]

@router.get("/", response_model=List[Report])
async def list_reports():
    """
    获取所有报告列表
    """
    return list(reports_db.values())
