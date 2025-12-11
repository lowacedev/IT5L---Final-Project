-- Migration script to fix POS-related tables and add cashier tracking
-- Run this if you get errors about missing columns or need to add cashier tracking

-- Add missing column to sales table if it doesn't exist
ALTER TABLE sales ADD COLUMN IF NOT EXISTS sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE sales ADD INDEX IF NOT EXISTS idx_sale_date (sale_date);

-- Add user_id column to sales table for cashier/user tracking
ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id INT;

-- Add FK constraint for user_id if it doesn't exist
-- Note: only run if the constraint doesn't already exist
ALTER TABLE sales 
ADD CONSTRAINT IF NOT EXISTS fk_sales_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Drop and recreate sale_items table to ensure proper structure
DROP TABLE IF EXISTS sale_items;

CREATE TABLE sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

ALTER TABLE inventory_items 
ADD CONSTRAINT IF NOT EXISTS fk_supplier 
FOREIGN KEY (supplier_id) REFERENCES suppliers(id) 
ON DELETE SET NULL;
