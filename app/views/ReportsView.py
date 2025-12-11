from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QDateEdit, QLabel, QComboBox, QSpinBox, QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import QDate, Qt
from datetime import datetime, timedelta
import csv

class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Sales Report
        self.tab_widget.addTab(self.create_sales_tab(), "Sales Report")
        
        # Tab 2: Top Selling Items
        self.tab_widget.addTab(self.create_top_items_tab(), "Top Selling Items")
        
        # Tab 3: Inventory Status
        self.tab_widget.addTab(self.create_inventory_tab(), "Inventory Status")
        
        # Tab 4: Low Stock Alert
        self.tab_widget.addTab(self.create_low_stock_tab(), "Low Stock Alert")
        
        # Tab 5: Supplier Performance
        self.tab_widget.addTab(self.create_supplier_tab(), "Supplier Performance")
        
        # Tab 6: Category Performance
        self.tab_widget.addTab(self.create_category_tab(), "Category Performance")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def create_sales_tab(self):
        """Create sales report tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Date range selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.sales_start_date = QDateEdit()
        self.sales_start_date.setDate(QDate.currentDate().addDays(-30))
        self.sales_start_date.setCalendarPopup(True)
        date_layout.addWidget(self.sales_start_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.sales_end_date = QDateEdit()
        self.sales_end_date.setDate(QDate.currentDate())
        self.sales_end_date.setCalendarPopup(True)
        date_layout.addWidget(self.sales_end_date)
        
        self.sales_refresh_btn = QPushButton("Refresh")
        self.sales_refresh_btn.setObjectName("search_button")
        date_layout.addWidget(self.sales_refresh_btn)
        
        self.sales_export_btn = QPushButton("Export to CSV")
        self.sales_export_btn.setObjectName("secondary_button")
        date_layout.addWidget(self.sales_export_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Sales by date table
        layout.addWidget(QLabel("Sales Summary by Date:"))
        self.sales_by_date_table = QTableWidget()
        self.sales_by_date_table.setColumnCount(4)
        self.sales_by_date_table.setHorizontalHeaderLabels(
            ["Date", "Transactions", "Total Revenue", "Avg Transaction"]
        )
        self.sales_by_date_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sales_by_date_table)
        
        # Detailed transactions table
        layout.addWidget(QLabel("Detailed Transactions:"))
        self.sales_detail_table = QTableWidget()
        self.sales_detail_table.setColumnCount(6)
        self.sales_detail_table.setHorizontalHeaderLabels(
            ["Transaction ID", "Date", "Time", "Total", "Items Count", "Cashier"]
        )
        self.sales_detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sales_detail_table)
        
        widget.setLayout(layout)
        return widget

    def create_top_items_tab(self):
        """Create top selling items tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Show top:"))
        self.top_items_limit = QSpinBox()
        self.top_items_limit.setValue(10)
        self.top_items_limit.setMinimum(1)
        self.top_items_limit.setMaximum(100)
        control_layout.addWidget(self.top_items_limit)
        
        self.top_items_refresh_btn = QPushButton("Refresh")
        self.top_items_refresh_btn.setObjectName("search_button")
        control_layout.addWidget(self.top_items_refresh_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Top items table
        self.top_items_table = QTableWidget()
        self.top_items_table.setColumnCount(6)
        self.top_items_table.setHorizontalHeaderLabels(
            ["Item ID", "Part Name", "Category", "Quantity Sold", "Total Revenue", "Avg Price"]
        )
        self.top_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.top_items_table)
        
        widget.setLayout(layout)
        return widget

    def create_inventory_tab(self):
        """Create inventory status tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        control_layout = QHBoxLayout()
        self.inventory_refresh_btn = QPushButton("Refresh")
        self.inventory_refresh_btn.setObjectName("search_button")
        control_layout.addWidget(self.inventory_refresh_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(9)
        self.inventory_table.setHorizontalHeaderLabels(
            ["ID", "Part Name", "Category", "Quantity", "Cost Price", "Selling Price", 
             "Total Cost Value", "Total Selling Value", "Potential Profit"]
        )
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.inventory_table)
        
        widget.setLayout(layout)
        return widget

    def create_low_stock_tab(self):
        """Create low stock alert tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Stock threshold:"))
        self.low_stock_threshold = QSpinBox()
        self.low_stock_threshold.setValue(5)
        self.low_stock_threshold.setMinimum(1)
        self.low_stock_threshold.setMaximum(100)
        control_layout.addWidget(self.low_stock_threshold)
        
        self.low_stock_refresh_btn = QPushButton("Refresh")
        self.low_stock_refresh_btn.setObjectName("search_button")
        control_layout.addWidget(self.low_stock_refresh_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Low stock table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels(
            ["ID", "Part Name", "Category", "Current Stock", "Supplier ID"]
        )
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.low_stock_table)
        
        widget.setLayout(layout)
        return widget

    def create_supplier_tab(self):
        """Create supplier performance tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        control_layout = QHBoxLayout()
        self.supplier_refresh_btn = QPushButton("Refresh")
        self.supplier_refresh_btn.setObjectName("search_button")
        control_layout.addWidget(self.supplier_refresh_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Supplier table
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(5)
        self.supplier_table.setHorizontalHeaderLabels(
            ["Supplier ID", "Supplier Name", "Number of Sales", "Total Items Sold", "Total Revenue"]
        )
        self.supplier_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.supplier_table)
        
        widget.setLayout(layout)
        return widget

    def create_category_tab(self):
        """Create category performance tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        control_layout = QHBoxLayout()
        self.category_refresh_btn = QPushButton("Refresh")
        self.category_refresh_btn.setObjectName("search_button")
        control_layout.addWidget(self.category_refresh_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Category table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(5)
        self.category_table.setHorizontalHeaderLabels(
            ["Category", "Number of Sales", "Total Quantity", "Total Revenue", "Avg Price"]
        )
        self.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.category_table)
        
        widget.setLayout(layout)
        return widget

    def populate_sales_by_date_table(self, data):
        """Populate sales by date table."""
        self.sales_by_date_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.sales_by_date_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.sales_by_date_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.sales_by_date_table.setItem(row, 2, QTableWidgetItem(f"Php {item[2]:,.2f}" if item[2] else "Php 0.00"))
            self.sales_by_date_table.setItem(row, 3, QTableWidgetItem(f"Php {item[3]:,.2f}" if item[3] else "Php 0.00"))

    def populate_sales_detail_table(self, data):
        """Populate detailed transactions table."""
        self.sales_detail_table.setRowCount(len(data))
        for row, item in enumerate(data):
            # item indices: 0=id,1=date,2=time,3=total,4=items_count,5=cashier
            self.sales_detail_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.sales_detail_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.sales_detail_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
            self.sales_detail_table.setItem(row, 3, QTableWidgetItem(f"Php {item[3]:,.2f}"))
            self.sales_detail_table.setItem(row, 4, QTableWidgetItem(str(item[4])))
            self.sales_detail_table.setItem(row, 5, QTableWidgetItem(str(item[5]) if item[5] else "Unknown"))

    def populate_top_items_table(self, data):
        """Populate top items table."""
        self.top_items_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.top_items_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.top_items_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.top_items_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
            self.top_items_table.setItem(row, 3, QTableWidgetItem(str(item[3])))
            self.top_items_table.setItem(row, 4, QTableWidgetItem(f"Php {item[4]:,.2f}" if item[4] else "Php 0.00"))
            self.top_items_table.setItem(row, 5, QTableWidgetItem(f"Php {item[5]:,.2f}" if item[5] else "Php 0.00"))

    def populate_inventory_table(self, data):
        """Populate inventory table."""
        self.inventory_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item[3])))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(f"Php {item[4]:,.2f}"))
            self.inventory_table.setItem(row, 5, QTableWidgetItem(f"Php {item[5]:,.2f}"))
            self.inventory_table.setItem(row, 6, QTableWidgetItem(f"Php {item[6]:,.2f}"))
            self.inventory_table.setItem(row, 7, QTableWidgetItem(f"Php {item[7]:,.2f}"))
            self.inventory_table.setItem(row, 8, QTableWidgetItem(f"Php {item[8]:,.2f}"))

    def populate_low_stock_table(self, data):
        """Populate low stock table."""
        self.low_stock_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(str(item[3])))
            self.low_stock_table.setItem(row, 4, QTableWidgetItem(str(item[4])))

    def populate_supplier_table(self, data):
        """Populate supplier table."""
        self.supplier_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.supplier_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.supplier_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.supplier_table.setItem(row, 2, QTableWidgetItem(str(item[2]) if item[2] else "0"))
            self.supplier_table.setItem(row, 3, QTableWidgetItem(str(item[3]) if item[3] else "0"))
            self.supplier_table.setItem(row, 4, QTableWidgetItem(f"Php {item[4]:,.2f}" if item[4] else "Php 0.00"))

    def populate_category_table(self, data):
        """Populate category table."""
        self.category_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.category_table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.category_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.category_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
            self.category_table.setItem(row, 3, QTableWidgetItem(f"Php {item[3]:,.2f}" if item[3] else "Php 0.00"))
            self.category_table.setItem(row, 4, QTableWidgetItem(f"Php {item[4]:,.2f}" if item[4] else "Php 0.00"))

    def export_to_csv(self, data, filename):
        """Export data to CSV file."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                headers = ["Transaction ID", "Sale Date", "Part Name", "Quantity", "Unit Price", "Line Total"]
                writer.writerow(headers)
                # Write data
                for row in data:
                    writer.writerow(row)
            QMessageBox.information(None, "Success", f"Report exported to {filename}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to export: {str(e)}")
