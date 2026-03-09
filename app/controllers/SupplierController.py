from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import SecurityAuditLogger
from app.controllers.signals import audit_log_signals


class SupplierController:
    def __init__(self, service, view, current_user=None):
        self.service = service
        self.view = view
        self.current_user = current_user

        view.add_btn.clicked.connect(self.add_supplier)
        view.update_btn.clicked.connect(self.update_supplier)
        view.delete_btn.clicked.connect(self.delete_supplier)
        view.refresh_btn.clicked.connect(self.load_data)
        view.clear_btn.clicked.connect(self.view.clear_form)
        
        self.load_data()

    def load_data(self):
        try:
            suppliers = self.service.fetch_all()
            self.view.load_table(suppliers)
        except Exception as e:
            self.view.show_error(f"Failed to load suppliers: {str(e)}")

    def _validate_supplier_form_data(self, name, contact_person, email, phone, address):
        """Validate supplier form fields. Returns error message if invalid, None if valid."""
        from app.security.input_validator import InputValidator
        
        # Check all fields are not empty
        if not name or not name.strip():
            return "Supplier name is required"
        
        if not contact_person or not contact_person.strip():
            return "Contact person is required"
        
        if not email or not email.strip():
            return "Email is required"
        
        if not phone or not phone.strip():
            return "Phone is required"
        
        if not address or not address.strip():
            return "Address is required"
        
        # Validate supplier name
        is_valid, msg = InputValidator.validate_supplier_name(name)
        if not is_valid:
            return f"Supplier name: {msg}"
        
        # Validate contact person
        is_valid, msg = InputValidator.validate_contact_person(contact_person)
        if not is_valid:
            return f"Contact person: {msg}"
        
        # Validate email
        is_valid, msg = InputValidator.validate_email(email)
        if not is_valid:
            return f"Email: {msg}"
        
        # Validate phone - PHILIPPINE FORMAT
        is_valid, msg = InputValidator.validate_philippine_phone(phone)
        if not is_valid:
            return f"Phone: {msg}"
        
        return None

    def add_supplier(self):
        data = self.view.collect_form_data()
        if data is None:
            return
        
        name, contact_person, email, phone, address = data
        
        # Validate input fields
        validation_error = self._validate_supplier_form_data(name, contact_person, email, phone, address)
        if validation_error:
            self.view.show_error(validation_error)
            return
        
        try:
            performed_by = self.current_user.get('username') if self.current_user else None
            self.service.create_supplier(name, contact_person, email, phone, address, performed_by=performed_by)
            
            # Log user action
            SecurityAuditLogger.log_user_action(
                performed_by or 'unknown',
                'create_supplier',
                f'Created supplier: {name} (Contact: {contact_person})'
            )
            
            # Emit signal to refresh audit logs
            print("[SupplierController.add_supplier] Emitting logs_updated signal...")
            audit_log_signals.logs_updated.emit()
            print("[SupplierController.add_supplier] Signal emitted!")
            
            self.view.show_success("Supplier added successfully!")
            self.view.clear_form()
            self.load_data()
        except ValidationError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def update_supplier(self):
        data_with_id = self.view.collect_form_data(with_id=True)
        if data_with_id is None:
            self.view.show_warning("Please select a supplier to update.")
            return
        
        supplier_id, name, contact_person, email, phone, address = data_with_id
        
        # Validate input fields
        validation_error = self._validate_supplier_form_data(name, contact_person, email, phone, address)
        if validation_error:
            self.view.show_error(validation_error)
            return
        
        if not self.view.ask_confirmation("Are you sure you want to update this supplier?"):
            return
        
        try:
            performed_by = self.current_user.get('username') if self.current_user else None
            self.service.update_supplier(supplier_id, name, contact_person, email, phone, address, performed_by=performed_by)
            
            # Log user action
            SecurityAuditLogger.log_user_action(
                performed_by or 'unknown',
                'update_supplier',
                f'Updated supplier ID {supplier_id}: {name}'
            )
            
            # Emit signal to refresh audit logs
            audit_log_signals.logs_updated.emit()
            
            self.view.show_success("Supplier updated successfully!")
            self.view.clear_form()
            self.load_data()
        except ValidationError as e:
            self.view.show_error(str(e))
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def delete_supplier(self):
        supplier_id = self.view.get_selected_id()
        if supplier_id is None:
            self.view.show_warning("Please select a supplier to delete.")
            return
        
        if not self.view.ask_confirmation("Are you sure you want to delete this supplier?"):
            return
        
        try:
            performed_by = self.current_user.get('username') if self.current_user else None
            self.service.delete_supplier(supplier_id, performed_by=performed_by)
            
            # Log user action
            SecurityAuditLogger.log_user_action(
                performed_by or 'unknown',
                'delete_supplier',
                f'Deleted supplier ID: {supplier_id}'
            )
            
            # Emit signal to refresh audit logs
            audit_log_signals.logs_updated.emit()
            
            self.view.show_success("Supplier deleted successfully!")
            self.view.clear_form()
            self.load_data()
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")
