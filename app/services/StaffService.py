from mysql.connector import Error
from app.models.entities import User
from app.exceptions import ValidationError, NotFoundError, DatabaseError


class StaffService:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, full_name, username, role, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            return [self._map_row_to_user(row) for row in results]
        except Error as e:
            raise DatabaseError(f"Failed to fetch staff: {str(e)}")

    def create_staff(self, full_name, username, password, role):
        self._validate_staff_data(full_name, username, password, role)
        
        if not full_name:
            raise ValidationError("Full name is required")
        
        if len(password) < 4:
            raise ValidationError("Password must be at least 4 characters")
        
        if role not in ["cashier", "admin"]:
            raise ValidationError("Role must be 'cashier' or 'admin'")
        
        try:
            cursor = self.db.cursor()
            query = """
            INSERT INTO users (full_name, username, password, role)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, username, password, role))
            self.db.commit()
            staff_id = cursor.lastrowid
            cursor.close()
            return self.get_by_id(staff_id)
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create staff: {str(e)}")

    def update_staff(self, staff_id, full_name, username, password, role):
        self._validate_staff_data(full_name, username, password, role, allow_empty_password=True)
        
        if not full_name:
            raise ValidationError("Full name is required")
        
        if password and len(password) < 4:
            raise ValidationError("Password must be at least 4 characters")
        
        if role not in ["cashier", "admin"]:
            raise ValidationError("Role must be 'cashier' or 'admin'")
        
        existing = self.get_by_id(staff_id)
        if not existing:
            raise NotFoundError(f"Staff member with ID {staff_id} not found")
        
        try:
            cursor = self.db.cursor()
            if password:
                query = """
                UPDATE users SET 
                    full_name=%s, username=%s, password=%s, role=%s
                WHERE id=%s
                """
                params = (full_name, username, password, role, staff_id)
            else:
                query = """
                UPDATE users SET 
                    full_name=%s, username=%s, role=%s
                WHERE id=%s
                """
                params = (full_name, username, role, staff_id)
            
            cursor.execute(query, params)
            self.db.commit()
            cursor.close()
            return self.get_by_id(staff_id)
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update staff: {str(e)}")

    def delete_staff(self, staff_id):
        existing = self.get_by_id(staff_id)
        if not existing:
            raise NotFoundError(f"Staff member with ID {staff_id} not found")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM users WHERE id=%s", (staff_id,))
            self.db.commit()
            cursor.close()
            return True
        except Error as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete staff: {str(e)}")

    def get_by_id(self, staff_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, full_name, username, role, created_at
                FROM users
                WHERE id=%s
            """, (staff_id,))
            result = cursor.fetchone()
            cursor.close()
            return self._map_row_to_user(result) if result else None
        except Error as e:
            raise DatabaseError(f"Failed to get staff: {str(e)}")

    def _validate_staff_data(self, full_name, username, password, role, allow_empty_password=False):
        if not username or not username.strip():
            raise ValidationError("Username is required")
        
        if not password and not allow_empty_password:
            raise ValidationError("Password is required")

    def _map_row_to_user(self, row):
        if not row:
            return None
        return User(
            id=row[0],
            full_name=row[1],
            username=row[2],
            role=row[3],
            created_at=row[4] if len(row) > 4 else None
        )
