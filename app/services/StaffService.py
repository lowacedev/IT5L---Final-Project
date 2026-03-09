from mysql.connector import Error
from app.models.entities import User
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.security.password_manager import PasswordManager
from app.security.input_validator import InputValidator
import logging


logger = logging.getLogger(__name__)


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

    def create_staff(self, full_name, username, password, role, performed_by=None):
        """Create a new staff member with proper validation and password hashing"""
        # Validate input
        self._validate_staff_data(full_name, username, password)
        
        if not full_name or len(full_name.strip()) < 2:
            raise ValidationError("Full name must be at least 2 characters")
        
        # Validate password strength
        is_valid, msg = PasswordManager.validate_password_strength(password)
        if not is_valid:
            raise ValidationError(msg)
        
        if role not in ["cashier", "admin"]:
            raise ValidationError("Role must be 'cashier' or 'admin'")
        
        try:
            # Check if username already exists
            cursor = self.db.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                raise ValidationError(f"Username '{username}' already exists")
            
            # Hash the password
            hashed_password = PasswordManager.hash_password(password)
            
            # Insert with all security fields
            query = """
            INSERT INTO users (full_name, username, password, role, is_active, failed_login_attempts)
            VALUES (%s, %s, %s, %s, 1, 0)
            """
            cursor.execute(query, (full_name, username, hashed_password, role))
            self.db.commit()
            staff_id = cursor.lastrowid
            cursor.close()
            
            # Log with USER_CREATED event type
            from app.utils.logger import get_logger
            create_logger = get_logger('USER_CREATED')
            if performed_by:
                create_logger.info(f"Staff member created: {username} (ID: {staff_id}) - Username: {performed_by}")
            else:
                create_logger.info(f"Staff member created: {username} (ID: {staff_id})")
            return self.get_by_id(staff_id)
        except ValidationError:
            raise
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to create staff: {str(e)}")
            raise DatabaseError(f"Failed to create staff: {str(e)}")

    def update_staff(self, staff_id, full_name, username, password, role, performed_by=None):
        """Update staff member with password hashing if password provided"""
        self._validate_staff_data(full_name, username, password, allow_empty_password=True)
        
        if not full_name or len(full_name.strip()) < 2:
            raise ValidationError("Full name must be at least 2 characters")
        
        # Validate password strength if provided
        if password:
            is_valid, msg = PasswordManager.validate_password_strength(password)
            if not is_valid:
                raise ValidationError(msg)
        
        if role not in ["cashier", "admin"]:
            raise ValidationError("Role must be 'cashier' or 'admin'")
        
        existing = self.get_by_id(staff_id)
        if not existing:
            raise NotFoundError(f"Staff member with ID {staff_id} not found")
        
        try:
            cursor = self.db.cursor()
            
            # Check if new username already exists (and is not the same staff member)
            cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (username, staff_id))
            if cursor.fetchone():
                cursor.close()
                raise ValidationError(f"Username '{username}' already exists")
            
            if password:
                # Hash the password
                hashed_password = PasswordManager.hash_password(password)
                query = """
                UPDATE users SET 
                    full_name=%s, username=%s, password=%s, role=%s
                WHERE id=%s
                """
                params = (full_name, username, hashed_password, role, staff_id)
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
            
            # Log with USER_CREATED event type (treating update similar to creation for tracking)
            from app.utils.logger import get_logger
            update_logger = get_logger('USER_CREATED')
            if performed_by:
                update_logger.info(f"Staff member updated: {username} (ID: {staff_id}) - Username: {performed_by}")
            else:
                update_logger.info(f"Staff member updated: {username} (ID: {staff_id})")
            return self.get_by_id(staff_id)
        except ValidationError:
            raise
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to update staff: {str(e)}")
            raise DatabaseError(f"Failed to update staff: {str(e)}")

    def delete_staff(self, staff_id, performed_by=None):
        existing = self.get_by_id(staff_id)
        if not existing:
            raise NotFoundError(f"Staff member with ID {staff_id} not found")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM users WHERE id=%s", (staff_id,))
            self.db.commit()
            cursor.close()
            
            # Log with USER_DELETED event type
            from app.utils.logger import get_logger
            delete_logger = get_logger('USER_DELETED')
            if performed_by:
                delete_logger.info(f"Staff member deleted: ID {staff_id} - Username: {performed_by}")
            else:
                delete_logger.info(f"Staff member deleted: ID {staff_id}")
            return True
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to delete staff: {str(e)}")
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

    def _validate_staff_data(self, full_name, username, password, allow_empty_password=False):
        """Validate staff data before creating/updating"""
        if not username or not username.strip():
            raise ValidationError("Username is required")
        
        # Validate username format
        is_valid, msg = InputValidator.validate_username(username)
        if not is_valid:
            raise ValidationError(f"Invalid username: {msg}")
        
        if not password and not allow_empty_password:
            raise ValidationError("Password is required")
        
        if not full_name or not full_name.strip():
            raise ValidationError("Full name is required")

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
