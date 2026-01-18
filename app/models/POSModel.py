from app.services.POSService import POSService


class POSModel:
    def __init__(self, db):
        self._service = POSService(db)

    def fetch_all(self):
        return self._service.fetch_all()

    def search_item(self, keyword):
        return self._service.search_item(keyword)

    def save_transaction(self, items, total, user_id=None, vat_amount=0, payment_mode=None, amount_received=0, change=0):
        return self._service.save_transaction(items, total, user_id, vat_amount, payment_mode, amount_received, change)

    def get_item_stock(self, item_id):
        return self._service.get_item_stock(item_id)