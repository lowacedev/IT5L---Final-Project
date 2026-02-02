from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QLineEdit, QLabel, QTableWidgetItem, QHeaderView,
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from app.views.BaseView import BaseView

class SupplierView(BaseView):
    def __init__(self):
        super().__init__()
        self.setObjectName("content_area")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel("Supplier Management")
        header.setObjectName("page_title")
        layout.addWidget(header)

        # Form Section
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        form_title = QLabel("Supplier Details")
        form_title.setObjectName("section_title")
        form_layout.addWidget(form_title)

        # Form fields in 2-column grid
        form_grid = QGridLayout()
        form_grid.setSpacing(12)
        form_grid.setColumnStretch(1, 1)
        form_grid.setColumnStretch(3, 1)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("Supplier name")
        
        self.contact_person = QLineEdit()
        self.contact_person.setPlaceholderText("Contact person name")
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email address")
        
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone number")
        
        self.address = QLineEdit()
        self.address.setPlaceholderText("Street address")
        
        # Row 1: Name | Contact Person
        form_grid.addWidget(QLabel("Supplier Name*:"), 0, 0)
        form_grid.addWidget(self.name, 0, 1)
        form_grid.addWidget(QLabel("Contact Person:"), 0, 2)
        form_grid.addWidget(self.contact_person, 0, 3)
        
        # Row 2: Email | Phone
        form_grid.addWidget(QLabel("Email:"), 1, 0)
        form_grid.addWidget(self.email, 1, 1)
        form_grid.addWidget(QLabel("Phone:"), 1, 2)
        form_grid.addWidget(self.phone, 1, 3)
        
        # Row 3: Address
        form_grid.addWidget(QLabel("Address:"), 2, 0)
        form_grid.addWidget(self.address, 2, 1)

        form_layout.addLayout(form_grid)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.add_btn = QPushButton("+ Add Supplier")
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
        table_title = QLabel("Suppliers List")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Contact", "Email", "Phone", "Address"])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
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
        
        supplier_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        contact = self.table.item(row, 2).text()
        email = self.table.item(row, 3).text()
        phone = self.table.item(row, 4).text()
        address = self.table.item(row, 5).text()
        
        self.name.setText(name)
        self.contact_person.setText(contact)
        self.email.setText(email)
        self.phone.setText(phone)
        self.address.setText(address)

    def load_table(self, items):
        self.table.setRowCount(len(items))
        
        for r, item in enumerate(items):
            values = [item.id, item.name, item.contact_person, item.email, item.phone, item.address]
            for c, value in enumerate(values):
                cell = QTableWidgetItem(str(value) if value else "")
          
                if c in [0, 1]:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(r, c, cell)

    def collect_form_data(self, with_id=False):
        name = self.name.text().strip()
        contact_person = self.contact_person.text().strip()
        email = self.email.text().strip()
        phone = self.phone.text().strip()
        address = self.address.text().strip()
        
        if with_id:
            selected_row = self.table.currentRow()
            if selected_row < 0:
                return None
            supplier_id = int(self.table.item(selected_row, 0).text())
            return (supplier_id, name, contact_person, email, phone, address)
        
        return (name, contact_person, email, phone, address)

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def clear_form(self):
        self.name.clear()
        self.contact_person.clear()
        self.email.clear()
        self.phone.clear()
        self.address.clear()
