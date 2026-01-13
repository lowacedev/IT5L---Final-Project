from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTextBrowser, QWidget, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QGuiApplication
from app.utils.ReceiptGenerator import ReceiptGenerator
from datetime import datetime


class ReceiptDisplayDialog(QDialog):
    """Dialog that displays a printable receipt preview rendered from HTML."""

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
        self.sale_date = datetime.now()
        
        self.init_ui()
        self.setWindowTitle(f"Receipt #{sale_id}")
    
    def init_ui(self):
        """Initialize receipt display dialog rendered from HTML preview."""
        layout = QVBoxLayout()
        self.resize(360, 520)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint)
        layout.setSpacing(8)

        # HTML receipt preview
        self.preview_browser = QTextBrowser()
        self.preview_browser.setOpenExternalLinks(True)
        self.preview_browser.setReadOnly(True)
        self.preview_browser.setMinimumWidth(320)
        self.preview_browser.setStyleSheet("background: #fff; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.preview_browser)

        # Generate HTML from ReceiptGenerator and render
        html = ReceiptGenerator.generate_receipt_html(
            self.sale_id, self.items, self.subtotal, self.vat_amount, self.total,
            self.payment_mode, self.amount_received, self.change,
            cashier_name=self.cashier_name, sale_date=self.sale_date
        )
        self.preview_browser.setHtml(html)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(16, 16, 16, 16)

        self.pdf_btn = QPushButton("Save as PDF")
        self.pdf_btn.setFixedHeight(44)
        self.pdf_btn.setFont(QFont("Segoe UI", 10))
    
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
                    sale_date=self.sale_date,
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