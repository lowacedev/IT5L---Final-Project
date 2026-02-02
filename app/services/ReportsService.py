from mysql.connector import Error
from app.exceptions import DatabaseError


class ReportsService:
    def __init__(self, db):
        self.db = db

    def get_sales_by_date_range(self, start_date, end_date):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    DATE(sale_date) as date,
                    COUNT(*) as num_transactions,
                    SUM(total) as total_revenue,
                    AVG(total) as avg_transaction
                FROM sales
                WHERE DATE(sale_date) BETWEEN %s AND %s
                GROUP BY DATE(sale_date)
                ORDER BY date DESC
            """, (start_date, end_date))
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get sales by date range: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_sales_by_date_range_detailed(self, start_date, end_date):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    s.id,
                    DATE(s.sale_date) as date,
                    TIME(s.sale_date) as time,
                    s.total,
                    COALESCE(COUNT(si.id), 0) as items_count,
                    COALESCE(u.full_name, u.username) as cashier
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                LEFT JOIN users u ON s.user_id = u.id
                WHERE DATE(s.sale_date) BETWEEN %s AND %s
                GROUP BY s.id, DATE(s.sale_date), TIME(s.sale_date), s.total, u.id, u.username, u.full_name
                ORDER BY s.sale_date DESC
            """, (start_date, end_date))
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get detailed sales: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_top_selling_items(self, limit=10):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
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
            """, (limit,))
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get top selling items: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_inventory_summary(self):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
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
            """)
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get inventory summary: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_low_stock_items(self, threshold=5):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    id,
                    part_name,
                    category,
                    quantity,
                    supplier_id
                FROM inventory_items
                WHERE quantity <= %s
                ORDER BY quantity ASC
            """, (threshold,))
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get low stock items: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_supplier_performance(self):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
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
            """)
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get supplier performance: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_daily_summary(self, date):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(total) as total_revenue,
                    AVG(total) as avg_transaction,
                    MIN(total) as min_transaction,
                    MAX(total) as max_transaction,
                    SUM((SELECT COUNT(*) FROM sale_items si WHERE si.sale_id = s.id)) as total_items
                FROM sales s
                WHERE DATE(sale_date) = %s
            """, (date,))
            return cursor.fetchone()
        except Error as e:
            raise DatabaseError(f"Failed to get daily summary: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_daily_revenue(self, date):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0) as total_revenue
                FROM sales
                WHERE DATE(sale_date) = %s
            """, (date,))
            data = cursor.fetchone()
            return float(data[0]) if data and data[0] is not None else 0.0
        except Error as e:
            raise DatabaseError(f"Failed to get daily revenue: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_category_performance(self):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
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
            """)
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get category performance: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_sales_aggregate(self, start_date, end_date, period='daily'):
        cursor = None
        try:
            cursor = self.db.cursor()
            if period == 'daily':
                query = """
                    SELECT DATE(sale_date) as label, SUM(total) as total_revenue
                    FROM sales
                    WHERE DATE(sale_date) BETWEEN %s AND %s
                    GROUP BY DATE(sale_date)
                    ORDER BY DATE(sale_date) ASC
                """
            elif period == 'weekly':
                query = """
                    SELECT CONCAT(YEAR(sale_date), '-W', LPAD(WEEK(sale_date, 1),2,'0')) as label,
                           SUM(total) as total_revenue
                    FROM sales
                    WHERE DATE(sale_date) BETWEEN %s AND %s
                    GROUP BY YEAR(sale_date), WEEK(sale_date, 1)
                    ORDER BY YEAR(sale_date), WEEK(sale_date, 1)
                """
            else:
                query = """
                    SELECT DATE_FORMAT(sale_date, '%%Y-%%m') as label, SUM(total) as total_revenue
                    FROM sales
                    WHERE DATE(sale_date) BETWEEN %s AND %s
                    GROUP BY DATE_FORMAT(sale_date, '%%Y-%%m')
                    ORDER BY DATE_FORMAT(sale_date, '%%Y-%%m') ASC
                """

            cursor.execute(query, (start_date, end_date))
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to get sales aggregate: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def export_sales_to_csv(self, start_date, end_date):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
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
            """, (start_date, end_date))
            return cursor.fetchall()
        except Error as e:
            raise DatabaseError(f"Failed to export sales data: {str(e)}")
        finally:
            if cursor:
                cursor.close()
