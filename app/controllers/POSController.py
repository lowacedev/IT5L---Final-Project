from app.exceptions import ValidationError, NotFoundError, DatabaseError


class POSController:
    def __init__(self, service, view, user=None):
        self.service = service
        self.view = view
        self.cart = []
        self.user = user or {}

        view.search_btn.clicked.connect(self.search)
        view.results_table.cellDoubleClicked.connect(self.add_item)
        view.checkout_btn.clicked.connect(self.checkout)
        view.clear_cart_btn.clicked.connect(self.clear_cart)
        view.update_qty_btn.clicked.connect(self.update_quantity)
        view.remove_item_btn.clicked.connect(self.remove_item)
        
        self.load_all_items()

    def load_all_items(self):
        try:
            results = self.service.fetch_all()
            items_data = [
                (item.id, item.part_name, item.selling_price, item.quantity)
                for item in results
            ]
            self.view.add_result(items_data)
        except (ValidationError, NotFoundError, DatabaseError) as e:
            self.view.show_error(f"Failed to load inventory: {str(e)}")
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def search(self):
        keyword = self.view.search_box.text().strip()
        if not keyword:
            self.view.show_warning("Please enter a search term.")
            return
        
        try:
            results = self.service.search_item(keyword)
            items_data = [
                (item.id, item.part_name, item.selling_price, item.quantity)
                for item in results
            ]
            self.view.add_result(items_data)
            if not results:
                self.view.show_info("No items found.")
        except (ValidationError, NotFoundError, DatabaseError) as e:
            self.view.show_error(f"Search failed: {str(e)}")
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def add_item(self, row, col):
        try:
            item_id = int(self.view.results_table.item(row, 0).text())
            name = self.view.results_table.item(row, 1).text()
            price_text = self.view.results_table.item(row, 2).text()
            stock_text = self.view.results_table.item(row, 3).text()
            
            price = float(price_text.replace(",", "")) if price_text else 0.0
            stock = int(stock_text.replace(",", "")) if stock_text else 0
            
            if stock <= 0:
                self.view.show_warning("This item is out of stock.")
                return

            for i, cart_item in enumerate(self.cart):
                if cart_item["id"] == item_id:
                    new_qty = cart_item["qty"] + 1
                    if new_qty > stock:
                        self.view.show_warning(f"Cannot add more. Only {stock} in stock.")
                        return
                    cart_item["qty"] = new_qty
                    self.view.update_cart_row(i, new_qty, price)
                    self.update_total()
                    return

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
            self.view.show_error(f"Failed to add item: {str(e)}")

    def update_quantity(self):
        row = self.view.cart_table.currentRow()
        if row < 0:
            self.view.show_warning("Please select an item from cart.")
            return
        try:
            new_qty_text = self.view.qty_input.text()
            new_qty = int(new_qty_text)
            if new_qty <= 0:
                self.view.show_warning("Quantity must be greater than 0.")
                return

            if row >= len(self.cart):
                self.view.show_warning("Selected cart item not found.")
                return

            cart_item = self.cart[row]
            if new_qty > cart_item["stock"]:
                self.view.show_warning(f"Cannot set quantity to {new_qty}. Only {cart_item['stock']} in stock.")
                return

            cart_item["qty"] = new_qty
            self.view.update_cart_row(row, new_qty, cart_item["price"])
            self.update_total()
            self.view.qty_input.clear()

        except ValueError:
            self.view.show_warning("Please enter a valid number.")
        except Exception as e:
            self.view.show_error(f"Failed to update quantity: {str(e)}")

    def remove_item(self):
        row = self.view.cart_table.currentRow()
        if row < 0:
            self.view.show_warning("Please select an item to remove.")
            return
        
        self.cart.pop(row)
        self.view.cart_table.removeRow(row)
        self.update_total()

    def clear_cart(self):
        if not self.cart:
            return
        
        if self.view.ask_confirmation("Are you sure you want to clear the cart?", "Clear Cart"):
            self.cart.clear()
            self.view.clear_cart()

    def update_total(self):
        subtotal = sum(item["price"] * item["qty"] for item in self.cart)
        vat_amount = subtotal * 0.12
        total = subtotal + vat_amount
        
        self.view.subtotal_label.setText(f"Subtotal: Php {subtotal:,.2f}")
        self.view.vat_label.setText(f"VAT (12%): Php {vat_amount:,.2f}")
        self.view.total_label.setText(f"Total: Php {total:,.2f}")

    def checkout(self):
        if not self.cart:
            self.view.show_warning("Cart is empty.")
            return

        try:
            subtotal = sum(item["price"] * item["qty"] for item in self.cart)
            
            from app.views.CheckoutReceiptDialog import CheckoutReceiptDialog
            cashier_name = self.user.get('full_name') if self.user else None
            
            checkout_dialog = CheckoutReceiptDialog(
                items=self.cart,
                subtotal=subtotal,
                cashier_name=cashier_name,
                parent=self.view
            )
            
            if checkout_dialog.exec() != CheckoutReceiptDialog.DialogCode.Accepted:
                return
            
            payment_details = checkout_dialog.get_payment_details()
            vat_amount = payment_details['vat_amount']
            total = payment_details['total']
            payment_mode = payment_details['payment_mode']
            amount_received = payment_details['amount_received']
            change = payment_details['change']
            
            if amount_received < total:
                self.view.show_warning(
                    f"Insufficient Payment. Amount received (Php {amount_received:,.2f}) is less than total (Php {total:,.2f})"
                )
                return
            
            user_id = None
            try:
                user_id = self.user.get('id') if self.user else None
            except Exception:
                user_id = None

            sale_id = self.service.save_transaction(
                items=self.cart,
                total=total,
                user_id=user_id,
                vat_amount=vat_amount,
                payment_mode=payment_mode,
                amount_received=amount_received,
                change=change
            )
            
            from app.views.ReceiptDisplayDialog import ReceiptDisplayDialog
            receipt_dialog = ReceiptDisplayDialog(
                sale_id=sale_id,
                items=self.cart,
                subtotal=subtotal,
                vat_amount=vat_amount,
                total=total,
                payment_mode=payment_mode,
                amount_received=amount_received,
                change=change,
                cashier_name=self.user.get('full_name') if self.user else None,
                parent=self.view
            )
            receipt_dialog.exec()
            
            self.cart.clear()
            self.view.clear_cart()
            self.load_all_items()
            self.view.show_success("Transaction completed successfully")
            
        except (ValidationError, NotFoundError, DatabaseError) as e:
            self.view.show_error(f"Checkout failed: {str(e)}")
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")