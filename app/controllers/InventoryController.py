from PyQt6.QtWidgets import QMessageBox

class InventoryController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect signals
        view.add_btn.clicked.connect(self.add_item)
        view.update_btn.clicked.connect(self.update_item)
        view.delete_btn.clicked.connect(self.delete_item)
        view.refresh_btn.clicked.connect(self.load_data)
        view.search_btn.clicked.connect(self.search)
        view.search_box.returnPressed.connect(self.search)  # Allow Enter key to trigger search
        
        print("[CONTROLLER] InventoryController initialized")
        print(f"[CONTROLLER] add_btn connected: {view.add_btn.receivers(view.add_btn.clicked)}")
        print(f"[CONTROLLER] update_btn connected: {view.update_btn.receivers(view.update_btn.clicked)}")
        print(f"[CONTROLLER] delete_btn connected: {view.delete_btn.receivers(view.delete_btn.clicked)}")
        print(f"[CONTROLLER] refresh_btn connected: {view.refresh_btn.receivers(view.refresh_btn.clicked)}")
        print(f"[CONTROLLER] search_btn connected: {view.search_btn.receivers(view.search_btn.clicked)}")

        self.load_data()

    def load_data(self):
        """Load all inventory items."""
        try:
            items = self.model.fetch_all()
            self.view.load_table(items)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load data: {str(e)}")

    def add_item(self):
        """Add a new inventory item."""
        print("[CONTROLLER] add_item() called")
        data = self.view.get_form_data()
        if data is None:
            return
        
        # Validate data
        if not data[0]:  # part_name
            QMessageBox.warning(self.view, "Validation", "Part name is required.")
            return
        
        if data[4] < 0:  # quantity
            QMessageBox.warning(self.view, "Validation", "Quantity cannot be negative.")
            return
            
        if data[5] < 0 or data[6] < 0:  # prices
            QMessageBox.warning(self.view, "Validation", "Prices cannot be negative.")
            return
        
        try:
            print(f"Adding item: {data}")  # Debug
            self.model.create_item(data)
            QMessageBox.information(self.view, "Success", "Item added successfully!")
            self.view.clear_form()
            self.load_data()
        except Exception as e:
            print(f"Add error: {e}")  # Debug
            QMessageBox.critical(self.view, "Error", f"Failed to add item:\n{str(e)}")


    def update_item(self):
        """Update an existing inventory item."""
        print("[CONTROLLER] update_item() called")
        data_with_id = self.view.get_form_data(with_id=True)
        if data_with_id is None:
            return
        
        # Extract ID and data
        item_id = data_with_id[0]
        data = data_with_id[1:]
        
        if not data[0]:  # part_name
            QMessageBox.warning(self.view, "Validation", "Part name is required.")
            return
        
        try:
            reply = QMessageBox.question(
                self.view,
                "Confirm Update",
                "Are you sure you want to update this item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.update_item(item_id, data)
                QMessageBox.information(self.view, "Success", "Item updated successfully!")
                self.view.clear_form()
                self.load_data()
        except Exception as e:
            print(f"[CONTROLLER ERROR] update_item: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to update item: {str(e)}")

    def delete_item(self):
        """Delete an inventory item."""
        print("[CONTROLLER] delete_item() called")
        item_id = self.view.get_selected_id()
        if item_id is None:
            QMessageBox.warning(self.view, "No Selection", "Please select an item to delete.")
            return
        
        try:
            reply = QMessageBox.question(
                self.view,
                "Confirm Delete",
                "Are you sure you want to delete this item?\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.delete_item(item_id)
                QMessageBox.information(self.view, "Success", "Item deleted successfully!")
                self.view.clear_form()
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to delete item: {str(e)}")

    def search(self):
        """Search inventory by keyword (part name, category, brand, model)."""
        keyword = self.view.search_box.text()
        print(f"[CONTROLLER] Searching for: '{keyword}'")
        self.view.search_inventory(keyword)