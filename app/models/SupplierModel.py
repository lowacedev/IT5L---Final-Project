from mysql.connector import Error


class SupplierModel:
    """Model for managing suppliers."""

    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        """Fetch all suppliers with full details."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, contact_person, email, phone, address, created_at
                FROM suppliers
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            print(f"[SUPPLIER MODEL] Fetched {len(results)} suppliers: {results}")
            return results
        except Error as e:
            print(f"[SUPPLIER MODEL ERROR] fetch_all: {e}")
            return []

    def get_name_by_id(self, supplier_id):
        """Get supplier name by ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT name FROM suppliers WHERE id = %s", (supplier_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            print(f"[MODEL ERROR] get_name_by_id: {e}")
            return None

    def get_id_by_name(self, supplier_name):
        """Get supplier ID by name."""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT id FROM suppliers WHERE name = %s", (supplier_name,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            print(f"[MODEL ERROR] get_id_by_name: {e}")
            return None

    def create_supplier(self, name, contact_person=None, email=None, phone=None, address=None):
        """Create a new supplier."""
        try:
            cursor = self.db.cursor()
            query = """
            INSERT INTO suppliers (name, contact_person, email, phone, address)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, contact_person, email, phone, address))
            self.db.commit()
            supplier_id = cursor.lastrowid
            cursor.close()
            print(f"[SUPPLIER MODEL] Created supplier with ID: {supplier_id}")
            return supplier_id
        except Error as e:
            self.db.rollback()
            print(f"[SUPPLIER MODEL ERROR] create_supplier: {e}")
            raise e

    def update_supplier(self, supplier_id, name, contact_person=None, email=None, phone=None, address=None):
        """Update an existing supplier."""
        try:
            cursor = self.db.cursor()
            query = """
            UPDATE suppliers SET 
                name=%s, contact_person=%s, email=%s, phone=%s, address=%s
            WHERE id=%s
            """
            cursor.execute(query, (name, contact_person, email, phone, address, supplier_id))
            self.db.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            print(f"[SUPPLIER MODEL] Updated {rows_affected} row(s)")
            return rows_affected > 0
        except Error as e:
            self.db.rollback()
            print(f"[SUPPLIER MODEL ERROR] update_supplier: {e}")
            raise e

    def delete_supplier(self, supplier_id):
        """Delete a supplier."""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
            self.db.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            print(f"[SUPPLIER MODEL] Deleted {rows_affected} row(s)")
            return rows_affected > 0
        except Error as e:
            self.db.rollback()
            print(f"[SUPPLIER MODEL ERROR] delete_supplier: {e}")
            raise e

    def get_by_id(self, supplier_id):
        """Get a single supplier by ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, contact_person, email, phone, address, created_at
                FROM suppliers
                WHERE id=%s
            """, (supplier_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"[SUPPLIER MODEL ERROR] get_by_id: {e}")
            return None