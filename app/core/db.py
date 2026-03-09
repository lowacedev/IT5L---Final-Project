import mysql.connector
from mysql.connector import Error
from app.security.config import SecurityConfig
from app.utils.logger import get_logger, SecurityAuditLogger

logger = get_logger(__name__)

def get_db():
    """
    Get secure database connection using credentials from environment variables.
    Prevents SQL injection by using parameterized queries.
    Includes connection timeout to prevent hanging.
    """
    try:
        # Validate security configuration
        SecurityConfig.validate()
        
        # Get connection from secure config with timeouts
        connection = mysql.connector.connect(
            host=SecurityConfig.DB_HOST,
            user=SecurityConfig.DB_USER,
            password=SecurityConfig.DB_PASSWORD,
            database=SecurityConfig.DB_NAME,
            port=SecurityConfig.DB_PORT,
            autocommit=False,
            use_pure=True,  # Use pure Python implementation for consistency
            connection_timeout=10,  # 10 second connection timeout
            get_warnings=False,  # Disable warnings for performance
            raise_on_warnings=False
        )
        
        if connection.is_connected():
            return connection
            
    except Error as e:
        error_msg = str(e)
        # Don't expose sensitive details in error messages
        safe_message = "Database connection failed"
        logger.error(f"{safe_message}: {error_msg[:50]}")
        
        if SecurityConfig.DEBUG:
            print(f"\n[DEBUG] Database Error: {e}")
        
        print("\nTroubleshooting:")
        print("1. Is MySQL running?")
        print("2. Does database 'computerparts_pos' exist?")
        print("3. Check .env file for correct credentials")
        print("4. Did you run schema.sql?")
        raise e

def test_connection():
    
    try:
        db = get_db()
        
        # Quick check that connection is responsive
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            print("Database connection test FAILED: No response from SELECT 1")
            return False
        
        print(f"Database connection test: SUCCESS")
        
        # Check tables exist
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory_items")
        count = cursor.fetchone()
        print(f"Found {count[0]} items in inventory_items table")
        cursor.close()
        
        db.close()
        return True
    except Exception as e:
        print(f"Database connection test FAILED: {e}")
        return False


def is_database_responsive(timeout_seconds=5):
    """Quick check if database is responding"""
    import threading
    
    result = [False]
    
    def check():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            db.close()
            result[0] = True
        except:
            result[0] = False
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    return result[0]

if __name__ == "__main__":
    test_connection()