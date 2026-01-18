from app.services.StaffService import StaffService


class StaffModel:
    def __init__(self, db):
        self._service = StaffService(db)

    def fetch_all(self):
        return self._service.fetch_all()

    def create_staff(self, full_name, username, password, role):
        return self._service.create_staff(full_name, username, password, role)

    def update_staff(self, staff_id, full_name, username, password, role):
        return self._service.update_staff(staff_id, full_name, username, password, role)

    def delete_staff(self, staff_id):
        return self._service.delete_staff(staff_id)

    def get_by_id(self, staff_id):
        return self._service.get_by_id(staff_id)
