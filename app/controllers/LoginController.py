import logging
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.CaptchaGenerator import CaptchaGenerator


class LoginController:
    def __init__(self, service, view):
        self.service = service
        self.view = view
        self.captcha_generator = CaptchaGenerator()
        self.logger = logging.getLogger(__name__)
        
        # Connect signals
        view.btn_login.clicked.connect(self.handle_login)
        view.btn_refresh_captcha.clicked.connect(self.refresh_captcha)
        
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
        try:
            username, password, captcha_input = self.view.collect_form_data()
            
            # Validate all fields are provided
            if not username or not password or not captcha_input:
                self.view.show_warning("Please enter username, password, and CAPTCHA code.")
                return
            
            # Check for empty username
            if not username.strip():
                self.view.show_warning("Please enter a username.")
                return
            
            # Check if account is locked BEFORE validating CAPTCHA
            from app.security.config import SecurityConfig
            lockout_minutes = SecurityConfig.LOGIN_LOCKOUT_DURATION // 60
            
            if self.service.login_tracker.is_account_locked(
                username,
                SecurityConfig.MAX_LOGIN_ATTEMPTS,
                lockout_minutes
            ):
                self.logger.warning(f"Blocked login attempt for locked account: {username}")
                self.view.show_error(f"Account locked due to too many failed attempts. Try again in {lockout_minutes} minutes.")
                self.generate_new_captcha()
                return
            
            # Validate CAPTCHA
            if not self.captcha_generator.validate(captcha_input):
                self.logger.warning(f"Failed CAPTCHA attempt for username: {username}")
                # Record CAPTCHA failure as login attempt
                self.service.login_tracker.record_attempt(username, False, reason="Invalid CAPTCHA")
                self.view.show_error("Invalid CAPTCHA code. Please try again.")
                # Generate new CAPTCHA after failed attempt
                self.generate_new_captcha()
                return
            
            # CAPTCHA is correct, now check username and password
            user = self.service.authenticate(username, password)

            if user:
                self.logger.info(f"Successful login for user: {username}")
                self.view.accept()
                self.view.logged_in_user = user
            else:
                self.logger.warning(f"Failed login attempt for username: {username}")
                self.view.show_error("Invalid username or password.")
                # Regenerate CAPTCHA for next attempt
                self.generate_new_captcha()
        except (ValidationError, NotFoundError, DatabaseError) as e:
            self.logger.error(f"Login failed with exception: {str(e)}")
            self.view.show_error(f"Login failed: {str(e)}")
            # Regenerate CAPTCHA for next attempt
            self.generate_new_captcha()
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            self.view.show_error(f"Unexpected error: {str(e)}")
            # Regenerate CAPTCHA for next attempt
            self.generate_new_captcha()

