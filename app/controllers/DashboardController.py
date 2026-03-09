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

    def _extract_daily_summary(self, today):
        """Extract daily summary data with defaults."""
        data = self.service.get_daily_summary(today)
        if data:
            total_transactions = data[0] if data[0] is not None else 0
            total_revenue = float(data[1]) if data[1] is not None else 0.0
        else:
            total_transactions = 0
            total_revenue = 0.0
        return total_transactions, total_revenue

    def _update_kpi_labels(self, total_revenue, total_transactions, total_products):
        """Update KPI labels in the view."""
        self._safe_set_text(self.view.kpi_sales_label, f"Php {total_revenue:,.2f}")
        self._safe_set_text(self.view.kpi_transactions_label, str(total_transactions))
        self._safe_set_text(self.view.kpi_total_products_label, str(total_products))

    def _safe_set_text(self, widget, text):
        """Safely set widget text, suppressing errors."""
        try:
            widget.setText(text)
        except Exception:
            pass

    def _load_charts(self):
        """Load sales and inventory charts with period selection."""
        try:
            sel = getattr(self.view, 'period_selector', None)
            period = sel.currentText().lower() if sel else None
            
            self._safe_load_chart(lambda: self.view.load_sales_chart(days=60, period=period))
            self._safe_load_chart(lambda: self.view.load_top_items_chart())
        except Exception:
            pass

    def _safe_load_chart(self, chart_loader):
        """Load a chart, suppressing errors."""
        try:
            chart_loader()
        except Exception:
            pass

    def refresh(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            total_transactions, total_revenue = self._extract_daily_summary(today)
            inventory = self.service.get_inventory_summary()
            total_products = len(inventory) if inventory else 0

            self._update_kpi_labels(total_revenue, total_transactions, total_products)
            self._load_charts()

        except DatabaseError as e:
            self.view.show_error(f"Failed to refresh dashboard: {str(e)}")
        except Exception as e:
            self.view.show_error(f"Unexpected error: {str(e)}")