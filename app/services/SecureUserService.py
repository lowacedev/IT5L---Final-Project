"""
Secure User Service
Handles user authentication, registration, and password management with security features.
"""

from datetime import datetime, timedelta
import hashlib
from app.security.password_manager import PasswordManager
from app.security.input_validator import InputValidator
from app.security.rbac import get_session_manager, UserRole
from app.utils.logger import get_logger, SecurityAuditLogger
from app.core.db import get_db

logger = get_logger(__name__)

class LoginAttemptTracker:
    """Tracks login attempts in database to prevent brute force attacks"""
    
    def __init__(self, db):
        self.db = db
    
    def record_attempt(self, username: str, success: bool, reason: str = None):
        """Record login attempt in database"""
        try:
            cursor = self.db.cursor()
            
            # Insert into login_attempts table
            insert_query = """
                INSERT INTO login_attempts (username, success, reason)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (username, success, reason))
            
            # Update user record with latest attempt timestamp
            if not success:
                # Failed attempt: increment counter and update timestamp
                update_query = """
                    UPDATE users 
                    SET failed_login_attempts = failed_login_attempts + 1,
                        last_login_attempt = NOW()
                    WHERE username = %s
                """
                cursor.execute(update_query, (username,))
            else:
                # Successful login: clear counter, update timestamp, clear locked_until
                clear_query = """
                    UPDATE users 
                    SET failed_login_attempts = 0,
                        last_login_attempt = NOW(),
                        locked_until = NULL
                    WHERE username = %s
                """
                cursor.execute(clear_query, (username,))
            
            self.db.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Failed to record login attempt for {username}: {str(e)}")
            try:
                self.db.rollback()
            except:
                pass
    
    def get_failed_attempts(self, username: str, minutes: int = 60) -> int:
        """Get number of failed attempts in last N minutes from database"""
        try:
            cursor = self.db.cursor()
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            query = """
                SELECT COUNT(*) as count
                FROM login_attempts
                WHERE username = %s AND success = 0 AND attempt_time > %s
            """
            cursor.execute(query, (username, cutoff_time))
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Failed to get login attempts for {username}: {str(e)}")
            return 0
    
    def is_account_locked(self, username: str, max_attempts: int = 5, lockout_minutes: int = 15) -> bool:
        """Check if account is locked based on recent failed attempts"""
        failed_attempts = self.get_failed_attempts(username, lockout_minutes)
        is_locked = failed_attempts >= max_attempts
        
        if is_locked:
            # Set locked_until timestamp
            self._set_account_locked(username, lockout_minutes)
            logger.warning(f"Account {username} is locked due to {failed_attempts} failed attempts")
            SecurityAuditLogger.log_account_lockout(username, f"Failed {failed_attempts} attempts in last {lockout_minutes} minutes")
        
        return is_locked
    
    def _set_account_locked(self, username: str, lockout_minutes: int):
        """Set the locked_until timestamp for an account"""
        try:
            cursor = self.db.cursor()
            locked_until = datetime.now() + timedelta(minutes=lockout_minutes)
            
            update_query = """
                UPDATE users
                SET locked_until = %s
                WHERE username = %s
            """
            cursor.execute(update_query, (locked_until, username))
            self.db.commit()
            cursor.close()
            logger.info(f"Account {username} locked until {locked_until}")
        except Exception as e:
            logger.error(f"Failed to set locked_until for {username}: {str(e)}")
            try:
                self.db.rollback()
            except:
                pass


class SecureUserService:
    """Secure user service with authentication and authorization"""
    
    def __init__(self, db):
        self.db = db
        self.login_tracker = LoginAttemptTracker(db)
    
    def authenticate(self, username: str, password: str) -> dict:
        """
        Authenticate user with username and password.
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            username (str): Username
            password (str): Plain text password
            
        Returns:
            dict: User data if authenticated, None otherwise
        """
        # Validate inputs
        is_valid, msg = InputValidator.validate_username(username)
        if not is_valid:
            logger.warning(f"Invalid username format: {username}")
            return None
        
        if not password:
            logger.warning(f"Empty password attempt for user: {username}")
            self.login_tracker.record_attempt(username, False, reason="Empty password")
            return None
        
        # Check if account is locked
        from app.security.config import SecurityConfig
        lockout_minutes = SecurityConfig.LOGIN_LOCKOUT_DURATION // 60
        
        if self.login_tracker.is_account_locked(
            username,
            SecurityConfig.MAX_LOGIN_ATTEMPTS,
            lockout_minutes
        ):
            self.login_tracker.record_attempt(username, False, reason="Account locked")
            return None
        
        try:
            # Use parameterized query to prevent SQL injection
            cursor = self.db.cursor(dictionary=True)
            
            # Query only username and password hash (and required fields)
            query = """
                SELECT id, username, full_name, role, password, is_active, created_at
                FROM users
                WHERE username = %s
            """
            
            # Execute with parameterized query
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                # Verify password
                if PasswordManager.verify_password(password, result['password']):
                    if result['is_active']:
                        # Login successful
                        self.login_tracker.record_attempt(username, True, reason="Successful login")
                        SecurityAuditLogger.log_login_attempt(username, True)
                        logger.info(f"User {username} logged in successfully")
                        
                        # Return user data (without password)
                        return {
                            'id': result['id'],
                            'username': result['username'],
                            'full_name': result['full_name'],
                            'role': result['role'],
                        }
                    else:
                        # Account is inactive
                        self.login_tracker.record_attempt(username, False, reason="Account inactive")
                        SecurityAuditLogger.log_login_attempt(username, False, reason="Account inactive")
                        logger.warning(f"Login attempt for inactive account: {username}")
                        return None
                else:
                    # Password mismatch
                    self.login_tracker.record_attempt(username, False, reason="Invalid password")
                    SecurityAuditLogger.log_login_attempt(username, False, reason="Invalid password")
                    logger.warning(f"Invalid password attempt for user: {username}")
                    return None
            else:
                # User not found
                self.login_tracker.record_attempt(username, False, reason="User not found")
                SecurityAuditLogger.log_login_attempt(username, False, reason="User not found")
                logger.warning(f"Login attempt for non-existent user: {username}")
                return None
            
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {str(e)[:100]}")
            SecurityAuditLogger.log_system_error("AUTH_ERROR", str(e), username)
            return None
    
    def register_user(self, username: str, password: str, full_name: str, role: str = 'cashier') -> dict:
        """
        Register a new user with password hashing.
        
        Args:
            username (str): Username
            password (str): Plain text password
            full_name (str): Full name
            role (str): User role (admin, manager, cashier)
            
        Returns:
            dict: Result with success status and message
        """
        # Validate inputs
        username_valid, username_msg = InputValidator.validate_username(username)
        if not username_valid:
            return {'success': False, 'message': username_msg}
        
        password_valid, password_msg = PasswordManager.validate_password_strength(password)
        if not password_valid:
            return {'success': False, 'message': password_msg}
        
        if not full_name or len(full_name) < 2:
            return {'success': False, 'message': 'Full name must be at least 2 characters'}
        
        # Validate role
        try:
            UserRole(role)
        except ValueError:
            return {'success': False, 'message': 'Invalid role'}
        
        try:
            cursor = self.db.cursor()
            
            # Check if user already exists (using parameterized query)
            query = "SELECT id FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            if cursor.fetchone():
                cursor.close()
                return {'success': False, 'message': 'Username already exists'}
            
            # Hash password
            hashed_password = PasswordManager.hash_password(password)
            
            # Insert new user (using parameterized query)
            insert_query = """
                INSERT INTO users (username, password, full_name, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, 1, NOW())
            """
            
            cursor.execute(insert_query, (username, hashed_password, full_name, role))
            self.db.commit()
            cursor.close()
            
            logger.info(f"New user registered: {username} with role: {role}")
            SecurityAuditLogger.log_user_action('system', 'create_user', f'Created user: {username}')
            
            return {'success': True, 'message': 'User registered successfully'}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"User registration error: {str(e)[:100]}")
            return {'success': False, 'message': 'Registration failed. Please try again.'}
    
    def change_password(self, username: str, old_password: str, new_password: str) -> dict:
        """
        Change user password with validation.
        
        Args:
            username (str): Username
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            dict: Result with success status and message
        """
        # Validate new password
        is_valid, msg = PasswordManager.validate_password_strength(new_password)
        if not is_valid:
            return {'success': False, 'message': msg}
        
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Get user's current password hash
            query = "SELECT id, password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                return {'success': False, 'message': 'User not found'}
            
            # Verify old password
            if not PasswordManager.verify_password(old_password, result['password']):
                cursor.close()
                SecurityAuditLogger.log_password_change(username, False)
                return {'success': False, 'message': 'Current password is incorrect'}
            
            # Hash new password
            new_hashed = PasswordManager.hash_password(new_password)
            
            # Update password
            update_query = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(update_query, (new_hashed, result['id']))
            self.db.commit()
            cursor.close()
            
            logger.info(f"Password changed for user: {username}")
            SecurityAuditLogger.log_password_change(username, True)
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Password change error: {str(e)[:100]}")
            SecurityAuditLogger.log_system_error("PASSWORD_CHANGE_ERROR", str(e), username)
            return {'success': False, 'message': 'Password change failed'}
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user data by ID using parameterized query"""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = "SELECT id, username, full_name, role, is_active FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)[:100]}")
            return None
    
    def get_all_users(self) -> list:
        """Get all users (admin only - should be checked by controller)"""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = "SELECT id, username, full_name, role, is_active, created_at FROM users ORDER BY created_at DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)[:100]}")
            return []


# Example usage
if __name__ == "__main__":
    from app.core.db import get_db
    
    db = get_db()
    user_service = SecureUserService(db)
    
    # Test registration
    result = user_service.register_user('testuser', 'TestPass123!', 'Test User', 'cashier')
    print(f"Registration: {result}")
    
    # Test authentication
    user = user_service.authenticate('testuser', 'TestPass123!')
    print(f"Authentication: {user}")
    
    db.close()
