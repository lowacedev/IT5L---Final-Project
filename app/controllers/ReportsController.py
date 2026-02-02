from datetime import datetime
from app.exceptions import DatabaseError


class ReportsController:
    def __init__(self, service, view):
        self.service = service
        self.view = view

        view.sales_refresh_btn.clicked.connect(self.refresh_sales_report)
        view.sales_export_btn.clicked.connect(self.export_sales_report)

        view.top_items_refresh_btn.clicked.connect(self.refresh_top_items)

        view.inventory_refresh_btn.clicked.connect(self.refresh_inventory)

        view.low_stock_refresh_btn.clicked.connect(self.refresh_low_stock)

        view.supplier_refresh_btn.clicked.connect(self.refresh_supplier_performance)

        view.category_refresh_btn.clicked.connect(self.refresh_category_performance)
        
        self.refresh_sales_report()
        self.refresh_top_items()
        self.refresh_inventory()
        self.refresh_low_stock()
        self.refresh_supplier_performance()
        self.refresh_category_performance()

    def refresh_sales_report(self):
        try:
            start_date = self.view.sales_start_date.date().toString("yyyy-MM-dd")
            end_date = self.view.sales_end_date.date().toString("yyyy-MM-dd")
            
            sales_data = self.service.get_sales_by_date_range(start_date, end_date)
            self.view.populate_sales_by_date_table(sales_data)
            
            detail_data = self.service.get_sales_by_date_range_detailed(start_date, end_date)
            self.view.populate_sales_detail_table(detail_data)
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to load sales report: {str(e)}")

    def refresh_top_items(self):
        try:
            limit = self.view.top_items_limit.value()
            data = self.service.get_top_selling_items(limit)
            self.view.populate_top_items_table(data)
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to load top items: {str(e)}")

    def refresh_inventory(self):
        try:
            data = self.service.get_inventory_summary()
            self.view.populate_inventory_table(data)
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to load inventory: {str(e)}")

    def refresh_low_stock(self):
        try:
            threshold = self.view.low_stock_threshold.value()
            data = self.service.get_low_stock_items(threshold)
            self.view.populate_low_stock_table(data)
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to load low stock items: {str(e)}")

    def refresh_supplier_performance(self):
        try:
            data = self.service.get_supplier_performance()
            self.view.populate_supplier_table(data)
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to load supplier performance: {str(e)}")

    def refresh_category_performance(self):
        try:
            data = self.service.get_category_performance()
            self.view.populate_category_table(data)
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to load category performance: {str(e)}")

    def export_sales_report(self):
        try:
            start_date = self.view.sales_start_date.date().toString("yyyy-MM-dd")
            end_date = self.view.sales_end_date.date().toString("yyyy-MM-dd")
            
            filename, _ = self.view._choose_save_file(
                f"sales_report_{start_date}_to_{end_date}.xlsx"
            )
            
            if not filename:
                return
            
            data = self.service.export_sales_to_csv(start_date, end_date)
            
            if not data:
                self.view.show_warning("No sales data found for the selected period.")
                return
            
            if filename.lower().endswith('.xlsx'):
                self.view.export_to_xlsx(data, filename)
            else:
                self.view.export_to_csv(data, filename)
                
        except DatabaseError as e:
            self.view.show_error(str(e))
        except Exception as e:
            self.view.show_error(f"Failed to export report: {str(e)}")
