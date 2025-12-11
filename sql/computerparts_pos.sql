-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 11, 2025 at 09:33 AM
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
(1, 'ASUS ROG Strix B550-F Gaming', 'Motherboard', 'SAARA', 'ROG-B550-F', 0, 8500.00, 10500.00, 4, '2025-12-02 06:51:17', '2025-12-10 08:49:49'),
(3, 'Corsair Vengeance 16GB DDR4', 'RAM', 'Corsair', 'CMK16GX4', 30, 3200.00, 4200.00, 2, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(4, 'Samsung 980 PRO 1TB NVMe', 'Storage', 'Samsung', '980-PRO-1TB', 25, 6500.00, 8000.00, 2, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(5, 'MSI GeForce RTX 3060', 'Graphics Card', 'MSI', 'RTX-3060-12G', 10, 18000.00, 22000.00, NULL, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(6, 'Corsair RM750x 750W', 'Power Supply', 'Corsair', 'RM750X', 18, 5500.00, 7000.00, 2, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(7, 'NZXT H510 Elite', 'Case', 'NZXT', 'H510-ELITE', 12, 7000.00, 8500.00, NULL, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(8, 'Cooler Master Hyper 212', 'CPU Cooler', 'Cooler Master', 'HYPER-212', 22, 1500.00, 2200.00, NULL, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(9, 'Logitech G502 HERO', 'Mouse', 'Logitech', 'G502-HERO', 35, 2500.00, 3500.00, 4, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(10, 'Corsair K70 RGB', 'Keyboard', 'Corsair', 'K70-RGB-MK2', 20, 6000.00, 7500.00, 4, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(11, 'ASUS TUF Gaming VG27AQ', 'Monitor', 'ASUS', 'VG27AQ', 8, 15000.00, 18500.00, NULL, '2025-12-02 06:51:17', '2025-12-02 06:51:17'),
(13, 'ASUS ROG Strix B550-F Gaming', 'Motherboard', 'ASUS', 'ROG-B550-F', 0, 8500.00, 10500.00, NULL, '2025-12-02 08:23:52', '2025-12-04 10:20:32'),
(15, 'Corsair Vengeance 16GB DDR4', 'RAM', 'Corsair', 'CMK16GX4', 30, 3200.00, 4200.00, 2, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(16, 'Samsung 980 PRO 1TB NVMe', 'Storage', 'Samsung', '980-PRO-1TB', 25, 6500.00, 8000.00, 2, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(17, 'MSI GeForce RTX 3060', 'Graphics Card', 'MSI', 'RTX-3060-12G', 10, 18000.00, 22000.00, NULL, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(18, 'Corsair RM750x 750W', 'Power Supply', 'Corsair', 'RM750X', 17, 5500.00, 7000.00, 2, '2025-12-02 08:23:52', '2025-12-04 07:38:57'),
(19, 'NZXT H510 Elite', 'Case', 'NZXT', 'H510-ELITE', 12, 7000.00, 8500.00, NULL, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(20, 'Cooler Master Hyper 212', 'CPU Cooler', 'Cooler Master', 'HYPER-212', 22, 1500.00, 2200.00, NULL, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(21, 'Logitech G502 HERO', 'Mouse', 'Logitech', 'G502-HERO', 35, 2500.00, 3500.00, 4, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(22, 'Corsair K70 RGB', 'Keyboard', 'Corsair', 'K70-RGB-MK2', 19, 6000.00, 7500.00, 4, '2025-12-02 08:23:52', '2025-12-04 07:38:52'),
(23, 'ASUS TUF Gaming VG27AQ', 'Monitor', 'ASUS', 'VG27AQ', 8, 15000.00, 18500.00, NULL, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(24, 'Western Digital 2TB HDD', 'Storage', 'WD', 'WD-BLUE-2TB', 28, 2800.00, 3500.00, 2, '2025-12-02 08:23:52', '2025-12-02 08:23:52'),
(27, 'Part', 'RAM', 'ASUS', '99292911', 15, 30.00, 40.00, NULL, '2025-12-03 09:27:43', '2025-12-04 10:11:48'),
(28, 'ASUS ROG Strix B550-F Gaming', 'Motherboard', 'ASUS', 'ROG-B550-F', 15, 8500.00, 10500.00, NULL, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(29, 'AMD Ryzen 5 5600X', 'Processor', 'AMD', '5600X', 9, 9500.00, 11500.00, 2, '2025-12-03 09:38:19', '2025-12-11 06:15:18'),
(30, 'Corsair Vengeance 16GB DDR4', 'RAM', 'Corsair', 'CMK16GX4', 30, 3200.00, 4200.00, 2, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(31, 'Samsung 980 PRO 1TB NVMe', 'Storage', 'Samsung', '980-PRO-1TB', 25, 6500.00, 8000.00, 2, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(32, 'MSI GeForce RTX 3060', 'Graphics Card', 'MSI', 'RTX-3060-12G', 10, 18000.00, 22000.00, NULL, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(33, 'Corsair RM750x 750W', 'Power Supply', 'Corsair', 'RM750X', 18, 5500.00, 7000.00, 2, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(34, 'NZXT H510 Elite', 'Case', 'NZXT', 'H510-ELITE', 12, 7000.00, 8500.00, NULL, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(35, 'Cooler Master Hyper 212', 'CPU Cooler', 'Cooler Master', 'HYPER-212', 22, 1500.00, 2200.00, NULL, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(36, 'Logitech G502 HERO', 'Mouse', 'Logitech', 'G502-HERO', 35, 2500.00, 3500.00, 4, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(37, 'Corsair K70 RGB', 'Keyboard', 'Corsair', 'K70-RGB-MK2', 20, 6000.00, 7500.00, 4, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(38, 'ASUS TUF Gaming VG27AQ', 'Monitor', 'ASUS', 'VG27AQ', 7, 15000.00, 18500.00, NULL, '2025-12-03 09:38:19', '2025-12-04 07:38:54'),
(39, 'Western Digital 2TB HDD', 'Storage', 'WD', 'WD-BLUE-2TB', 28, 2800.00, 3500.00, 2, '2025-12-03 09:38:19', '2025-12-03 09:38:19'),
(40, 'ASUS ROG Strix B550-F Gaming', 'Motherboard', 'ASUS', 'ROG-B550-F', 15, 8500.00, 10500.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(41, 'AMD Ryzen 5 5600X', 'Processor', 'AMD', '5600X', 14, 9500.00, 11500.00, NULL, '2025-12-10 04:10:31', '2025-12-11 05:03:27'),
(42, 'Corsair Vengeance 16GB DDR4', 'RAM', 'Corsair', 'CMK16GX4', 30, 3200.00, 4200.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(43, 'Samsung 980 PRO 1TB NVMe', 'Storage', 'Samsung', '980-PRO-1TB', 25, 6500.00, 8000.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(44, 'MSI GeForce RTX 3060', 'Graphics Card', 'MSI', 'RTX-3060-12G', 10, 18000.00, 22000.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(45, 'Corsair RM750x 750W', 'Power Supply', 'Corsair', 'RM750X', 18, 5500.00, 7000.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(46, 'NZXT H510 Elite', 'Case', 'NZXT', 'H510-ELITE', 12, 7000.00, 8500.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(47, 'Cooler Master Hyper 212', 'CPU Cooler', 'Cooler Master', 'HYPER-212', 22, 1500.00, 2200.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(48, 'Logitech G502 HERO', 'Mouse', 'Logitech', 'G502-HERO', 35, 2500.00, 3500.00, 4, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(49, 'Corsair K70 RGB', 'Keyboard', 'Corsair', 'K70-RGB-MK2', 20, 6000.00, 7500.00, 4, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(50, 'ASUS TUF Gaming VG27AQ', 'Monitor', 'ASUS', 'VG27AQ', 8, 15000.00, 18500.00, NULL, '2025-12-10 04:10:31', '2025-12-10 04:10:31'),
(51, 'Western Digital 2TB HDD', 'Storage', 'WD', 'WD-BLUE-2TB', 28, 2800.00, 3500.00, 2, '2025-12-10 04:10:31', '2025-12-10 04:10:31');

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `id` int(11) NOT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `sale_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sales`
--

INSERT INTO `sales` (`id`, `total`, `created_at`, `sale_date`, `user_id`) VALUES
(2, 11500.00, '2025-12-03 10:05:26', '2025-12-03 10:05:26', NULL),
(3, 11500.00, '2025-12-03 10:05:40', '2025-12-03 10:05:40', NULL),
(4, 11500.00, '2025-12-03 10:07:55', '2025-12-03 10:07:55', NULL),
(5, 22000.00, '2025-12-03 10:09:59', '2025-12-03 10:09:59', NULL),
(6, 11500.00, '2025-12-04 07:38:36', '2025-12-04 07:38:36', NULL),
(7, 7500.00, '2025-12-04 07:38:52', '2025-12-04 07:38:52', NULL),
(8, 18500.00, '2025-12-04 07:38:54', '2025-12-04 07:38:54', NULL),
(9, 7000.00, '2025-12-04 07:38:57', '2025-12-04 07:38:57', NULL),
(10, 11500.00, '2025-12-04 09:58:42', '2025-12-04 09:58:42', NULL),
(11, 11500.00, '2025-12-04 10:11:25', '2025-12-04 10:11:25', NULL),
(12, 115000.00, '2025-12-04 10:11:36', '2025-12-04 10:11:36', NULL),
(13, 400.00, '2025-12-04 10:11:48', '2025-12-04 10:11:48', NULL),
(14, 22000.00, '2025-12-04 10:20:12', '2025-12-04 10:20:12', NULL),
(15, 136500.00, '2025-12-04 10:20:24', '2025-12-04 10:20:24', NULL),
(16, 157500.00, '2025-12-04 10:20:32', '2025-12-04 10:20:32', NULL),
(17, 11500.00, '2025-12-10 05:29:00', '2025-12-10 05:29:00', NULL),
(18, 11500.00, '2025-12-11 05:00:47', '2025-12-11 05:00:47', NULL),
(19, 57500.00, '2025-12-11 05:03:27', '2025-12-11 05:03:27', NULL),
(20, 11500.00, '2025-12-11 06:15:18', '2025-12-11 06:15:18', 1);

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
(5, 5, 1, 1, 10500.00),
(6, 6, 29, 1, 11500.00),
(7, 7, 22, 1, 7500.00),
(8, 8, 38, 1, 18500.00),
(9, 9, 18, 1, 7000.00),
(10, 10, 29, 1, 11500.00),
(11, 11, 29, 1, 11500.00),
(12, 12, 29, 10, 11500.00),
(13, 13, 27, 10, 40.00),
(14, 14, 29, 1, 11500.00),
(15, 14, 1, 1, 10500.00),
(16, 15, 1, 13, 10500.00),
(17, 16, 13, 15, 10500.00),
(18, 17, 29, 1, 11500.00),
(19, 18, 41, 1, 11500.00),
(20, 19, 41, 5, 11500.00),
(21, 20, 29, 1, 11500.00);

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
(4, 'Premium Parts Inc.', 'Alice Williams', 'alice@premiumparts.com', '555-0104', '321 Premium Ln', '2025-12-03 09:38:19'),
(7, 'test', 'testt', '123@gmail.com', '124124141', '124141', '2025-12-10 08:41:18'),
(8, '412412', '12412', '123124', '412', '1241', '2025-12-10 08:43:39'),
(9, '124', '41241', '124', '241', '1241241', '2025-12-10 08:43:43'),
(10, '12414', '4124', '141', '1412412', '41241', '2025-12-10 08:43:52'),
(11, '531', '531', '531', '12', '531', '2025-12-10 08:43:57');

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
(8, 'test', '123', NULL, 'cashier', '2025-12-10 05:20:04'),
(9, 'testst', '12414', NULL, 'cashier', '2025-12-10 05:20:04'),
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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT for table `sales`
--
ALTER TABLE `sales`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `sale_items`
--
ALTER TABLE `sale_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

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
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
