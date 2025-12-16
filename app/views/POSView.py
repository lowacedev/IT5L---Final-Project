from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QLineEdit, QLabel, QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt

class POSView(QWidget):
    def __init__(self):
        super().__init__()
        print("[POS VIEW] Initializing POSView...")
        self.setObjectName("content_area")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Left Panel - Product Search
        left_panel = QFrame()
        left_panel.setObjectName("form_frame")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        # Search Section
        search_label = QLabel("Product Search")
        search_label.setObjectName("section_title")
        left_layout.addWidget(search_label)

        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by part name...")
        self.search_box.returnPressed.connect(lambda: self.search_btn.click())
        
        self.search_btn = QPushButton(" Search")
        self.search_btn.setObjectName("search_button")
        
        search_row.addWidget(self.search_box)
        search_row.addWidget(self.search_btn)
        left_layout.addLayout(search_row)

        # Search Results Table
        results_label = QLabel("Search Results (Double-click to add)")
        results_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        left_layout.addWidget(results_label)

        self.results_table = QTableWidget()
        self.results_table.setObjectName("data_table")
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["ID", "Part Name", "Price", "Stock"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)
        left_layout.addWidget(self.results_table)

        layout.addWidget(left_panel, stretch=3)

        # Right Panel - Cart
        right_panel = QFrame()
        right_panel.setObjectName("form_frame")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # Cart Header
        cart_header = QHBoxLayout()
        cart_label = QLabel("Shopping Cart")
        cart_label.setObjectName("section_title")
        
        self.clear_cart_btn = QPushButton("Clear Cart")
        self.clear_cart_btn.setObjectName("search_button")
        
        cart_header.addWidget(cart_label)
        cart_header.addStretch()
        cart_header.addWidget(self.clear_cart_btn)
        right_layout.addLayout(cart_header)

        # Cart Table (ID removed from view: columns are Name, Qty, Price, Total)
        self.cart_table = QTableWidget()
        self.cart_table.setObjectName("data_table")
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Name", "Qty", "Price", "Total"])
        # Make the Name column stretch and Price/Total sized to contents
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cart_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.cart_table)

        # Quantity Controls
        qty_frame = QFrame()
        qty_layout = QHBoxLayout(qty_frame)
        qty_layout.setContentsMargins(0, 0, 0, 0)
        
        qty_label = QLabel("Selected Item Quantity:")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("1")
        self.qty_input.setFixedWidth(80)
        
        self.update_qty_btn = QPushButton("Update Qty")
        self.update_qty_btn.setObjectName("update_button")
        
        self.remove_item_btn = QPushButton("Remove Item")
        self.remove_item_btn.setObjectName("remove_item_button")
        
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_input)
        qty_layout.addWidget(self.update_qty_btn)
        qty_layout.addWidget(self.remove_item_btn)
        qty_layout.addStretch()
        
        right_layout.addWidget(qty_frame)

        # Total and Checkout
        total_frame = QFrame()
        total_frame.setObjectName("total_frame")
        total_layout = QVBoxLayout(total_frame)
        total_layout.setContentsMargins(15, 15, 15, 15)

        self.subtotal_label = QLabel("Subtotal: Php 0.00")
        self.subtotal_label.setObjectName("total_label")
        self.subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self.subtotal_label)

        self.vat_label = QLabel("VAT (12%): Php 0.00")
        self.vat_label.setObjectName("total_label")
        self.vat_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self.vat_label)

        self.total_label = QLabel("Total: Php 0.00")
        self.total_label.setObjectName("total_label")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_label.setStyleSheet("font-weight: bold; font-size: 26px;")
        total_layout.addWidget(self.total_label)

        self.checkout_btn = QPushButton(" Checkout")
        self.checkout_btn.setObjectName("checkout_button")
        self.checkout_btn.setFixedHeight(50)
        total_layout.addWidget(self.checkout_btn)

        right_layout.addWidget(total_frame)
        layout.addWidget(right_panel, stretch=2)

        self.setLayout(layout)
        print("[POS VIEW] POSView initialization complete")

    def add_result(self, results):
        """Display search results."""
        self.results_table.setRowCount(len(results))
        for r, item in enumerate(results):
            for c, value in enumerate(item):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_table.setItem(r, c, cell)

    def add_to_cart(self, item_id, name, qty, price):
        """Add item to cart table."""
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        
        total = qty * price
        
        # Populate visible columns: Name (0), Qty (1), Price (2), Total (3)
        name_item = QTableWidgetItem(name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.cart_table.setItem(row, 0, name_item)

        qty_item = QTableWidgetItem(str(qty))
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cart_table.setItem(row, 1, qty_item)

        price_item = QTableWidgetItem(f"Php {price:.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.cart_table.setItem(row, 2, price_item)

        total_item = QTableWidgetItem(f"Php {total:.2f}")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.cart_table.setItem(row, 3, total_item)

    def update_cart_row(self, row, qty, price):
        """Update quantity and total for a cart row."""
        total = qty * price
        # Columns: 0=Name, 1=Qty, 2=Price, 3=Total
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(qty)))
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"Php {total:.2f}"))

        for col in [1, 3]:
            item = self.cart_table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def clear_cart(self):
        """Clear all items from cart."""
        self.cart_table.setRowCount(0)
        self.subtotal_label.setText("Subtotal: Php 0.00")
        self.vat_label.setText("VAT (12%): Php 0.00")
        self.total_label.setText("Total: Php 0.00")
        self.qty_input.clear()