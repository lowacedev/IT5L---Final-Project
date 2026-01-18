from app.services.ReportsService import ReportsService


class ReportsModel:
    def __init__(self):
        self._service = ReportsService()

    def get_sales_by_date_range(self, start_date, end_date):
        return self._service.get_sales_by_date_range(start_date, end_date)

    def get_sales_by_date_range_detailed(self, start_date, end_date):
        return self._service.get_sales_by_date_range_detailed(start_date, end_date)

    def get_top_selling_items(self, limit=10):
        return self._service.get_top_selling_items(limit)

    def get_inventory_summary(self):
        return self._service.get_inventory_summary()

    def get_low_stock_items(self, threshold=5):
        return self._service.get_low_stock_items(threshold)

    def get_supplier_performance(self):
        return self._service.get_supplier_performance()

    def get_daily_summary(self, date):
        return self._service.get_daily_summary(date)

    def get_daily_revenue(self, date):
        return self._service.get_daily_revenue(date)

    def get_category_performance(self):
        return self._service.get_category_performance()

    def get_sales_aggregate(self, start_date, end_date, period='daily'):
        return self._service.get_sales_aggregate(start_date, end_date, period)

    def export_sales_to_csv(self, start_date, end_date):
        return self._service.export_sales_to_csv(start_date, end_date)