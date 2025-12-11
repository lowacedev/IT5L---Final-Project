class POSModel:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
        print("[POS MODEL] POSModel initialized")

    def fetch_all(self):
        """Fetch all inventory items for initial display."""
        sql = """
        SELECT id, part_name, selling_price, quantity 
        FROM inventory_items 
        ORDER BY part_name
        """
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            print(f"[POS MODEL] Fetched {len(results)} total inventory items")
            return results
        except Exception as e:
            print(f"[POS MODEL ERROR] fetch_all: {e}")
            return []

    def search_item(self, keyword):
        """Search for items by part name."""
        sql = """
        SELECT id, part_name, selling_price, quantity 
        FROM inventory_items 
        WHERE part_name LIKE %s OR category LIKE %s OR brand LIKE %s
        ORDER BY part_name
        """
        search_term = "%" + keyword + "%"
        try:
            self.cursor.execute(sql, (search_term, search_term, search_term))
            results = self.cursor.fetchall()
            print(f"[POS MODEL] Found {len(results)} items matching '{keyword}'")
            return results
        except Exception as e:
            print(f"[POS MODEL ERROR] search_item: {e}")
            return []

    def save_transaction(self, items, total, user_id=None):
        """Save a sale transaction and update stock.

        user_id: optional integer id of the cashier/user who processed the sale.
        """
        try:
            print(f"[POS MODEL] Saving transaction with {len(items)} items, total: Php {total:,.2f}")
            
            # Insert sale (let sale_date default to CURRENT_TIMESTAMP if column exists)
            sql_sale = "INSERT INTO sales (total, user_id) VALUES (%s, %s)"
            self.cursor.execute(sql_sale, (total, user_id))
            sale_id = self.cursor.lastrowid
            print(f"[POS MODEL] Created sale with ID: {sale_id}")

            # Insert sale items and update stock
            sql_item = """
                INSERT INTO sale_items (sale_id, item_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """
            sql_update_stock = """
                UPDATE inventory_items 
                SET quantity = quantity - %s 
                WHERE id = %s
            """
            
            for item in items:
                # Add to sale_items
                self.cursor.execute(sql_item, (
                    sale_id, 
                    item["id"], 
                    item["qty"], 
                    item["price"]
                ))
                
                # Decrease stock
                self.cursor.execute(sql_update_stock, (
                    item["qty"], 
                    item["id"]
                ))
                print(f"[POS MODEL] Added {item['qty']}x {item['name']} to sale")

            self.db.commit()
            print(f"[POS MODEL] Transaction saved successfully")
            return sale_id
            
        except Exception as e:
            self.db.rollback()
            print(f"[POS MODEL ERROR] save_transaction: {e}")
            raise e

    def get_item_stock(self, item_id):
        """Get current stock for an item."""
        sql = "SELECT quantity FROM inventory_items WHERE id = %s"
        try:
            self.cursor.execute(sql, (item_id,))
            result = self.cursor.fetchone()
            stock = result[0] if result else 0
            print(f"[POS MODEL] Item {item_id} stock: {stock}")
            return stock
        except Exception as e:
            print(f"[POS MODEL ERROR] get_item_stock: {e}")
            return 0