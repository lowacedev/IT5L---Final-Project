from mysql.connector import Error


class InventoryModel:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT ii.id, ii.part_name, ii.category, ii.brand, ii.model_number, 
                       ii.quantity, ii.cost_price, ii.selling_price, COALESCE(s.name, 'N/A')
                FROM inventory_items ii
                LEFT JOIN suppliers s ON ii.supplier_id = s.id
                ORDER BY ii.part_name
            """)
            return cursor.fetchall()
        except Error:
            raise
        finally:
            if cursor:
                cursor.close()

    def create_item(self, data):
        cursor = None
        try:
    
            try:
                cost_price = float(data[5])
                selling_price = float(data[6])
                if selling_price < cost_price:
                    raise ValueError("Selling price cannot be below cost price")
            except (ValueError, TypeError) as e:
                raise
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO inventory_items 
                (part_name, category, brand, model_number, quantity, 
                 cost_price, selling_price, supplier_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
            self.db.commit()
            return cursor.lastrowid
        except Error:
            if self.db:
                self.db.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def update_item(self, item_id, data):
        cursor = None
        try:
            try:
                cost_price = float(data[5])
                selling_price = float(data[6])
                if selling_price < cost_price:
                    raise ValueError("Selling price cannot be below cost price")
            except (ValueError, TypeError):
                raise
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE inventory_items SET 
                    part_name=%s, category=%s, brand=%s, model_number=%s,
                    quantity=%s, cost_price=%s, selling_price=%s, supplier_id=%s
                WHERE id=%s
            """, data + (item_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Error:
            if self.db:
                self.db.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def delete_item(self, item_id):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM inventory_items WHERE id=%s", (item_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Error:
            if self.db:
                self.db.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def get_by_id(self, item_id):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, part_name, category, brand, model_number, 
                       quantity, cost_price, selling_price, supplier_id
                FROM inventory_items
                WHERE id=%s
            """, (item_id,))
            return cursor.fetchone()
        except Error:
            raise
        finally:
            if cursor:
                cursor.close()

    def record_stock_movement(self, item_id, movement_type, quantity, reason, notes, user_id):
        if movement_type not in ("IN", "OUT", "ADJUSTMENT"):
            raise ValueError("Invalid movement type")

        cursor = None
        try:
            cursor = self.db.cursor()

            cursor.execute("SELECT quantity FROM inventory_items WHERE id=%s", (item_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Item not found")

            current_qty = result[0]

            if movement_type == "IN":
                new_qty = current_qty + quantity
            elif movement_type == "OUT":
                new_qty = current_qty - quantity
                if new_qty < 0:
                    raise ValueError("Insufficient stock")
            else:
                new_qty = quantity

            cursor.execute("""
                INSERT INTO stock_movements 
                (item_id, movement_type, quantity, reason, notes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item_id, movement_type, quantity, reason, notes, user_id))

            movement_id = cursor.lastrowid

            cursor.execute(
                "UPDATE inventory_items SET quantity=%s WHERE id=%s",
                (new_qty, item_id)
            )

            self.db.commit()
            return movement_id
        except ValueError:
            raise
        except Error:
            if self.db:
                self.db.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def get_stock_movements(self, item_id=None, limit=100):
        cursor = None
        try:
            cursor = self.db.cursor()
            if item_id:
                cursor.execute("""
                    SELECT sm.id, ii.part_name, sm.movement_type, sm.quantity, sm.reason, 
                           sm.notes, sm.movement_date, COALESCE(u.full_name, u.username, 'System')
                    FROM stock_movements sm
                    JOIN inventory_items ii ON sm.item_id = ii.id
                    LEFT JOIN users u ON sm.created_by = u.id
                    WHERE sm.item_id = %s
                    ORDER BY sm.movement_date DESC
                    LIMIT %s
                """, (item_id, limit))
            else:
                cursor.execute("""
                    SELECT sm.id, ii.part_name, sm.movement_type, sm.quantity, sm.reason, 
                           sm.notes, sm.movement_date, COALESCE(u.full_name, u.username, 'System')
                    FROM stock_movements sm
                    JOIN inventory_items ii ON sm.item_id = ii.id
                    LEFT JOIN users u ON sm.created_by = u.id
                    ORDER BY sm.movement_date DESC
                    LIMIT %s
                """, (limit,))
            return cursor.fetchall()
        except Error:
            raise
        finally:
            if cursor:
                cursor.close()
