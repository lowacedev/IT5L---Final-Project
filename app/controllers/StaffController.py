from app.exceptions import ValidationError, NotFoundError, DatabaseError


class StaffController:
    def __init__(self, service, view):
        self.service = service
        self.view = view

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
            self.view.show_error(f"Failed to load staff: {str(e)}")

    def add_staff(self):
        data = self.view.collect_form_data()
        if data is None:
            return
        
        full_name, username, password, role = data
        
        try:
            self.service.create_staff(full_name, username, password, role)
            self.view.show_success("Staff member added successfully!")
            self.view.clear_form()
            self.load_data()
        except ValidationError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")

    def update_staff(self):
        data_with_id = self.view.collect_form_data(with_id=True)
        if data_with_id is None:
            self.view.show_warning("Please select a staff member to update.")
            return
        
        staff_id, full_name, username, password, role = data_with_id
        
        if not self.view.ask_confirmation("Are you sure you want to update this staff member?"):
            return
        
        try:
            self.service.update_staff(staff_id, full_name, username, password if password else "", role)
            self.view.show_success("Staff member updated successfully!")
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

    def delete_staff(self):
        staff_id = self.view.get_selected_id()
        if staff_id is None:
            self.view.show_warning("Please select a staff member to delete.")
            return
        
        if not self.view.ask_confirmation("Are you sure you want to delete this staff member?"):
            return
        
        try:
            self.service.delete_staff(staff_id)
            self.view.show_success("Staff member deleted successfully!")
            self.view.clear_form()
            self.load_data()
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")
