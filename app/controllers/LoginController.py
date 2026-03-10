import logging
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.CaptchaGenerator import CaptchaGenerator
from PyQt6.QtCore import QThread, pyqtSignal


class AuthenticationWorker(QThread):
    """Worker thread for authentication to prevent UI blocking"""
    
    authentication_complete = pyqtSignal(dict)  # Emits user dict if successful
    authentication_error = pyqtSignal(str)      # Emits error message
    validation_error = pyqtSignal(str)          # Emits validation error before auth
    
    def __init__(self, service, view, captcha_generator, username, password, captcha_input, ip_address="127.0.0.1"):
        super().__init__()
        self.service = service
        self.view = view
        self.captcha_generator = captcha_generator
        self.username = username
        self.password = password
        self.captcha_input = captcha_input
        self.ip_address = ip_address
        self.logger = logging.getLogger("AUTH_WORKER")
    
    def run(self):
        """Run all login validation and authentication in background thread"""
        self.logger.info(f"[WORKER] Starting authentication for {self.username}")
        
        try:
            from app.security.config import SecurityConfig
            from app.core.db import is_database_responsive
            
            # Step 0: Basic field validation (UI layer already checked, but double-check)
            self.logger.info("[WORKER] Step 0: Validating fields")
            if not self.username or not self.password or not self.captcha_input:
                self.logger.warning("[WORKER] Step 0 FAILED: Missing fields")
                self.validation_error.emit("Please enter username, password, and CAPTCHA code.")
                return
            
            if not self.username.strip():
                self.logger.warning("[WORKER] Step 0 FAILED: Empty username")
                self.validation_error.emit("Please enter a username.")
                return
            
            self.logger.info("[WORKER] Step 0 PASSED: All fields present")
            
            # Step 1: Check if account is locked (database operation - now off main thread!)
            self.logger.info("[WORKER] Step 1: Checking if account is locked")
            lockout_minutes = SecurityConfig.LOGIN_LOCKOUT_DURATION // 60
            try:
                is_locked = self.service.login_tracker.is_account_locked(
                    self.username,
                    SecurityConfig.MAX_LOGIN_ATTEMPTS,
                    lockout_minutes
                )
                self.logger.info(f"[WORKER] Step 1: Account locked = {is_locked}")
                
                if is_locked:
                    self.logger.warning(f"[WORKER] Step 1 FAILED: Account {self.username} is locked")
                    self.validation_error.emit(f"Account locked due to too many failed attempts. Try again in {lockout_minutes} minutes.")
                    return
            except Exception as e:
                self.logger.error(f"[WORKER] Step 1 ERROR: {str(e)}")
                self.authentication_error.emit(f"Error checking account status: {str(e)}")
                return
            
            self.logger.info("[WORKER] Step 1 PASSED: Account not locked")
            
            # Step 2: Validate CAPTCHA (now off main thread!)
            self.logger.info("[WORKER] Step 2: Validating CAPTCHA")
            try:
                captcha_valid = self.captcha_generator.validate(self.captcha_input)
                self.logger.info(f"[WORKER] Step 2: CAPTCHA valid = {captcha_valid}")
                
                if not captcha_valid:
                    self.logger.warning(f"[WORKER] Step 2 FAILED: Invalid CAPTCHA for {self.username}")
                    # Record CAPTCHA failure as login attempt (database op - now off main thread!)
                    try:
                        self.service.login_tracker.record_attempt(self.username, False, reason="Invalid CAPTCHA")
                        self.logger.info("[WORKER] Step 2: Recorded failed CAPTCHA attempt")
                    except Exception as e:
                        self.logger.error(f"[WORKER] Step 2: Failed to record attempt: {str(e)}")
                    
                    self.validation_error.emit("Invalid CAPTCHA code. Please try again.")
                    return
            except Exception as e:
                self.logger.error(f"[WORKER] Step 2 ERROR: {str(e)}")
                self.authentication_error.emit(f"Error validating CAPTCHA: {str(e)}")
                return
            
            self.logger.info("[WORKER] Step 2 PASSED: CAPTCHA valid")
            
            # Step 3: Check database connectivity (now off main thread!)
            self.logger.info("[WORKER] Step 3: Checking database connectivity")
            try:
                db_responsive = is_database_responsive(timeout_seconds=5)
                self.logger.info(f"[WORKER] Step 3: Database responsive = {db_responsive}")
                
                if not db_responsive:
                    self.logger.warning("[WORKER] Step 3 FAILED: Database not responsive")
                    self.validation_error.emit("Database is not responding. Please check your connection and try again.")
                    return
            except Exception as e:
                self.logger.error(f"[WORKER] Step 3 ERROR: {str(e)}")
                self.authentication_error.emit(f"Error checking database: {str(e)}")
                return
            
            self.logger.info("[WORKER] Step 3 PASSED: Database responsive")
            
            # Step 4: All validation passed, now authenticate
            self.logger.info("[WORKER] Step 4: Starting authentication")
            try:
                user = self.service.authenticate(
                    self.username,
                    self.password,
                    self.ip_address
                )
                self.logger.info(f"[WORKER] Step 4: Authentication returned user={user is not None}")
                
                if user:
                    self.logger.info(f"[WORKER] SUCCESS: User {self.username} authenticated")
                    self.authentication_complete.emit(user)
                else:
                    self.logger.warning(f"[WORKER] FAILED: Authentication returned None for {self.username}")
                    self.authentication_error.emit("Invalid username or password. Please check credentials and try again.")
            except Exception as e:
                self.logger.error(f"[WORKER] Step 4 ERROR: {str(e)}")
                import traceback
                self.logger.error(f"[WORKER] Traceback: {traceback.format_exc()}")
                self.authentication_error.emit(f"Authentication error: {str(e)}")
                return
                
        except Exception as e:
            self.logger.error(f"[WORKER] CRITICAL ERROR: {str(e)}")
            import traceback
            self.logger.error(f"[WORKER] Traceback: {traceback.format_exc()}")
            # Emit error signal with exception details
            error_msg = f"Login error: {str(e)}"
            self.authentication_error.emit(error_msg)


class LoginController:
    def __init__(self, service, view):
        self.service = service
        self.view = view
        self.captcha_generator = CaptchaGenerator()
        self.logger = logging.getLogger(__name__)
        self.auth_worker = None  # Will hold authentication worker thread
        
        # Connect signals
        view.btn_login.clicked.connect(self.handle_login)
        view.btn_refresh_captcha.clicked.connect(self.refresh_captcha)
        
        # Also connect dialog close to cleanup
        view.finished.connect(self.cleanup)
        
        # Generate initial CAPTCHA
        self.generate_new_captcha()
    
    def generate_new_captcha(self):
        """Generate a new CAPTCHA and display it"""
        try:
            # Generate CAPTCHA image and save to temp file
            image_path = self.captcha_generator.generate_image_file()
            
            # Display CAPTCHA image in view
            self.view.set_captcha_image(image_path)
            
            # Clear previous CAPTCHA input
            self.view.clear_captcha_input()
            
            self.logger.info("New CAPTCHA generated")
        except Exception as e:
            self.logger.error(f"Failed to generate CAPTCHA: {str(e)}")
            self.view.show_error(f"Failed to generate CAPTCHA: {str(e)}")
    
    def refresh_captcha(self):
        """Handle refresh CAPTCHA button click"""
        self.generate_new_captcha()

    def handle_login(self):
        """Handle login button click - minimal work on main thread"""
        try:
            # If a login is already in progress, don't allow another one
            if self.auth_worker is not None and self.auth_worker.isRunning():
                self.logger.warning("Login already in progress, ignoring duplicate click")
                return
            
            username, password, captcha_input = self.view.collect_form_data()
            
            # Only check if fields exist on main thread (fast check)
            # All other validation happens in worker thread
            if not username or not password or not captcha_input:
                self.view.show_warning("Please enter username, password, and CAPTCHA code.")
                return
            
            self.logger.info(f"Starting login process for user: {username}")
            
            # Disable login button to prevent multiple submissions
            self.view.btn_login.setEnabled(False)
            self.view.btn_login.setText("Logging in...")
            
            # Create and start authentication worker thread
            # Worker will handle ALL validation and authentication off the main thread
            self.auth_worker = AuthenticationWorker(
                self.service,
                self.view,
                self.captcha_generator,
                username,
                password,
                captcha_input,
                "127.0.0.1"
            )
            
            # Connect worker signals
            self.auth_worker.validation_error.connect(self.on_validation_error)
            self.auth_worker.authentication_complete.connect(self.on_authentication_success)
            self.auth_worker.authentication_error.connect(self.on_authentication_error)
            
            # Start worker thread
            self.logger.info(f"[MAIN] Starting worker thread for {username}")
            self.auth_worker.start()
            self.logger.info("[MAIN] Worker thread started")
            
        except Exception as e:
            self.logger.error(f"Unexpected error starting login: {str(e)}")
            self.view.show_error(f"Unexpected error: {str(e)}")
            self._reset_login_button()
    
    def on_validation_error(self, error_message):
        """Handle validation errors from worker thread"""
        try:
            self.logger.info(f"[SIGNAL] on_validation_error received: {error_message}")
            self._reset_login_button()
            self.view.show_error(error_message)
            self.generate_new_captcha()
        except Exception as e:
            self.logger.error(f"Error handling validation error: {str(e)}")
            self._reset_login_button()
    
    def on_authentication_success(self, user):
        """Handle successful authentication from worker thread"""
        try:
            self.logger.info(f"[SIGNAL] on_authentication_success received for user: {user.get('username')}")
            self._reset_login_button()
            
            auth_logger = logging.getLogger('AUTH')
            auth_logger.info(f"Login attempt [SUCCESS] - Username: {user.get('username')}")
            self.logger.info(f"Successful login for user: {user.get('username')}")
            
            self.view.logged_in_user = user
            
            # Close the login dialog (accept means logged in)
            self.view.accept()
        except Exception as e:
            self.logger.error(f"Error processing successful login: {str(e)}")
            self.view.show_error(f"Error: {str(e)}")
            self._reset_login_button()
    
    def on_authentication_error(self, error_message):
        """Handle authentication error from worker thread"""
        try:
            self.logger.info(f"[SIGNAL] on_authentication_error received: {error_message}")
            self._reset_login_button()
            
            try:
                username, _, _ = self.view.collect_form_data()
            except Exception:
                username = "unknown"
            
            auth_logger = logging.getLogger('AUTH')
            auth_logger.error(f"Login attempt [FAILED] - Username: {username} - Reason: {error_message}")
            self.logger.warning(f"Failed login attempt for username: {username}")
            
            # Record failed attempt
            try:
                self.service.login_tracker.record_attempt(username, False, reason=error_message)
            except Exception as e:
                self.logger.error(f"Failed to record login attempt: {str(e)}")
            
            self.view.show_error(error_message)
            self.generate_new_captcha()
        except Exception as e:
            self.logger.error(f"Error processing login error: {str(e)}")
            self.view.show_error(f"Error: {str(e)}")
            self._reset_login_button()
    
    def _reset_login_button(self):
        """Reset login button to default state"""
        self.view.btn_login.setEnabled(True)
        self.view.btn_login.setText("Login")
    
    def cleanup(self):
        """Clean up resources when dialog is closed"""
        try:
            # Stop and wait for worker thread if it's running
            if self.auth_worker is not None and self.auth_worker.isRunning():
                self.logger.info("Stopping authentication worker thread...")
                self.auth_worker.quit()
                self.auth_worker.wait(timeout=5000)  # Wait up to 5 seconds
                self.logger.info("Worker thread stopped")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

