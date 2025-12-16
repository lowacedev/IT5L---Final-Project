-- Migration script to add VAT and payment tracking
-- Run this if you get errors about missing columns

-- Add missing columns to sales table if they don't exist
ALTER TABLE sales ADD COLUMN IF NOT EXISTS sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE sales ADD INDEX IF NOT EXISTS idx_sale_date (sale_date);

-- Add user_id column to sales table for cashier/user tracking
ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id INT;

-- Add payment and VAT columns for receipt tracking
ALTER TABLE sales ADD COLUMN IF NOT EXISTS vat_amount DECIMAL(10, 2) DEFAULT 0.00;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS payment_mode VARCHAR(20);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS amount_received DECIMAL(10, 2) DEFAULT 0.00;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS change_amount DECIMAL(10, 2) DEFAULT 0.00;

-- Add FK constraints if they don't exist
ALTER TABLE sales 
ADD CONSTRAINT IF NOT EXISTS fk_sales_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
-- Create stock_movements table for tracking stock in/out operations
CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    movement_type ENUM('IN', 'OUT', 'ADJUSTMENT') NOT NULL,
    quantity INT NOT NULL,
    reason VARCHAR(255),
    notes TEXT,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (item_id) REFERENCES inventory_items(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_item_id (item_id),
    INDEX idx_movement_date (movement_date),
    INDEX idx_movement_type (movement_type)
);