import mysql.connector
from mysql.connector import Error

class StaffModel:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        """Fetch all staff/users."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, full_name, username, role, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            print(f"[STAFF MODEL] Fetched {len(results)} staff members: {results}")
            return results
        except Error as e:
            print(f"[STAFF MODEL ERROR] fetch_all: {e}")
            return []

    def create_staff(self, full_name, username, password, role):
        """Create a new staff member."""
        try:
            cursor = self.db.cursor()
            query = """
            INSERT INTO users (full_name, username, password, role)
            VALUES (%s, %s, %s, %s)
            """
            print(f"[STAFF MODEL] Creating staff: {username} (role: {role}) full_name={full_name}")
            cursor.execute(query, (full_name, username, password, role))
            self.db.commit()
            staff_id = cursor.lastrowid
            cursor.close()
            print(f"[STAFF MODEL] Created staff with ID: {staff_id}")
            return staff_id
        except Error as e:
            self.db.rollback()
            print(f"[STAFF MODEL ERROR] create_staff: {e}")
            raise e

    def update_staff(self, staff_id, full_name, username, password, role):
        """Update an existing staff member."""
        try:
            cursor = self.db.cursor()
            if password:
                # Update with new password
                query = """
                UPDATE users SET 
                    full_name=%s, username=%s, password=%s, role=%s
                WHERE id=%s
                """
                params = (full_name, username, password, role, staff_id)
            else:
                # Update without changing password
                query = """
                UPDATE users SET 
                    full_name=%s, username=%s, role=%s
                WHERE id=%s
                """
                params = (full_name, username, role, staff_id)
            
            print(f"[STAFF MODEL] Updating staff {staff_id}")
            cursor.execute(query, params)
            self.db.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            print(f"[STAFF MODEL] Updated {rows_affected} row(s)")
            return rows_affected > 0
        except Error as e:
            self.db.rollback()
            print(f"[STAFF MODEL ERROR] update_staff: {e}")
            raise e

    def delete_staff(self, staff_id):
        """Delete a staff member."""
        try:
            cursor = self.db.cursor()
            print(f"[STAFF MODEL] Deleting staff with ID: {staff_id}")
            cursor.execute("DELETE FROM users WHERE id=%s", (staff_id,))
            self.db.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            print(f"[STAFF MODEL] Deleted {rows_affected} row(s)")
            return rows_affected > 0
        except Error as e:
            self.db.rollback()
            print(f"[STAFF MODEL ERROR] delete_staff: {e}")
            raise e

    def get_by_id(self, staff_id):
        """Get a single staff member by ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, full_name, username, role, created_at
                FROM users
                WHERE id=%s
            """, (staff_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"[STAFF MODEL ERROR] get_by_id: {e}")
            return None
