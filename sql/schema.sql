-- Database Schema for Computer Parts POS System
-- Create database
CREATE DATABASE IF NOT EXISTS computerparts_pos;
USE computerparts_pos;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'cashier', 'manager') DEFAULT 'cashier',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory items table
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
);

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total DECIMAL(10, 2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    INDEX idx_sale_date (sale_date)
);

-- Sale items table
CREATE TABLE IF NOT EXISTS sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password, role) 
VALUES ('admin', 'admin123', 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- Insert default suppliers
INSERT INTO suppliers (name, contact_person, email, phone, address) VALUES
('TechSupply Co.', 'John Smith', 'john@techsupply.com', '555-0101', '123 Tech Ave'),
('Global Electronics', 'Jane Doe', 'jane@globalelectronics.com', '555-0102', '456 Electronics Blvd'),
('Component Direct', 'Bob Johnson', 'bob@componentdirect.com', '555-0103', '789 Component St'),
('Premium Parts Inc.', 'Alice Williams', 'alice@premiumparts.com', '555-0104', '321 Premium Ln')
ON DUPLICATE KEY UPDATE name=name;

-- Insert sample inventory items
INSERT INTO inventory_items (part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id) VALUES
('ASUS ROG Strix B550-F Gaming', 'Motherboard', 'ASUS', 'ROG-B550-F', 15, 8500.00, 10500.00, 1),
('AMD Ryzen 5 5600X', 'Processor', 'AMD', '5600X', 20, 9500.00, 11500.00, 1),
('Corsair Vengeance 16GB DDR4', 'RAM', 'Corsair', 'CMK16GX4', 30, 3200.00, 4200.00, 2),
('Samsung 980 PRO 1TB NVMe', 'Storage', 'Samsung', '980-PRO-1TB', 25, 6500.00, 8000.00, 2),
('MSI GeForce RTX 3060', 'Graphics Card', 'MSI', 'RTX-3060-12G', 10, 18000.00, 22000.00, 1),
('Corsair RM750x 750W', 'Power Supply', 'Corsair', 'RM750X', 18, 5500.00, 7000.00, 2),
('NZXT H510 Elite', 'Case', 'NZXT', 'H510-ELITE', 12, 7000.00, 8500.00, 3),
('Cooler Master Hyper 212', 'CPU Cooler', 'Cooler Master', 'HYPER-212', 22, 1500.00, 2200.00, 3),
('Logitech G502 HERO', 'Mouse', 'Logitech', 'G502-HERO', 35, 2500.00, 3500.00, 4),
('Corsair K70 RGB', 'Keyboard', 'Corsair', 'K70-RGB-MK2', 20, 6000.00, 7500.00, 4),
('ASUS TUF Gaming VG27AQ', 'Monitor', 'ASUS', 'VG27AQ', 8, 15000.00, 18500.00, 1),
('Western Digital 2TB HDD', 'Storage', 'WD', 'WD-BLUE-2TB', 28, 2800.00, 3500.00, 2)
ON DUPLICATE KEY UPDATE part_name=part_name;