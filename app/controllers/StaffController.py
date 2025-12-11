from PyQt6.QtWidgets import QMessageBox

class StaffController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect signals
        view.add_btn.clicked.connect(self.add_staff)
        view.update_btn.clicked.connect(self.update_staff)
        view.delete_btn.clicked.connect(self.delete_staff)
        view.refresh_btn.clicked.connect(self.load_data)
        view.clear_btn.clicked.connect(self.view.clear_form)
        
        print("[STAFF CONTROLLER] StaffController initialized")

        self.load_data()

    def load_data(self):
        """Load all staff."""
        try:
            print("[STAFF CONTROLLER] Loading staff data...")
            staff = self.model.fetch_all()
            print(f"[STAFF CONTROLLER] Fetched {len(staff)} staff members")
            self.view.load_table(staff)
            print("[STAFF CONTROLLER] Staff table loaded successfully")
        except Exception as e:
            print(f"[STAFF CONTROLLER ERROR] load_data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.view, "Error", f"Failed to load data: {str(e)}")

    def add_staff(self):
        """Add a new staff member."""
        print("[STAFF CONTROLLER] add_staff() called")
        data = self.view.get_form_data()
        if data is None:
            return
        
        full_name, username, password, role = data
        
        try:
            self.model.create_staff(full_name, username, password, role)
            QMessageBox.information(self.view, "Success", "Staff member added successfully!")
            self.view.clear_form()
            self.load_data()
        except Exception as e:
            print(f"[STAFF CONTROLLER ERROR] add_staff: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to add staff:\n{str(e)}")

    def update_staff(self):
        """Update an existing staff member."""
        print("[STAFF CONTROLLER] update_staff() called")
        data_with_id = self.view.get_form_data(with_id=True)
        if data_with_id is None:
            return
        
        staff_id, full_name, username, password, role = data_with_id
        
        try:
            reply = QMessageBox.question(
                self.view,
                "Confirm Update",
                "Are you sure you want to update this staff member?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.update_staff(staff_id, full_name, username, password if password else None, role)
                QMessageBox.information(self.view, "Success", "Staff member updated successfully!")
                self.view.clear_form()
                self.load_data()
        except Exception as e:
            print(f"[STAFF CONTROLLER ERROR] update_staff: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to update staff: {str(e)}")

    def delete_staff(self):
        """Delete a staff member."""
        print("[STAFF CONTROLLER] delete_staff() called")
        staff_id = self.view.get_selected_id()
        if staff_id is None:
            QMessageBox.warning(self.view, "No Selection", "Please select a staff member to delete.")
            return
        
        try:
            reply = QMessageBox.question(
                self.view,
                "Confirm Delete",
                "Are you sure you want to delete this staff member?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.delete_staff(staff_id)
                QMessageBox.information(self.view, "Success", "Staff member deleted successfully!")
                self.view.clear_form()
                self.load_data()
        except Exception as e:
            print(f"[STAFF CONTROLLER ERROR] delete_staff: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to delete staff: {str(e)}")
