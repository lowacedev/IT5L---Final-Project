from app.core.db import get_db

class ReportsModel:
    def __init__(self):
        self.conn = get_db()

    def get_sales_by_date_range(self, start_date, end_date):
        """Get sales data for a date range."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    DATE(sale_date) as date,
                    COUNT(*) as num_transactions,
                    SUM(total) as total_revenue,
                    AVG(total) as avg_transaction
                FROM sales
                WHERE DATE(sale_date) BETWEEN %s AND %s
                GROUP BY DATE(sale_date)
                ORDER BY date DESC
            """
            cursor.execute(query, (start_date, end_date))
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_sales_by_date_range: {e}")
            return []

    def get_sales_by_date_range_detailed(self, start_date, end_date):
        """Get detailed transaction data for a date range."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    s.id,
                    DATE(s.sale_date) as date,
                    TIME(s.sale_date) as time,
                    s.total,
                    COUNT(si.id) as items_count,
                    COALESCE(u.full_name, u.username) as cashier
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                LEFT JOIN users u ON s.user_id = u.id
                WHERE DATE(s.sale_date) BETWEEN %s AND %s
                GROUP BY s.id, DATE(s.sale_date), TIME(s.sale_date), s.total, cashier
                ORDER BY s.sale_date DESC
            """
            cursor.execute(query, (start_date, end_date))
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_sales_by_date_range_detailed: {e}")
            return []

    def get_top_selling_items(self, limit=10):
        """Get top selling items by quantity sold."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    i.id,
                    i.part_name,
                    i.category,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.quantity * si.price) as total_revenue,
                    AVG(si.price) as avg_price
                FROM sale_items si
                JOIN inventory_items i ON si.item_id = i.id
                GROUP BY i.id, i.part_name, i.category
                ORDER BY total_quantity DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_top_selling_items: {e}")
            return []

    def get_inventory_summary(self):
        """Get inventory summary - stock levels and values."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    id,
                    part_name,
                    category,
                    quantity,
                    cost_price,
                    selling_price,
                    (quantity * cost_price) as total_cost_value,
                    (quantity * selling_price) as total_selling_value,
                    (quantity * (selling_price - cost_price)) as potential_profit
                FROM inventory_items
                ORDER BY quantity ASC
            """
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_inventory_summary: {e}")
            return []

    def get_low_stock_items(self, threshold=5):
        """Get items with stock below threshold."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    id,
                    part_name,
                    category,
                    quantity,
                    supplier_id
                FROM inventory_items
                WHERE quantity <= %s
                ORDER BY quantity ASC
            """
            cursor.execute(query, (threshold,))
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_low_stock_items: {e}")
            return []

    def get_supplier_performance(self):
        """Get supplier performance - total sales value and items sold."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    s.id,
                    s.name,
                    COUNT(DISTINCT si.sale_id) as num_sales,
                    SUM(si.quantity) as total_items_sold,
                    SUM(si.quantity * si.price) as total_revenue
                FROM suppliers s
                LEFT JOIN inventory_items i ON s.id = i.supplier_id
                LEFT JOIN sale_items si ON i.id = si.item_id
                GROUP BY s.id, s.name
                ORDER BY total_revenue DESC
            """
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_supplier_performance: {e}")
            return []

    def get_daily_summary(self, date):
        """Get summary for a specific day."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(total) as total_revenue,
                    AVG(total) as avg_transaction,
                    MIN(total) as min_transaction,
                    MAX(total) as max_transaction,
                    SUM((SELECT COUNT(*) FROM sale_items si WHERE si.sale_id = s.id)) as total_items
                FROM sales s
                WHERE DATE(sale_date) = %s
            """
            cursor.execute(query, (date,))
            data = cursor.fetchone()
            cursor.close()
            return data if data else None
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_daily_summary: {e}")
            return None

    def get_daily_revenue(self, date):
        """Get total revenue for a specific day."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT COALESCE(SUM(total), 0) as total_revenue
                FROM sales
                WHERE DATE(sale_date) = %s
            """
            cursor.execute(query, (date,))
            data = cursor.fetchone()
            cursor.close()
            return float(data[0]) if data and data[0] is not None else 0.0
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_daily_revenue: {e}")
            return 0.0

    def get_category_performance(self):
        """Get sales performance by category."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    i.category,
                    COUNT(DISTINCT si.sale_id) as num_sales,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.quantity * si.price) as total_revenue,
                    AVG(si.price) as avg_price
                FROM sale_items si
                JOIN inventory_items i ON si.item_id = i.id
                GROUP BY i.category
                ORDER BY total_revenue DESC
            """
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_category_performance: {e}")
            return []

    def get_sales_aggregate(self, start_date, end_date, period='daily'):
        """Get aggregated sales by period.

        period: 'daily', 'weekly', or 'monthly'
        Returns list of tuples (period_label, total_revenue)
        """
        try:
            cursor = self.conn.cursor()
            if period == 'daily':
                query = """
                    SELECT DATE(sale_date) as label, SUM(total) as total_revenue
                    FROM sales
                    WHERE DATE(sale_date) BETWEEN %s AND %s
                    GROUP BY DATE(sale_date)
                    ORDER BY DATE(sale_date) ASC
                """
            elif period == 'weekly':
                # Use ISO week label Year-Wweek (e.g., 2025-W49)
                query = """
                    SELECT CONCAT(YEAR(sale_date), '-W', LPAD(WEEK(sale_date, 1),2,'0')) as label,
                           SUM(total) as total_revenue
                    FROM sales
                    WHERE DATE(sale_date) BETWEEN %s AND %s
                    GROUP BY YEAR(sale_date), WEEK(sale_date, 1)
                    ORDER BY YEAR(sale_date), WEEK(sale_date, 1)
                """
            else:
                # monthly
                query = """
                    SELECT DATE_FORMAT(sale_date, '%%Y-%%m') as label, SUM(total) as total_revenue
                    FROM sales
                    WHERE DATE(sale_date) BETWEEN %s AND %s
                    GROUP BY DATE_FORMAT(sale_date, '%%Y-%%m')
                    ORDER BY DATE_FORMAT(sale_date, '%%Y-%%m') ASC
                """

            cursor.execute(query, (start_date, end_date))
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] get_sales_aggregate: {e}")
            return []

    def export_sales_to_csv(self, start_date, end_date):
        """Get detailed sales data for CSV export."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    s.id as transaction_id,
                    s.sale_date,
                    s.total as transaction_total,
                    COALESCE(u.full_name, u.username) as cashier,
                    i.part_name,
                    si.quantity,
                    si.price,
                    (si.quantity * si.price) as line_total
                FROM sales s
                JOIN sale_items si ON s.id = si.sale_id
                JOIN inventory_items i ON si.item_id = i.id
                LEFT JOIN users u ON s.user_id = u.id
                WHERE DATE(s.sale_date) BETWEEN %s AND %s
                ORDER BY s.sale_date DESC, s.id DESC
            """
            cursor.execute(query, (start_date, end_date))
            data = cursor.fetchall()
            cursor.close()
            return data if data else []
        except Exception as e:
            print(f"[REPORTS MODEL ERROR] export_sales_to_csv: {e}")
            return []