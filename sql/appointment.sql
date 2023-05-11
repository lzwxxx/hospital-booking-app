SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `appointment` 
--

CREATE DATABASE IF NOT EXISTS `appointment` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `appointment`;

-- --------------------------------------------------------

--
-- Table structure for table `appointment`
--

DROP TABLE IF EXISTS `appointment`;
CREATE TABLE IF NOT EXISTS `appointment` (
  	`appointment_id` int NOT NULL AUTO_INCREMENT,
	`patient_id` int NOT NULL, 
	`doctor_id` int NOT NULL,
	`date` date NOT NULL,
	`time` int NOT NULL, 
	PRIMARY KEY (`appointment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ALTER TABLE `appointment` 
-- ADD CONSTRAINT `patient_id` FOREIGN KEY (`patient_id`) REFERENCES `patient`.`patient`(`patient_id`) 
-- ON DELETE RESTRICT ON UPDATE RESTRICT; 

-- ALTER TABLE `appointment` 
-- ADD CONSTRAINT `doctor_id` FOREIGN KEY (`doctor_id`) REFERENCES `doctor`.`doctor`(`doctor_id`) 
-- ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Dumping data for table `appointment`
--

INSERT INTO `appointment` (`patient_id`, `doctor_id`, `date`, `time`) VALUES
(1, 1, '2022-03-02', 10), 
(2, 1, '2022-03-05', 15),
(3, 2, '2022-03-05', 15),
(4, 3, '2022-03-05', 15),
(5, 4, '2022-03-05', 15),
(6, 5, '2022-03-05', 15),
(7, 6, '2022-03-05', 15),
(8, 7, '2022-03-05', 15),
(9, 8, '2022-03-05', 15),
(10, 9, '2022-03-05', 15),
(11, 5, '2022-03-06', 15),
(12, 3, '2022-03-07', 17),
(13, 2, '2022-03-08', 17),
(14, 6, '2022-03-08', 17),
(15, 1, '2022-03-09', 17),
(16, 4, '2022-03-09', 17),
(17, 5, '2022-03-09', 17);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;