from PyQt6.QtWidgets import QMessageBox, QFileDialog
from datetime import datetime

class ReportsController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect signals for Sales Report tab
        view.sales_refresh_btn.clicked.connect(self.refresh_sales_report)
        view.sales_export_btn.clicked.connect(self.export_sales_report)

        # Connect signals for Top Items tab
        view.top_items_refresh_btn.clicked.connect(self.refresh_top_items)

        # Connect signals for Inventory tab
        view.inventory_refresh_btn.clicked.connect(self.refresh_inventory)

        # Connect signals for Low Stock tab
        view.low_stock_refresh_btn.clicked.connect(self.refresh_low_stock)

        # Connect signals for Supplier tab
        view.supplier_refresh_btn.clicked.connect(self.refresh_supplier_performance)

        # Connect signals for Category tab
        view.category_refresh_btn.clicked.connect(self.refresh_category_performance)

        print("[REPORTS CONTROLLER] ReportsController initialized")
        
        # Load initial data
        self.refresh_sales_report()
        self.refresh_top_items()
        self.refresh_inventory()
        self.refresh_low_stock()
        self.refresh_supplier_performance()
        self.refresh_category_performance()

    def refresh_sales_report(self):
        """Refresh sales report data."""
        print("[REPORTS CONTROLLER] refresh_sales_report() called")
        try:
            start_date = self.view.sales_start_date.date().toString("yyyy-MM-dd")
            end_date = self.view.sales_end_date.date().toString("yyyy-MM-dd")
            
            # Get sales by date
            sales_data = self.model.get_sales_by_date_range(start_date, end_date)
            self.view.populate_sales_by_date_table(sales_data)
            
            # Get detailed sales
            detail_data = self.model.get_sales_by_date_range_detailed(start_date, end_date)
            self.view.populate_sales_detail_table(detail_data)
            
            print(f"[REPORTS CONTROLLER] Loaded {len(sales_data)} date summaries and {len(detail_data)} transactions")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] refresh_sales_report: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to load sales report: {error_msg}")

    def refresh_top_items(self):
        """Refresh top selling items."""
        print("[REPORTS CONTROLLER] refresh_top_items() called")
        try:
            limit = self.view.top_items_limit.value()
            data = self.model.get_top_selling_items(limit)
            self.view.populate_top_items_table(data)
            print(f"[REPORTS CONTROLLER] Loaded {len(data)} top items")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] refresh_top_items: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to load top items: {error_msg}")

    def refresh_inventory(self):
        """Refresh inventory summary."""
        print("[REPORTS CONTROLLER] refresh_inventory() called")
        try:
            data = self.model.get_inventory_summary()
            self.view.populate_inventory_table(data)
            print(f"[REPORTS CONTROLLER] Loaded {len(data)} inventory items")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] refresh_inventory: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to load inventory: {error_msg}")

    def refresh_low_stock(self):
        """Refresh low stock items."""
        print("[REPORTS CONTROLLER] refresh_low_stock() called")
        try:
            threshold = self.view.low_stock_threshold.value()
            data = self.model.get_low_stock_items(threshold)
            self.view.populate_low_stock_table(data)
            print(f"[REPORTS CONTROLLER] Loaded {len(data)} low stock items")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] refresh_low_stock: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to load low stock items: {error_msg}")

    def refresh_supplier_performance(self):
        """Refresh supplier performance."""
        print("[REPORTS CONTROLLER] refresh_supplier_performance() called")
        try:
            data = self.model.get_supplier_performance()
            self.view.populate_supplier_table(data)
            print(f"[REPORTS CONTROLLER] Loaded {len(data)} suppliers")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] refresh_supplier_performance: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to load supplier performance: {error_msg}")

    def refresh_category_performance(self):
        """Refresh category performance."""
        print("[REPORTS CONTROLLER] refresh_category_performance() called")
        try:
            data = self.model.get_category_performance()
            self.view.populate_category_table(data)
            print(f"[REPORTS CONTROLLER] Loaded {len(data)} categories")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] refresh_category_performance: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to load category performance: {error_msg}")

    def export_sales_report(self):
        """Export sales report to CSV."""
        print("[REPORTS CONTROLLER] export_sales_report() called")
        try:
            start_date = self.view.sales_start_date.date().toString("yyyy-MM-dd")
            end_date = self.view.sales_end_date.date().toString("yyyy-MM-dd")
            
            # Get file path from user
            filename, _ = QFileDialog.getSaveFileName(
                self.view,
                "Export Sales Report",
                f"sales_report_{start_date}_to_{end_date}.xlsx",
                "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if not filename:
                return
            
            # Get data
            data = self.model.export_sales_to_csv(start_date, end_date)
            
            if not data:
                QMessageBox.information(self.view, "No Data", "No sales data found for the selected period.")
                return
            
            # Export to XLSX if requested, otherwise CSV fallback
            try:
                if filename.lower().endswith('.xlsx'):
                    self.view.export_to_xlsx(data, filename)
                else:
                    self.view.export_to_csv(data, filename)
            except AttributeError:
                # In case view is missing the xlsx method, fallback to CSV
                self.view.export_to_csv(data, filename)
            print(f"[REPORTS CONTROLLER] Exported {len(data)} records to {filename}")
            
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[REPORTS CONTROLLER ERROR] export_sales_report: {error_msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to export report: {error_msg}")
