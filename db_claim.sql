-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 09, 2025 at 03:07 PM
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
  `user` varchar(30) NOT NULL,
  `reference` varchar(50) NOT NULL,
  `week_report` varchar(30) NOT NULL,
  `close_claim` date NOT NULL,
  `bin` int(11) NOT NULL,
  `routing` varchar(50) NOT NULL,
  `claim_entry_boa` varchar(50) NOT NULL,
  `remarks` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_claim`
--

INSERT INTO `tb_claim` (`claim_id`, `claim_status`, `claim_number`, `claim_inisiator`, `claim_type`, `terminal`, `no_acq`, `no_pan`, `no_receipt`, `trx_date`, `trx_time`, `due_date`, `claim_date`, `trx_amount`, `description`, `user`, `reference`, `week_report`, `close_claim`, `bin`, `routing`, `claim_entry_boa`, `remarks`) VALUES
(8002, 'Solved', 'WDL/20250127/34', '004205/ATMi-Klaim/25/01/27', 'Web Claim', 1000002, 10011, 232221929122235, 1002, '2025-05-01', '09:31:00', '2025-05-31', '2025-05-17', 200000, 'Transaction Not Complete', 'admin', '0', 'W3-May-25', '2025-05-31', 411012, 'ALTO', 'Solved', '....'),
(8004, 'Crosscheck', '1', '1', 'Web Claim AJ', 1, 1, 1, 1, '2025-05-09', '21:00:00', '2025-05-23', '2025-05-22', 100000, '1', '', '1', '1', '2025-05-31', 1, 'ARTAJASA', 'On Process', '1'),
(8005, 'Active', '1', '1', 'Web Claim AJ', 1, 1, 1, 1, '2025-05-22', '20:08:00', '2025-05-29', '2025-05-29', 1111110000, '1', 'Rudi', '1', '1', '2025-05-23', 1, 'ARTAJASA', 'On Process', '1');

-- --------------------------------------------------------

--
-- Table structure for table `tb_user`
--

CREATE TABLE `tb_user` (
  `user_id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` enum('admin','user') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_user`
--

INSERT INTO `tb_user` (`user_id`, `username`, `password`, `role`) VALUES
(1, 'Rudi', '123', 'admin'),
(8, 'Ronaldo', '123', 'user'),
(9, 'Rolando', '123', 'user'),
(10, 'Ricky', '111', 'admin'),
(11, 'Ricky', '111', 'admin'),
(12, 'Jodi', '11', 'admin'),
(13, 'Nana', '123', 'user');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_claim`
--
ALTER TABLE `tb_claim`
  ADD PRIMARY KEY (`claim_id`);

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
  MODIFY `claim_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8007;

--
-- AUTO_INCREMENT for table `tb_user`
--
ALTER TABLE `tb_user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
