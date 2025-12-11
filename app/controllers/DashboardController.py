from datetime import datetime, timedelta
from PyQt6.QtWidgets import QMessageBox
from app.models.ReportsModel import ReportsModel

class DashboardController:
    def __init__(self, view):
        self.view = view
        self.model = ReportsModel()

        # Connect refresh button
        try:
            self.view.refresh_btn.clicked.connect(self.refresh)
        except Exception:
            pass

        # Connect period selector change to refresh chart
        try:
            sel = getattr(self.view, 'period_selector', None)
            if sel:
                sel.currentIndexChanged.connect(self.refresh)
        except Exception:
            pass

        # Initial load
        self.refresh()

    def refresh(self):
        try:
            # Today's KPIs
            today = datetime.now().strftime("%Y-%m-%d")
            data = self.model.get_daily_summary(today)
            if data:
                total_transactions = data[0] if data[0] is not None else 0
                total_revenue = float(data[1]) if data[1] is not None else 0.0
            else:
                total_transactions = 0
                total_revenue = 0.0

            # Total products
            inventory = self.model.get_inventory_summary()
            total_products = len(inventory) if inventory else 0

            # Update view KPI labels if available
            try:
                self.view.kpi_sales_label.setText(f"Php {total_revenue:,.2f}")
            except Exception:
                pass
            try:
                self.view.kpi_transactions_label.setText(str(total_transactions))
            except Exception:
                pass
            try:
                self.view.kpi_total_products_label.setText(str(total_products))
            except Exception:
                pass

            # Refresh chart (synchronous Matplotlib loaders)
            try:
                sel = getattr(self.view, 'period_selector', None)
                period = None
                if sel:
                    period = sel.currentText().lower()
                try:
                    self.view.load_sales_chart(days=30, period=period)
                except Exception:
                    pass
                try:
                    self.view.load_top_items_chart()
                except Exception:
                    pass
            except Exception:
                pass

        except Exception as e:
            msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[DASHBOARD CONTROLLER ERROR] refresh: {msg}")
            QMessageBox.critical(self.view, "Error", f"Failed to refresh dashboard: {msg}")
