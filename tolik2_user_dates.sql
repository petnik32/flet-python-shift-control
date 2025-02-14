-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: tolik2
-- ------------------------------------------------------
-- Server version	8.0.39

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
-- Table structure for table `user_dates`
--

DROP TABLE IF EXISTS `user_dates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_dates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fio` varchar(255) NOT NULL,
  `date_selected` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_dates`
--

LOCK TABLES `user_dates` WRITE;
/*!40000 ALTER TABLE `user_dates` DISABLE KEYS */;
INSERT INTO `user_dates` VALUES (20,'Иванчук Максим Андреевич','2025-01-30','2025-01-29 15:27:24'),(21,'Иванчук Максим Андреевич','2025-01-31','2025-01-29 15:27:24'),(23,'Иванчук Максим Андреевич','2025-02-14','2025-02-02 08:53:18'),(24,'Иванчук Максим Андреевич','2025-02-28','2025-02-02 08:53:18'),(25,'Иванчук Максим Андреевич','2025-02-26','2025-02-02 08:53:18'),(26,'Иванчук Максим Андреевич','2025-02-22','2025-02-02 08:58:39'),(27,'Иванчук Максим Андреевич','2025-02-25','2025-02-02 09:03:34'),(28,'Иванчук Максим Андреевич','2025-02-18','2025-02-02 17:52:02'),(29,'Петровский Никита Александрович','2025-02-19','2025-02-08 07:32:46'),(30,'Петровский Никита Александрович','2025-02-28','2025-02-08 07:32:46'),(31,'Петровский Никита Александрович','2025-02-25','2025-02-08 07:32:46');
/*!40000 ALTER TABLE `user_dates` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-02-09 12:15:35
