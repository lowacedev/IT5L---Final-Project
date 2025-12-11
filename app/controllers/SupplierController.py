from PyQt6.QtWidgets import QMessageBox

class SupplierController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect signals
        view.add_btn.clicked.connect(self.add_supplier)
        view.update_btn.clicked.connect(self.update_supplier)
        view.delete_btn.clicked.connect(self.delete_supplier)
        view.refresh_btn.clicked.connect(self.load_data)
        view.clear_btn.clicked.connect(self.view.clear_form)
        
        print("[SUPPLIER CONTROLLER] SupplierController initialized")

        self.load_data()

    def load_data(self):
        """Load all suppliers."""
        try:
            print("[SUPPLIER CONTROLLER] Loading supplier data...")
            suppliers = self.model.fetch_all()
            print(f"[SUPPLIER CONTROLLER] Fetched {len(suppliers)} suppliers")
            self.view.load_table(suppliers)
            print("[SUPPLIER CONTROLLER] Supplier table loaded successfully")
        except Exception as e:
            print(f"[SUPPLIER CONTROLLER ERROR] load_data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.view, "Error", f"Failed to load data: {str(e)}")

    def add_supplier(self):
        """Add a new supplier."""
        print("[SUPPLIER CONTROLLER] add_supplier() called")
        data = self.view.get_form_data()
        if data is None:
            return
        
        name, contact_person, email, phone, address = data
        
        try:
            self.model.create_supplier(name, contact_person, email, phone, address)
            QMessageBox.information(self.view, "Success", "Supplier added successfully!")
            self.view.clear_form()
            self.load_data()
        except Exception as e:
            print(f"[SUPPLIER CONTROLLER ERROR] add_supplier: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to add supplier:\n{str(e)}")

    def update_supplier(self):
        """Update an existing supplier."""
        print("[SUPPLIER CONTROLLER] update_supplier() called")
        data_with_id = self.view.get_form_data(with_id=True)
        if data_with_id is None:
            return
        
        supplier_id, name, contact_person, email, phone, address = data_with_id
        
        try:
            reply = QMessageBox.question(
                self.view,
                "Confirm Update",
                "Are you sure you want to update this supplier?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.update_supplier(supplier_id, name, contact_person, email, phone, address)
                QMessageBox.information(self.view, "Success", "Supplier updated successfully!")
                self.view.clear_form()
                self.load_data()
        except Exception as e:
            print(f"[SUPPLIER CONTROLLER ERROR] update_supplier: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to update supplier: {str(e)}")

    def delete_supplier(self):
        """Delete a supplier."""
        print("[SUPPLIER CONTROLLER] delete_supplier() called")
        supplier_id = self.view.get_selected_id()
        if supplier_id is None:
            QMessageBox.warning(self.view, "No Selection", "Please select a supplier to delete.")
            return
        
        try:
            reply = QMessageBox.question(
                self.view,
                "Confirm Delete",
                "Are you sure you want to delete this supplier?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model.delete_supplier(supplier_id)
                QMessageBox.information(self.view, "Success", "Supplier deleted successfully!")
                self.view.clear_form()
                self.load_data()
        except Exception as e:
            print(f"[SUPPLIER CONTROLLER ERROR] delete_supplier: {e}")
            QMessageBox.critical(self.view, "Error", f"Failed to delete supplier: {str(e)}")
