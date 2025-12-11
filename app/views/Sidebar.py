from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo/Title area
        title_widget = QWidget()
        title_widget.setObjectName("sidebar_header")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 20, 20, 20)
        title_layout.setSpacing(6)

        # Logo label (loads image from app/assets/images)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setObjectName("sidebar_logo")
        # Build path relative to this file to ensure it works on different working dirs
        logo_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'techbayanlogo.jpg'))
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            pix = pix.scaled(160, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            # fallback to text if logo not found
            logo_label.setText("POS System")
            logo_label.setObjectName("sidebar_title")

        title_layout.addWidget(logo_label)

        # Brand text under logo
        brand_label = QLabel("TechBayan")
        brand_label.setObjectName("sidebar_brand")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(brand_label)

        layout.addWidget(title_widget)

        # Navigation buttons
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_pos = QPushButton("Point of Sale")
        self.btn_inventory = QPushButton("Inventory")
        self.btn_reports = QPushButton("Reports")
        self.btn_suppliers = QPushButton("Suppliers")
        self.btn_staff = QPushButton("Staff")

        self.buttons = [self.btn_dashboard, self.btn_pos, self.btn_inventory, self.btn_reports, self.btn_suppliers, self.btn_staff]
        
        for btn in self.buttons:
            btn.setObjectName("sidebar_button")
            btn.setCheckable(True)
            btn.setFixedHeight(45)
            nav_layout.addWidget(btn)

        layout.addWidget(nav_widget)
        layout.addStretch()

        self.setLayout(layout)

    def set_active(self, button_name):
        """Set the active button state."""
        for btn in self.buttons:
            btn.setChecked(False)
        
        if button_name == "dashboard":
            self.btn_dashboard.setChecked(True)
        elif button_name == "pos":
            self.btn_pos.setChecked(True)
        elif button_name == "inventory":
            self.btn_inventory.setChecked(True)
        elif button_name == "reports":
            self.btn_reports.setChecked(True)
        elif button_name == "suppliers":
            self.btn_suppliers.setChecked(True)
        elif button_name == "staff":
            self.btn_staff.setChecked(True)