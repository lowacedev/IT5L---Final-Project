from PyQt6.QtWidgets import QMessageBox

class POSController:
    def __init__(self, model, view, user=None):
        self.model = model
        self.view = view
        self.cart = []
        self.user = user or {}

        # Connect signals
        view.search_btn.clicked.connect(self.search)
        view.results_table.cellDoubleClicked.connect(self.add_item)
        view.checkout_btn.clicked.connect(self.checkout)
        view.clear_cart_btn.clicked.connect(self.clear_cart)
        view.update_qty_btn.clicked.connect(self.update_quantity)
        view.remove_item_btn.clicked.connect(self.remove_item)
        
        print("[POS CONTROLLER] POSController initialized")
        print(f"[POS CONTROLLER] search_btn connected: {view.search_btn.receivers(view.search_btn.clicked)}")
        print(f"[POS CONTROLLER] checkout_btn connected: {view.checkout_btn.receivers(view.checkout_btn.clicked)}")
        try:
            print(f"[POS CONTROLLER] current user: {self.user.get('username')} (id: {self.user.get('id')})")
        except Exception:
            pass
        
        # Load all inventory items on startup
        self.load_all_items()

    def load_all_items(self):
        """Load all inventory items on startup."""
        print("[POS CONTROLLER] Loading all inventory items...")
        try:
            results = self.model.fetch_all()
            self.view.add_result(results)
            if results:
                print(f"[POS CONTROLLER] Loaded {len(results)} items into results table")
            else:
                print("[POS CONTROLLER] No items found in inventory")
        except Exception as e:
            print(f"[POS CONTROLLER ERROR] load_all_items: {e}")
            QMessageBox.warning(self.view, "Error", f"Failed to load inventory: {str(e)}")

    def search(self):
        """Search for items based on keyword."""
        print("[POS CONTROLLER] search() called")
        keyword = self.view.search_box.text().strip()
        if not keyword:
            QMessageBox.warning(self.view, "Search", "Please enter a search term.")
            return
        
        results = self.model.search_item(keyword)
        self.view.add_result(results)
        
        if not results:
            QMessageBox.information(self.view, "Search", "No items found.")

    def add_item(self, row, col):
        """Add item from search results to cart."""
        print(f"[POS CONTROLLER] add_item() called - row: {row}, col: {col}")
        try:
            item_id = int(self.view.results_table.item(row, 0).text())
            name = self.view.results_table.item(row, 1).text()
            price = float(self.view.results_table.item(row, 2).text())
            stock = int(self.view.results_table.item(row, 3).text())
            
            print(f"[POS CONTROLLER] Adding {name} (ID: {item_id}, Price: Php {price}, Stock: {stock})")
            
            if stock <= 0:
                QMessageBox.warning(self.view, "Out of Stock", "This item is out of stock.")
                return

            # Check if item already in cart
            for i, cart_item in enumerate(self.cart):
                if cart_item["id"] == item_id:
                    # Update quantity
                    new_qty = cart_item["qty"] + 1
                    if new_qty > stock:
                        QMessageBox.warning(self.view, "Stock Limit", 
                                          f"Cannot add more. Only {stock} in stock.")
                        return
                    cart_item["qty"] = new_qty
                    self.view.update_cart_row(i, new_qty, price)
                    self.update_total()
                    return

            # Add new item to cart
            self.cart.append({
                "id": item_id,
                "name": name,
                "qty": 1,
                "price": price,
                "stock": stock
            })
            
            self.view.add_to_cart(item_id, name, 1, price)
            self.update_total()
            
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[POS CONTROLLER ERROR] add_item: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to add item: {error_msg}")

    def update_quantity(self):
        """Update quantity for selected cart item."""
        row = self.view.cart_table.currentRow()
        if row < 0:
            QMessageBox.warning(self.view, "No Selection", "Please select an item from cart.")
            return
        try:
            new_qty_text = self.view.qty_input.text()
            new_qty = int(new_qty_text)
            if new_qty <= 0:
                QMessageBox.warning(self.view, "Invalid Quantity", "Quantity must be greater than 0.")
                return

            # Ensure cart index exists
            if row >= len(self.cart):
                QMessageBox.warning(self.view, "Selection Error", "Selected cart item not found.")
                return

            cart_item = self.cart[row]
            if new_qty > cart_item["stock"]:
                QMessageBox.warning(self.view, "Stock Limit",
                                    f"Cannot set quantity to {new_qty}. Only {cart_item['stock']} in stock.")
                return

            cart_item["qty"] = new_qty
            self.view.update_cart_row(row, new_qty, cart_item["price"])
            self.update_total()
            self.view.qty_input.clear()

        except ValueError:
            QMessageBox.warning(self.view, "Invalid Input", "Please enter a valid number.")
        except Exception as e:
            # Catch-all to prevent the app from crashing on unexpected errors
            print(f"[POS CONTROLLER ERROR] update_quantity: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to update quantity: {str(e)}")

    def remove_item(self):
        """Remove selected item from cart."""
        row = self.view.cart_table.currentRow()
        if row < 0:
            QMessageBox.warning(self.view, "No Selection", "Please select an item to remove.")
            return
        
        self.cart.pop(row)
        self.view.cart_table.removeRow(row)
        self.update_total()

    def clear_cart(self):
        """Clear all items from cart."""
        if not self.cart:
            return
        
        reply = QMessageBox.question(
            self.view,
            "Clear Cart",
            "Are you sure you want to clear the cart?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cart.clear()
            self.view.clear_cart()

    def update_total(self):
        """Update the total amount."""
        total = sum(item["price"] * item["qty"] for item in self.cart)
        self.view.total_label.setText(f"Total: Php {total:,.2f}")

    def checkout(self):
        """Process the checkout."""
        print("[POS CONTROLLER] checkout() called")
        if not self.cart:
            QMessageBox.warning(self.view, "Empty Cart", "Cart is empty.")
            return

        try:
            total = sum(item["price"] * item["qty"] for item in self.cart)
            
            # Confirm checkout
            reply = QMessageBox.question(
                self.view,
                "Confirm Checkout",
                f"Total Amount: Php {total:,.2f}\n\nProceed with checkout?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Save transaction (include user id if available)
            user_id = None
            try:
                user_id = self.user.get('id') if self.user else None
            except Exception:
                user_id = None

            self.model.save_transaction(self.cart, total, user_id)
            
            # Show success
            QMessageBox.information(
                self.view,
                "Success",
                f"Transaction completed!\nTotal: Php {total:,.2f}"
            )
            
            # Clear cart
            self.cart.clear()
            self.view.clear_cart()
            self.view.search_box.clear()
            
            # Refresh inventory table
            self.load_all_items()
            
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Checkout failed: {str(e)}")