from mysql.connector import Error
from app.models.entities import InventoryItem, Sale, SaleItem
from app.exceptions import ValidationError, NotFoundError, DatabaseError


class POSService:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, part_name, category, brand, model_number, 
                       quantity, cost_price, selling_price, supplier_id
                FROM inventory_items
                ORDER BY part_name
            """)
            results = cursor.fetchall()
            return [self._map_row_to_item(row) for row in results]
        except Error as e:
            raise DatabaseError(f"Failed to fetch inventory: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def search_item(self, keyword):
        if not keyword or not keyword.strip():
            raise ValidationError("Search keyword cannot be empty")
        
        cursor = None
        try:
            cursor = self.db.cursor()
            search_term = f"%{keyword}%"
            cursor.execute("""
                SELECT id, part_name, category, brand, model_number, 
                       quantity, cost_price, selling_price, supplier_id
                FROM inventory_items
                WHERE part_name LIKE %s OR category LIKE %s OR brand LIKE %s
                ORDER BY part_name
            """, (search_term, search_term, search_term))
            results = cursor.fetchall()
            return [self._map_row_to_item(row) for row in results]
        except Error as e:
            raise DatabaseError(f"Failed to search items: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def save_transaction(self, items, total, user_id=None, vat_amount=0.0, payment_mode=None, amount_received=0.0, change=0.0):
        if not items:
            raise ValidationError("Transaction must have at least one item")
        
        try:
            total = float(total)
            vat_amount = float(vat_amount)
            amount_received = float(amount_received)
            change = float(change)
        except (ValueError, TypeError):
            raise ValidationError("Invalid total or payment values")
        
        if total <= 0:
            raise ValidationError("Total must be greater than zero")
        
        if amount_received < total:
            raise ValidationError(f"Insufficient payment: received {amount_received}, required {total}")
        
        cursor = None
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                INSERT INTO sales (total, user_id, vat_amount, payment_mode, amount_received, change_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (total, user_id, vat_amount, payment_mode, amount_received, change))
            
            sale_id = cursor.lastrowid
            
            for item in items:
                item_id = item.get("id")
                qty = item.get("qty")
                price = item.get("price")
                
                if not item_id or not qty or not price:
                    raise ValidationError("Invalid item data in transaction")
                
                try:
                    qty = int(qty)
                    price = float(price)
                except (ValueError, TypeError):
                    raise ValidationError("Invalid quantity or price in transaction")
                
                cursor.execute("""
                    SELECT quantity FROM inventory_items WHERE id = %s
                """, (item_id,))
                result = cursor.fetchone()
                if not result:
                    raise NotFoundError(f"Item ID {item_id} not found")
                
                current_qty = result[0]
                if current_qty < qty:
                    raise ValidationError(f"Insufficient stock for item {item_id}: available {current_qty}, requested {qty}")
                
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, item_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (sale_id, item_id, qty, price))
                
                cursor.execute("""
                    UPDATE inventory_items SET quantity = quantity - %s WHERE id = %s
                """, (qty, item_id))
            
            self.db.commit()
            return sale_id
        except (ValidationError, NotFoundError):
            self.db.rollback()
            raise
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to save transaction: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_item_stock(self, item_id):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT quantity FROM inventory_items WHERE id = %s
            """, (item_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            raise DatabaseError(f"Failed to get item stock: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _map_row_to_item(self, row):
        if not row:
            return None
        return InventoryItem(
            id=row[0],
            part_name=row[1],
            category=row[2],
            brand=row[3],
            model_number=row[4],
            quantity=row[5],
            cost_price=row[6],
            selling_price=row[7],
            supplier_id=row[8]
        )
