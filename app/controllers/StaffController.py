from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.security.input_validator import InputValidator
from app.security.password_manager import PasswordManager
import logging


logger = logging.getLogger(__name__)


class StaffController:
    def __init__(self, service, view, current_user=None):
        self.service = service
        self.view = view
        self.current_user = current_user

        view.add_btn.clicked.connect(self.add_staff)
        view.update_btn.clicked.connect(self.update_staff)
        view.delete_btn.clicked.connect(self.delete_staff)
        view.refresh_btn.clicked.connect(self.load_data)
        view.clear_btn.clicked.connect(self.view.clear_form)
        
        self.load_data()

    def load_data(self):
        try:
            staff = self.service.fetch_all()
            self.view.load_table(staff)
        except Exception as e:
            logger.error(f"Failed to load staff: {str(e)}")
            self.view.show_error(f"Failed to load staff: {str(e)}")

    def add_staff(self):
        data = self.view.collect_form_data()
        if data is None:
            return
        
        full_name, username, password, role = data
        
        try:
            # Validate full name
            is_valid, msg = InputValidator.validate_full_name(full_name)
            if not is_valid:
                self.view.show_error(f"Full name: {msg}")
                return
            
            # Validate username
            is_valid, msg = InputValidator.validate_username(username)
            if not is_valid:
                self.view.show_error(f"Username: {msg}")
                return
            
            # Validate password (use PasswordManager, not InputValidator!)
            is_valid, msg = PasswordManager.validate_password_strength(password)
            if not is_valid:
                self.view.show_error(f"Password: {msg}")
                return
            
            # Validate role
            is_valid, msg = InputValidator.validate_role(role)
            if not is_valid:
                self.view.show_error(f"Role: {msg}")
                return
            
            # Get current user's username for logging
            performed_by = self.current_user.get('username') if self.current_user else None
            self.service.create_staff(full_name, username, password, role, performed_by=performed_by)
            self.view.show_success("Staff member added successfully!")
            self.view.clear_form()
            self.load_data()
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            self.view.show_error(str(e))
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            self.view.show_error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.view.show_error(f"Unexpected error: {str(e)}")

    def update_staff(self):
        data_with_id = self.view.collect_form_data(with_id=True)
        if data_with_id is None:
            self.view.show_warning("Please select a staff member to update.")
            return
        
        staff_id, full_name, username, password, role = data_with_id
        
        try:
            # Validate full name
            is_valid, msg = InputValidator.validate_full_name(full_name)
            if not is_valid:
                self.view.show_error(f"Full name: {msg}")
                return
            
            # Validate username
            is_valid, msg = InputValidator.validate_username(username)
            if not is_valid:
                self.view.show_error(f"Username: {msg}")
                return
            
            # Validate password only if provided (for update, password is optional)
            if password:
                is_valid, msg = PasswordManager.validate_password_strength(password)
                if not is_valid:
                    self.view.show_error(f"Password: {msg}")
                    return
            
            # Validate role
            is_valid, msg = InputValidator.validate_role(role)
            if not is_valid:
                self.view.show_error(f"Role: {msg}")
                return
            
            if not self.view.ask_confirmation("Are you sure you want to update this staff member?"):
                return
            
            # Get current user's username for logging
            performed_by = self.current_user.get('username') if self.current_user else None
            self.service.update_staff(staff_id, full_name, username, password if password else "", role, performed_by=performed_by)
            self.view.show_success("Staff member updated successfully!")
            self.view.clear_form()
            self.load_data()
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            self.view.show_error(str(e))
        except NotFoundError as e:
            logger.warning(f"Not found error: {str(e)}")
            self.view.show_error(str(e))
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            self.view.show_error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.view.show_error(f"Unexpected error: {str(e)}")

    def delete_staff(self):
        staff_id = self.view.get_selected_id()
        if staff_id is None:
            self.view.show_warning("Please select a staff member to delete.")
            return
        
        if not self.view.ask_confirmation("Are you sure you want to delete this staff member?"):
            return
        
        try:
            # Get current user's username for logging
            performed_by = self.current_user.get('username') if self.current_user else None
            self.service.delete_staff(staff_id, performed_by=performed_by)
            self.view.show_success("Staff member deleted successfully!")
            self.view.clear_form()
            self.load_data()
        except NotFoundError as e:
            logger.warning(f"Not found error: {str(e)}")
            self.view.show_error(str(e))
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            self.view.show_error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.view.show_error(f"Unexpected error: {str(e)}")
