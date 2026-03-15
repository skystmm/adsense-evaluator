from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import os
import json

router = APIRouter()

# 报告存储目录
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')


class HistoryItem(BaseModel):
    report_id: str
    url: str
    overall_score: int
    pass_probability: float
    rating: str
    created_at: str
    issues_count: int
    high_priority_issues: int


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    has_more: bool


@router.get("/", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    days: int = Query(default=30, ge=1, le=365),
    min_score: Optional[int] = Query(default=None, ge=0, le=100),
):
    """
    获取评估历史记录（支持筛选和分页）
    
    Args:
        limit: 每页数量（1-100）
        offset: 偏移量
        days: 最近多少天（1-365）
        min_score: 最低分数筛选
    
    Returns:
        历史记录列表
    
    Examples:
        GET /api/history/?limit=20&offset=0&days=30
        GET /api/history/?min_score=70&days=7
    """
    reports = _list_reports(limit=1000)  # 先获取较多数据用于筛选
    
    # 时间筛选
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []
    
    for r in reports:
        try:
            created_at = datetime.fromisoformat(r.get('created_at', ''))
            if created_at < cutoff_date:
                continue
        except:
            pass
        
        # 分数筛选
        if min_score is not None and r.get('overall_score', 0) < min_score:
            continue
        
        filtered.append(r)
    
    # 分页
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    
    items = [
        HistoryItem(
            report_id=r.get('report_id', ''),
            url=r.get('url', ''),
            overall_score=r.get('overall_score', 0),
            pass_probability=r.get('pass_probability', 0),
            rating=r.get('rating', ''),
            created_at=r.get('created_at', ''),
            issues_count=r.get('issues_count', 0),
            high_priority_issues=r.get('high_priority_issues', 0),
        )
        for r in paginated
    ]
    
    return HistoryResponse(
        items=items,
        total=total,
        has_more=offset + limit < total
    )


@router.get("/url/{url:path}")
async def get_history_by_url(url: str):
    """
    根据 URL 获取历史评估记录
    
    Args:
        url: 网站 URL（需要 URL 编码）
    
    Returns:
        该 URL 的所有历史评估记录
    
    Examples:
        GET /api/history/url/https%3A%2F%2Fexample.com
    """
    from urllib.parse import unquote
    
    decoded_url = unquote(url)
    reports = _list_reports(limit=1000)
    
    # 筛选匹配的 URL
    matched = [
        r for r in reports
        if r.get('url', '').rstrip('/') == decoded_url.rstrip('/')
    ]
    
    # 按时间排序（最新在前）
    matched.sort(
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )
    
    return {
        'url': decoded_url,
        'total_evaluations': len(matched),
        'evaluations': matched,
    }


@router.get("/trend")
async def get_score_trend(
    days: int = Query(default=30, ge=1, le=90),
):
    """
    获取评分趋势（最近 N 天的平均分数变化）
    
    Args:
        days: 天数（1-90）
    
    Returns:
        评分趋势数据
    
    Examples:
        GET /api/history/trend?days=30
    """
    reports = _list_reports(limit=1000)
    
    # 按日期分组
    daily_scores = {}
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for r in reports:
        try:
            created_at = datetime.fromisoformat(r.get('created_at', ''))
            if created_at < cutoff_date:
                continue
            
            date_str = created_at.strftime('%Y-%m-%d')
            if date_str not in daily_scores:
                daily_scores[date_str] = []
            
            daily_scores[date_str].append(r.get('overall_score', 0))
        except:
            pass
    
    # 计算每日平均分
    trend = []
    for date_str in sorted(daily_scores.keys()):
        scores = daily_scores[date_str]
        avg_score = sum(scores) / len(scores) if scores else 0
        trend.append({
            'date': date_str,
            'average_score': round(avg_score, 1),
            'evaluations_count': len(scores),
        })
    
    return {
        'days': days,
        'trend': trend,
    }


def _list_reports(limit: int = 50) -> List[dict]:
    """列出所有报告（带问题统计）"""
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
                    issues = report_data.get('issues', [])
                    reports.append({
                        'report_id': report_id,
                        'url': report_data.get('url', ''),
                        'overall_score': report_data.get('overall_score', 0),
                        'pass_probability': report_data.get('pass_probability', 0),
                        'rating': report_data.get('rating', ''),
                        'created_at': report_data.get('created_at', ''),
                        'issues_count': len(issues),
                        'high_priority_issues': sum(1 for i in issues if i.get('priority') == 'high'),
                    })
    except Exception as e:
        print(f"列出报告失败：{e}")
    
    return reports


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
