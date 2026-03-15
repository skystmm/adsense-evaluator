"""
PDF 报告生成服务
使用 ReportLab 生成专业的评估报告 PDF
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import os
from typing import Dict, List, Optional


class PDFReportGenerator:
    """PDF 报告生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_chinese_font()
    
    def _setup_chinese_font(self):
        """设置中文字体（如果可用）"""
        # 尝试注册常见中文字体
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    self.chinese_font = 'ChineseFont'
                    return
                except Exception:
                    continue
        
        # 如果没有中文字体，使用默认字体
        self.chinese_font = None
    
    def _get_style(self, name: str, **kwargs):
        """获取或创建样式"""
        if name in self.styles:
            return self.styles[name]
        
        # 创建自定义样式
        parent = self.styles.get('Normal')
        style = ParagraphStyle(
            name=name,
            parent=parent,
            **kwargs
        )
        return style
    
    def generate(self, report_data: Dict, output_path: Optional[str] = None) -> BytesIO:
        """
        生成 PDF 报告
        
        :param report_data: 报告数据
        :param output_path: 输出路径（可选，如果为 None 则返回 BytesIO）
        :return: BytesIO 对象或文件路径
        """
        # 创建 PDF 文档
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
        else:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # 构建内容
        story = self._build_story(report_data)
        
        # 生成 PDF
        doc.build(story)
        
        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer
    
    def _build_story(self, report_data: Dict) -> List:
        """构建 PDF 内容"""
        story = []
        
        # 标题
        title_style = self._get_style(
            'CustomTitle',
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("AdSense 网站评估报告", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # 基本信息
        story.extend(self._build_basic_info(report_data))
        story.append(Spacer(1, 0.3*inch))
        
        # 总体评分
        story.extend(self._build_overall_score(report_data))
        story.append(Spacer(1, 0.3*inch))
        
        # 详细评分
        story.extend(self._build_metrics(report_data))
        story.append(Spacer(1, 0.3*inch))
        
        # 问题清单
        story.extend(self._build_issues(report_data))
        story.append(Spacer(1, 0.3*inch))
        
        # AI 建议
        if report_data.get('ai_suggestions'):
            story.extend(self._build_suggestions(report_data))
            story.append(Spacer(1, 0.3*inch))
        
        # 页脚信息
        story.extend(self._build_footer(report_data))
        
        return story
    
    def _build_basic_info(self, report_data: Dict) -> List:
        """构建基本信息表格"""
        story = []
        
        subtitle_style = self._get_style(
            'Subtitle',
            fontSize=14,
            leading=18,
            spaceAfter=10
        )
        story.append(Paragraph("基本信息", subtitle_style))
        
        # 基本信息表格
        data = [
            ['评估网站', report_data.get('url', 'N/A')],
            ['报告 ID', report_data.get('report_id', 'N/A')],
            ['评估时间', report_data.get('created_at', 'N/A')],
        ]
        
        table = Table(data, colWidths=[4*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(table)
        return story
    
    def _build_overall_score(self, report_data: Dict) -> List:
        """构建总体评分部分"""
        story = []
        
        subtitle_style = self._get_style(
            'Subtitle',
            fontSize=14,
            leading=18,
            spaceAfter=10
        )
        story.append(Paragraph("总体评分", subtitle_style))
        
        overall_score = report_data.get('overall_score', 0)
        pass_probability = report_data.get('pass_probability', 0)
        rating = report_data.get('rating', 'N/A')
        
        # 确定颜色
        if overall_score >= 80:
            score_color = colors.green
        elif overall_score >= 60:
            score_color = colors.orange
        else:
            score_color = colors.red
        
        data = [
            ['总体得分', f'{overall_score}/100'],
            ['通过概率', f'{pass_probability}%'],
            ['评级', rating],
        ]
        
        table = Table(data, colWidths=[5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (1, 0), (1, 0), score_color),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(table)
        return story
    
    def _build_metrics(self, report_data: Dict) -> List:
        """构建详细评分部分"""
        story = []
        
        subtitle_style = self._get_style(
            'Subtitle',
            fontSize=14,
            leading=18,
            spaceAfter=10
        )
        story.append(Paragraph("详细评分", subtitle_style))
        
        metrics = report_data.get('metrics', {})
        
        # 评分维度映射
        metric_names = {
            'content_quality': '内容质量',
            'site_structure': '网站结构',
            'traffic_source': '流量来源',
            'technical_compliance': '技术合规',
            'policy_compliance': '政策遵守',
        }
        
        metric_max = {
            'content_quality': 35,
            'site_structure': 20,
            'traffic_source': 15,
            'technical_compliance': 20,
            'policy_compliance': 10,
        }
        
        # 表格数据
        data = [['维度', '得分', '满分', '完成率']]
        for key, name in metric_names.items():
            score = metrics.get(key, 0)
            max_score = metric_max.get(key, 0)
            rate = f'{(score/max_score*100):.1f}%' if max_score > 0 else 'N/A'
            data.append([name, str(score), str(max_score), rate])
        
        table = Table(data, colWidths=[4*cm, 2*cm, 2*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        return story
    
    def _build_issues(self, report_data: Dict) -> List:
        """构建问题清单部分"""
        story = []
        
        subtitle_style = self._get_style(
            'Subtitle',
            fontSize=14,
            leading=18,
            spaceAfter=10
        )
        story.append(Paragraph("问题清单", subtitle_style))
        
        issues = report_data.get('issues', [])
        
        if not issues:
            story.append(Paragraph("未发现明显问题", self.styles['Normal']))
            return story
        
        # 优先级颜色
        priority_colors = {
            'high': colors.red,
            'medium': colors.orange,
            'low': colors.green,
        }
        
        priority_names = {
            'high': '高',
            'medium': '中',
            'low': '低',
        }
        
        # 按优先级排序
        sorted_issues = sorted(issues, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low'), 3))
        
        for i, issue in enumerate(sorted_issues, 1):
            # 问题标题
            priority = issue.get('priority', 'low')
            priority_color = priority_colors.get(priority, colors.black)
            priority_name = priority_names.get(priority, '低')
            
            title_style = self._get_style(
                f'IssueTitle{i}',
                fontSize=11,
                leading=14,
                spaceAfter=5,
                textColor=priority_color
            )
            story.append(Paragraph(f"{i}. {issue.get('title', '未知问题')} [{priority_name}优先级]", title_style))
            
            # 问题描述
            desc_style = self._get_style(
                f'IssueDesc{i}',
                fontSize=10,
                leading=12,
                spaceAfter=3,
                alignment=TA_JUSTIFY
            )
            story.append(Paragraph(f"描述：{issue.get('description', 'N/A')}", desc_style))
            
            # 改进建议
            suggestion_style = self._get_style(
                f'IssueSuggestion{i}',
                fontSize=10,
                leading=12,
                spaceAfter=8,
                textColor=colors.darkgreen
            )
            story.append(Paragraph(f"建议：{issue.get('suggestion', 'N/A')}", suggestion_style))
        
        return story
    
    def _build_suggestions(self, report_data: Dict) -> List:
        """构建 AI 建议部分"""
        story = []
        
        subtitle_style = self._get_style(
            'Subtitle',
            fontSize=14,
            leading=18,
            spaceAfter=10
        )
        story.append(Paragraph("AI 智能建议", subtitle_style))
        
        suggestions = report_data.get('ai_suggestions', [])
        
        if not suggestions:
            story.append(Paragraph("暂无 AI 建议", self.styles['Normal']))
            return story
        
        for i, suggestion in enumerate(suggestions, 1):
            # 建议标题
            title_style = self._get_style(
                f'SuggestionTitle{i}',
                fontSize=11,
                leading=14,
                spaceAfter=5,
                textColor=colors.darkblue
            )
            story.append(Paragraph(f"{i}. {suggestion.get('title', '未知建议')}", title_style))
            
            # 建议描述
            desc_style = self._get_style(
                f'SuggestionDesc{i}',
                fontSize=10,
                leading=12,
                spaceAfter=3,
                alignment=TA_JUSTIFY
            )
            story.append(Paragraph(f"描述：{suggestion.get('description', 'N/A')}", desc_style))
            
            # 行动项
            action_items = suggestion.get('action_items', [])
            if action_items:
                for item in action_items:
                    item_style = self._get_style(
                        f'SuggestionItem{i}',
                        fontSize=10,
                        leading=12,
                        leftIndent=10,
                        spaceAfter=2
                    )
                    story.append(Paragraph(f"• {item}", item_style))
            
            # 预期影响
            expected_impact = suggestion.get('expected_impact')
            if expected_impact:
                impact_style = self._get_style(
                    f'SuggestionImpact{i}',
                    fontSize=10,
                    leading=12,
                    spaceAfter=8,
                    textColor=colors.darkgreen,
                    fontStyle='italic'
                )
                story.append(Paragraph(f"预期影响：{expected_impact}", impact_style))
        
        return story
    
    def _build_footer(self, report_data: Dict) -> List:
        """构建页脚信息"""
        story = []
        
        footer_style = self._get_style(
            'Footer',
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("=" * 50, footer_style))
        story.append(Paragraph("本报告由 AdSense Evaluator 自动生成", footer_style))
        story.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        story.append(Paragraph("仅供参考，具体政策要求请以 Google AdSense 官方为准", footer_style))
        
        return story


def generate_pdf_report(report_data: Dict, output_path: Optional[str] = None) -> BytesIO:
    """
    便捷函数：生成 PDF 报告
    
    :param report_data: 报告数据
    :param output_path: 输出路径（可选）
    :return: BytesIO 对象或文件路径
    """
    generator = PDFReportGenerator()
    return generator.generate(report_data, output_path)
