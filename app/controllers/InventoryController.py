from PyQt6.QtWidgets import QMessageBox
from datetime import datetime

class InventoryController:
    def __init__(self, model, view, current_user=None):
        self.model = model
        self.view = view
        self.current_user = current_user  # Current logged-in user

        # Inventory tab signals
        self.view.add_btn.clicked.connect(self.add_item)
        self.view.update_btn.clicked.connect(self.update_item)
        self.view.delete_btn.clicked.connect(self.delete_item)
        self.view.refresh_btn.clicked.connect(self.refresh_inventory)
        self.view.search_btn.clicked.connect(self.search_inventory)
        self.view.search_box.returnPressed.connect(self.search_inventory)

        # Stock In signals
        self.view.stock_in_btn.clicked.connect(self.record_stock_in)
        self.view.stock_in_clear_btn.clicked.connect(self.clear_stock_in_form)

        # Stock Out signals
        self.view.stock_out_btn.clicked.connect(self.record_stock_out)
        self.view.stock_out_clear_btn.clicked.connect(self.clear_stock_out_form)

        # Stock Log signals
        self.view.stock_log_refresh_btn.clicked.connect(self.refresh_stock_log)
        self.view.stock_log_item_filter.currentIndexChanged.connect(self.refresh_stock_log)

        print("[INVENTORY CONTROLLER] InventoryController initialized")
        
        # Load initial data
        self.refresh_inventory()
        self.refresh_stock_log()

    def refresh_inventory(self):
        """Refresh inventory table."""
        print("[INVENTORY CONTROLLER] refresh_inventory() called")
        try:
            items = self.model.fetch_all()
            self.view.load_table(items)
            print(f"[INVENTORY CONTROLLER] Loaded {len(items)} items")
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] refresh_inventory: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to load inventory: {str(e)}")

    def add_item(self):
        """Add a new inventory item."""
        print("[INVENTORY CONTROLLER] add_item() called")
        try:
            data = self.view.get_form_data()
            if not data:
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
            
            self.model.create_item(data)
            self.view.clear_form()
            self.refresh_inventory()
            QMessageBox.information(self.view, "Success", "Item added successfully")
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] add_item: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to add item: {str(e)}")

    def update_item(self):
        """Update selected inventory item."""
        print("[INVENTORY CONTROLLER] update_item() called")
        try:
            data = self.view.get_form_data(with_id=True)
            if not data:
                return
            
            self.model.update_item(data[0], data[1:])
            self.view.clear_form()
            self.refresh_inventory()
            QMessageBox.information(self.view, "Success", "Item updated successfully")
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] update_item: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to update item: {str(e)}")

    def delete_item(self):
        """Delete selected inventory item."""
        print("[INVENTORY CONTROLLER] delete_item() called")
        try:
            item_id = self.view.get_selected_id()
            if not item_id:
                QMessageBox.warning(self.view, "Warning", "Please select an item to delete")
                return
            
            # Confirm deletion
            reply = QMessageBox.question(
                self.view,
                "Confirm Delete",
                "Are you sure you want to delete this item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.delete_item(item_id)
                self.view.clear_form()
                self.refresh_inventory()
                QMessageBox.information(self.view, "Success", "Item deleted successfully")
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] delete_item: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to delete item: {str(e)}")

    def search_inventory(self):
        """Search inventory by keyword."""
        print("[INVENTORY CONTROLLER] search_inventory() called")
        keyword = self.view.search_box.text()
        self.view.search_inventory(keyword)

    def record_stock_in(self):
        """Record stock in (add to inventory)."""
        print("[INVENTORY CONTROLLER] record_stock_in() called")
        try:
            item_id = self.view.stock_in_item_combo.currentData()
            if item_id is None:
                QMessageBox.warning(self.view, "Warning", "Please select an item")
                return
            
            qty = self.view.stock_in_qty.value()
            if qty <= 0:
                QMessageBox.warning(self.view, "Warning", "Quantity must be greater than 0")
                return
            
            reason = self.view.stock_in_reason.currentText()
            notes = self.view.stock_in_notes.toPlainText()
            user_id = self.current_user.get('id') if self.current_user else None
            
            result = self.model.record_stock_movement(
                item_id,
                'IN',
                qty,
                reason,
                notes,
                user_id
            )
            
            if result:
                self.clear_stock_in_form()
                self.refresh_inventory()
                self.refresh_stock_log()
                QMessageBox.information(self.view, "Success", f"Recorded stock in: {qty} units")
            else:
                QMessageBox.critical(self.view, "Error", "Failed to record stock in")
                
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] record_stock_in: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to record stock in: {str(e)}")

    def record_stock_out(self):
        """Record stock out (remove from inventory)."""
        print("[INVENTORY CONTROLLER] record_stock_out() called")
        try:
            item_id = self.view.stock_out_item_combo.currentData()
            if item_id is None:
                QMessageBox.warning(self.view, "Warning", "Please select an item")
                return
            
            qty = self.view.stock_out_qty.value()
            if qty <= 0:
                QMessageBox.warning(self.view, "Warning", "Quantity must be greater than 0")
                return
            
            reason = self.view.stock_out_reason.currentText()
            notes = self.view.stock_out_notes.toPlainText()
            user_id = self.current_user.get('id') if self.current_user else None
            
            result = self.model.record_stock_movement(
                item_id,
                'OUT',
                qty,
                reason,
                notes,
                user_id
            )
            
            if result:
                self.clear_stock_out_form()
                self.refresh_inventory()
                self.refresh_stock_log()
                QMessageBox.information(self.view, "Success", f"Recorded stock out: {qty} units")
            else:
                QMessageBox.critical(self.view, "Error", "Failed to record stock out (insufficient stock?)")
                
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] record_stock_out: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to record stock out: {str(e)}")

    def refresh_stock_log(self):
        """Refresh stock log table."""
        print("[INVENTORY CONTROLLER] refresh_stock_log() called")
        try:
            selected_item_id = self.view.stock_log_item_filter.currentData()
            movements = self.model.get_stock_movements(item_id=selected_item_id, limit=100)
            self.view.load_stock_log_table(movements)
            print(f"[INVENTORY CONTROLLER] Loaded {len(movements)} stock movements")
        except Exception as e:
            print(f"[INVENTORY CONTROLLER ERROR] refresh_stock_log: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to load stock log: {str(e)}")

    def clear_stock_in_form(self):
        """Clear stock in form."""
        self.view.stock_in_qty.setValue(1)
        self.view.stock_in_reason.setCurrentIndex(0)
        self.view.stock_in_notes.clear()

    def clear_stock_out_form(self):
        """Clear stock out form."""
        self.view.stock_out_qty.setValue(1)
        self.view.stock_out_reason.setCurrentIndex(0)
        self.view.stock_out_notes.clear()
