from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.colors import HexColor
from datetime import datetime
from typing import List, Dict
import os


class LegalContractPDFReport:
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.story = []
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ClauseTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#e74c3c'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#f39c12'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#27ae60'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Citation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#7f8c8d'),
            leftIndent=20,
            spaceAfter=5
        ))
    
    def add_title_page(self, contract_name: str, analysis_date: str = None):
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph("AI LEGAL CONTRACT ANALYSIS REPORT", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        contract_para = Paragraph(f"<b>Contract:</b> {contract_name}", self.styles['CustomBody'])
        self.story.append(contract_para)
        self.story.append(Spacer(1, 0.2*inch))
        
        date_para = Paragraph(f"<b>Analysis Date:</b> {analysis_date}", self.styles['CustomBody'])
        self.story.append(date_para)
        self.story.append(Spacer(1, 0.2*inch))
        
        system_para = Paragraph("<b>Analysis System:</b> AI Legal Contract Auditor v1.0", self.styles['CustomBody'])
        self.story.append(system_para)
        self.story.append(Spacer(1, 0.2*inch))
        
        model_para = Paragraph("<b>AI Model:</b> Llama 3.2 (Local Ollama)", self.styles['CustomBody'])
        self.story.append(model_para)
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self, results: List[Dict]):
        self.story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        found_count = sum(1 for r in results if r['found'])
        high_risk = sum(1 for r in results if r.get('risk_rating') == 'HIGH')
        medium_risk = sum(1 for r in results if r.get('risk_rating') == 'MEDIUM')
        low_risk = sum(1 for r in results if r.get('risk_rating') == 'LOW')
        
        summary_data = [
            ['Metric', 'Count'],
            ['Total Clauses Analyzed', str(len(results))],
            ['Clauses Found', str(found_count)],
            ['Clauses Not Found', str(len(results) - found_count)],
            ['High Risk Clauses', str(high_risk)],
            ['Medium Risk Clauses', str(medium_risk)],
            ['Low Risk Clauses', str(low_risk)]
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#ecf0f1')])
        ]))
        
        self.story.append(summary_table)
        self.story.append(Spacer(1, 0.3*inch))
        
        if high_risk > 0:
            warning = Paragraph(
                f"⚠️ <b>WARNING:</b> {high_risk} HIGH RISK clause(s) identified. Immediate review recommended.",
                self.styles['RiskHigh']
            )
            self.story.append(warning)
            self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(PageBreak())
    
    def add_clause_analysis(self, result: Dict, include_redline: bool = False):
        clause_type = result['clause_type']
        
        self.story.append(Paragraph(f"CLAUSE: {clause_type}", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        if not result['found']:
            not_found = Paragraph("✗ <b>NOT FOUND</b> - This clause was not identified in the contract.", self.styles['CustomBody'])
            self.story.append(not_found)
            self.story.append(Spacer(1, 0.3*inch))
            return
        
        found = Paragraph("✓ <b>FOUND</b>", self.styles['CustomBody'])
        self.story.append(found)
        self.story.append(Spacer(1, 0.15*inch))
        
        if result.get('risk_rating'):
            risk_rating = result['risk_rating']
            if risk_rating == 'HIGH':
                style = self.styles['RiskHigh']
                icon = "🔴"
            elif risk_rating == 'MEDIUM':
                style = self.styles['RiskMedium']
                icon = "🟡"
            else:
                style = self.styles['RiskLow']
                icon = "🟢"
            
            risk_para = Paragraph(f"{icon} <b>Risk Level: {risk_rating}</b>", style)
            self.story.append(risk_para)
            self.story.append(Spacer(1, 0.1*inch))
        
        if result.get('summary'):
            self.story.append(Paragraph("<b>Summary (Plain English):</b>", self.styles['ClauseTitle']))
            summary_para = Paragraph(result['summary'], self.styles['CustomBody'])
            self.story.append(summary_para)
            self.story.append(Spacer(1, 0.15*inch))
        
        if result.get('risk_explanation'):
            self.story.append(Paragraph("<b>Risk Assessment:</b>", self.styles['ClauseTitle']))
            risk_exp = Paragraph(result['risk_explanation'], self.styles['CustomBody'])
            self.story.append(risk_exp)
            self.story.append(Spacer(1, 0.15*inch))
        
        if result.get('content'):
            self.story.append(Paragraph("<b>Extracted Clause Text:</b>", self.styles['ClauseTitle']))
            content_para = Paragraph(result['content'][:1000] + "..." if len(result['content']) > 1000 else result['content'], self.styles['CustomBody'])
            self.story.append(content_para)
            self.story.append(Spacer(1, 0.15*inch))
        
        if result.get('citations'):
            self.story.append(Paragraph("<b>Citations:</b>", self.styles['ClauseTitle']))
            for idx, citation in enumerate(result['citations'][:3], 1):
                citation_text = f"[{idx}] Page {citation['page']}, Section: {citation['section']}"
                citation_para = Paragraph(citation_text, self.styles['Citation'])
                self.story.append(citation_para)
            self.story.append(Spacer(1, 0.15*inch))
        
        if include_redline and result.get('redline_suggestion'):
            self.story.append(Paragraph("<b>Redline Suggestion:</b>", self.styles['ClauseTitle']))
            redline_para = Paragraph(result['redline_suggestion'], self.styles['CustomBody'])
            self.story.append(redline_para)
            self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_qa_section(self, qa_results: List[Dict]):
        self.story.append(PageBreak())
        self.story.append(Paragraph("INTERACTIVE Q&A RESULTS", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        for idx, qa in enumerate(qa_results, 1):
            question = Paragraph(f"<b>Q{idx}:</b> {qa['question']}", self.styles['ClauseTitle'])
            self.story.append(question)
            self.story.append(Spacer(1, 0.1*inch))
            
            answer = Paragraph(f"<b>A:</b> {qa['answer']}", self.styles['CustomBody'])
            self.story.append(answer)
            self.story.append(Spacer(1, 0.1*inch))
            
            confidence = Paragraph(f"<i>Confidence: {qa['confidence']}</i>", self.styles['Citation'])
            self.story.append(confidence)
            self.story.append(Spacer(1, 0.2*inch))
    
    def generate(self):
        self.doc.build(self.story)
        print(f"\n✅ PDF Report generated: {self.output_path}")
        return self.output_path
