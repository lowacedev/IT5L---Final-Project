from datetime import datetime, timedelta
from app.exceptions import DatabaseError


class DashboardController:
    def __init__(self, service, view):
        self.service = service
        self.view = view

        try:
            self.view.refresh_btn.clicked.connect(self.refresh)
        except Exception:
            pass

        try:
            sel = getattr(self.view, 'period_selector', None)
            if sel:
                sel.currentIndexChanged.connect(self.refresh)
        except Exception:
            pass

        self.refresh()

    def refresh(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            data = self.service.get_daily_summary(today)
            if data:
                total_transactions = data[0] if data[0] is not None else 0
                total_revenue = float(data[1]) if data[1] is not None else 0.0
            else:
                total_transactions = 0
                total_revenue = 0.0

            yesterday_revenue = self.service.get_daily_revenue(yesterday)

            if yesterday_revenue > 0:
                percentage_change = ((total_revenue - yesterday_revenue) / yesterday_revenue) * 100
            else:
                percentage_change = 100.0 if total_revenue > 0 else 0.0

            inventory = self.service.get_inventory_summary()
            total_products = len(inventory) if inventory else 0

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

            try:
                sel = getattr(self.view, 'period_selector', None)
                period = None
                if sel:
                    period = sel.currentText().lower()
                try:
                    self.view.load_sales_chart(days=60, period=period)
                except Exception:
                    pass
                try:
                    self.view.load_top_items_chart()
                except Exception:
                    pass
            except Exception:
                pass

        except DatabaseError as e:
            self.view.show_error(f"Failed to refresh dashboard: {str(e)}")
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")