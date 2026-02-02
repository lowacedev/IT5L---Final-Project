

class InventoryModel:
    
    def __init__(self, db):
        self.db = db
        from app.services.InventoryService import InventoryService
        self._service = InventoryService(db)

    def fetch_all(self):
        return self._service.fetch_all()

    def create_item(self, data):
        return self._service.create_item(data)

    def update_item(self, item_id, data):
        return self._service.update_item(item_id, data)

    def delete_item(self, item_id):
        return self._service.delete_item(item_id)

    def get_by_id(self, item_id):
        return self._service.get_by_id(item_id)

    def record_stock_movement(self, item_id, movement_type, quantity, reason, notes, user_id):
        
        return self._service.record_stock_movement(item_id, movement_type, quantity, reason, notes, user_id)

    def get_stock_movements(self, item_id=None, limit=100):
        return self._service.get_stock_movements(item_id, limit)
