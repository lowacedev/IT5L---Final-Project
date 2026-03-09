from app.exceptions import DatabaseError


class DashboardService:
    def __init__(self, db):
        self.db = db

    def get_daily_summary(self, date):
        try:
            cursor = self.db.cursor()
            query = """
            SELECT COUNT(DISTINCT id) as transaction_count, COALESCE(SUM(total), 0) as total_revenue
            FROM sales
            WHERE DATE(sale_date) = %s
            """
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            raise DatabaseError(f"Failed to get daily summary: {str(e)}")

    def get_daily_revenue(self, date):
        try:
            cursor = self.db.cursor()
            query = """
            SELECT COALESCE(SUM(total), 0)
            FROM sales
            WHERE DATE(sale_date) = %s
            """
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            cursor.close()
            return float(result[0]) if result and result[0] else 0.0
        except Exception as e:
            raise DatabaseError(f"Failed to get daily revenue: {str(e)}")

    def get_inventory_summary(self):
        try:
            cursor = self.db.cursor()
            query = "SELECT id, part_name, quantity FROM inventory_items"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            # If table doesn't exist, return empty list instead of crashing
            if "doesn't exist" in str(e).lower() or "no table" in str(e).lower():
                return []
            raise DatabaseError(f"Failed to get inventory summary: {str(e)}")

    def get_sales_trend(self, start_date, end_date):
        try:
            cursor = self.db.cursor()
            query = """
            SELECT DATE(sale_date) as date, COALESCE(SUM(total), 0) as daily_revenue
            FROM sales
            WHERE sale_date BETWEEN %s AND %s
            GROUP BY DATE(sale_date)
            ORDER BY DATE(sale_date)
            """
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            raise DatabaseError(f"Failed to get sales trend: {str(e)}")

    def get_top_selling_items(self, limit=5):
        try:
            cursor = self.db.cursor()
            query = """
            SELECT i.part_name, SUM(si.quantity) as total_sold, SUM(si.quantity * si.unit_price) as total_revenue
            FROM sales_items si
            JOIN inventory i ON si.item_id = i.id
            GROUP BY si.item_id, i.part_name
            ORDER BY total_sold DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            raise DatabaseError(f"Failed to get top selling items: {str(e)}")
