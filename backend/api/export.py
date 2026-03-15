"""
报告导出 API
支持 PDF、CSV 等格式导出
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from io import BytesIO

from models.database import SessionLocal, EvaluationReport
from services.pdf_generator import generate_pdf_report
from api.auth import get_current_user
from models.database import User

router = APIRouter()

# 报告存储目录
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/pdf/{report_id}", tags=["导出"])
async def export_report_pdf(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出单个报告为 PDF
    
    :param report_id: 报告 ID
    :param db: 数据库会话
    :param current_user: 当前用户（需要登录）
    :return: PDF 文件
    """
    # 从数据库或文件加载报告
    report_data = _load_report(report_id)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 生成 PDF
    try:
        pdf_buffer = generate_pdf_report(report_data)
        
        # 返回 PDF 文件
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=adsense_report_{report_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 生成失败：{str(e)}")


@router.post("/pdf/batch", tags=["导出"])
async def export_reports_pdf_batch(
    report_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量导出报告为 PDF（合并为一个文件）
    
    :param report_ids: 报告 ID 列表
    :param db: 数据库会话
    :param current_user: 当前用户（需要登录）
    :return: 合并的 PDF 文件
    """
    if not report_ids:
        raise HTTPException(status_code=400, detail="请提供报告 ID 列表")
    
    if len(report_ids) > 10:
        raise HTTPException(status_code=400, detail="最多支持 10 个报告合并")
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, PageBreak
        from reportlab.pdfgen import canvas
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        from services.pdf_generator import PDFReportGenerator
        generator = PDFReportGenerator()
        
        for i, report_id in enumerate(report_ids):
            report_data = _load_report(report_id)
            if report_data:
                # 添加每个报告的内容
                report_story = generator._build_story(report_data)
                story.extend(report_story)
                
                # 如果不是最后一个报告，添加分页
                if i < len(report_ids) - 1:
                    story.append(PageBreak())
        
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=adsense_reports_batch.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 批量生成失败：{str(e)}")


@router.get("/csv", tags=["导出"])
async def export_reports_csv(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出报告列表为 CSV
    
    :param limit: 报告数量限制
    :param offset: 偏移量
    :param db: 数据库会话
    :param current_user: 当前用户（需要登录）
    :return: CSV 文件
    """
    try:
        # 查询报告
        reports = db.query(EvaluationReport).order_by(
            EvaluationReport.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # 生成 CSV
        import csv
        
        buffer = BytesIO()
        buffer.write(b'\xef\xbb\xbf')  # UTF-8 BOM
        
        writer = csv.writer(buffer)
        writer.writerow([
            '报告 ID', '网站 URL', '总体得分', '通过概率', 
            '内容质量', '网站结构', '流量来源', '技术合规', '政策遵守',
            '问题数量', '创建时间'
        ])
        
        for report in reports:
            metrics = report.metrics or {}
            issues = report.issues or []
            
            writer.writerow([
                report.report_id,
                report.url,
                report.overall_score,
                report.pass_probability,
                metrics.get('content_quality', 0),
                metrics.get('site_structure', 0),
                metrics.get('traffic_source', 0),
                metrics.get('technical_compliance', 0),
                metrics.get('policy_compliance', 0),
                len(issues),
                report.created_at.strftime('%Y-%m-%d %H:%M:%S') if report.created_at else ''
            ])
        
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=adsense_reports.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV 导出失败：{str(e)}")


@router.get("/json/{report_id}", tags=["导出"])
async def export_report_json(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出单个报告为 JSON
    
    :param report_id: 报告 ID
    :param db: 数据库会话
    :param current_user: 当前用户（需要登录）
    :return: JSON 文件
    """
    report_data = _load_report(report_id)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return Response(
        content=json.dumps(report_data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=adsense_report_{report_id}.json"
        }
    )


def _load_report(report_id: str) -> Optional[dict]:
    """从文件或数据库加载报告"""
    # 先尝试从数据库加载
    db = SessionLocal()
    try:
        report = db.query(EvaluationReport).filter(
            EvaluationReport.report_id == report_id
        ).first()
        
        if report:
            return {
                'report_id': report.report_id,
                'url': report.url,
                'overall_score': report.overall_score,
                'pass_probability': report.pass_probability,
                'metrics': report.metrics,
                'issues': report.issues,
                'ai_suggestions': report.ai_suggestions,
                'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S') if report.created_at else '',
            }
    finally:
        db.close()
    
    # 从文件加载（向后兼容）
    report_file = os.path.join(REPORTS_DIR, f"{report_id}.json")
    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    return None
