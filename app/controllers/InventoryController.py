from app.exceptions import ValidationError, NotFoundError, DatabaseError
import logging
from app.utils.logger import SecurityAuditLogger
from app.security.input_validator import InputValidator


class InventoryController:
    def __init__(self, service, view, user=None):
        self.service = service
        self.view = view
        self.user = user
        self.logger = logging.getLogger(__name__)

        try:
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

            # Load initial data without excessive logging
            self.refresh_inventory()
            self.refresh_stock_log()
        except Exception as e:
            self.logger.error(f"Error during InventoryController initialization: {str(e)}")
            import traceback
            full_traceback = traceback.format_exc()
            self.logger.error(f"Full traceback:\n{full_traceback}")
            print(f"ERROR: {str(e)}")
            print(full_traceback)
            # Don't show error dialog during initialization - just log it
            # self.view.show_error(f"Failed to initialize inventory: {str(e)}")

    def refresh_inventory(self):
        try:
            items = self.service.fetch_all()
            self.view.load_table(items)
            self.view.load_suppliers()
        except Exception as e:
            self.logger.error(f"Error in refresh_inventory: {str(e)}")
            import traceback
            full_traceback = traceback.format_exc()
            self.logger.error(f"Full traceback:\n{full_traceback}")
            print(f"ERROR in refresh_inventory: {str(e)}")
            print(full_traceback)

    def _check_admin_permission(self, action):
        """Check if user has admin permissions for the action."""
        if self.user and self.user.get('role') != 'admin':
            self.view.show_error(f"You do not have permission to {action}. Contact an admin.")
            return False
        return True

    def _validate_inventory_fields(self, part_name, category, brand, model_number, quantity, cost_price, selling_price):
        """Validate all inventory item fields and return error message if invalid."""
        validations = [
            (InputValidator.validate_product_name(part_name), "Product name"),
            (InputValidator.validate_category(category) if category else (True, ""), "Category"),
            (InputValidator.validate_brand(brand) if brand else (True, ""), "Brand"),
            (InputValidator.validate_model_number(model_number) if model_number else (True, ""), "Model number"),
            (InputValidator.validate_quantity(quantity), "Quantity"),
            (InputValidator.validate_price(cost_price), "Cost price"),
            (InputValidator.validate_price(selling_price), "Selling price"),
        ]
        
        for (is_valid, msg), field_name in validations:
            if not is_valid:
                return f"{field_name}: {msg}"
        return None

    def _create_and_log_item(self, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id):
        """Create item and log the action."""
        self.service.create_item(
            part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id,
            performed_by=self.user.get('username') if self.user else None
        )
        
        username = self.user.get('username') if self.user else 'unknown'
        SecurityAuditLogger.log_user_action(
            username,
            'create_inventory_item',
            f'Created item: {part_name} (Qty: {quantity}, Price: {selling_price})'
        )

    def _update_and_log_item(self, item_id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id):
        """Update item and log the action."""
        self.service.update_item(
            item_id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id,
            performed_by=self.user.get('username') if self.user else None
        )
        
        username = self.user.get('username') if self.user else 'unknown'
        SecurityAuditLogger.log_user_action(
            username,
            'update_inventory_item',
            f'Updated item ID {item_id}: {part_name} (Qty: {quantity}, Price: {selling_price})'
        )

    def add_item(self):
        # Check permission for non-admin users
        if not self._check_admin_permission("add inventory items"):
            return
        
        raw = self.view.collect_form_data()
        if not raw:
            return

        part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id = raw

        if supplier_id is None:
            self.view.show_warning("Please select a supplier.")
            return

        # Validate input fields
        validation_error = self._validate_inventory_fields(
            part_name, category, brand, model_number, quantity, cost_price, selling_price
        )
        if validation_error:
            self.view.show_error(validation_error)
            return

        try:
            self._create_and_log_item(
                part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id
            )
            self.view.show_success("Item added successfully!")
            self.view.clear_form()
            self.refresh_inventory()
        except ValidationError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def update_item(self):
        # Check permission for non-admin users
        if not self._check_admin_permission("update inventory items"):
            return
        
        raw = self.view.collect_form_data(with_id=True)
        if not raw:
            self.view.show_warning("Please select an item to update.")
            return

        item_id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id = raw

        if supplier_id is None:
            self.view.show_warning("Please select a supplier.")
            return

        # Validate input fields
        validation_error = self._validate_inventory_fields(
            part_name, category, brand, model_number, quantity, cost_price, selling_price
        )
        if validation_error:
            self.view.show_error(validation_error)
            return

        if not self.view.ask_confirmation("Are you sure you want to update this item?"):
            return

        try:
            self._update_and_log_item(
                item_id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id
            )
            self.view.show_success("Item updated successfully!")
            self.view.clear_form()
            self.refresh_inventory()
        except ValidationError as e:
            self.view.show_error(str(e))
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def search_inventory(self):
        keyword = self.view.search_box.text().strip()
        if not keyword:
            self.view.show_warning("Please enter a search term.")
            return

        try:
            results = self.service.fetch_all()
            filtered = [item for item in results if keyword.lower() in item.part_name.lower() or keyword.lower() in item.category.lower() or keyword.lower() in item.brand.lower()]
            self.view.load_table(filtered)
        except Exception as e:
            self.view.show_error(f"Search failed: {str(e)}")

    def record_stock_in(self):
        # Check permission for non-admin users
        if not self._check_admin_permission("record stock movements"):
            return
        
        try:
            item_id = self.view.stock_in_item_combo.currentData()
            if item_id is None:
                self.view.show_warning("Please select an item.")
                return

            qty = self.view.stock_in_qty.value()
            if qty <= 0:
                self.view.show_warning("Quantity must be greater than 0.")
                return

            reason = self.view.stock_in_reason.currentText()
            notes = self.view.stock_in_notes.toPlainText()
            user_id = self.user.get('id') if self.user else None

            self.service.record_stock_movement(item_id, 'IN', qty, reason, notes, user_id)
            
            # Log user action
            username = self.user.get('username') if self.user else 'unknown'
            SecurityAuditLogger.log_user_action(
                username, 
                'stock_in', 
                f'Stock In - Item ID: {item_id}, Quantity: {qty}, Reason: {reason}'
            )
            
            self.clear_stock_in_form()
            self.refresh_inventory()
            self.refresh_stock_log()
            self.view.show_success(f"Recorded stock in: {qty} units")
        except ValidationError as e:
            self.view.show_error(str(e))
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to record stock in: {str(e)}")

    def record_stock_out(self):
        # Check permission for non-admin users
        if not self._check_admin_permission("record stock movements"):
            return
        
        try:
            item_id = self.view.stock_out_item_combo.currentData()
            if item_id is None:
                self.view.show_warning("Please select an item.")
                return

            qty = self.view.stock_out_qty.value()
            if qty <= 0:
                self.view.show_warning("Quantity must be greater than 0.")
                return

            reason = self.view.stock_out_reason.currentText()
            notes = self.view.stock_out_notes.toPlainText()
            user_id = self.user.get('id') if self.user else None

            self.service.record_stock_movement(item_id, 'OUT', qty, reason, notes, user_id)
            
            # Log user action
            username = self.user.get('username') if self.user else 'unknown'
            SecurityAuditLogger.log_user_action(
                username, 
                'stock_out', 
                f'Stock Out - Item ID: {item_id}, Quantity: {qty}, Reason: {reason}'
            )
            
            self.clear_stock_out_form()
            self.refresh_inventory()
            self.refresh_stock_log()
            self.view.show_success(f"Recorded stock out: {qty} units")
        except ValidationError as e:
            self.view.show_error(str(e))
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to record stock out: {str(e)}")

    def refresh_stock_log(self):
        try:
            selected_item_id = self.view.stock_log_item_filter.currentData()
            movements = self.service.get_stock_movements(item_id=selected_item_id, limit=100)
            self.view.load_stock_log_table(movements if movements else [])
        except Exception as e:
            self.logger.error(f"Error in refresh_stock_log: {str(e)}")
            import traceback
            traceback.print_exc()
            self.view.show_error(f"Failed to load stock log: {str(e)}")

    def clear_stock_in_form(self):
        self.view.stock_in_qty.setValue(1)
        self.view.stock_in_reason.setCurrentIndex(0)
        self.view.stock_in_notes.clear()

    def clear_stock_out_form(self):
        self.view.stock_out_qty.setValue(1)
        self.view.stock_out_reason.setCurrentIndex(0)
        self.view.stock_out_notes.clear()