from app.services.SupplierService import SupplierService


class SupplierModel:
    def __init__(self, db):
        self._service = SupplierService(db)

    def fetch_all(self):
        return self._service.fetch_all()

    def get_name_by_id(self, supplier_id):
        return self._service.get_name_by_id(supplier_id)

    def get_id_by_name(self, supplier_name):
        return self._service.get_id_by_name(supplier_name)

    def create_supplier(self, name, contact_person=None, email=None, phone=None, address=None):
        return self._service.create_supplier(name, contact_person, email, phone, address)

    def update_supplier(self, supplier_id, name, contact_person=None, email=None, phone=None, address=None):
        return self._service.update_supplier(supplier_id, name, contact_person, email, phone, address)

    def delete_supplier(self, supplier_id):
        return self._service.delete_supplier(supplier_id)

    def get_by_id(self, supplier_id):
        return self._service.get_by_id(supplier_id)