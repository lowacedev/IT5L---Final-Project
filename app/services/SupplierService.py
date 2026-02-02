from mysql.connector import Error
from app.models.entities import Supplier
from app.exceptions import ValidationError, NotFoundError, DatabaseError


class SupplierService:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, contact_person, email, phone, address, created_at
                FROM suppliers
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            return [self._map_row_to_supplier(row) for row in results]
        except Error as e:
            raise DatabaseError(f"Failed to fetch suppliers: {str(e)}")

    def get_name_by_id(self, supplier_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT name FROM suppliers WHERE id = %s", (supplier_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            raise DatabaseError(f"Failed to get supplier name: {str(e)}")

    def get_id_by_name(self, supplier_name):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT id FROM suppliers WHERE name = %s", (supplier_name,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            raise DatabaseError(f"Failed to get supplier ID: {str(e)}")

    def create_supplier(self, name, contact_person=None, email=None, phone=None, address=None):
        if not name or not name.strip():
            raise ValidationError("Supplier name is required")
        
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
            return self.get_by_id(supplier_id)
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create supplier: {str(e)}")

    def update_supplier(self, supplier_id, name, contact_person=None, email=None, phone=None, address=None):
        if not name or not name.strip():
            raise ValidationError("Supplier name is required")
        
        existing = self.get_by_id(supplier_id)
        if not existing:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")
        
        try:
            cursor = self.db.cursor()
            query = """
            UPDATE suppliers SET 
                name=%s, contact_person=%s, email=%s, phone=%s, address=%s
            WHERE id=%s
            """
            cursor.execute(query, (name, contact_person, email, phone, address, supplier_id))
            self.db.commit()
            cursor.close()
            return self.get_by_id(supplier_id)
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update supplier: {str(e)}")

    def delete_supplier(self, supplier_id):
        existing = self.get_by_id(supplier_id)
        if not existing:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
            self.db.commit()
            cursor.close()
            return True
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete supplier: {str(e)}")

    def get_by_id(self, supplier_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, contact_person, email, phone, address, created_at
                FROM suppliers
                WHERE id=%s
            """, (supplier_id,))
            result = cursor.fetchone()
            cursor.close()
            return self._map_row_to_supplier(result) if result else None
        except Error as e:
            raise DatabaseError(f"Failed to get supplier: {str(e)}")

    def _map_row_to_supplier(self, row):
        if not row:
            return None
        return Supplier(
            id=row[0],
            name=row[1],
            contact_person=row[2],
            email=row[3],
            phone=row[4],
            address=row[5],
            created_at=row[6] if len(row) > 6 else None
        )
