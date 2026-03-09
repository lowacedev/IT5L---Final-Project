from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QLineEdit, QLabel, QTableWidgetItem, QHeaderView,
    QFrame, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt
from app.views.BaseView import BaseView

class StaffView(BaseView):
    def __init__(self):
        super().__init__()
        self.setObjectName("content_area")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel("Staff Management")
        header.setObjectName("page_title")
        layout.addWidget(header)

        # Form Section
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        form_title = QLabel("Staff Details")
        form_title.setObjectName("section_title")
        form_layout.addWidget(form_title)

        # Form fields in 2-column grid
        form_grid = QGridLayout()
        form_grid.setSpacing(12)
        form_grid.setColumnStretch(1, 1)
        form_grid.setColumnStretch(3, 1)
        
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Enter full name")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password (leave empty to keep current)")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["cashier", "admin"])

        # Row 0: Full Name (label + field) | Role (label + dropdown)
        form_grid.addWidget(QLabel("Full Name:"), 0, 0)
        form_grid.addWidget(self.full_name, 0, 1)
        form_grid.addWidget(QLabel("Role*:"), 0, 2)
        form_grid.addWidget(self.role_dropdown, 0, 3)

        # Row 1: Username
        form_grid.addWidget(QLabel("Username*:"), 1, 0)
        form_grid.addWidget(self.username, 1, 1)

        # Row 2: Password
        form_grid.addWidget(QLabel("Password*:"), 2, 0)
        form_grid.addWidget(self.password, 2, 1)

        form_layout.addLayout(form_grid)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.add_btn = QPushButton("+ Add Staff")
        self.add_btn.setObjectName("primary_button")
        
        self.update_btn = QPushButton("Update")
        self.update_btn.setObjectName("update_button")
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("danger_button")
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("secondary_button")

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.update_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()

        form_layout.addLayout(btn_row)
        layout.addWidget(form_frame)

        # Table Section
        table_header = QHBoxLayout()
        table_title = QLabel("Staff List")
        table_title.setObjectName("section_title")
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("search_button")
        
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_header.addWidget(self.refresh_btn)
        
        layout.addLayout(table_header)

        # Table
        self.table = QTableWidget()
        self.table.setObjectName("data_table")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Full Name", "Username", "Role", "Created"])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.on_row_selected)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

    def on_row_selected(self, index):
        row = self.table.currentRow()
        if row < 0:
            return
        
       
        full_name = self.table.item(row, 1).text() if self.table.item(row,1) else ""
        username = self.table.item(row, 2).text()
        role = self.table.item(row, 3).text()
        
        self.full_name.setText(full_name)
        self.username.setText(username)
        self.role_dropdown.setCurrentText(role)
        self.password.clear()

    def load_table(self, items):
        self.table.setRowCount(len(items))
        
        for r, item in enumerate(items):
            values = [item.id, item.full_name, item.username, item.role, item.created_at]
            for c, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, cell)

    def collect_form_data(self, with_id=False):
        full_name = self.full_name.text().strip()
        username = self.username.text().strip()
        password = self.password.text().strip()
        role = self.role_dropdown.currentText()
        
        if with_id:
            selected_row = self.table.currentRow()
            if selected_row < 0:
                return None
            staff_id = int(self.table.item(selected_row, 0).text())
            return (staff_id, full_name, username, password, role)
        
        return (full_name, username, password, role)

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def clear_form(self):
        self.full_name.clear()
        self.username.clear()
        self.password.clear()
        self.role_dropdown.setCurrentIndex(0)
