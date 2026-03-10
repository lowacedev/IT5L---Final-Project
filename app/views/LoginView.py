# app/views/login_view.py
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
import logging

logger = logging.getLogger(__name__)

# Style constants
LABEL_STYLE = "font-weight: 600; color: #374151;"


class LoginView(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("TechBayan")
        self.setFixedSize(450, 750)
        self.logged_in_user = None
        self.setup_ui()
        self.setStyleSheet(open("app/styles/styles.qss").read())

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'techbayanlogo.jpg'))
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            pix = pix.scaled(120, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("TechBayan")
            logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #111827;")
        
        brand_label = QLabel("TechBayan")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(brand_label)
        main_layout.addLayout(header_layout)
        
        main_layout.addSpacing(20)
        
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        
        self.lbl_username = QLabel("Username")
        self.lbl_username.setStyleSheet(LABEL_STYLE)
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Enter your username")
        self.txt_username.setMinimumHeight(40)
        
        self.lbl_password = QLabel("Password")
        self.lbl_password.setStyleSheet(LABEL_STYLE)
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Enter your password")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setMinimumHeight(40)
        
        form_layout.addWidget(self.lbl_username)
        form_layout.addWidget(self.txt_username)
        form_layout.addWidget(self.lbl_password)
        form_layout.addWidget(self.txt_password)
        
        # CAPTCHA Section
        captcha_label = QLabel("Verify CAPTCHA")
        captcha_label.setStyleSheet(LABEL_STYLE)
        form_layout.addWidget(captcha_label)
        
        # CAPTCHA Image Display
        self.captcha_image_label = QLabel()
        self.captcha_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.captcha_image_label.setFixedHeight(120)
        self.captcha_image_label.setStyleSheet("background-color: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 4px;")
        form_layout.addWidget(self.captcha_image_label)
        
        # CAPTCHA Refresh Button (below image)
        self.btn_refresh_captcha = QPushButton(" Refresh CAPTCHA")
        self.btn_refresh_captcha.setFixedHeight(38)
        self.btn_refresh_captcha.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
                border-color: #9CA3AF;
            }
            QPushButton:pressed {
                background-color: #D1D5DB;
            }
        """)
        form_layout.addWidget(self.btn_refresh_captcha)
        
        # Add spacing after refresh button
        form_layout.addSpacing(5)
        
        # CAPTCHA Input
        self.lbl_captcha = QLabel("Enter CAPTCHA Code")
        self.lbl_captcha.setStyleSheet(LABEL_STYLE)
        self.txt_captcha = QLineEdit()
        self.txt_captcha.setPlaceholderText("Enter the code above (case-insensitive)")
        self.txt_captcha.setMinimumHeight(40)
        form_layout.addWidget(self.lbl_captcha)
        form_layout.addWidget(self.txt_captcha)
        
        main_layout.addWidget(form_frame)
        
        self.btn_login = QPushButton("Login")
        self.btn_login.setObjectName("primary_button")
        self.btn_login.setMinimumHeight(45)
        self.btn_login.setStyleSheet("""
            #primary_button {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: 1px solid #2563EB;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            #primary_button:hover {
                background-color: #2563EB;
                border-color: #1D4ED8;
            }
            #primary_button:pressed {
                background-color: #1D4ED8;
            }
        """)
        
        main_layout.addWidget(self.btn_login)
        main_layout.addStretch()
        
        self.setLayout(main_layout)

    def collect_form_data(self):
        return (
            self.txt_username.text().strip(),
            self.txt_password.text().strip(),
            self.txt_captcha.text().strip()
        )

    def clear_form(self):
        self.txt_username.clear()
        self.txt_password.clear()
        self.txt_captcha.clear()
    
    def clear_captcha_input(self):
        """Clear only the CAPTCHA input field"""
        self.txt_captcha.clear()
    
    def set_captcha_image(self, image_path: str):
        """
        Display CAPTCHA image.
        
        Args:
            image_path (str): Path to CAPTCHA image
        """
        logger.debug(f"set_captcha_image called with path: {image_path}")
        
        if os.path.exists(image_path):
            logger.debug(f"File exists: {image_path}")
            pixmap = QPixmap(image_path)
            
            if pixmap.isNull():
                logger.error(f"QPixmap failed to load image: {image_path}")
                self.captcha_image_label.setText("Failed to load CAPTCHA image")
            else:
                logger.debug(f"QPixmap loaded successfully, size: {pixmap.width()}x{pixmap.height()}")
                pixmap = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
                self.captcha_image_label.setPixmap(pixmap)
        else:
            logger.error(f"File does not exist: {image_path}")
            self.captcha_image_label.setText("CAPTCHA image not found")

    def show_error(self, message, title="Error"):
        QMessageBox.critical(self, title, message)

    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_success(self, message):
        QMessageBox.information(self, "Success", message)
    
    def showEvent(self, event):
        """Reset button state when dialog is shown"""
        super().showEvent(event)
        # Ensure login button is enabled when dialog is shown
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Login")
        self.btn_refresh_captcha.setEnabled(True)


