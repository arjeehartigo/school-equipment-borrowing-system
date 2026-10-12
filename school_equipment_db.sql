-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 12, 2026 at 05:56 PM
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
-- Database: `school_equipment_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `barrows`
--

CREATE TABLE `barrows` (
  `id` int(11) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `borrower` varchar(100) NOT NULL,
  `role` varchar(50) NOT NULL,
  `purpose` varchar(100) NOT NULL,
  `date_borrowed` date NOT NULL,
  `date_returned` date DEFAULT NULL,
  `status` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `barrows`
--

INSERT INTO `barrows` (`id`, `item_name`, `borrower`, `role`, `purpose`, `date_borrowed`, `date_returned`, `status`) VALUES
(7, 'pencil', 'arjeeh', 'Student', 'exam', '2026-09-16', '2026-09-16', 'Returned'),
(9, 'books', 'ryan', 'Student', 'for exam', '2026-09-16', '2026-10-10', 'Returned'),
(10, 'vape', 'james', 'Student', 'for fun\r\n', '2026-09-18', '2026-09-18', 'Returned'),
(12, 'bola', 'timo', 'Student', 'for games\r\n', '2026-10-10', '2926-10-10', 'Borrowed'),
(13, 'ballpen', 'timothy', 'Student', 'exam', '2026-10-11', '2026-10-13', 'Returned');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` varchar(20) DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES
(2, 'admin', '1234', 'user'),
(3, 'teacher1', 'pass123', 'user'),
(4, 'student1', 'mypassword', 'user'),
(8, 'timo', 'fruto', 'user'),
(9, 'arjeeh', 'secret123', 'admin');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `barrows`
--
ALTER TABLE `barrows`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `barrows`
--
ALTER TABLE `barrows`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
