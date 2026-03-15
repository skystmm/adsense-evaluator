from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import os
import json

router = APIRouter()

# 报告存储目录
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')


class ReportSummary(BaseModel):
    report_id: str
    url: str
    overall_score: int
    pass_probability: float
    rating: str
    created_at: str


class ReportDetail(BaseModel):
    report_id: str
    url: str
    overall_score: int
    pass_probability: float
    metrics: Dict
    issues: List
    ai_suggestions: Optional[List] = None
    rating: str
    created_at: str
    website_data: Optional[Dict] = None


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(report_id: str):
    """
    获取评估报告详情
    
    Args:
        report_id: 报告 ID（格式：rpt_xxxxxxxxxxxx）
    
    Returns:
        完整报告详情
    
    Examples:
        GET /api/reports/rpt_abc123def456
    """
    report_data = _load_report(report_id)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return ReportDetail(
        report_id=report_data.get('report_id', report_id),
        url=report_data.get('url', ''),
        overall_score=report_data.get('overall_score', 0),
        pass_probability=report_data.get('pass_probability', 0),
        metrics=report_data.get('metrics', {}),
        issues=report_data.get('issues', []),
        ai_suggestions=report_data.get('ai_suggestions'),
        rating=report_data.get('rating', ''),
        created_at=report_data.get('created_at', ''),
        website_data=report_data.get('website_data')
    )


@router.get("/", response_model=List[ReportSummary])
async def list_reports(limit: int = 50, offset: int = 0):
    """
    获取报告列表（分页）
    
    Args:
        limit: 每页数量（默认 50，最大 100）
        offset: 偏移量（默认 0）
    
    Returns:
        报告摘要列表
    
    Examples:
        GET /api/reports/?limit=20&offset=0
    """
    limit = min(limit, 100)
    reports = _list_reports(limit=limit + offset)
    
    # 分页
    paginated = reports[offset:offset + limit]
    
    return [
        ReportSummary(
            report_id=r.get('report_id', ''),
            url=r.get('url', ''),
            overall_score=r.get('overall_score', 0),
            pass_probability=r.get('pass_probability', 0),
            rating=r.get('rating', ''),
            created_at=r.get('created_at', '')
        )
        for r in paginated
    ]


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """
    删除评估报告
    
    Args:
        report_id: 报告 ID
    
    Returns:
        删除结果
    
    Examples:
        DELETE /api/reports/rpt_abc123def456
    """
    report_file = os.path.join(REPORTS_DIR, f"{report_id}.json")
    
    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    try:
        os.remove(report_file)
        return {"success": True, "message": "报告已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败：{str(e)}")


@router.get("/stats/summary")
async def get_stats_summary():
    """
    获取统计摘要
    
    Returns:
        统计信息
    
    Examples:
        GET /api/reports/stats/summary
    """
    reports = _list_reports(limit=1000)
    
    if not reports:
        return {
            'total_reports': 0,
            'average_score': 0,
            'average_pass_probability': 0,
        }
    
    total = len(reports)
    avg_score = sum(r.get('overall_score', 0) for r in reports) / total
    avg_prob = sum(r.get('pass_probability', 0) for r in reports) / total
    
    # 按评分分布
    score_distribution = {
        'excellent': 0,  # 90+
        'good': 0,       # 75-89
        'fair': 0,       # 60-74
        'poor': 0,       # 40-59
        'very_poor': 0,  # <40
    }
    
    for r in reports:
        score = r.get('overall_score', 0)
        if score >= 90:
            score_distribution['excellent'] += 1
        elif score >= 75:
            score_distribution['good'] += 1
        elif score >= 60:
            score_distribution['fair'] += 1
        elif score >= 40:
            score_distribution['poor'] += 1
        else:
            score_distribution['very_poor'] += 1
    
    return {
        'total_reports': total,
        'average_score': round(avg_score, 1),
        'average_pass_probability': round(avg_prob, 1),
        'score_distribution': score_distribution,
    }


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
        if not os.path.exists(REPORTS_DIR):
            return reports
        
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
