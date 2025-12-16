from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox, QWidget, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QGuiApplication


class CheckoutReceiptDialog(QDialog):
    """Payment & Receipt dialog for POS checkout."""
    
    def __init__(self, items, subtotal, cashier_name=None, parent=None):
        super().__init__(parent)
        self.items = items
        self.subtotal = subtotal
        self.vat_amount = subtotal * 0.12  # 12% VAT
        self.total = subtotal + self.vat_amount
        self.cashier_name = cashier_name
        
        self.payment_mode = None
        self.amount_received = 0
        self.change = 0
        
        self.init_ui()
        self.setWindowTitle("Checkout - Payment & Receipt")

    
    def init_ui(self):
        """Initialize the modern payment dialog."""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header section
        header = QLabel("Complete Payment")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1a1a1a; margin-bottom: 4px;")
        layout.addWidget(header)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #e5e7eb; max-height: 1px;")
        layout.addWidget(divider)

        # Main content container
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        # ===== Order Summary Card =====
        summary_card = self._create_summary_card()
        content_layout.addWidget(summary_card)

        # ===== Payment Details Card =====
        payment_card = self._create_payment_card()
        content_layout.addWidget(payment_card)

        layout.addLayout(content_layout)

        # Spacer
        layout.addStretch()

        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(44)
        self.cancel_btn.setFont(QFont("Segoe UI", 10))
        self.cancel_btn.setStyleSheet("""
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
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("Complete Transaction")
        self.confirm_btn.setFixedHeight(44)
        self.confirm_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 32px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Finalize size and center the dialog
        self.setFixedSize(700, 750)
        self._center_dialog()

    def _create_summary_card(self):
        """Create the order summary card."""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(12)

        # Card title
        title = QLabel("Order Summary")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #374151; background: transparent; border: none;")
        card_layout.addWidget(title)

        # Summary items
        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(10)

        # Subtotal row
        subtotal_row = QHBoxLayout()
        subtotal_label = QLabel("Subtotal")
        subtotal_label.setFont(QFont("Segoe UI", 10))
        subtotal_label.setStyleSheet("color: #6b7280;")
        self.subtotal_val_label = QLabel(f"₱{self.subtotal:,.2f}")
        self.subtotal_val_label.setFont(QFont("Segoe UI", 10))
        self.subtotal_val_label.setStyleSheet("color: #1f2937;")
        self.subtotal_val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        subtotal_row.addWidget(subtotal_label)
        subtotal_row.addStretch()
        subtotal_row.addWidget(self.subtotal_val_label)
        summary_layout.addLayout(subtotal_row)

        # VAT row
        vat_row = QHBoxLayout()
        vat_label = QLabel("VAT (12%)")
        vat_label.setFont(QFont("Segoe UI", 10))
        vat_label.setStyleSheet("color: #6b7280;")
        self.vat_val_label = QLabel(f"₱{self.vat_amount:,.2f}")
        self.vat_val_label.setFont(QFont("Segoe UI", 10))
        self.vat_val_label.setStyleSheet("color: #1f2937;")
        self.vat_val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        vat_row.addWidget(vat_label)
        vat_row.addStretch()
        vat_row.addWidget(self.vat_val_label)
        summary_layout.addLayout(vat_row)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #cbd5e1; max-height: 1px; margin: 4px 0;")
        summary_layout.addWidget(divider)

        # Total row
        total_row = QHBoxLayout()
        total_label = QLabel("Total")
        total_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        total_label.setStyleSheet("color: #111827;")
        self.total_val_label = QLabel(f"₱{self.total:,.2f}")
        self.total_val_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.total_val_label.setStyleSheet("color: #2563eb;")
        self.total_val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row.addWidget(total_label)
        total_row.addStretch()
        total_row.addWidget(self.total_val_label)
        summary_layout.addLayout(total_row)

        card_layout.addLayout(summary_layout)
        return card

    def _create_payment_card(self):
        """Create the payment details card."""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(16)

        # Card title
        title = QLabel("Payment Details")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #374151; background: transparent; border: none;")
        card_layout.addWidget(title)

        # Payment mode
        mode_label = QLabel("Payment Mode")
        mode_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        mode_label.setStyleSheet("color: #374151; background: transparent; border: none; margin-bottom: 2px;")
        card_layout.addWidget(mode_label)
        
        self.payment_mode_combo = QComboBox()
        self.payment_mode_combo.addItems(["Cash", "Card", "GCash"])
        self.payment_mode_combo.setFixedHeight(42)
        self.payment_mode_combo.setFont(QFont("Segoe UI", 10))
        self.payment_mode_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                color: #1f2937;
            }
            QComboBox:hover {
                border-color: #2563eb;
            }
            QComboBox:focus {
                border-color: #2563eb;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6b7280;
                margin-right: 8px;
            }
        """)
        card_layout.addWidget(self.payment_mode_combo)

        # Amount received
        amount_label = QLabel("Amount Received")
        amount_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        amount_label.setStyleSheet("color: #374151; background: transparent; border: none; margin-top: 8px; margin-bottom: 2px;")
        card_layout.addWidget(amount_label)
        
        self.amount_received_input = QLineEdit()
        self.amount_received_input.setPlaceholderText("0.00")
        self.amount_received_input.setFixedHeight(42)
        self.amount_received_input.setFont(QFont("Segoe UI", 10))
        self.amount_received_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.amount_received_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                color: #1f2937;
            }
            QLineEdit:hover {
                border-color: #2563eb;
            }
            QLineEdit:focus {
                border-color: #2563eb;
                outline: none;
            }
        """)
        self.amount_received_input.textChanged.connect(self.calculate_change)
        card_layout.addWidget(self.amount_received_input)

        # Add spacing before change display
        card_layout.addSpacing(8)

        # Change display
        change_container = QWidget()
        change_container.setStyleSheet("""
            QWidget {
                background-color: #f0f9ff;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
            }
        """)
        change_layout = QHBoxLayout(change_container)
        change_layout.setContentsMargins(16, 12, 16, 12)
        
        change_label = QLabel("Change")
        change_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        change_label.setStyleSheet("color: #1e40af; background: transparent; border: none;")
        
        self.change_val_label = QLabel(f"₱{self.change:,.2f}")
        self.change_val_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.change_val_label.setStyleSheet("color: #1e40af; background: transparent; border: none;")
        self.change_val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        change_layout.addWidget(change_label)
        change_layout.addStretch()
        change_layout.addWidget(self.change_val_label)
        
        card_layout.addWidget(change_container)

        return card
    
    def calculate_change(self):
        """Calculate change when amount received changes."""
        try:
            amount_text = self.amount_received_input.text().strip()
            if amount_text:
                amount = float(amount_text)
                self.amount_received = amount
                self.change = max(0, amount - self.total)
                self.change_val_label.setText(f"₱{self.change:,.2f}")
                
                # Update change display styling based on validation
                if amount < self.total:
                    self.change_val_label.setStyleSheet("color: #dc2626; background: transparent; border: none; font-weight: bold;")
                    self.amount_received_input.setStyleSheet("""
                        QLineEdit {
                            background-color: white;
                            border: 2px solid #dc2626;
                            border-radius: 8px;
                            padding: 8px 12px;
                            color: #1f2937;
                        }
                    """)
                else:
                    self.change_val_label.setStyleSheet("color: #059669; background: transparent; border: none; font-weight: bold;")
                    self.amount_received_input.setStyleSheet("""
                        QLineEdit {
                            background-color: #f0fdf4;
                            border: 2px solid #059669;
                            border-radius: 8px;
                            padding: 8px 12px;
                            color: #1f2937;
                        }
                    """)
            else:
                self.change = 0
                self.change_val_label.setText(f"₱0.00")
                self.change_val_label.setStyleSheet("color: #1e40af; background: transparent; border: none; font-weight: bold;")
                self.amount_received_input.setStyleSheet("""
                    QLineEdit {
                        background-color: white;
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                        padding: 8px 12px;
                        color: #1f2937;
                    }
                    QLineEdit:hover {
                        border-color: #2563eb;
                    }
                    QLineEdit:focus {
                        border-color: #2563eb;
                    }
                """)
        except ValueError:
            self.change = 0
            self.change_val_label.setText(f"₱0.00 (Invalid)")
            self.change_val_label.setStyleSheet("color: #dc2626; background: transparent; border: none;")
            self.amount_received_input.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    border: 2px solid #dc2626;
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #1f2937;
                }
            """)

    def _center_dialog(self):
        """Center the dialog on screen or parent."""
        try:
            parent_widget = self.parent() or self.parentWidget()
            if parent_widget is not None:
                try:
                    parent_center_global = parent_widget.mapToGlobal(parent_widget.rect().center())
                    geo = self.frameGeometry()
                    geo.moveCenter(parent_center_global)
                    self.move(geo.topLeft())
                except Exception:
                    parent_geo = parent_widget.frameGeometry()
                    parent_center = parent_geo.center()
                    geo = self.frameGeometry()
                    geo.moveCenter(parent_center)
                    self.move(geo.topLeft())
            else:
                screen_geo = QGuiApplication.primaryScreen().availableGeometry()
                x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
                y = screen_geo.y() + (screen_geo.height() - self.height()) // 2
                self.move(x, y)
        except Exception:
            pass

    def showEvent(self, event):
        """Re-center when the dialog is shown to ensure it appears centered."""
        super().showEvent(event)
        self._center_dialog()
    
    def get_payment_details(self):
        """Return payment details."""
        return {
            'payment_mode': self.payment_mode_combo.currentText(),
            'amount_received': self.amount_received,
            'change': self.change,
            'vat_amount': self.vat_amount,
            'total': self.total
        }