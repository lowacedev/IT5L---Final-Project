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