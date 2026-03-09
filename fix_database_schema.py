#!/usr/bin/env python3
"""
Fix missing database tables after restore
Recreates missing tables from schema if they don't exist
"""

import mysql.connector
from app.security.config import SecurityConfig

def recreate_missing_tables():
    """Recreate missing tables from schema"""
    
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=SecurityConfig.DB_HOST,
            user=SecurityConfig.DB_USER,
            password=SecurityConfig.DB_PASSWORD,
            database=SecurityConfig.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # Create inventory_items table if it doesn't exist
        create_inventory = """
        CREATE TABLE IF NOT EXISTS inventory_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            part_name VARCHAR(200) NOT NULL,
            category VARCHAR(100),
            brand VARCHAR(100),
            model_number VARCHAR(100),
            quantity INT DEFAULT 0,
            cost_price DECIMAL(10, 2) DEFAULT 0.00,
            selling_price DECIMAL(10, 2) DEFAULT 0.00,
            supplier_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_part_name (part_name),
            INDEX idx_category (category),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        )
        """
        
        # Create sales_items table if it doesn't exist
        create_sales_items = """
        CREATE TABLE IF NOT EXISTS sales_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sale_id INT NOT NULL,
            item_id INT NOT NULL,
            quantity INT DEFAULT 1,
            unit_price DECIMAL(10, 2),
            subtotal DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES inventory_items(id) ON DELETE RESTRICT
        )
        """
        
        # Execute table creations
        print("Creating missing tables...")
        
        cursor.execute(create_inventory)
        print("✓ inventory_items table created/verified")
        
        cursor.execute(create_sales_items)
        print("✓ sales_items table created/verified")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✓ Database schema fixed successfully!")
        print("The dashboard should now work without errors.")
        
    except Exception as e:
        print(f"✗ Error fixing database schema: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check that database 'computerparts_pos' exists")
        print("3. Verify credentials in .env file")
        print("4. Try running: mysql -u root -p computerparts_pos < sql/schema.sql")

if __name__ == "__main__":
    recreate_missing_tables()
