from app.exceptions import ValidationError, NotFoundError, DatabaseError
import logging


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

            self.logger.info("Connecting signals...")
            self.refresh_inventory()
            self.logger.info("Refreshing inventory...")
            self.refresh_stock_log()
            self.logger.info("Refreshing stock log...")
        except Exception as e:
            self.logger.error(f"Error during InventoryController initialization: {str(e)}")
            import traceback
            traceback.print_exc()
            self.view.show_error(f"Failed to initialize inventory: {str(e)}")

    def refresh_inventory(self):
        try:
            self.logger.info("Fetching all inventory items...")
            items = self.service.fetch_all()
            self.logger.info(f"Fetched {len(items)} items, loading table...")
            self.view.load_table(items)
            self.logger.info("Loading suppliers...")
            self.view.load_suppliers()
            self.logger.info("Inventory refresh completed successfully")
        except Exception as e:
            self.logger.error(f"Error in refresh_inventory: {str(e)}")
            import traceback
            traceback.print_exc()
            self.view.show_error(f"Failed to load inventory: {str(e)}")

    def add_item(self):
        # Check permission for non-admin users
        if self.user and self.user.get('role') != 'admin':
            self.view.show_error("You do not have permission to add inventory items. Contact an admin.")
            return
        
        raw = self.view.collect_form_data()
        if not raw:
            return

        part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id = raw

        if supplier_id is None:
            self.view.show_warning("Please select a supplier.")
            return

        # Validate input fields
        from app.security.input_validator import InputValidator
        
        # Validate product name
        is_valid, msg = InputValidator.validate_product_name(part_name)
        if not is_valid:
            self.view.show_error(f"Product name: {msg}")
            return
        
        # Validate category
        if category:  # Optional field
            is_valid, msg = InputValidator.validate_category(category)
            if not is_valid:
                self.view.show_error(f"Category: {msg}")
                return
        
        # Validate brand
        if brand:  # Optional field
            is_valid, msg = InputValidator.validate_brand(brand)
            if not is_valid:
                self.view.show_error(f"Brand: {msg}")
                return
        
        # Validate model number
        if model_number:  # Optional field
            is_valid, msg = InputValidator.validate_model_number(model_number)
            if not is_valid:
                self.view.show_error(f"Model number: {msg}")
                return
        
        # Validate quantity
        is_valid, msg = InputValidator.validate_quantity(quantity)
        if not is_valid:
            self.view.show_error(f"Quantity: {msg}")
            return
        
        # Validate prices
        is_valid, msg = InputValidator.validate_price(cost_price)
        if not is_valid:
            self.view.show_error(f"Cost price: {msg}")
            return
        
        is_valid, msg = InputValidator.validate_price(selling_price)
        if not is_valid:
            self.view.show_error(f"Selling price: {msg}")
            return

        try:
            self.service.create_item(part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id, performed_by=self.user.get('username') if self.user else None)
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
        if self.user and self.user.get('role') != 'admin':
            self.view.show_error("You do not have permission to update inventory items. Contact an admin.")
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
        from app.security.input_validator import InputValidator
        
        # Validate product name
        is_valid, msg = InputValidator.validate_product_name(part_name)
        if not is_valid:
            self.view.show_error(f"Product name: {msg}")
            return
        
        # Validate category
        if category:
            is_valid, msg = InputValidator.validate_category(category)
            if not is_valid:
                self.view.show_error(f"Category: {msg}")
                return
        
        # Validate brand
        if brand:
            is_valid, msg = InputValidator.validate_brand(brand)
            if not is_valid:
                self.view.show_error(f"Brand: {msg}")
                return
        
        # Validate model number
        if model_number:
            is_valid, msg = InputValidator.validate_model_number(model_number)
            if not is_valid:
                self.view.show_error(f"Model number: {msg}")
                return
        
        # Validate quantity
        is_valid, msg = InputValidator.validate_quantity(quantity)
        if not is_valid:
            self.view.show_error(f"Quantity: {msg}")
            return
        
        # Validate prices
        is_valid, msg = InputValidator.validate_price(cost_price)
        if not is_valid:
            self.view.show_error(f"Cost price: {msg}")
            return
        
        is_valid, msg = InputValidator.validate_price(selling_price)
        if not is_valid:
            self.view.show_error(f"Selling price: {msg}")
            return

        if not self.view.ask_confirmation("Are you sure you want to update this item?"):
            return

        try:
            self.service.update_item(item_id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id, performed_by=self.user.get('username') if self.user else None)
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
        if self.user and self.user.get('role') != 'admin':
            self.view.show_error("You do not have permission to record stock movements. Contact an admin.")
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
        if self.user and self.user.get('role') != 'admin':
            self.view.show_error("You do not have permission to record stock movements. Contact an admin.")
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
            self.logger.info("Refreshing stock log...")
            selected_item_id = self.view.stock_log_item_filter.currentData()
            self.logger.info(f"Selected item ID: {selected_item_id}")
            movements = self.service.get_stock_movements(item_id=selected_item_id, limit=100)
            self.logger.info(f"Fetched {len(movements) if movements else 0} movements")
            self.view.load_stock_log_table(movements if movements else [])
            self.logger.info("Stock log refresh completed successfully")
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