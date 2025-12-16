import mysql.connector
from mysql.connector import Error

class InventoryModel:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        """Fetch all inventory items with supplier name."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT ii.id, ii.part_name, ii.category, ii.brand, ii.model_number, 
                       ii.quantity, ii.cost_price, ii.selling_price, COALESCE(s.name, 'N/A')
                FROM inventory_items ii
                LEFT JOIN suppliers s ON ii.supplier_id = s.id
                ORDER BY ii.part_name
            """)
            results = cursor.fetchall()
            cursor.close()
            print(f"[MODEL] Fetched {len(results)} items")
            return results
        except Error as e:
            print(f"[MODEL ERROR] fetch_all: {e}")
            return []

    def create_item(self, data):
        """Create a new inventory item.
        data = (part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id)
        """
        try:
            cursor = self.db.cursor()
            query = """
            INSERT INTO inventory_items 
            (part_name, category, brand, model_number, quantity, 
             cost_price, selling_price, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            print(f"[MODEL] Creating item: {data}")
            cursor.execute(query, data)
            self.db.commit()
            item_id = cursor.lastrowid
            cursor.close()
            print(f"[MODEL] Created item with ID: {item_id}")
            return item_id
        except Error as e:
            self.db.rollback()
            print(f"[MODEL ERROR] create_item: {e}")
            raise e

    def update_item(self, item_id, data):
        """Update an existing inventory item.
        item_id = the ID of the item to update
        data = (part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id)
        """
        try:
            cursor = self.db.cursor()
            query = """
            UPDATE inventory_items SET 
                part_name=%s, category=%s, brand=%s, model_number=%s,
                quantity=%s, cost_price=%s, selling_price=%s, supplier_id=%s
            WHERE id=%s
            """
            # Append ID to the end
            params = data + (item_id,)
            print(f"[MODEL] Updating item {item_id} with params: {params}")
            cursor.execute(query, params)
            self.db.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            print(f"[MODEL] Updated {rows_affected} row(s)")
            return rows_affected > 0
        except Error as e:
            self.db.rollback()
            print(f"[MODEL ERROR] update_item: {e}")
            raise e

    def delete_item(self, item_id):
        """Delete an inventory item."""
        try:
            cursor = self.db.cursor()
            print(f"[MODEL] Deleting item with ID: {item_id}")
            cursor.execute("DELETE FROM inventory_items WHERE id=%s", (item_id,))
            self.db.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            print(f"[MODEL] Deleted {rows_affected} row(s)")
            return rows_affected > 0
        except Error as e:
            self.db.rollback()
            print(f"[MODEL ERROR] delete_item: {e}")
            raise e

    def get_by_id(self, item_id):
        """Get a single item by ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, part_name, category, brand, model_number, 
                       quantity, cost_price, selling_price, supplier_id
                FROM inventory_items
                WHERE id=%s
            """, (item_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"[MODEL ERROR] get_by_id: {e}")
            return None

    def record_stock_movement(self, item_id, movement_type, quantity, reason, notes, user_id):
        """Record a stock movement (IN, OUT, ADJUSTMENT).
        Args:
            item_id: ID of the inventory item
            movement_type: 'IN', 'OUT', or 'ADJUSTMENT'
            quantity: amount to add/remove
            reason: reason for movement (e.g., 'Supplier Purchase', 'Sale', 'Damage', etc.)
            notes: additional notes
            user_id: user who recorded the movement
        Returns: movement_id if successful, None if failed
        """
        try:
            cursor = self.db.cursor()
            
            # Get current quantity
            cursor.execute("SELECT quantity FROM inventory_items WHERE id=%s", (item_id,))
            result = cursor.fetchone()
            if not result:
                print(f"[MODEL ERROR] Item {item_id} not found")
                cursor.close()
                return None
            
            current_qty = result[0]
            
            # Calculate new quantity based on movement type
            if movement_type == 'IN':
                new_qty = current_qty + quantity
            elif movement_type == 'OUT':
                new_qty = current_qty - quantity
                if new_qty < 0:
                    print(f"[MODEL ERROR] Insufficient stock. Current: {current_qty}, trying to remove: {quantity}")
                    cursor.close()
                    return None
            elif movement_type == 'ADJUSTMENT':
                new_qty = quantity  # Set to specific quantity
            else:
                print(f"[MODEL ERROR] Invalid movement type: {movement_type}")
                cursor.close()
                return None
            
            # Record movement in stock_movements table
            insert_query = """
                INSERT INTO stock_movements 
                (item_id, movement_type, quantity, reason, notes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (item_id, movement_type, quantity, reason, notes, user_id))
            movement_id = cursor.lastrowid
            
            # Update inventory quantity
            cursor.execute(
                "UPDATE inventory_items SET quantity=%s WHERE id=%s",
                (new_qty, item_id)
            )
            
            self.db.commit()
            cursor.close()
            print(f"[MODEL] Recorded {movement_type} movement: item_id={item_id}, qty={quantity}, new_total={new_qty}")
            return movement_id
            
        except Error as e:
            self.db.rollback()
            print(f"[MODEL ERROR] record_stock_movement: {e}")
            return None

    def get_stock_movements(self, item_id=None, limit=100):
        """Get stock movements log.
        Args:
            item_id: Optional, filter by specific item
            limit: max rows to return
        Returns: list of movement records
        """
        try:
            cursor = self.db.cursor()
            if item_id:
                query = """
                    SELECT sm.id, ii.part_name, sm.movement_type, sm.quantity, sm.reason, 
                           sm.notes, sm.movement_date, COALESCE(u.full_name, u.username, 'System')
                    FROM stock_movements sm
                    JOIN inventory_items ii ON sm.item_id = ii.id
                    LEFT JOIN users u ON sm.created_by = u.id
                    WHERE sm.item_id = %s
                    ORDER BY sm.movement_date DESC
                    LIMIT %s
                """
                cursor.execute(query, (item_id, limit))
            else:
                query = """
                    SELECT sm.id, ii.part_name, sm.movement_type, sm.quantity, sm.reason, 
                           sm.notes, sm.movement_date, COALESCE(u.full_name, u.username, 'System')
                    FROM stock_movements sm
                    JOIN inventory_items ii ON sm.item_id = ii.id
                    LEFT JOIN users u ON sm.created_by = u.id
                    ORDER BY sm.movement_date DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
            
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Error as e:
            print(f"[MODEL ERROR] get_stock_movements: {e}")
            return []