-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 16, 2025 at 08:41 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `computerparts_pos`
--

-- --------------------------------------------------------

--
-- Table structure for table `inventory_items`
--

CREATE TABLE `inventory_items` (
  `id` int(11) NOT NULL,
  `part_name` varchar(200) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `model_number` varchar(100) DEFAULT NULL,
  `quantity` int(11) DEFAULT 0,
  `cost_price` decimal(10,2) DEFAULT 0.00,
  `selling_price` decimal(10,2) DEFAULT 0.00,
  `supplier_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `inventory_items`
--

INSERT INTO `inventory_items` (`id`, `part_name`, `category`, `brand`, `model_number`, `quantity`, `cost_price`, `selling_price`, `supplier_id`, `created_at`, `updated_at`) VALUES
(29, 'AMD Ryzen 5 5600X', 'Processor', 'AMD', '5600X', 47, 9500.00, 11500.00, 2, '2025-12-03 09:38:19', '2025-12-16 07:36:44'),
(40, 'ASUS ROG Strix B550-F Gaming', 'Motherboard', 'ASUS', 'ROG-B550-F', 12, 8500.00, 10500.00, NULL, '2025-12-10 04:10:31', '2025-12-11 15:16:26'),
(42, 'Corsair Vengeance 16GB DDR4', 'RAM', 'Corsair', 'CMK16GX4', 29, 3200.00, 4200.00, 2, '2025-12-10 04:10:31', '2025-12-11 15:13:07'),
(43, 'Samsung 980 PRO 1TB NVMe', 'Storage', 'Samsung', '980-PRO-1TB', 25, 6500.00, 8000.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(44, 'MSI GeForce RTX 3060', 'Graphics Card', 'MSI', 'RTX-3060-12G', 10, 18000.00, 22000.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(45, 'Corsair RM750x 750W', 'Power Supply', 'Corsair', 'RM750X', 18, 5500.00, 7000.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(46, 'NZXT H510 Elite', 'Case', 'NZXT', 'H510-ELITE', 12, 7000.00, 8500.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(47, 'Cooler Master Hyper 212', 'CPU Cooler', 'Cooler Master', 'HYPER-212', 22, 1500.00, 2200.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(48, 'Logitech G502 HERO', 'Mouse', 'Logitech', 'G502-HERO', 35, 2500.00, 3500.00, 4, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(49, 'Corsair K70 RGB', 'Keyboard', 'Corsair', 'K70-RGB-MK2', 20, 6000.00, 7500.00, 4, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(50, 'ASUS TUF Gaming VG27AQ', 'Monitor', 'ASUS', 'VG27AQ', 8, 15000.00, 18500.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(51, 'Western Digital 2TB HDD', 'Storage', 'WD', 'WD-BLUE-2TB', 28, 2800.00, 3500.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(52, 'Ryzen 5 5600X Processor', 'CPU', 'AMD', '100-100000065BOX', 10, 12500.00, 15000.00, 2, '2025-12-16 07:02:49', '2025-12-16 07:02:49');

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `id` int(11) NOT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `sale_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_id` int(11) DEFAULT NULL,
  `vat_amount` decimal(10,2) DEFAULT 0.00,
  `payment_mode` varchar(20) DEFAULT NULL,
  `amount_received` decimal(10,2) DEFAULT 0.00,
  `change_amount` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sales`
--

INSERT INTO `sales` (`id`, `total`, `created_at`, `sale_date`, `user_id`, `vat_amount`, `payment_mode`, `amount_received`, `change_amount`) VALUES
(2, 11500.00, '2025-12-03 10:05:26', '2025-12-03 10:05:26', NULL, 0.00, NULL, 0.00, 0.00),
(3, 11500.00, '2025-12-03 10:05:40', '2025-12-03 10:05:40', NULL, 0.00, NULL, 0.00, 0.00),
(4, 11500.00, '2025-12-03 10:07:55', '2025-12-03 10:07:55', NULL, 0.00, NULL, 0.00, 0.00),
(5, 22000.00, '2025-12-03 10:09:59', '2025-12-03 10:09:59', NULL, 0.00, NULL, 0.00, 0.00),
(6, 11500.00, '2025-12-04 07:38:36', '2025-12-04 07:38:36', NULL, 0.00, NULL, 0.00, 0.00),
(7, 7500.00, '2025-12-04 07:38:52', '2025-12-04 07:38:52', NULL, 0.00, NULL, 0.00, 0.00),
(8, 18500.00, '2025-12-04 07:38:54', '2025-12-04 07:38:54', NULL, 0.00, NULL, 0.00, 0.00),
(9, 7000.00, '2025-12-04 07:38:57', '2025-12-04 07:38:57', NULL, 0.00, NULL, 0.00, 0.00),
(10, 11500.00, '2025-12-04 09:58:42', '2025-12-04 09:58:42', NULL, 0.00, NULL, 0.00, 0.00),
(11, 11500.00, '2025-12-04 10:11:25', '2025-12-04 10:11:25', NULL, 0.00, NULL, 0.00, 0.00),
(12, 115000.00, '2025-12-04 10:11:36', '2025-12-04 10:11:36', NULL, 0.00, NULL, 0.00, 0.00),
(13, 400.00, '2025-12-04 10:11:48', '2025-12-04 10:11:48', NULL, 0.00, NULL, 0.00, 0.00),
(14, 22000.00, '2025-12-04 10:20:12', '2025-12-04 10:20:12', NULL, 0.00, NULL, 0.00, 0.00),
(15, 136500.00, '2025-12-04 10:20:24', '2025-12-04 10:20:24', NULL, 0.00, NULL, 0.00, 0.00),
(16, 157500.00, '2025-12-04 10:20:32', '2025-12-04 10:20:32', NULL, 0.00, NULL, 0.00, 0.00),
(17, 11500.00, '2025-12-10 05:29:00', '2025-12-10 05:29:00', NULL, 0.00, NULL, 0.00, 0.00),
(18, 11500.00, '2025-12-11 05:00:47', '2025-12-11 05:00:47', NULL, 0.00, NULL, 0.00, 0.00),
(19, 57500.00, '2025-12-11 05:03:27', '2025-12-11 05:03:27', NULL, 0.00, NULL, 0.00, 0.00),
(20, 11500.00, '2025-12-11 06:15:18', '2025-12-11 06:15:18', 1, 0.00, NULL, 0.00, 0.00),
(21, 12880.00, '2025-12-11 13:45:56', '2025-12-11 13:45:56', 1, 1380.00, 'Cash', 15000.00, 2120.00),
(22, 20720.00, '2025-12-11 14:05:49', '2025-12-11 14:05:49', 1, 2220.00, 'Cash', 35000.00, 14280.00),
(23, 11760.00, '2025-12-11 14:11:34', '2025-12-11 14:11:34', 1, 1260.00, 'Cash', 12000.00, 240.00),
(24, 12880.00, '2025-12-11 14:40:47', '2025-12-11 14:40:47', 1, 1380.00, 'Cash', 50000.00, 37120.00),
(25, 12880.00, '2025-12-11 14:45:23', '2025-12-11 14:45:23', 1, 1380.00, 'Cash', 50000.00, 37120.00),
(26, 12880.00, '2025-12-11 14:50:21', '2025-12-11 14:50:21', 1, 1380.00, 'Cash', 50000.00, 37120.00),
(27, 11760.00, '2025-12-11 14:55:31', '2025-12-11 14:55:31', 1, 1260.00, 'Cash', 50000.00, 38240.00),
(28, 11760.00, '2025-12-11 15:00:59', '2025-12-11 15:00:59', 1, 1260.00, 'Cash', 12000.00, 240.00),
(29, 12880.00, '2025-12-11 15:05:24', '2025-12-11 15:05:24', 1, 1380.00, 'Cash', 13000.00, 120.00),
(30, 2464.00, '2025-12-11 15:07:00', '2025-12-11 15:07:00', 1, 264.00, 'Cash', 3000.00, 536.00),
(31, 11760.00, '2025-12-11 15:08:32', '2025-12-11 15:08:32', 1, 1260.00, 'Cash', 12000.00, 240.00),
(32, 12880.00, '2025-12-11 15:09:16', '2025-12-11 15:09:16', 1, 1380.00, 'Cash', 13000.00, 120.00),
(33, 3920.00, '2025-12-11 15:09:33', '2025-12-11 15:09:33', 1, 420.00, 'Cash', 4000.00, 80.00),
(34, 4704.00, '2025-12-11 15:13:07', '2025-12-11 15:13:07', 1, 504.00, 'Cash', 5000.00, 296.00),
(35, 11760.00, '2025-12-11 15:14:47', '2025-12-11 15:14:47', 1, 1260.00, 'Cash', 12000.00, 240.00),
(36, 11760.00, '2025-12-11 15:15:12', '2025-12-11 15:15:12', 1, 1260.00, 'Cash', 13000.00, 1240.00),
(37, 11760.00, '2025-12-11 15:16:26', '2025-12-11 15:16:26', 1, 1260.00, 'Cash', 13000.00, 1240.00),
(38, 12880.00, '2025-12-16 06:13:41', '2025-12-16 06:13:41', 1, 1380.00, 'Cash', 13000.00, 120.00),
(39, 64400.00, '2025-12-16 07:36:44', '2025-12-16 07:36:44', 1, 6900.00, 'Cash', 70000.00, 5600.00);

-- --------------------------------------------------------

--
-- Table structure for table `sale_items`
--

CREATE TABLE `sale_items` (
  `id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sale_items`
--

INSERT INTO `sale_items` (`id`, `sale_id`, `item_id`, `quantity`, `price`) VALUES
(1, 2, 29, 1, 11500.00),
(2, 3, 29, 1, 11500.00),
(3, 4, 29, 1, 11500.00),
(4, 5, 29, 1, 11500.00),
(6, 6, 29, 1, 11500.00),
(10, 10, 29, 1, 11500.00),
(11, 11, 29, 1, 11500.00),
(12, 12, 29, 10, 11500.00),
(14, 14, 29, 1, 11500.00),
(18, 17, 29, 1, 11500.00),
(21, 20, 29, 1, 11500.00),
(22, 21, 29, 1, 11500.00),
(28, 27, 40, 1, 10500.00),
(32, 31, 40, 1, 10500.00),
(35, 34, 42, 1, 4200.00),
(38, 37, 40, 1, 10500.00),
(39, 38, 29, 1, 11500.00),
(40, 39, 29, 5, 11500.00);

-- --------------------------------------------------------

--
-- Table structure for table `stock_movements`
--

CREATE TABLE `stock_movements` (
  `id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `movement_type` enum('IN','OUT','ADJUSTMENT') NOT NULL,
  `quantity` int(11) NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `movement_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `created_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stock_movements`
--

INSERT INTO `stock_movements` (`id`, `item_id`, `movement_type`, `quantity`, `reason`, `notes`, `movement_date`, `created_by`) VALUES
(1, 29, 'IN', 50, 'Supplier Purchase', 'test', '2025-12-16 06:06:51', 1),
(2, 29, 'OUT', 5, 'Damaged', 'test', '2025-12-16 06:16:32', 1);

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`id`, `name`, `contact_person`, `email`, `phone`, `address`, `created_at`) VALUES
(2, 'Global Electronics', 'Jane Doe', 'jane@globalelectronics.com', '555-0102', '456 Electronics Blvd', '2025-12-03 09:38:19'),
(4, 'Premium Parts Inc.', 'Alice Williams', 'alice@premiumparts.com', '555-0104', '321 Premium Ln', '2025-12-03 09:38:19');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `role` varchar(20) DEFAULT 'staff',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `full_name`, `role`, `created_at`) VALUES
(1, 'admin', 'admin123', 'Administrator', 'admin', '2025-12-10 05:20:04'),
(2, 'staff', 'staff123', 'Staff Member', 'staff', '2025-12-10 05:20:04'),
(10, 'luis123', '1234', 'Luis Daniel Panal', 'cashier', '2025-12-10 05:20:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `inventory_items`
--
ALTER TABLE `inventory_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_part_name` (`part_name`),
  ADD KEY `idx_category` (`category`),
  ADD KEY `fk_supplier` (`supplier_id`);

--
-- Indexes for table `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sale_date` (`sale_date`),
  ADD KEY `fk_sales_user` (`user_id`);

--
-- Indexes for table `sale_items`
--
ALTER TABLE `sale_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sale_id` (`sale_id`),
  ADD KEY `item_id` (`item_id`);

--
-- Indexes for table `stock_movements`
--
ALTER TABLE `stock_movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `idx_item_id` (`item_id`),
  ADD KEY `idx_movement_date` (`movement_date`),
  ADD KEY `idx_movement_type` (`movement_type`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `inventory_items`
--
ALTER TABLE `inventory_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT for table `sales`
--
ALTER TABLE `sales`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `sale_items`
--
ALTER TABLE `sale_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT for table `stock_movements`
--
ALTER TABLE `stock_movements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `inventory_items`
--
ALTER TABLE `inventory_items`
  ADD CONSTRAINT `fk_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `sales`
--
ALTER TABLE `sales`
  ADD CONSTRAINT `fk_sales_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `sale_items`
--
ALTER TABLE `sale_items`
  ADD CONSTRAINT `sale_items_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `sale_items_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `inventory_items` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `stock_movements`
--
ALTER TABLE `stock_movements`
  ADD CONSTRAINT `stock_movements_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `inventory_items` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `stock_movements_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
