"""
PDF Report Generator

Generates PDF reports with test results.
Includes title page, summary, and detailed results.
"""

from typing import List, Dict, Any
from datetime import datetime
import os


def generate_pdf_report(test_results: List[Dict[str, Any]], output_dir: str = ".") -> str:
    """
    Generate a PDF report from test results.
    
    Args:
        test_results: List of test result dictionaries
        output_dir: Directory where the PDF file will be saved
    
    Returns:
        Path to the generated PDF file
    
    Raises:
        ImportError: If reportlab library is not installed
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        use_reportlab = True
    except ImportError:
        use_reportlab = False
    
    if not use_reportlab:
        raise ImportError(
            "reportlab library is required for PDF report generation.\n"
            "Install it with: pip install reportlab"
        )
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"SmartBU_TestResults_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#0066CC"),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#0066CC"),
        spaceAfter=12,
        spaceBefore=12
    )
    normal_style = styles['Normal']
    
    # Title Page
    story.append(Paragraph("SmartBU Test Report", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Generate timestamp for report
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Generated: {report_date}", normal_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Summary Section
    story.append(Paragraph("Executive Summary", heading_style))
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.get("Status") == "PASS")
    failed_tests = sum(1 for r in test_results if r.get("Status") == "FAIL")
    
    summary_text = f"""
    <b>Total Tests:</b> {total_tests}<br/>
    <b>Passed:</b> {passed_tests}<br/>
    <b>Failed:</b> {failed_tests}<br/>
    """
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Detailed Results Section
    story.append(Paragraph("Detailed Test Results", heading_style))
    story.append(Spacer(1, 0.1 * inch))
    
    # Create results table
    table_data = [["Test ID", "Test Name", "Measured", "Expected", "Status"]]
    
    for result in test_results:
        measured_value = result.get("MeasuredValue")
        if measured_value is not None:
            measured_value = f"{measured_value:.3f}" if isinstance(measured_value, float) else str(measured_value)
        else:
            measured_value = "N/A"
        
        status = result.get("Status", "")
        table_data.append([
            result.get("TestCaseID", ""),
            result.get("TestName", ""),
            measured_value,
            result.get("Expected", ""),
            status
        ])
    
    # Create table with styling
    table = Table(table_data, colWidths=[1.0*inch, 2.5*inch, 1.0*inch, 1.5*inch, 0.8*inch])
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0066CC")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Status column styling
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
    ]))
    
    # Color status cells
    for row_idx, result in enumerate(test_results, start=1):
        status = result.get("Status", "")
        if status == "PASS":
            table.setStyle(TableStyle([
                ('BACKGROUND', (4, row_idx), (4, row_idx), colors.HexColor("#92D050")),
                ('TEXTCOLOR', (4, row_idx), (4, row_idx), colors.black),
            ]))
        elif status == "FAIL":
            table.setStyle(TableStyle([
                ('BACKGROUND', (4, row_idx), (4, row_idx), colors.HexColor("#FF0000")),
                ('TEXTCOLOR', (4, row_idx), (4, row_idx), colors.white),
            ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    
    return filepath
