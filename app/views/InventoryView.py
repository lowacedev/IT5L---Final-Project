from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QLineEdit, QLabel, QFormLayout, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt

class InventoryView(QWidget):
    def __init__(self, supplier_model=None):
        super().__init__()
        print("[VIEW] Initializing InventoryView...")
        self.setObjectName("content_area")
        self.supplier_model = supplier_model
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel("Inventory Management")
        header.setObjectName("page_title")
        layout.addWidget(header)

        # Form Section
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        form_title = QLabel("Item Details")
        form_title.setObjectName("section_title")
        form_layout.addWidget(form_title)

        # Form fields in 2-column grid
        form_grid = QGridLayout()
        form_grid.setSpacing(12)
        form_grid.setColumnStretch(1, 1)
        form_grid.setColumnStretch(3, 1)
        
        self.part_name = QLineEdit()
        self.part_name.setPlaceholderText("Enter part name")
        
        self.category = QLineEdit()
        self.category.setPlaceholderText("e.g., Motherboard, RAM, CPU")
        
        self.brand = QLineEdit()
        self.brand.setPlaceholderText("Brand name")
        
        self.model_number = QLineEdit()
        self.model_number.setPlaceholderText("Model number")
        
        self.quantity = QLineEdit()
        self.quantity.setPlaceholderText("0")
        
        self.cost_price = QLineEdit()
        self.cost_price.setPlaceholderText("0.00")
        
        self.selling_price = QLineEdit()
        self.selling_price.setPlaceholderText("0.00")
        
        # Replace supplier_id input with dropdown
        self.supplier_dropdown = QComboBox()
        self.supplier_dropdown.setPlaceholderText("Select a supplier")
        self.load_suppliers()

        # Row 1: Part Name | Category
        form_grid.addWidget(QLabel("Part Name*:"), 0, 0)
        form_grid.addWidget(self.part_name, 0, 1)
        form_grid.addWidget(QLabel("Category:"), 0, 2)
        form_grid.addWidget(self.category, 0, 3)
        
        # Row 2: Brand | Model Number
        form_grid.addWidget(QLabel("Brand:"), 1, 0)
        form_grid.addWidget(self.brand, 1, 1)
        form_grid.addWidget(QLabel("Model Number:"), 1, 2)
        form_grid.addWidget(self.model_number, 1, 3)
        
        # Row 3: Quantity | Cost Price
        form_grid.addWidget(QLabel("Quantity*:"), 2, 0)
        form_grid.addWidget(self.quantity, 2, 1)
        form_grid.addWidget(QLabel("Cost Price*:"), 2, 2)
        form_grid.addWidget(self.cost_price, 2, 3)
        
        # Row 4: Selling Price | Supplier
        form_grid.addWidget(QLabel("Selling Price*:"), 3, 0)
        form_grid.addWidget(self.selling_price, 3, 1)
        form_grid.addWidget(QLabel("Supplier*:"), 3, 2)
        form_grid.addWidget(self.supplier_dropdown, 3, 3)

        form_layout.addLayout(form_grid)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        print("[VIEW] Creating buttons...")
        
        self.add_btn = QPushButton("+ Add Item")
        self.add_btn.setObjectName("primary_button")
        print(f"[VIEW] add_btn created: {self.add_btn}")
        
        self.update_btn = QPushButton("Update")
        self.update_btn.setObjectName("update_button")
        print(f"[VIEW] update_btn created: {self.update_btn}")
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("danger_button")
        print(f"[VIEW] delete_btn created: {self.delete_btn}")
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("secondary_button")
        print(f"[VIEW] clear_btn created: {self.clear_btn}")
        
        # Connect clear button HERE in the view
        print("[VIEW] Connecting clear_btn.clicked signal...")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        print("[VIEW] clear_btn connected to _on_clear_clicked")

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.update_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()

        form_layout.addLayout(btn_row)
        layout.addWidget(form_frame)

        # Table Section
        table_header = QHBoxLayout()
        table_title = QLabel("Current Inventory")
        table_title.setObjectName("section_title")
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("search_button")
        print(f"[VIEW] refresh_btn created: {self.refresh_btn}")
        
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_header.addWidget(self.refresh_btn)
        
        layout.addLayout(table_header)

        # Search Section for Table
        search_row = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by part name, category, brand...")
        
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.setObjectName("search_button")
        
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_box)
        search_row.addWidget(self.search_btn)
        search_row.addStretch()
        
        layout.addLayout(search_row)

        # Table
        self.table = QTableWidget()
        self.table.setObjectName("data_table")
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Part Name", "Category", "Brand", "Model",
            "Qty", "Cost", "Price", "Supplier"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.on_row_selected)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        print("[VIEW] InventoryView initialization complete")

    def _on_clear_clicked(self):
        """Internal handler for clear button"""
        print("[VIEW] Clear button clicked!")
        self.clear_form()

    def load_suppliers(self):
        """Load suppliers into the dropdown."""
        if not self.supplier_model:
            print("[VIEW] No supplier model provided")
            return
        
        try:
            suppliers = self.supplier_model.fetch_all()
            self.supplier_dropdown.clear()
            self.supplier_dropdown.addItem("", None)  # Empty item for "select supplier"

            # SupplierModel.fetch_all may return full rows (id, name, ...).
            # Safely extract id and name from each row.
            for row in suppliers:
                if not row:
                    continue
                supplier_id = row[0]
                supplier_name = row[1] if len(row) > 1 else str(supplier_id)
                self.supplier_dropdown.addItem(supplier_name, supplier_id)

            if len(suppliers) == 0:
                self.supplier_dropdown.addItem("No suppliers available", None)
            print(f"[VIEW] Loaded {len(suppliers)} suppliers into dropdown")
        except Exception as e:
            print(f"[VIEW ERROR] load_suppliers: {e}")

    def load_table(self, items):
        """Load items into the table."""
        print(f"[VIEW] Loading {len(items)} items into table")
        self.table.setRowCount(len(items))
        
        for r, item in enumerate(items):
            for c, value in enumerate(item):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, cell)
        
        print(f"[VIEW] Table now has {self.table.rowCount()} rows")

    def on_row_selected(self):
        """When a row is selected, populate the form."""
        row = self.table.currentRow()
        if row >= 0:
            print(f"[VIEW] Row {row} selected")
            try:
                # Get values from table cells
                part_name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                category = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
                brand = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
                model_number = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
                quantity = self.table.item(row, 5).text() if self.table.item(row, 5) else "0"
                cost_price = self.table.item(row, 6).text() if self.table.item(row, 6) else "0.00"
                selling_price = self.table.item(row, 7).text() if self.table.item(row, 7) else "0.00"
                supplier_id_text = self.table.item(row, 8).text() if self.table.item(row, 8) else "1"
                
                # Set form fields
                self.part_name.setText(part_name)
                self.category.setText(category)
                self.brand.setText(brand)
                self.model_number.setText(model_number)
                self.quantity.setText(quantity)
                self.cost_price.setText(cost_price)
                self.selling_price.setText(selling_price)
                
                # Set supplier dropdown by ID
                try:
                    supplier_id = int(supplier_id_text)
                    index = self.supplier_dropdown.findData(supplier_id)
                    if index >= 0:
                        self.supplier_dropdown.setCurrentIndex(index)
                except:
                    self.supplier_dropdown.setCurrentIndex(0)
                
                print(f"[VIEW] Form populated with item: {part_name}")
                
            except Exception as e:
                print(f"[VIEW ERROR] on_row_selected: {e}")

    def get_selected_id(self):
        """Get the ID of the selected row."""
        row = self.table.currentRow()
        if row >= 0 and self.table.item(row, 0):
            item_id = int(self.table.item(row, 0).text())
            print(f"[VIEW] Selected ID: {item_id}")
            return item_id
        print("[VIEW] No row selected")
        return None

    def get_form_data(self, with_id=False):
        """Get data from form fields.
        Returns tuple: (part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id)
        If with_id=True, returns (id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id)
        """
        try:
            print("[VIEW] Getting form data...")
            
            # Get text values
            part_name = self.part_name.text().strip()
            category = self.category.text().strip() or "Uncategorized"
            brand = self.brand.text().strip() or "Generic"
            model_number = self.model_number.text().strip() or "N/A"
            
            # Get numeric values
            quantity_text = self.quantity.text().strip()
            if not quantity_text:
                raise ValueError("Quantity is required")
            quantity = int(quantity_text)
            
            cost_text = self.cost_price.text().strip()
            if not cost_text:
                raise ValueError("Cost price is required")
            cost_price = float(cost_text)
            
            selling_text = self.selling_price.text().strip()
            if not selling_text:
                raise ValueError("Selling price is required")
            selling_price = float(selling_text)
            
            # Get supplier ID from dropdown
            supplier_id = self.supplier_dropdown.currentData()
            if supplier_id is None:
                raise ValueError("Please select a supplier")
            
            data = (
                part_name,
                category,
                brand,
                model_number,
                quantity,
                cost_price,
                selling_price,
                supplier_id
            )
            
            if with_id:
                item_id = self.get_selected_id()
                if item_id is None:
                    raise ValueError("No item selected for update")
                data = (item_id,) + data
            
            print(f"[VIEW] Form data collected: {data}")
            return data
            
        except ValueError as e:
            print(f"[VIEW ERROR] Invalid input: {e}")
            QMessageBox.warning(self, "Invalid Input", f"Please check your inputs:\n{str(e)}")
            return None
        except Exception as e:
            print(f"[VIEW ERROR] get_form_data: {e}")
            QMessageBox.critical(self, "Error", f"Error reading form data:\n{str(e)}")
            return None

    def clear_form(self):
        """Clear all form fields."""
        print("[VIEW] Clearing form")
        self.part_name.clear()
        self.category.clear()
        self.brand.clear()
        self.model_number.clear()
        self.quantity.clear()
        self.cost_price.clear()
        self.selling_price.clear()

    def search_inventory(self, keyword):
        """Filter inventory table by keyword (part name, category, brand)."""
        if not keyword.strip():
            # Show all rows if search is empty
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return
        
        keyword_lower = keyword.lower()
        for row in range(self.table.rowCount()):
            # Check columns: Part Name (1), Category (2), Brand (3), Model (4)
            part_name = self.table.item(row, 1).text().lower() if self.table.item(row, 1) else ""
            category = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""
            brand = self.table.item(row, 3).text().lower() if self.table.item(row, 3) else ""
            model = self.table.item(row, 4).text().lower() if self.table.item(row, 4) else ""
            
            # Show row if keyword matches any of these fields
            match = keyword_lower in part_name or keyword_lower in category or keyword_lower in brand or keyword_lower in model
            self.table.setRowHidden(row, not match)
        self.supplier_dropdown.setCurrentIndex(0)  # Reset to first empty item
        self.table.clearSelection()