"""
Professional PDF Report Generator for POS System.
Generates polished, metrics-rich reports with company branding.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table as RLTable,
    TableStyle,
    Image as RLImage,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ProfessionalPDFReportGenerator:
    """Generate professional PDF reports with metrics and branding."""
    
    COMPANY_NAME = "TechBayan POS System"
    LOGO_CANDIDATES = [
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'techbayanlogo.jpg'),
    ]
    
    def __init__(self, filename, page_size=letter, landscape_mode=False):
        """
        Initialize report generator.
        
        Args:
            filename: Output PDF file path
            page_size: reportlab page size (letter, A4, etc.)
            landscape_mode: If True, use landscape orientation
        """
        self.filename = filename
        if landscape_mode:
            page_size = landscape(page_size)
        
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=page_size,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=1.2 * inch,
            bottomMargin=0.75 * inch,
        )
        self.elements = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.logo_path = self._find_logo()
        self.page_size = page_size
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=12,
            alignment=TA_CENTER,
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=2,
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold',
            spaceAfter=8,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold',
            spaceAfter=10,
            spaceBefore=10,
        ))
    
    def _find_logo(self):
        """Find and return logo path if it exists."""
        for candidate in self.LOGO_CANDIDATES:
            normalized = os.path.normpath(candidate)
            if os.path.exists(normalized):
                return normalized
        return None
    
    def add_header(self):
        """Add report header with logo and company name."""
        # Create a centered header with logo and company name
        header_elements = []
        
        # Add logo if available
        if self.logo_path:
            try:
                logo = RLImage(self.logo_path, width=1.2 * inch, height=0.5 * inch)
                header_elements.append(logo)
            except Exception:
                pass
        
        # Add company name centered
        company_style = ParagraphStyle(
            'CenteredCompanyName',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=10,
        )
        company_para = Paragraph(self.COMPANY_NAME, company_style)
        header_elements.append(company_para)
        
        # Create a container table for centered alignment
        header_table_data = [[Spacer(1, 0)]]
        for elem in header_elements:
            header_table_data.append([elem])
        
        header_table = RLTable(header_table_data, colWidths=[None])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.elements.append(header_table)
        self.elements.append(Spacer(1, 0.15 * inch))
    
    def add_title_and_metadata(self, title, filters=None, metrics=None):
        """
        Add report title, filters applied, and key metrics.
        
        Args:
            title: Report title
            filters: Dict of filter names and values
            metrics: Dict of metric names and values
        """
        # Title
        self.elements.append(Paragraph(title, self.styles['ReportTitle']))
        self.elements.append(Spacer(1, 0.1 * inch))
        
        # Metadata bar (Date Generated, etc.)
        generated_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        metadata_text = f"<b>Report Generated:</b> {generated_date}"
        self.elements.append(Paragraph(metadata_text, self.styles['ReportSubtitle']))
        self.elements.append(Spacer(1, 0.15 * inch))
        
        # Filters Applied Section
        if filters and any(filters.values()):
            self.elements.append(Paragraph("Filters Applied", self.styles['SectionHeader']))
            
            filter_data = []
            for key, value in filters.items():
                if value:
                    filter_data.append([
                        Paragraph(f"<b>{key}:</b>", self.styles['MetricLabel']),
                        Paragraph(str(value), self.styles['MetricLabel']),
                    ])
            
            if filter_data:
                filter_table = RLTable(filter_data, colWidths=[2 * inch, None])
                filter_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
                ]))
                self.elements.append(filter_table)
                self.elements.append(Spacer(1, 0.15 * inch))
        
        # Key Metrics Section
        if metrics and any(metrics.values()):
            self.elements.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
            
            # Create metric boxes (simple table)
            metric_rows = []
            metric_items = list(metrics.items())
            
            # Create rows with up to 3 metrics per row
            for i in range(0, len(metric_items), 3):
                row = []
                for j in range(3):
                    if i + j < len(metric_items):
                        key, value = metric_items[i + j]
                        cell = f"<b>{key}</b><br/><font size=12 color=#1f2937><b>{value}</b></font>"
                        row.append(Paragraph(cell, self.styles['Normal']))
                    else:
                        row.append("")
                metric_rows.append(row)
            
            metrics_table = RLTable(metric_rows, colWidths=[1.8 * inch] * 3)
            metrics_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4f8')),
            ]))
            self.elements.append(metrics_table)
            self.elements.append(Spacer(1, 0.2 * inch))
    
    def add_data_table(self, title, headers, data):
        """
        Add a data table with professional styling.
        
        Args:
            title: Table section title
            headers: List of column headers
            data: List of rows, each row is a list of values
        """
        if title:
            self.elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Prepare table data with headers
        table_data = [headers] + data
        
        # Create table
        col_widths = [None] * len(headers)  # Auto-width
        table = RLTable(table_data, colWidths=col_widths)
        
        # Apply styling
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ])
        
        # Alternate row background
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9fafb'))
        
        # Right-align numeric columns (heuristic)
        for col_idx in range(len(headers)):
            numeric_count = 0
            for r in range(1, min(10, len(table_data))):
                try:
                    val_str = str(table_data[r][col_idx]).replace('Php', '').replace(',', '').strip()
                    float(val_str)
                    numeric_count += 1
                except Exception:
                    pass
            
            if numeric_count >= max(1, (len(table_data) - 1) // 2):
                table_style.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')
        
        table.setStyle(table_style)
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.2 * inch))
    
    def add_footer_note(self, note_text):
        """Add a footer note/disclaimer."""
        footer_style = ParagraphStyle(
            'FooterNote',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceAfter=10,
        )
        self.elements.append(Spacer(1, 0.1 * inch))
        self.elements.append(Paragraph(note_text, footer_style))
    
    def add_page_break(self):
        """Add a page break."""
        self.elements.append(PageBreak())
    
    def build(self, on_first_page=None, on_later_pages=None):
        """
        Build and write the PDF document.
        
        Args:
            on_first_page: Callback function for first page (canvas, doc)
            on_later_pages: Callback function for later pages (canvas, doc)
        """
        if on_first_page and on_later_pages:
            self.doc.build(
                self.elements,
                onFirstPage=on_first_page,
                onLaterPages=on_later_pages,
            )
        else:
            self.doc.build(self.elements)
