from app.exceptions import ValidationError, NotFoundError, DatabaseError


class SupplierController:
    def __init__(self, service, view):
        self.service = service
        self.view = view

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

    def add_supplier(self):
        data = self.view.collect_form_data()
        if data is None:
            return
        
        name, contact_person, email, phone, address = data
        
        try:
            self.service.create_supplier(name, contact_person, email, phone, address)
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
        
        if not self.view.ask_confirmation("Are you sure you want to update this supplier?"):
            return
        
        try:
            self.service.update_supplier(supplier_id, name, contact_person, email, phone, address)
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
            self.service.delete_supplier(supplier_id)
            self.view.show_success("Supplier deleted successfully!")
            self.view.clear_form()
            self.load_data()
        except NotFoundError as e:
            self.view.show_error(str(e))
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")
