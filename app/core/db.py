import mysql.connector
from mysql.connector import Error
from app.security.config import SecurityConfig
from app.utils.logger import get_logger, SecurityAuditLogger

logger = get_logger(__name__)

def get_db():
    """
    Get secure database connection using credentials from environment variables.
    Prevents SQL injection by using parameterized queries.
    """
    try:
        # Validate security configuration
        SecurityConfig.validate()
        
        # Get connection from secure config
        connection = mysql.connector.connect(
            host=SecurityConfig.DB_HOST,
            user=SecurityConfig.DB_USER,
            password=SecurityConfig.DB_PASSWORD,
            database=SecurityConfig.DB_NAME,
            port=SecurityConfig.DB_PORT,
            autocommit=False,
            use_pure=True  # Use pure Python implementation for consistency
        )
        
        if connection.is_connected():
            logger.info("Successfully connected to database")
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
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Database connection test: {'SUCCESS' if result else 'FAILED'}")
        
       
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