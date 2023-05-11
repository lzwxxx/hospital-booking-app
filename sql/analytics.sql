-- --------------------------------------------------------

-- PURPOSE OF ANALYTICS DATABASE:
	-- 1. using the data to: 
		-- > doctor's peak hour (more doctors to accept more patients)
        -- > scheduling for the following week 
        
-- Assumptions:
	-- each doctor have FIXED time schedule for each week (A - 8-3 // B - 10-6) 
    -- each time slot is 1 hour
    -- patients are okay to consult with other available doctors in the event where their desired doctor is not available for their desired time slot
    
--

CREATE DATABASE IF NOT EXISTS `analytics` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `analytics`;

--
-- Table structure for table `weekly_average_patient`
--
DROP TABLE IF EXISTS `weekly_average_patient`;
CREATE TABLE IF NOT EXISTS `weekly_average_patient` (
  `hour`  int NOT NULL,
  `average_num_patients` int NOT NULL,
  PRIMARY KEY (`hour`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `weekly_average_patient`
--
INSERT INTO `weekly_average_patient` (`hour`, `average_num_patients`) VALUES
('0', '4'),
('1', '4'),
('2', '2'),
('3', '1'),
('4', '1'),
('5', '1'),
('6', '1'),
('7', '5'),
('8', '5'),
('9', '5'),
('10', '2'),
('11', '0'),
('12', '1'),
('13', '3'),
('14', '4'),
('15', '2'),
('16', '2'),
('17', '2'),
('18', '0'),
('19', '2'),
('20', '4'),
('21', '3'),
('22', '3'),
('23', '2');


--
-- Table structure for table `weekly_average_patient_snapshots`
--
DROP TABLE IF EXISTS `weekly_average_patient_snapshots`;
CREATE TABLE IF NOT EXISTS `weekly_average_patient_snapshots` (
  `hour`  int NOT NULL,
  `average_num_patients` int NOT NULL,
  `snapshot_timestamp` datetime, 
  PRIMARY KEY (`snapshot_timestamp`,`hour`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO `weekly_average_patient_snapshots` (`hour`, `average_num_patients`,`snapshot_timestamp`) VALUES
('0', '4','2022-01-01'),
('1', '4','2022-01-01'),
('2', '2','2022-01-01'),
('3', '1','2022-01-01'),
('4', '1','2022-01-01'),
('5', '1','2022-01-01'),
('6', '1','2022-01-01'),
('7', '5','2022-01-01'),
('8', '5','2022-01-01'),
('9', '5','2022-01-01'),
('10', '2','2022-01-01'),
('11', '0','2022-01-01'),
('12', '1','2022-01-01'),
('13', '3','2022-01-01'),
('14', '4','2022-01-01'),
('15', '2','2022-01-01'),
('16', '2','2022-01-01'),
('17', '2','2022-01-01'),
('18', '0','2022-01-01'),
('19', '2','2022-01-01'),
('20', '4','2022-01-01'),
('21', '3','2022-01-01'),
('22', '3','2022-01-01'),
('23', '2','2022-01-01');