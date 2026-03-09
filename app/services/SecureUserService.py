"""
Secure User Service
Handles user authentication, registration, and password management with security features.
"""

from datetime import datetime, timedelta
import secrets
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
            # Check if connection is still valid
            try:
                if not self.db.is_connected():
                    logger.warning("record_attempt: Connection not connected, reconnecting...")
                    self.db.reconnect()
            except Exception as e:
                logger.warning(f"record_attempt: Connection check failed: {str(e)}, getting new connection")
                self.db = get_db()
            
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
            except Exception:
                pass
    
    def get_failed_attempts(self, username: str, minutes: int = 60) -> int:
        """Get number of failed attempts in last N minutes from database"""
        cursor = None
        try:
            # Check if connection is still valid
            try:
                logger.info(f"get_failed_attempts: Checking connection for {username}")
                if not self.db.is_connected():
                    logger.warning("get_failed_attempts: Connection is not connected, reconnecting...")
                    self.db.reconnect()
                    logger.info("get_failed_attempts: Reconnected to database")
            except Exception as e:
                logger.warning(f"get_failed_attempts: Connection check failed: {str(e)}, getting new connection")
                # If reconnection fails, get a fresh connection
                self.db = get_db()
                logger.info("get_failed_attempts: Got fresh database connection")
            
            # Now try to get the cursor
            logger.info(f"get_failed_attempts: Creating cursor for {username}")
            cursor = self.db.cursor()
            logger.info(f"get_failed_attempts: Cursor created, type={type(cursor)}")
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            logger.info("get_failed_attempts: Cutoff time calculated")
            
            query = """
                SELECT COUNT(*) as attempt_count
                FROM login_attempts
                WHERE username = %s AND success = 0 AND attempt_time > %s
            """
            logger.info("get_failed_attempts: Executing query")
            cursor.execute(query, (username, cutoff_time))
            logger.info("get_failed_attempts: Query executed")
            
            result = cursor.fetchone()
            logger.info(f"get_failed_attempts: fetchone() returned, result={result}, type={type(result)}")
            
            # Access as tuple (first element is the count)
            if result:
                # Try to handle different result types
                if isinstance(result, (list, tuple)):
                    count = int(result[0])
                    logger.info(f"get_failed_attempts: Returning count={count} from tuple/list")
                    return count
                elif isinstance(result, dict):
                    # If for some reason we got a dict, extract the first value
                    count = int(result.get('attempt_count', 0))
                    logger.info(f"get_failed_attempts: Returning count={count} from dict")
                    return count
                else:
                    logger.warning(f"Unexpected result type: {type(result)}, attempting conversion")
                    count = int(result)
                    logger.info(f"get_failed_attempts: Returning count={count} from direct conversion")
                    return count
            logger.info("get_failed_attempts: Result is None, returning 0")
            return 0
        except Exception as e:
            logger.error(f"Failed to get login attempts for {username}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return 0
        finally:
            if cursor:
                try:
                    cursor.close()
                    logger.info("get_failed_attempts: Cursor closed")
                except Exception as e:
                    logger.error(f"get_failed_attempts: Error closing cursor: {str(e)}")
    
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
            except Exception:
                pass


class SessionManager:
    """Manages user sessions for tracking active logins"""
    
    def __init__(self, db):
        self.db = db
    
    def create_session(self, user_id: int, username: str, ip_address: str = "127.0.0.1", user_agent: str = None) -> "str | None":
        """
        Create a new user session in database.
        
        Args:
            user_id: User ID
            username: Username
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            session_token: Generated session token or None if failed
        """
        try:
            # Generate unique session token
            session_token = secrets.token_urlsafe(64)
            
            cursor = self.db.cursor()
            query = """
                INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, login_time, is_active)
                VALUES (%s, %s, %s, %s, NOW(), 1)
            """
            cursor.execute(query, (user_id, session_token, ip_address, user_agent))
            self.db.commit()
            cursor.close()
            
            logger.info(f"Session created for user {username} (ID: {user_id})")
            SecurityAuditLogger.log_user_action(username, 'session_created', f'New session from IP: {ip_address}')
            
            return session_token
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {str(e)}")
            try:
                self.db.rollback()
            except Exception:
                pass
            return None  # type: ignore
    
    def close_session(self, user_id: int, session_token: str) -> bool:
        """
        Close a user session.
        
        Args:
            user_id: User ID
            session_token: Session token
            
        Returns:
            bool: Success status
        """
        try:
            cursor = self.db.cursor()
            query = """
                UPDATE user_sessions
                SET is_active = 0, logout_time = NOW()
                WHERE user_id = %s AND session_token = %s
            """
            cursor.execute(query, (user_id, session_token))
            self.db.commit()
            cursor.close()
            
            logger.info(f"Session closed for user ID: {user_id}")
            SecurityAuditLogger.log_user_action('user', 'session_closed', 'Session logged out')
            
            return True
        except Exception as e:
            logger.error(f"Failed to close session for user {user_id}: {str(e)}")
            try:
                self.db.rollback()
            except Exception:
                pass
            return False
    
    def get_active_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
                SELECT id, session_token, ip_address, login_time, last_activity
                FROM user_sessions
                WHERE user_id = %s AND is_active = 1
            """
            cursor.execute(query, (user_id,))
            sessions = cursor.fetchall()
            cursor.close()
            return sessions if sessions else []
        except Exception as e:
            logger.error(f"Failed to get active sessions for user {user_id}: {str(e)}")
            return []


class SecureUserService:
    """Secure user service with authentication and authorization"""
    
    def __init__(self, db):
        self.db = db
        self.login_tracker = LoginAttemptTracker(db)
        self.session_manager = SessionManager(db)
    
    def _validate_auth_inputs(self, username: str, password: str) -> "bool":
        """Validate username and password inputs. Returns True if valid."""
        logger.info(f"[AUTH] Step 1: Validating username format for {username}")
        is_valid, _ = InputValidator.validate_username(username)
        if not is_valid:
            logger.warning(f"Invalid username format: {username}")
            return False
        
        if not password:
            logger.warning(f"Empty password attempt for user: {username}")
            self.login_tracker.record_attempt(username, False, reason="Empty password")
            return False
        
        return True
    
    def _check_account_locked(self, username: str) -> "bool":
        """Check if account is locked. Returns True if locked."""
        logger.info(f"[AUTH] Step 2: Checking if account is locked for {username}")
        from app.security.config import SecurityConfig
        lockout_minutes = SecurityConfig.LOGIN_LOCKOUT_DURATION // 60
        
        if self.login_tracker.is_account_locked(
            username,
            SecurityConfig.MAX_LOGIN_ATTEMPTS,
            lockout_minutes
        ):
            self.login_tracker.record_attempt(username, False, reason="Account locked")
            return True
        
        return False
    
    def _fetch_user_from_db(self, username: str) -> "dict | None":
        """Fetch user data from database."""
        logger.info(f"[AUTH] Step 3: Querying database for user {username}")
        cursor = None
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
                SELECT id, username, full_name, role, password, is_active, created_at
                FROM users
                WHERE username = %s
            """
            cursor.execute(query, (username,))
            logger.info(f"[AUTH] Step 3b: Query executed for {username}, fetching result")
            result = cursor.fetchone()
            logger.info("[AUTH] Step 3c: Result fetched, closing cursor")
            return result
        finally:
            if cursor:
                try:
                    cursor.close()
                    logger.info("[AUTH] Step 3d: Cursor closed, proceeding with password check")
                except Exception as e:
                    logger.error(f"[AUTH] Error closing cursor: {str(e)}")
    
    def _process_successful_login(self, result: dict, username: str, ip_address: str, user_agent: str) -> "dict | None":
        """Process successful login and create session."""
        if result['is_active']:
            logger.info(f"[AUTH] Step 5: User account is active, creating session for {username}")
            self.login_tracker.record_attempt(username, True, reason="Successful login")
            SecurityAuditLogger.log_login_attempt(username, True, ip_address=ip_address)
            logger.info(f"User {username} logged in successfully")
            
            session_token = self.session_manager.create_session(
                result['id'], username, ip_address, user_agent
            )
            logger.info(f"[AUTH] Step 5b: Session created, token={'***' if session_token else 'None'}")
            
            return {
                'id': result['id'],
                'username': result['username'],
                'full_name': result['full_name'],
                'role': result['role'],
                'session_token': session_token,
            }
        else:
            self.login_tracker.record_attempt(username, False, reason="Account inactive")
            SecurityAuditLogger.log_login_attempt(username, False, reason="Account inactive")
            logger.warning(f"Login attempt for inactive account: {username}")
            return None
    
    def authenticate(self, username: str, password: str, ip_address: str = "127.0.0.1", user_agent: str = None) -> "dict | None":
        """
        Authenticate user with username and password.
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            username (str): Username
            password (str): Plain text password
            ip_address (str): Client IP address
            user_agent (str): Client user agent
            
        Returns:
            dict: User data with session token if authenticated, None otherwise
        """
        import time
        start_time = time.time()
        
        try:
            if not self._validate_auth_inputs(username, password):
                return None  # type: ignore
            
            if self._check_account_locked(username):
                return None  # type: ignore
            
            result = self._fetch_user_from_db(username)
            
            if result:
                logger.info("[AUTH] Step 4: User found, verifying password")
                logger.info("[AUTH] Step 4a: Starting bcrypt password verification")
                password_valid = PasswordManager.verify_password(password, result['password'])
                logger.info(f"[AUTH] Step 4b: Password verification completed, result={password_valid}")
                
                if password_valid:
                    auth_result = self._process_successful_login(result, username, ip_address, user_agent)
                    if auth_result:
                        elapsed = time.time() - start_time
                        logger.info(f"[AUTH] Authentication completed for {username} in {elapsed:.2f}s")
                    return auth_result
                else:
                    self.login_tracker.record_attempt(username, False, reason="Invalid password")
                    SecurityAuditLogger.log_login_attempt(username, False, reason="Invalid password")
                    logger.warning(f"Invalid password attempt for user: {username}")
                    return None  # type: ignore
            else:
                self.login_tracker.record_attempt(username, False, reason="User not found")
                SecurityAuditLogger.log_login_attempt(username, False, reason="User not found")
                logger.warning(f"Login attempt for non-existent user: {username}")
                return None  # type: ignore
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Authentication error for user {username} (after {elapsed:.2f}s): {str(e)}")
            SecurityAuditLogger.log_system_error("AUTH_ERROR", str(e), username)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None  # type: ignore
    
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
    
    def get_user_by_id(self, user_id: int) -> "dict | None":
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
            return None  # type: ignore
    
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
