from mysql.connector import Error
from app.models.entities import Supplier
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.security.encryption import DataEncryption
import logging


class SupplierService:
    def __init__(self, db):
        self.db = db
        self.encryption = DataEncryption()
        self.logger = logging.getLogger('INVENTORY_UPDATED')  # Supplier data affects inventory

    def fetch_all(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, contact_person, address, created_at, 
                       email_encrypted, phone_encrypted, data_encrypted
                FROM suppliers
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            return [self._map_row_to_supplier(row) for row in results]
        except Error as e:
            self.logger.error(f"Failed to fetch suppliers: {str(e)}")
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

    def create_supplier(self, name, contact_person=None, email=None, phone=None, address=None, performed_by=None):
        if not name or not name.strip():
            raise ValidationError("Supplier name is required")
        
        try:
            # Encrypt sensitive data
            encrypted_phone = None
            encrypted_email = None
            
            if phone:
                encrypted_phone = self.encryption.encrypt(phone)
                self.logger.info(f"Phone encrypted for supplier: {name}")
            
            if email:
                encrypted_email = self.encryption.encrypt(email)
                self.logger.info(f"Email encrypted for supplier: {name}")
            
            cursor = self.db.cursor()
            query = """
            INSERT INTO suppliers (name, contact_person, address, email_encrypted, phone_encrypted, data_encrypted)
            VALUES (%s, %s, %s, %s, %s, 1)
            """
            cursor.execute(query, (name, contact_person, address, encrypted_email, encrypted_phone))
            self.db.commit()
            supplier_id = cursor.lastrowid
            cursor.close()
            if performed_by:
                self.logger.info(f"Supplier created with ID {supplier_id}: {name} - Username: {performed_by}")
            else:
                self.logger.info(f"Supplier created with ID {supplier_id}: {name}")
            return self.get_by_id(supplier_id)
        except Error as e:
            self.db.rollback()
            self.logger.error(f"Failed to create supplier: {str(e)}")
            raise DatabaseError(f"Failed to create supplier: {str(e)}")

    def update_supplier(self, supplier_id, name, contact_person=None, email=None, phone=None, address=None, performed_by=None):
        if not name or not name.strip():
            raise ValidationError("Supplier name is required")
        
        existing = self.get_by_id(supplier_id)
        if not existing:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")
        
        try:
            # Encrypt sensitive data
            encrypted_phone = None
            encrypted_email = None
            
            if phone:
                encrypted_phone = self.encryption.encrypt(phone)
                self.logger.info(f"Phone encrypted for supplier update: {name}")
            
            if email:
                encrypted_email = self.encryption.encrypt(email)
                self.logger.info(f"Email encrypted for supplier update: {name}")
            
            cursor = self.db.cursor()
            query = """
            UPDATE suppliers SET 
                name=%s, contact_person=%s, address=%s,
                email_encrypted=%s, phone_encrypted=%s, data_encrypted=1
            WHERE id=%s
            """
            cursor.execute(query, (name, contact_person, address, encrypted_email, encrypted_phone, supplier_id))
            self.db.commit()
            cursor.close()
            if performed_by:
                self.logger.info(f"Supplier updated: {name} (ID: {supplier_id}) - Username: {performed_by}")
            else:
                self.logger.info(f"Supplier updated: {name} (ID: {supplier_id})")
            return self.get_by_id(supplier_id)
        except Error as e:
            self.db.rollback()
            self.logger.error(f"Failed to update supplier: {str(e)}")
            raise DatabaseError(f"Failed to update supplier: {str(e)}")

    def delete_supplier(self, supplier_id, performed_by=None):
        existing = self.get_by_id(supplier_id)
        if not existing:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
            self.db.commit()
            cursor.close()
            if performed_by:
                self.logger.info(f"Supplier deleted: ID {supplier_id} - Username: {performed_by}")
            else:
                self.logger.info(f"Supplier deleted: ID {supplier_id}")
            return True
        except Error as e:
            self.db.rollback()
            self.logger.error(f"Failed to delete supplier: {str(e)}")
            raise DatabaseError(f"Failed to delete supplier: {str(e)}")

    def get_by_id(self, supplier_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, contact_person, address, created_at,
                       email_encrypted, phone_encrypted, data_encrypted
                FROM suppliers
                WHERE id=%s
            """, (supplier_id,))
            result = cursor.fetchone()
            cursor.close()
            return self._map_row_to_supplier(result) if result else None
        except Error as e:
            self.logger.error(f"Failed to get supplier: {str(e)}")
            raise DatabaseError(f"Failed to get supplier: {str(e)}")

    def _map_row_to_supplier(self, row):
        if not row:
            return None
        
        # Extract fields from row (no longer includes plaintext email/phone columns)
        supplier_id = row[0]
        name = row[1]
        contact_person = row[2]
        address = row[3]
        created_at = row[4] if len(row) > 4 else None
        email_encrypted = row[5] if len(row) > 5 else None
        phone_encrypted = row[6] if len(row) > 6 else None
        data_encrypted = row[7] if len(row) > 7 else False
        
        email = None
        phone = None
        
        # Decrypt from encrypted columns
        if data_encrypted and email_encrypted:
            try:
                email = self.encryption.decrypt(email_encrypted)
            except Exception as e:
                self.logger.warning(f"Failed to decrypt email for supplier {supplier_id}: {str(e)}")
        
        if data_encrypted and phone_encrypted:
            try:
                phone = self.encryption.decrypt(phone_encrypted)
            except Exception as e:
                self.logger.warning(f"Failed to decrypt phone for supplier {supplier_id}: {str(e)}")
        
        return Supplier(
            id=supplier_id,
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            created_at=created_at
        )
