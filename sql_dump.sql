CREATE DATABASE  IF NOT EXISTS `robo_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `testdb`;
-- MySQL dump 10.13  Distrib 8.0.19, for macos10.15 (x86_64)
--
-- Host: 127.0.0.1    Database: testdb
-- ------------------------------------------------------
-- Server version	8.0.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `robo_tb`
--

DROP TABLE IF EXISTS `robo_tb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `robo_tb` (
  `id` int DEFAULT NULL,
  `salt` varchar(60) DEFAULT NULL,
  `hash_pword` varchar(80) DEFAULT NULL,
  `curr_room` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `robo_tb`
--

LOCK TABLES `robo_tb` WRITE;
/*!40000 ALTER TABLE `robo_tb` DISABLE KEYS */;
INSERT INTO `robo_tb` VALUES (1,'$2b$14$y1.Hk0K5ZlOddaVF1oWP6.','$2b$14$y1.Hk0K5ZlOddaVF1oWP6.NPRLt8YPfDHeOa2DkmU63E1Wvii5FOy',0),(2,'$2b$14$ZmesmMUmDrSdaFLWpMf6Fe','$2b$14$ZmesmMUmDrSdaFLWpMf6FeWmuF3eB/WBFxC6HUKTvgfdfaGWWBOBe',0),(3,'$2b$14$IVxGsAYb8ycDW1JnTyDTuO','$2b$14$IVxGsAYb8ycDW1JnTyDTuOUjyIFwgttZeGafTGV6i1Gj3qo41VXE6',0),(4,'$2b$14$/Dq6GdyDWR9CrYzkrbnUW.','$2b$14$/Dq6GdyDWR9CrYzkrbnUW.qAFqSuvcubQq/MXn1sJgMhfn8h29OLW',0);
/*!40000 ALTER TABLE `robo_tb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_tb`
--

DROP TABLE IF EXISTS `room_tb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_tb` (
  `id` int DEFAULT NULL,
  `status` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_tb`
--

LOCK TABLES `room_tb` WRITE;
/*!40000 ALTER TABLE `room_tb` DISABLE KEYS */;
INSERT INTO `room_tb` VALUES (1,0),(2,0),(3,0),(4,0),(5,0);
/*!40000 ALTER TABLE `room_tb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_tb`
--

DROP TABLE IF EXISTS `staff_tb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_tb` (
  `name` text(255) DEFAULT NULL,
  `salt` varchar(60) DEFAULT NULL,
  `hash_pword` varchar(80) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_tb`
--

LOCK TABLES `staff_tb` WRITE;
/*!40000 ALTER TABLE `staff_tb` DISABLE KEYS */;
INSERT INTO `staff_tb` VALUES ('Gwen','$2b$14$getcgbCfJbfBPe5BgRrcGO','$2b$14$getcgbCfJbfBPe5BgRrcGOf/LhvnalJ6GkUa5ZJL8Z3OtZQ1wBCPq'),('Nico','$2b$14$xE0hfDYcUE5B0y2YCIOhue','$2b$14$xE0hfDYcUE5B0y2YCIOhueSi1m9Zbv8lvwHMGuePh0xk6zJxPkHBK'),('Amiel','$2b$14$iQeWFL/oIeJw8nxcsMDPO.','$2b$14$iQeWFL/oIeJw8nxcsMDPO.JOKaKE9MTx9pz9mmfi9cSyLWXESQRBW'),('Bellard','$2b$14$21KgNRRVsCG8yHwmeerP5u','$2b$14$21KgNRRVsCG8yHwmeerP5uraOPoJBU5wQ03UuHsaco6.zaBwARy4O');
/*!40000 ALTER TABLE `staff_tb` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-04-02  8:21:04
