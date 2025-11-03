"""
PDF Report Generator for AI Automation Audits
Creates professional PDF reports with automation recommendations
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from io import BytesIO

def generate_automation_report_pdf(analysis_data: dict, lead_data: dict) -> BytesIO:
    """
    Generate PDF report for automation opportunities
    
    Args:
        analysis_data: Website analysis results
        lead_data: Lead information (name, email, website)
    
    Returns:
        BytesIO: PDF file in memory
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'],
                              fontSize=24, textColor=colors.HexColor('#0c969b'),
                              spaceAfter=30, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'],
                              fontSize=16, textColor=colors.HexColor('#0c969b'),
                              spaceAfter=12, spaceBefore=20))
    
    # Cover Page
    elements.append(Spacer(1, 1.5*inch))
    
    title = Paragraph("AI Automation Report", styles['CustomTitle'])
    elements.append(title)
    
    subtitle = Paragraph(f"for {analysis_data.get('url', 'Your Website')}", styles['Heading3'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    date_text = Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", 
                          ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=TA_CENTER))
    elements.append(date_text)
    elements.append(Spacer(1, 0.5*inch))
    
    # Lead Info Box
    lead_name = lead_data.get('name', 'Valued Business Owner')
    prepared_for = Paragraph(
        f"<b>Prepared for:</b> {lead_name}<br/><b>Email:</b> {lead_data.get('email', 'N/A')}",
        styles['Normal']
    )
    elements.append(prepared_for)
    elements.append(Spacer(1, 0.3*inch))
    
    # Powered by
    powered = Paragraph(
        "<i>Powered by GR8 AI Automation</i>",
        ParagraphStyle('PoweredBy', parent=styles['Normal'], alignment=TA_CENTER, 
                      textColor=colors.grey, fontSize=10)
    )
    elements.append(powered)
    
    elements.append(PageBreak())
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles['SectionHeader']))
    summary_text = analysis_data.get('summary', 'Your website has significant automation potential.')
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Business Type & Score
    business_type = analysis_data.get('business_type', 'Business').title()
    confidence = analysis_data.get('confidence_score', 0.85) * 100
    
    info_data = [
        ['Business Type', business_type],
        ['Automation Score', f"{int(confidence)}%"],
        ['Opportunities Found', str(len(analysis_data.get('recommendations', [])))],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Strengths
    if analysis_data.get('strengths'):
        elements.append(Paragraph("Key Strengths", styles['SectionHeader']))
        for strength in analysis_data['strengths'][:3]:
            elements.append(Paragraph(f"• {strength}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Automation Opportunities
    elements.append(PageBreak())
    elements.append(Paragraph("Recommended Automations", styles['SectionHeader']))
    
    recommendations = analysis_data.get('recommendations', [])
    for i, rec in enumerate(recommendations[:6], 1):
        # Recommendation header
        rec_title = Paragraph(
            f"<b>{i}. {rec.get('title', 'Automation')}</b> - {rec.get('priority', 'Medium').upper()} Priority",
            ParagraphStyle('RecTitle', parent=styles['Heading3'], fontSize=12, 
                          textColor=colors.HexColor('#0c969b'))
        )
        elements.append(rec_title)
        elements.append(Spacer(1, 0.1*inch))
        
        # Description
        elements.append(Paragraph(f"<b>What it does:</b> {rec.get('description', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Rationale
        elements.append(Paragraph(f"<b>Why you need it:</b> {rec.get('rationale', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Impact
        elements.append(Paragraph(f"<b>Expected impact:</b> {rec.get('expected_impact', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 0.05*inch))
        
        # ROI
        if rec.get('estimated_value'):
            roi_style = ParagraphStyle('ROI', parent=styles['Normal'], 
                                      textColor=colors.HexColor('#10b981'), fontName='Helvetica-Bold')
            elements.append(Paragraph(f"💰 Estimated Value: {rec['estimated_value']}", roi_style))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Next Steps
    elements.append(PageBreak())
    elements.append(Paragraph("Next Steps", styles['SectionHeader']))
    
    next_steps = [
        "1. Review the automation recommendations above",
        "2. Prioritize automations based on your current needs",
        "3. Sign up for GR8 AI Automation to activate these automations",
        "4. Use our setup wizards to deploy in minutes",
        "5. Monitor performance through our analytics dashboard"
    ]
    
    for step in next_steps:
        elements.append(Paragraph(step, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Call to Action
    cta_style = ParagraphStyle('CTA', parent=styles['Normal'], alignment=TA_CENTER,
                               fontSize=14, textColor=colors.HexColor('#0c969b'), 
                               fontName='Helvetica-Bold')
    elements.append(Paragraph("Ready to start automating?", cta_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("Visit https://gr8ai.com to get started", 
                              ParagraphStyle('Link', parent=styles['Normal'], alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    buffer.seek(0)
    return buffer
