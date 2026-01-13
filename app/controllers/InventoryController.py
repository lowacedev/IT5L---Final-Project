from PyQt6.QtWidgets import QMessageBox
from datetime import datetime
import re

class InventoryController:
    def __init__(self, model, view, current_user=None):
        self.model = model
        self.view = view
        self.current_user = current_user  

        
        self.view.add_btn.clicked.connect(self.add_item)
        self.view.update_btn.clicked.connect(self.update_item)
        self.view.refresh_btn.clicked.connect(self.refresh_inventory)
        self.view.search_btn.clicked.connect(self.search_inventory)
        self.view.search_box.returnPressed.connect(self.search_inventory)

       
        self.view.stock_in_btn.clicked.connect(self.record_stock_in)
        self.view.stock_in_clear_btn.clicked.connect(self.clear_stock_in_form)

        
        self.view.stock_out_btn.clicked.connect(self.record_stock_out)
        self.view.stock_out_clear_btn.clicked.connect(self.clear_stock_out_form)

       
        self.view.stock_log_refresh_btn.clicked.connect(self.refresh_stock_log)
        self.view.stock_log_item_filter.currentIndexChanged.connect(self.refresh_stock_log)

        
        
       
        try:
            if hasattr(self.view, 'set_suppliers') and hasattr(self.view, 'supplier_model') and self.view.supplier_model:
                suppliers = self.view.supplier_model.fetch_all()
                self.view.set_suppliers(suppliers)
        except Exception:
            pass

        self.refresh_inventory()
        self.refresh_stock_log()

    def refresh_inventory(self):
       
        try:
            items = self.model.fetch_all()
            self.view.load_table(items)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load inventory: {str(e)}")

    def add_item(self):
        try:
            raw = self.view.collect_form_data()
            if not raw:
                QMessageBox.warning(self.view, "Validation", "Invalid form data")
                return

            part_name = raw[0]
            category = raw[1]
            brand = raw[2]
            model_number = raw[3]
            quantity_text = raw[4]
            cost_text = raw[5]
            selling_text = raw[6]
            supplier_id = raw[7]

            if not part_name:
                QMessageBox.warning(self.view, "Validation", "Part name is required.")
                return

            if supplier_id is None:
                QMessageBox.warning(self.view, "Validation", "Please select a supplier.")
                return

            quantity_clean = re.sub(r"[^\d-]", "", quantity_text or "")
            if not quantity_clean:
                QMessageBox.warning(self.view, "Validation", "Quantity is required.")
                return
            try:
                quantity = int(quantity_clean)
            except Exception:
                QMessageBox.warning(self.view, "Validation", "Invalid quantity.")
                return
            if quantity < 0:
                QMessageBox.warning(self.view, "Validation", "Quantity cannot be negative.")
                return

            cost_clean = re.sub(r"[^\d.\-]", "", cost_text or "")
            selling_clean = re.sub(r"[^\d.\-]", "", selling_text or "")
            if not cost_clean or not selling_clean:
                QMessageBox.warning(self.view, "Validation", "Cost and selling prices are required.")
                return
            try:
                cost_price = float(cost_clean)
                selling_price = float(selling_clean)
            except Exception:
                QMessageBox.warning(self.view, "Validation", "Invalid price values.")
                return
            if cost_price < 0 or selling_price < 0:
                QMessageBox.warning(self.view, "Validation", "Prices cannot be negative.")
                return
            if selling_price < cost_price:
                QMessageBox.warning(self.view, "Validation", "Selling price cannot be below cost price.")
                return

            data = (
                part_name,
                category,
                brand,
                model_number,
                quantity,
                cost_price,
                selling_price,
                supplier_id,
            )

            self.model.create_item(data)
            self.view.clear_form()
            self.refresh_inventory()
            QMessageBox.information(self.view, "Success", "Item added successfully")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to add item: {str(e)}")

    def update_item(self):
        """Update selected inventory item."""
        try:
            raw = self.view.collect_form_data(with_id=True)
            if not raw:
                QMessageBox.warning(self.view, "Validation", "Invalid form data")
                return
            item_id = raw[0]
            part_name = raw[1]
            category = raw[2]
            brand = raw[3]
            model_number = raw[4]
            quantity_text = raw[5]
            cost_text = raw[6]
            selling_text = raw[7]
            supplier_id = raw[8]

            if not part_name:
                QMessageBox.warning(self.view, "Validation", "Part name is required.")
                return
            if supplier_id is None:
                QMessageBox.warning(self.view, "Validation", "Please select a supplier.")
                return

            quantity_clean = re.sub(r"[^\d-]", "", quantity_text or "")
            if not quantity_clean:
                QMessageBox.warning(self.view, "Validation", "Quantity is required.")
                return
            try:
                quantity = int(quantity_clean)
            except Exception:
                QMessageBox.warning(self.view, "Validation", "Invalid quantity.")
                return
            if quantity < 0:
                QMessageBox.warning(self.view, "Validation", "Quantity cannot be negative.")
                return

            cost_clean = re.sub(r"[^\d.\-]", "", cost_text or "")
            selling_clean = re.sub(r"[^\d.\-]", "", selling_text or "")
            if not cost_clean or not selling_clean:
                QMessageBox.warning(self.view, "Validation", "Cost and selling prices are required.")
                return
            try:
                cost_price = float(cost_clean)
                selling_price = float(selling_clean)
            except Exception:
                QMessageBox.warning(self.view, "Validation", "Invalid price values.")
                return
            if cost_price < 0 or selling_price < 0:
                QMessageBox.warning(self.view, "Validation", "Prices cannot be negative.")
                return
            if selling_price < cost_price:
                QMessageBox.warning(self.view, "Validation", "Selling price cannot be below cost price.")
                return

            data = (
                part_name,
                category,
                brand,
                model_number,
                quantity,
                cost_price,
                selling_price,
                supplier_id,
            )

            self.model.update_item(item_id, data)
            self.view.clear_form()
            self.refresh_inventory()
            QMessageBox.information(self.view, "Success", "Item updated successfully")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to update item: {str(e)}")

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