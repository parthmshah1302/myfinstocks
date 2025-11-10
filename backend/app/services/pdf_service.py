from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime
from decimal import Decimal

class PDFService:
    """Service to generate portfolio PDFs"""
    
    @staticmethod
    def generate_portfolio_pdf(portfolio_data: dict) -> BytesIO:
        """
        Generate a PDF report for a client's portfolio
        Returns BytesIO object that can be sent as response
        """
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
        )
        
        # Title
        title = Paragraph("MyFinStocks Portfolio Report", title_style)
        elements.append(title)
        
        # Client Info
        client_info = f"""
        <b>Client:</b> {portfolio_data['client_name']}<br/>
        <b>Email:</b> {portfolio_data['client_email'] or 'N/A'}<br/>
        <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        elements.append(Paragraph(client_info, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Portfolio Summary
        elements.append(Paragraph("Portfolio Summary", heading_style))
        
        summary_data = [
            ['Total Current Value', f"Rs {portfolio_data['total_current_value']:,.2f}"],
            ['Yesterday\'s Value', f"Rs {portfolio_data['total_yesterday_value']:,.2f}"],
            ['Day Change', f"Rs {portfolio_data['total_day_change']:,.2f}"],
            ['Day Change %', f"{portfolio_data['total_day_change_percent']:.2f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Holdings Table
        elements.append(Paragraph("Holdings Details", heading_style))
        
        holdings_data = [
            ['Stock', 'Qty', 'Live Price', 'Current Value', 'Day Change', 'Change %']
        ]
        
        for holding in portfolio_data['holdings']:
            holdings_data.append([
                f"{holding['symbol']}\n{holding['company_name']}",
                str(holding['quantity']),
                f"Rs {float(holding['live_price'] or 0):,.2f}",
                f"Rs {float(holding['current_value']):,.2f}",
                f"Rs {float(holding['day_change']):,.2f}",
                f"{float(holding['day_change_percent']):.2f}%"
            ])
        
        holdings_table = Table(holdings_data, colWidths=[2*inch, 0.7*inch, 1*inch, 1.2*inch, 1*inch, 0.9*inch])
        holdings_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(holdings_table)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(
            "This report is generated by MyFinStocks Portfolio Management System<br/>For informational purposes only. Not financial advice.",
            footer_style
        )
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer