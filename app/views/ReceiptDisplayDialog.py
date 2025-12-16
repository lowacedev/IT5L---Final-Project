from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QGuiApplication
from app.utils.ReceiptGenerator import ReceiptGenerator

class ReceiptDisplayDialog(QDialog):
    """Display and allow PDF export of completed transaction receipt."""
    
    def __init__(self, sale_id, items, subtotal, vat_amount, total, 
                 payment_mode, amount_received, change, cashier_name=None, parent=None):
        super().__init__(parent)
        self.sale_id = sale_id
        self.items = items
        self.subtotal = subtotal
        self.vat_amount = vat_amount
        self.total = total
        self.payment_mode = payment_mode
        self.amount_received = amount_received
        self.change = change
        self.cashier_name = cashier_name
        
        self.init_ui()
        self.setWindowTitle(f"Receipt #{sale_id}")
    
    def init_ui(self):
        """Initialize receipt display dialog."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scrollable receipt preview
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")
        
        receipt_widget = QWidget()
        receipt_widget.setStyleSheet("background-color: white;")
        receipt_layout = QVBoxLayout(receipt_widget)
        receipt_layout.setContentsMargins(40, 30, 40, 30)
        receipt_layout.setSpacing(2)
        
        # Receipt header
        header = QLabel("===========================")
        header.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(header)
        
        title = QLabel("COMPUTER PARTS POS")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(title)
        
        receipt_num = QLabel(f"Receipt #{self.sale_id}")
        receipt_num.setFont(QFont("Courier New", 10))
        receipt_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(receipt_num)
        
        divider1 = QLabel("===========================")
        divider1.setFont(QFont("Courier New", 10))
        divider1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(divider1)
        
        # Cashier info
        if self.cashier_name:
            receipt_layout.addSpacing(5)
            cashier_line = QLabel(f"Cashier: {self.cashier_name}")
            cashier_line.setFont(QFont("Courier New", 9))
            cashier_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
            receipt_layout.addWidget(cashier_line)
            receipt_layout.addSpacing(5)
            
            cashier_divider = QLabel("---------------------------")
            cashier_divider.setFont(QFont("Courier New", 10))
            cashier_divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
            receipt_layout.addWidget(cashier_divider)
        
     

        # Items grid with columns: Name | Qty | Price
        from PyQt6.QtWidgets import QGridLayout
        items_grid = QGridLayout()
        items_grid.setHorizontalSpacing(8)
        items_grid.setVerticalSpacing(4)
        # Header row
        hdr_name = QLabel("Name")
        hdr_name.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        items_grid.addWidget(hdr_name, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        hdr_qty = QLabel("Qty")
        hdr_qty.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        items_grid.addWidget(hdr_qty, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        hdr_price = QLabel("Price")
        hdr_price.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        items_grid.addWidget(hdr_price, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)

        # Populate items
        row = 1
        for item in self.items:
            name = item.get('name', '')
            name_lbl = QLabel(name)
            name_lbl.setFont(QFont("Courier New", 9))
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            items_grid.addWidget(name_lbl, row, 0)

            qty_lbl = QLabel(str(item.get('qty', 0)))
            qty_lbl.setFont(QFont("Courier New", 9))
            qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            items_grid.addWidget(qty_lbl, row, 1)

            price_val = item.get('price', 0.0)
            price_lbl = QLabel(f"Php {price_val:,.2f}")
            price_lbl.setFont(QFont("Courier New", 9))
            price_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            items_grid.addWidget(price_lbl, row, 2)

            row += 1

        receipt_layout.addLayout(items_grid)
        
        receipt_layout.addSpacing(5)
        divider2 = QLabel("---------------------------")
        divider2.setFont(QFont("Courier New", 10))
        divider2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(divider2)
        
        # Totals section
        subtotal_line = QLabel(f"Subtotal:            Php {self.subtotal:,.2f}")
        subtotal_line.setFont(QFont("Courier New", 10))
        receipt_layout.addWidget(subtotal_line)
        
        vat_line = QLabel(f"VAT (12%):          Php {self.vat_amount:,.2f}")
        vat_line.setFont(QFont("Courier New", 10))
        receipt_layout.addWidget(vat_line)
        
        receipt_layout.addSpacing(5)
        divider3 = QLabel("===========================")
        divider3.setFont(QFont("Courier New", 10))
        divider3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(divider3)
        
        total_line = QLabel(f"TOTAL:              Php {self.total:,.2f}")
        total_line.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        receipt_layout.addWidget(total_line)
        
        receipt_layout.addSpacing(5)
        divider4 = QLabel("---------------------------")
        divider4.setFont(QFont("Courier New", 10))
        divider4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(divider4)
        
        # Payment section
        
        
        mode_line = QLabel(f"Payment Mode:       {self.payment_mode}")
        mode_line.setFont(QFont("Courier New", 10))
        receipt_layout.addWidget(mode_line)
        
        amount_line = QLabel(f"Amount Received:    Php {self.amount_received:,.2f}")
        amount_line.setFont(QFont("Courier New", 10))
        receipt_layout.addWidget(amount_line)
        
        change_line = QLabel(f"Change:                 Php {self.change:,.2f}")
        change_line.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        receipt_layout.addWidget(change_line)
        
        receipt_layout.addSpacing(5)
        divider5 = QLabel("===========================")
        divider5.setFont(QFont("Courier New", 10))
        divider5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(divider5)
        
        # Footer
        receipt_layout.addSpacing(5)
        thank_you = QLabel("Thank you for your purchase!")
        thank_you.setFont(QFont("Courier New", 9))
        thank_you.setAlignment(Qt.AlignmentFlag.AlignCenter)
        receipt_layout.addWidget(thank_you)
        
        receipt_layout.addStretch()
        scroll.setWidget(receipt_widget)
        layout.addWidget(scroll)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(16, 16, 16, 16)
        button_layout.setSpacing(12)
        
        self.pdf_btn = QPushButton(" Save as PDF")
        self.pdf_btn.setFixedHeight(44)
        self.pdf_btn.setFont(QFont("Segoe UI", 10))
        # Use same neutral bordered style as CheckoutReceiptDialog's cancel button
        self.pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #6b7280;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 0 24px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #f3f4f6;
            }
        """)
        self.pdf_btn.clicked.connect(self.save_pdf)
        button_layout.addWidget(self.pdf_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(44)
        self.close_btn.setFont(QFont("Segoe UI", 10))
        # Match the neutral cancel button style from CheckoutReceiptDialog
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #6b7280;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 0 24px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #f3f4f6;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Set fixed size to fit receipt content (width of 27 characters in Courier New)
        self.setFixedSize(380, 600)
        self._center_dialog()
    
    def _center_dialog(self):
        """Center the dialog on screen or parent."""
        try:
            parent_widget = self.parent() or self.parentWidget()
            if parent_widget is not None:
                # More reliable: map parent's center to global coordinates
                try:
                    parent_center_global = parent_widget.mapToGlobal(parent_widget.rect().center())
                    geo = self.frameGeometry()
                    geo.moveCenter(parent_center_global)
                    self.move(geo.topLeft())
                except Exception:
                    # Fallback to frameGeometry method
                    parent_geo = parent_widget.frameGeometry()
                    parent_center = parent_geo.center()
                    geo = self.frameGeometry()
                    geo.moveCenter(parent_center)
                    self.move(geo.topLeft())
            else:
                # Center on primary screen
                screen_geo = QGuiApplication.primaryScreen().availableGeometry()
                x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
                y = screen_geo.y() + (screen_geo.height() - self.height()) // 2
                self.move(x, y)
        except Exception:
            pass

    def showEvent(self, event):
        """Re-center when the dialog is shown to ensure correct positioning."""
        super().showEvent(event)
        self._center_dialog()
    
    def save_pdf(self):
        """Save receipt as PDF file."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            # Open file dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Receipt as PDF",
                f"receipt_{self.sale_id}_{self.total:,.0f}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                pdf_buffer, pdf_filename = ReceiptGenerator.generate_pdf_receipt(
                    sale_id=self.sale_id,
                    items=self.items,
                    subtotal=self.subtotal,
                    vat_amount=self.vat_amount,
                    total=self.total,
                    payment_mode=self.payment_mode,
                    amount_received=self.amount_received,
                    change=self.change,
                    cashier_name=self.cashier_name,
                    filename=filename
                )
                
                if pdf_buffer:
                    with open(filename, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    QMessageBox.information(self, "Success", f"Receipt saved to:\n{filename}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to generate PDF")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save PDF: {str(e)}")