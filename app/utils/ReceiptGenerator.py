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
        
        # Format the receipt as HTML with store header and contact info
        store_name = "TechBayan"
        store_address = "Matina, Davao City"
        store_contact = "Tel: (02) 1234-5678"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica', Arial, sans-serif; width: 300px; margin: 8px auto; color: #222; }}
                .receipt {{ padding: 12px; background: #fff; border-radius: 4px; }}
                .header {{ text-align: center; margin-bottom: 6px; }}
                .store-name {{ font-size: 16px; font-weight: 700; margin-bottom: 2px; }}
                .store-meta {{ font-size: 10px; color: #666; margin-bottom: 6px; }}
                .divider {{ border-top: 1px solid #e6e6e6; margin: 8px 0; }}
                .items {{ margin: 6px 0; font-size: 11px; }}
                .item-row {{ display: grid; grid-template-columns: 1fr auto; gap: 6px; align-items: start; margin: 4px 0; }}
                .item-name {{ font-weight: 500; }}
                .item-sub {{ font-size: 10px; color: #444; }}
                .item-total {{ text-align: right; font-weight: 600; min-width: 80px; }}
                .totals {{ margin: 8px 0; font-size: 12px; }}
                .total-row {{ display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: center; margin: 4px 0; }}
                .grand-total {{ font-weight: 700; font-size: 14px; margin-top: 6px; display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: center; }}
                .payment {{ margin: 8px 0; font-size: 11px; display: grid; grid-template-columns: 1fr auto; gap: 4px; }}
                .footer {{ text-align: center; margin-top: 10px; font-size: 10px; color: #666; }}
                .success {{ color: #0b7a4d; font-weight: bold; text-align: center; margin-top: 8px; }}
            </style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="store-name">{store_name}</div>
                    <div class="store-meta">{store_address} • {store_contact}</div>
                    <div class="store-meta">Receipt #{sale_id} • {sale_date.strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                <div class="divider"></div>
                <div class="items">
                    <div style="font-weight:700; font-size:11px; display:grid; grid-template-columns:1fr auto; gap:6px; margin-bottom:6px;">
                        <span>Item</span>
                        <span style="text-align:right;">Total</span>
                    </div>
"""
        
        for item in items:
            line_total = item['qty'] * item['price']
            html += f"""
                    <div class="item-row">
                        <div>
                            <div class="item-name">{item['name']}</div>
                            <div class="item-sub">{item['qty']} × Php {item['price']:,.2f}</div>
                        </div>
                        <div class="item-total">Php {line_total:,.2f}</div>
                    </div>
"""
        
        html += f"""
                </div>
                <div class="divider"></div>
                <div class="totals">
                    <div class="total-row">
                        <div>Subtotal:</div>
                        <div style="text-align:right;">Php {subtotal:,.2f}</div>
                    </div>
                    <div class="total-row">
                        <div>VAT (12%):</div>
                        <div style="text-align:right;">Php {vat_amount:,.2f}</div>
                    </div>
                    <div class="grand-total">
                        <div style="font-weight:700;">TOTAL:</div>
                        <div style="text-align:right; font-weight:700;">Php {total:,.2f}</div>
                    </div>
                </div>
                <div class="divider"></div>
                <div class="payment">
                    <div style="display:flex; justify-content:space-between;">
                        <div><strong>Payment Mode:</strong></div>
                        <div style="text-align:right;">{payment_mode}</div>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <div>Amount Received:</div>
                        <div style="text-align:right;">Php {amount_received:,.2f}</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-weight:700; margin-top:6px;">
                        <div>Change:</div>
                        <div style="text-align:right;">Php {change:,.2f}</div>
                    </div>
                </div>
                <div class="divider"></div>
                <div class="footer">
"""
        
        if cashier_name:
            html += f"<div style=\"font-size:11px; margin-bottom:4px;\">Cashier: {cashier_name}</div>"

        html += f"""
                    <div>Thank you for your purchase!</div>
                    <div style=\"font-size:10px; color:#888; margin-top:6px;\">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                <div class=\"success\">✓ TRANSACTION COMPLETE</div>
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
            
            # Header (store name and meta)
            store_name = "TechBayan"
            store_address = "Matina, Davao City"
            store_contact = "Tel: (02) 1234-5678"

            story.append(Paragraph(store_name, center_style))
            story.append(Paragraph(store_address + ' • ' + store_contact, small_style))
            story.append(Paragraph(f"Receipt #{sale_id} • {sale_date.strftime('%Y-%m-%d %H:%M:%S')}", small_style))
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
            story.append(Paragraph(" TRANSACTION COMPLETE", center_style))
            
            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)
            return pdf_buffer, filename
            
        except Exception as e:
            print(f"[RECEIPT GENERATOR ERROR] {e}")
            return None, None
