from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QDateEdit, QLabel, QComboBox, QSpinBox, QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import QDate, Qt
from datetime import datetime, timedelta
import csv
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table as RLTable,
    TableStyle,
    Paragraph,
    Spacer,
    Image as RLImage,
    PageBreak,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
try:
    import openpyxl
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Alignment
    from openpyxl.styles.numbers import FORMAT_NUMBER_00
    OPENPYXL_AVAILABLE = True
except Exception:
    OPENPYXL_AVAILABLE = False

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
        # wire export button signals
        self.connect_export_buttons()

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
        self.sales_export_pdf_btn = QPushButton("Export to PDF")
        self.sales_export_pdf_btn.setObjectName("secondary_button")
        date_layout.addWidget(self.sales_export_pdf_btn)
        
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
        self.top_items_export_btn = QPushButton("Export to PDF")
        self.top_items_export_btn.setObjectName("secondary_button")
        control_layout.addWidget(self.top_items_export_btn)
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
        self.inventory_export_btn = QPushButton("Export to PDF")
        self.inventory_export_btn.setObjectName("secondary_button")
        control_layout.addWidget(self.inventory_export_btn)
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

    def _export_table_widget_to_pdf(self, table_widget, filename, title=None):
        try:
            styles = getSampleStyleSheet()

            # Prepare document
            doc = SimpleDocTemplate(
                filename,
                pagesize=landscape(letter),
                rightMargin=36,
                leftMargin=36,
                topMargin=72,
                bottomMargin=36,
            )

            elements = []

            # Optional title block
            if title:
                elements.append(Paragraph(title, styles['Heading2']))
                elements.append(Spacer(1, 6))

            # Build data rows
            headers = [
                table_widget.horizontalHeaderItem(c).text()
                if table_widget.horizontalHeaderItem(c)
                else ""
                for c in range(table_widget.columnCount())
            ]

            data = [headers]

            # Track max text width per column (approx chars)
            col_max_chars = [len(h) for h in headers]

            for r in range(table_widget.rowCount()):
                row = []
                for c in range(table_widget.columnCount()):
                    item = table_widget.item(r, c)
                    text = item.text() if item else ""
                    row.append(text)
                    if len(text) > col_max_chars[c]:
                        col_max_chars[c] = len(text)
                data.append(row)

            # Estimate column widths based on character counts and available page width
            page_width = landscape(letter)[0] - doc.leftMargin - doc.rightMargin
            # assign relative weights clipped
            total_chars = sum(max(1, v) for v in col_max_chars)
            col_widths = [max(50, (v / total_chars) * page_width) for v in col_max_chars]

            # Create table with repeatRows for header and allow splitting across pages
            rl_table = RLTable(data, colWidths=col_widths, repeatRows=1)

            # Table styling: header row, alternate backgrounds, padding, alignment
            tbl_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f7fa')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0b2e4a')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#c8d0d8')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
            ])

            # Alternate row background
            for i in range(1, len(data)):
                if i % 2 == 0:
                    tbl_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fcfdff'))

            # Right-align numeric-looking columns (heuristic)
            for col_idx in range(len(headers)):
                # check a few rows to decide if numeric
                numeric_count = 0
                for r in range(1, min(10, len(data))):
                    try:
                        float(str(data[r][col_idx]).replace('Php', '').replace(',', '').strip())
                        numeric_count += 1
                    except Exception:
                        pass
                if numeric_count >= max(1, (len(data) - 1) // 2):
                    tbl_style.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')

            rl_table.setStyle(tbl_style)

            elements.append(rl_table)

            # Header/footer drawing functions
            logo_path = None
            try:
                # try to use embedded logo if available
                import os
                logo_candidate = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'techbayanlogo.jpg')
                logo_candidate = os.path.normpath(logo_candidate)
                if os.path.exists(logo_candidate):
                    logo_path = logo_candidate
            except Exception:
                logo_path = None

            def _header(canvas, doc_obj):
                canvas.saveState()
                width, height = doc_obj.pagesize
                # Draw logo at left
                if logo_path:
                    try:
                        img_w = 1.0 * inch
                        img_h = 0.35 * inch
                        canvas.drawImage(logo_path, doc_obj.leftMargin, height - 50, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
                    except Exception:
                        pass
                # Title centered
                canvas.setFont('Helvetica-Bold', 12)
                canvas.drawCentredString(width / 2.0, height - 36, title if title else '')
                # Date at right
                canvas.setFont('Helvetica', 8)
                canvas.drawRightString(width - doc_obj.rightMargin, height - 34, datetime.now().strftime('%Y-%m-%d %H:%M'))
                canvas.restoreState()

            def _footer(canvas, doc_obj):
                canvas.saveState()
                width, height = doc_obj.pagesize
                canvas.setFont('Helvetica', 8)
                footer_text = f"Generated by POS System"
                canvas.drawString(doc_obj.leftMargin, doc_obj.bottomMargin - 18, footer_text)
                # page number
                page_num = canvas.getPageNumber()
                canvas.drawRightString(width - doc_obj.rightMargin, doc_obj.bottomMargin - 18, f"Page {page_num}")
                canvas.restoreState()

            # Build document with header/footer callbacks
            doc.build(elements, onFirstPage=lambda c, d: (_header(c, d), _footer(c, d)), onLaterPages=lambda c, d: (_header(c, d), _footer(c, d)))
            QMessageBox.information(self, "Success", f"Exported PDF to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")

    def connect_export_buttons(self):
        # Connect export buttons to the handlers (call after controller sets up view)
        try:
            self.sales_export_pdf_btn.clicked.connect(self._handle_export_sales_pdf)
        except Exception:
            pass
        try:
            self.top_items_export_btn.clicked.connect(self._handle_export_top_items_pdf)
        except Exception:
            pass
        try:
            self.inventory_export_btn.clicked.connect(self._handle_export_inventory_pdf)
        except Exception:
            pass

    def _choose_save_file(self, suggested_name):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", suggested_name, "PDF Files (*.pdf)")
        return path

    def _handle_export_sales_pdf(self):
        filename = self._choose_save_file("sales_report.pdf")
        if not filename:
            return
        # Merge both tables into a single PDF by exporting the detailed transactions table
        title = "Sales Detailed Transactions"
        self._export_table_widget_to_pdf(self.sales_detail_table, filename, title=title)

    def _handle_export_top_items_pdf(self):
        filename = self._choose_save_file("top_items_report.pdf")
        if not filename:
            return
        title = "Top Selling Items"
        self._export_table_widget_to_pdf(self.top_items_table, filename, title=title)

    def _handle_export_inventory_pdf(self):
        filename = self._choose_save_file("inventory_report.pdf")
        if not filename:
            return
        title = "Inventory Status"
        self._export_table_widget_to_pdf(self.inventory_table, filename, title=title)

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

    def export_to_xlsx(self, data, filename):
        """Export data to XLSX (Excel) with proper types and column widths."""
        if not OPENPYXL_AVAILABLE:
            QMessageBox.critical(self, "Dependency Missing", "openpyxl is not installed. Please install openpyxl and try again.")
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sales Report"

            headers = ["Transaction ID", "Sale Date", "Transaction Total", "Cashier", "Part Name", "Quantity", "Unit Price", "Line Total"]
            ws.append(headers)

     
            col_widths = [len(h) for h in headers]

            for record in data:
           
                tx_id = record[0]
                sale_dt = record[1]
                tx_total = record[2]
                cashier = record[3]
                part_name = record[4]
                qty = record[5]
                unit_price = record[6]
                line_total = record[7]

                # Try to coerce sale_dt to a datetime if it's a string
                if isinstance(sale_dt, str):
                    try:
                        # Try common formats
                        sale_dt_val = datetime.fromisoformat(sale_dt)
                    except Exception:
                        try:
                            sale_dt_val = datetime.strptime(sale_dt, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            sale_dt_val = sale_dt
                else:
                    sale_dt_val = sale_dt

                row = [tx_id, sale_dt_val, tx_total, cashier, part_name, qty, unit_price, line_total]
                ws.append(row)

                # update widths
                for i, value in enumerate(row):
                    text = str(value) if value is not None else ""
                    if len(text) > col_widths[i]:
                        col_widths[i] = len(text)

            # Apply formatting for numeric columns and date column
            for row in ws.iter_rows(min_row=2, min_col=1, max_col=ws.max_column):
                # Sale Date is column 2
                cell_date = row[1]
                try:
                    if isinstance(cell_date.value, datetime):
                        cell_date.number_format = 'yyyy-mm-dd hh:mm:ss'
                except Exception:
                    pass

            # Apply number format for currency/number columns: Transaction Total (3), Unit Price (7), Line Total (8) using 1-based index
            for r in ws.iter_rows(min_row=2, min_col=1, max_col=ws.max_column):
                try:
                    # transaction total at index 3 (0-based 2)
                    if isinstance(r[2].value, (int, float)):
                        r[2].number_format = FORMAT_NUMBER_00
                    # quantity at index 5
                    if isinstance(r[5].value, (int, float)):
                        r[5].number_format = FORMAT_NUMBER_00
                    # unit price index 6
                    if isinstance(r[6].value, (int, float)):
                        r[6].number_format = FORMAT_NUMBER_00
                    # line total index 7
                    if isinstance(r[7].value, (int, float)):
                        r[7].number_format = FORMAT_NUMBER_00
                except Exception:
                    pass

            # Set column widths
            for i, width in enumerate(col_widths, start=1):
                col_letter = get_column_letter(i)
                # Set a minimum width and add some padding
                ws.column_dimensions[col_letter].width = max(10, width + 2)

            # Align headers center
            for cell in ws[1]:
                cell.alignment = Alignment(horizontal='center')

            wb.save(filename)
            QMessageBox.information(self, "Success", f"Report exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export XLSX: {str(e)}")
