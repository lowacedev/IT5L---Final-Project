import mysql.connector
from mysql.connector import Error

def get_db():
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="computerparts_pos",
            autocommit=False
        )
        
        if connection.is_connected():
            print("Successfully connected to database")
            return connection
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("\nTroubleshooting:")
        print("1. Is MySQL running?")
        print("2. Does database 'computerparts_pos' exist?")
        print("3. Are credentials correct in db.py?")
        print("4. Did you run schema.sql?")
        raise e

def test_connection():
    """Test the database connection."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Database connection test: {'SUCCESS' if result else 'FAILED'}")
        
        # Test inventory table
        cursor.execute("SELECT COUNT(*) FROM inventory_items")
        count = cursor.fetchone()[0]
        print(f"Found {count} items in inventory_items table")
        
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Database connection test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_connection()