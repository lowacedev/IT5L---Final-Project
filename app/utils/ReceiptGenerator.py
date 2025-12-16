from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

class ReceiptGenerator:
    """Generate printable/PDF receipts for POS transactions."""
    
    @staticmethod
    def generate_receipt_html(sale_id, items, subtotal, vat_amount, total, 
                             payment_mode, amount_received, change, 
                             cashier_name=None, sale_date=None):
        """Generate HTML receipt for display and printing."""
        if sale_date is None:
            sale_date = datetime.now()
        
        # Format the receipt as HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; width: 300px; margin: 20px auto; }}
                .receipt {{ border: 1px solid black; padding: 20px; }}
                .header {{ text-align: center; font-weight: bold; margin-bottom: 20px; }}
                .store-name {{ font-size: 16px; margin-bottom: 5px; }}
                .receipt-number {{ font-size: 12px; color: #666; margin-bottom: 10px; }}
                .divider {{ border-top: 1px dashed black; margin: 10px 0; }}
                .items {{ margin: 15px 0; }}
                .item-row {{ display: flex; justify-content: space-between; margin: 5px 0; font-size: 11px; }}
                .item-name {{ flex: 1; }}
                .item-qty {{ width: 30px; text-align: center; }}
                .item-price {{ width: 50px; text-align: right; }}
                .totals {{ margin: 15px 0; }}
                .total-row {{ display: flex; justify-content: space-between; margin: 5px 0; font-size: 12px; }}
                .grand-total {{ font-weight: bold; font-size: 14px; margin-top: 10px; }}
                .payment {{ margin: 15px 0; font-size: 11px; }}
                .payment-row {{ display: flex; justify-content: space-between; margin: 3px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 10px; color: #666; }}
                .success {{ color: green; font-weight: bold; text-align: center; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="store-name">COMPUTER PARTS POS</div>
                    <div class="receipt-number">Receipt #{sale_id}</div>
                    <div style="font-size: 10px;">{sale_date.strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                
                <div class="divider"></div>
                
                <div class="items">
                    <div style="font-weight: bold; font-size: 11px; display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Item</span>
                        <span style="width: 100px; text-align: right;">Qty × Price</span>
                    </div>
"""
        
        for item in items:
            html += f"""
                    <div class="item-row">
                        <span class="item-name">{item['name']}</span>
                        <span style="width: 100px; text-align: right;">{item['qty']}×Php {item['price']:,.2f}</span>
                    </div>
                    <div class="item-row" style="text-align: right; font-weight: bold;">
                        Php {item['qty'] * item['price']:,.2f}
                    </div>
"""
        
        html += f"""
                </div>
                
                <div class="divider"></div>
                
                <div class="totals">
                    <div class="total-row">
                        <span>Subtotal:</span>
                        <span>Php {subtotal:,.2f}</span>
                    </div>
                    <div class="total-row">
                        <span>VAT (12%):</span>
                        <span>Php {vat_amount:,.2f}</span>
                    </div>
                    <div class="total-row grand-total">
                        <span>TOTAL:</span>
                        <span>Php {total:,.2f}</span>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <div class="payment">
                    <div class="payment-row">
                        <span>Payment Mode:</span>
                        <span style="font-weight: bold;">{payment_mode}</span>
                    </div>
                    <div class="payment-row">
                        <span>Amount Received:</span>
                        <span>Php {amount_received:,.2f}</span>
                    </div>
                    <div class="payment-row" style="font-weight: bold;">
                        <span>Change:</span>
                        <span>Php {change:,.2f}</span>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <div class="footer">
"""
        
        if cashier_name:
            html += f"<div>Cashier: {cashier_name}</div>"
        
        html += f"""
                    <div>Thank you for your purchase!</div>
                    <div>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                
                <div class="success">✓ TRANSACTION COMPLETE</div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generate_pdf_receipt(sale_id, items, subtotal, vat_amount, total, 
                            payment_mode, amount_received, change, 
                            cashier_name=None, sale_date=None, filename=None):
        """Generate PDF receipt file."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            if sale_date is None:
                sale_date = datetime.now()
            
            if filename is None:
                filename = f"receipt_{sale_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create PDF
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=(3*inch, 8*inch), 
                                   rightMargin=0.25*inch, leftMargin=0.25*inch,
                                   topMargin=0.25*inch, bottomMargin=0.25*inch)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            center_style = ParagraphStyle(
                'Center',
                parent=styles['Normal'],
                alignment=1,  # Center
                fontSize=11,
                fontName='Helvetica-Bold'
            )
            
            small_style = ParagraphStyle(
                'Small',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1
            )
            
            # Header
            story.append(Paragraph("COMPUTER PARTS POS", center_style))
            story.append(Paragraph(f"Receipt #{sale_id}", small_style))
            story.append(Paragraph(sale_date.strftime('%Y-%m-%d %H:%M:%S'), small_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Items table
            item_data = [['Item', 'Qty', 'Price', 'Total']]
            for item in items:
                item_total = item['qty'] * item['price']
                item_data.append([
                    item['name'][:20],
                    str(item['qty']),
                    f"Php {item['price']:,.0f}",
                    f"Php {item_total:,.0f}"
                ])
            
            items_table = Table(item_data, colWidths=[1.2*inch, 0.4*inch, 0.6*inch, 0.7*inch])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(items_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Totals
            totals_data = [
                ['Subtotal:', f'Php {subtotal:,.2f}'],
                ['VAT (12%):', f'Php {vat_amount:,.2f}'],
                ['TOTAL:', f'Php {total:,.2f}'],
            ]
            totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, 0), 3),
            ]))
            story.append(totals_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Payment section
            payment_data = [
                ['Payment Mode:', payment_mode],
                ['Amount Received:', f'Php {amount_received:,.2f}'],
                ['Change:', f'Php {change:,.2f}'],
            ]
            payment_table = Table(payment_data, colWidths=[1.5*inch, 1.5*inch])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(payment_table)
            story.append(Spacer(1, 0.15*inch))
            
            # Footer
            if cashier_name:
                story.append(Paragraph(f"Cashier: {cashier_name}", small_style))
            story.append(Paragraph("Thank you for your purchase!", small_style))
            story.append(Paragraph("✓ TRANSACTION COMPLETE", center_style))
            
            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)
            return pdf_buffer, filename
            
        except Exception as e:
            print(f"[RECEIPT GENERATOR ERROR] {e}")
            return None, None
