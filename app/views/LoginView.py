# app/views/login_view.py
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os


class LoginView(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("TechBayan")
        self.setFixedSize(400, 500)
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
        form_layout.setSpacing(15)
        
        self.lbl_username = QLabel("Username")
        self.lbl_username.setStyleSheet("font-weight: 600; color: #374151;")
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Enter your username")
        self.txt_username.setMinimumHeight(40)
        
        self.lbl_password = QLabel("Password")
        self.lbl_password.setStyleSheet("font-weight: 600; color: #374151;")
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Enter your password")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setMinimumHeight(40)
        
        form_layout.addWidget(self.lbl_username)
        form_layout.addWidget(self.txt_username)
        form_layout.addWidget(self.lbl_password)
        form_layout.addWidget(self.txt_password)
        
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
            self.txt_password.text().strip()
        )

    def clear_form(self):
        self.txt_username.clear()
        self.txt_password.clear()

    def show_error(self, message, title="Error"):
        QMessageBox.critical(self, title, message)

    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_success(self, message):
        QMessageBox.information(self, "Success", message)

