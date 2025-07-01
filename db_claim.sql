-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 24, 2025 at 05:18 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_claim`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_claim`
--

CREATE TABLE `tb_claim` (
  `claim_id` int(11) NOT NULL,
  `claim_status` varchar(50) NOT NULL,
  `claim_number` varchar(50) NOT NULL,
  `claim_inisiator` varchar(50) NOT NULL,
  `claim_type` varchar(50) NOT NULL,
  `terminal` int(11) NOT NULL,
  `no_acq` int(11) NOT NULL,
  `no_pan` bigint(11) NOT NULL,
  `no_receipt` int(11) NOT NULL,
  `trx_date` date NOT NULL,
  `trx_time` time NOT NULL,
  `due_date` date NOT NULL,
  `claim_date` date NOT NULL,
  `trx_amount` float NOT NULL,
  `description` text NOT NULL,
  `user_id` int(11) NOT NULL,
  `user` varchar(30) NOT NULL,
  `reference` varchar(50) NOT NULL,
  `week_report` varchar(30) NOT NULL,
  `close_claim` date NOT NULL,
  `bin` int(11) NOT NULL,
  `error_code` int(6) DEFAULT NULL,
  `routing` varchar(50) NOT NULL,
  `claim_entry_boa` varchar(50) NOT NULL,
  `remarks` text NOT NULL,
  `approved_by` varchar(50) DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_claim`
--

INSERT INTO `tb_claim` (`claim_id`, `claim_status`, `claim_number`, `claim_inisiator`, `claim_type`, `terminal`, `no_acq`, `no_pan`, `no_receipt`, `trx_date`, `trx_time`, `due_date`, `claim_date`, `trx_amount`, `description`, `user_id`, `user`, `reference`, `week_report`, `close_claim`, `bin`, `error_code`, `routing`, `claim_entry_boa`, `remarks`, `approved_by`, `approved_at`) VALUES
(8002, 'Solved', 'WDL/20250127/34', '004205/ATMi-Klaim/25/01/27', 'Web Claim', 1000002, 10011, 232221929122235, 1002, '2025-05-01', '09:31:00', '2025-05-31', '2025-05-17', 200000, 'Transaction Not Complete', 0, '', '0', 'W3-May-25', '2025-05-31', 411012, NULL, 'ALTO', 'Solved', '....', NULL, NULL),
(8004, 'Reject', '1', '1', 'Web Claim AJ', 1, 1, 1, 1, '2025-05-09', '21:00:00', '2025-05-23', '2025-05-22', 100000, '1', 0, '', '1', '1', '2025-05-31', 1, NULL, 'ARTAJASA', 'On Process', '1', NULL, NULL),
(8005, 'Active', '1', '1', 'Web Claim AJ', 1, 1, 1, 1, '2025-05-22', '20:08:00', '2025-06-24', '2025-05-29', 1111110000, '1', 15, '12', '1', '1', '2025-05-23', 1, NULL, 'ARTAJASA', 'On Process', '1', NULL, NULL),
(8007, 'Active', '--', '004206/ATMi-Klaim/25/06/22', 'Pro-active Claim', 1111322, 12345, 1231298989746377, 1255, '2025-06-21', '08:31:00', '2025-06-25', '2025-06-22', 1500000, 'On Check', 12, 'Jodi', '', '', '0000-00-00', 0, NULL, 'ARTAJASA', 'On Process', '', NULL, NULL),
(8008, 'Active', '--', '004207/ATMi-Klaim/25/06/24', 'Pro-active Claim', 12345678, 12345, 1231298989746377, 1255, '2025-06-23', '21:57:00', '2025-06-25', '2025-06-24', 1500000, 'DIcheck lur', 12, '', '', '', '0000-00-00', 0, NULL, 'ALTO', 'On Process', '', 'Jaya', '2025-06-24 21:00:04'),
(8009, 'Active', '--', '004208/ATMi-Klaim/25/06/24', 'Pro-active Claim', 12345678, 12345, 1231298989746377, 1255, '2025-06-23', '00:52:00', '2025-06-27', '2025-06-24', 1500000, 'DIcheck lur', 8, '', '', '', '0000-00-00', 0, NULL, 'ALTO', 'On Process', '', 'Jaya', '2025-06-24 21:00:06'),
(8010, 'Active', '--', '004209/ATMi-Klaim/25/06/24', 'Pro-active Claim', 12345678, 12345, 1231298989746377, 1255, '2025-06-23', '00:52:00', '2025-06-27', '2025-06-24', 1500000, 'DIcheck lur', 8, '', '', '', '0000-00-00', 0, NULL, 'ALTO', 'On Process', '', 'Jaya', '2025-06-24 21:00:08'),
(8011, 'Active', '--', '004210/ATMi-Klaim/25/06/24', 'Pro-active Claim', 1001234, 2233, 988789928625252, 3333, '2025-06-23', '21:49:00', '2025-06-27', '2025-06-24', 500000, 'Masih dicek', 12, '', '', '', '0000-00-00', 0, NULL, 'ALTO', 'On Process', '', 'Jodi', '2025-06-24 21:54:53');

-- --------------------------------------------------------

--
-- Table structure for table `tb_log`
--

CREATE TABLE `tb_log` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `action` text DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_log`
--

INSERT INTO `tb_log` (`log_id`, `user_id`, `username`, `action`, `timestamp`) VALUES
(1, 15, 'Jaya', 'Logout', '2025-06-24 19:21:18'),
(2, 16, 'test', 'Login berhasil', '2025-06-24 19:21:26'),
(3, 16, 'test', 'Logout', '2025-06-24 19:21:30'),
(4, 15, 'Jaya', 'Login berhasil', '2025-06-24 19:21:34'),
(5, 12, 'Jodi', 'Login berhasil', '2025-06-24 19:24:37'),
(6, 12, 'Jodi', 'Login berhasil', '2025-06-24 19:24:54'),
(7, 12, 'Jodi', 'Update klaim ID 8006', '2025-06-24 19:41:37'),
(8, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:41:50'),
(9, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:45:16'),
(10, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:46:48'),
(11, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:48:06'),
(12, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:48:22'),
(13, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:49:21'),
(14, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:49:42'),
(15, 12, 'Jodi', 'Update klaim ID 8005', '2025-06-24 19:51:55'),
(16, 12, 'Jodi', 'Login berhasil', '2025-06-24 20:14:56'),
(17, 12, 'Jodi', 'Login berhasil', '2025-06-24 20:15:18'),
(18, 12, 'Jodi', 'Logout', '2025-06-24 20:46:32'),
(19, 12, 'Jodi', 'Login berhasil', '2025-06-24 20:46:41'),
(20, 12, 'Jodi', 'Logout', '2025-06-24 20:47:01'),
(21, 8, 'Ronaldo', 'Login berhasil', '2025-06-24 20:47:11'),
(22, 8, 'Ronaldo', 'Update klaim ID 8008', '2025-06-24 20:54:06'),
(23, 8, 'Ronaldo', 'Update klaim ID 8008', '2025-06-24 20:55:37'),
(24, 8, 'Ronaldo', 'Update klaim ID 8008', '2025-06-24 20:56:41'),
(25, 8, 'Ronaldo', 'Logout', '2025-06-24 20:56:54'),
(26, 15, 'Jaya', 'Login berhasil', '2025-06-24 20:57:03'),
(27, 15, 'Jaya', 'Update klaim ID 8010', '2025-06-24 20:57:11'),
(28, 15, 'Jaya', 'Logout', '2025-06-24 21:37:32'),
(29, 15, 'Jaya', 'Login berhasil', '2025-06-24 21:37:50'),
(30, 15, 'Jaya', 'Update klaim ID 8005', '2025-06-24 21:43:50'),
(31, 15, 'Jaya', 'Logout', '2025-06-24 21:45:04'),
(32, 8, 'Ronaldo', 'Login berhasil', '2025-06-24 21:45:10'),
(33, 8, 'Ronaldo', 'Update klaim ID 8011', '2025-06-24 21:49:36'),
(34, 8, 'Ronaldo', 'Update klaim ID 8011', '2025-06-24 21:51:29'),
(35, 8, 'Ronaldo', 'Update klaim ID 8011', '2025-06-24 21:52:15'),
(36, 8, 'Ronaldo', 'Update klaim ID 8011', '2025-06-24 21:53:16'),
(37, 8, 'Ronaldo', 'Logout', '2025-06-24 21:53:27'),
(38, 12, 'Jodi', 'Login berhasil', '2025-06-24 21:53:32'),
(39, 12, 'Jodi', 'Update klaim ID 8011', '2025-06-24 21:54:40'),
(40, 12, 'Jodi', 'Update klaim ID 8011', '2025-06-24 21:56:26'),
(41, 12, 'Jodi', 'Update klaim ID 8008', '2025-06-24 21:57:04');

-- --------------------------------------------------------

--
-- Table structure for table `tb_user`
--

CREATE TABLE `tb_user` (
  `user_id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` enum('admin','user') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_user`
--

INSERT INTO `tb_user` (`user_id`, `username`, `password`, `role`) VALUES
(1, 'Rudi', '$2b$12$qprkf727rzwVvN1VtB1eouFdJo7HGMgLNSPzDEE3KgvMUhrdbJBFW', 'admin'),
(8, 'Ronaldo', '$2b$12$J46SVxpfxuK7MN8KYw0HXuVy51/vlPKMD4qApofzmc7hmZD68nWIW', 'user'),
(9, 'Rolando', '$2b$12$meinYjctZL4CXj7tZBK./.tmB9COnxaXzRDp7c759TABEEda3F3Wu', 'user'),
(10, 'Ricky', '$2b$12$7CMzllqzinbJXvAnDsV8X.EV1bLB1U4W6NuCulb/iwXnnTpxJWT0S', 'admin'),
(11, 'Ricky', '$2b$12$RHaXBJODjfpmyr/AbaokZ.gj2qVHioCWTZ0rw6BvFlbyeValWv6im', 'admin'),
(12, 'Jodi', '$2b$12$wUig8Z1BsTLe5BaBRKqXle0bvCcTdgYj4JkVsbEVz/GFH3.dpTtM6', 'admin'),
(13, 'Nana', '$2b$12$TLEPmO7kshxwoIs6cGrtK.uxmJycprJkQJ8VONZeQtfASOEAx9RRC', 'user'),
(15, 'Jaya', '$2b$12$za0PaxDh9rVv5UWy/tNXyeDNdyiE8fz0W.eSdVT92kxYJ/R1jHnsG', 'admin'),
(16, 'test', '$2b$12$qpA4.98im16PnVRVwlvrtuFv.sDKoiDAsjqE9MXCr5H9FvX6k5CTy', 'user');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_claim`
--
ALTER TABLE `tb_claim`
  ADD PRIMARY KEY (`claim_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `tb_log`
--
ALTER TABLE `tb_log`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `tb_user`
--
ALTER TABLE `tb_user`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_claim`
--
ALTER TABLE `tb_claim`
  MODIFY `claim_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8012;

--
-- AUTO_INCREMENT for table `tb_log`
--
ALTER TABLE `tb_log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT for table `tb_user`
--
ALTER TABLE `tb_user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
