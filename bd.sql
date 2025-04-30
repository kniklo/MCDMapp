CREATE DATABASE  IF NOT EXISTS `mcdmapp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `mcdmapp`;
-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: mcdmapp
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `alternative`
--

DROP TABLE IF EXISTS `alternative`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alternative` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(65) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  FULLTEXT KEY `ft_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alternative_evaluation`
--

DROP TABLE IF EXISTS `alternative_evaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alternative_evaluation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `analysis_alternative_id` int NOT NULL,
  `analysis_criterion_id` int NOT NULL,
  `subj_value` float NOT NULL,
  `subj_value_relative` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_altev_alt_id_idx` (`analysis_alternative_id`),
  KEY `fk_altev_cr_id_idx` (`analysis_criterion_id`),
  CONSTRAINT `fk_altev_alt_id` FOREIGN KEY (`analysis_alternative_id`) REFERENCES `analysis_alternative` (`id`),
  CONSTRAINT `fk_altev_cr_id` FOREIGN KEY (`analysis_criterion_id`) REFERENCES `analysis_criterion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysis`
--

DROP TABLE IF EXISTS `analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `analysis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `expert_id` int NOT NULL,
  `task_id` int NOT NULL,
  `create_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fk_expert_task_uq` (`expert_id`,`task_id`),
  KEY `fk_expert_has_task_task1_idx` (`task_id`) /*!80000 INVISIBLE */,
  KEY `fk_expert_has_task_expert1_idx` (`expert_id`),
  CONSTRAINT `fk_an_ex_id` FOREIGN KEY (`expert_id`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_an_t_id` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysis_alternative`
--

DROP TABLE IF EXISTS `analysis_alternative`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `analysis_alternative` (
  `id` int NOT NULL AUTO_INCREMENT,
  `analysis_id` int NOT NULL,
  `alternative_id` int NOT NULL,
  `final_value` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_analysis_alternative` (`analysis_id`,`alternative_id`),
  KEY `fk_alt_id_idx` (`alternative_id`),
  KEY `fk_altan_an_id_idx` (`analysis_id`),
  CONSTRAINT `fk_altan_alt_id` FOREIGN KEY (`alternative_id`) REFERENCES `alternative` (`id`),
  CONSTRAINT `fk_altan_an_id` FOREIGN KEY (`analysis_id`) REFERENCES `analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysis_criterion`
--

DROP TABLE IF EXISTS `analysis_criterion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `analysis_criterion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `analysis_id` int NOT NULL,
  `criterion_id` int NOT NULL,
  `subj_value` int NOT NULL,
  `subj_value_relative` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_analyse_criterion` (`analysis_id`,`criterion_id`),
  KEY `fk_cr_an_id_idx` (`analysis_id`),
  KEY `fk_cr_cr_id_idx` (`criterion_id`),
  CONSTRAINT `fk_cran_an_id` FOREIGN KEY (`analysis_id`) REFERENCES `analysis` (`id`),
  CONSTRAINT `fk_cran_cr_id` FOREIGN KEY (`criterion_id`) REFERENCES `criterion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `criterion`
--

DROP TABLE IF EXISTS `criterion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `criterion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(65) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  FULLTEXT KEY `ft_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expert`
--

DROP TABLE IF EXISTS `expert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expert` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task`
--

DROP TABLE IF EXISTS `task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(65) NOT NULL,
  `description` varchar(95) DEFAULT NULL,
  `fl_new` tinyint NOT NULL DEFAULT '1',
  `owner` int NOT NULL,
  `create_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_taskowner_user_id_idx` (`owner`),
  CONSTRAINT `fk_taskowner_user_id` FOREIGN KEY (`owner`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task_alternative`
--

DROP TABLE IF EXISTS `task_alternative`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_alternative` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `alternative_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_taskalt_task_id_idx` (`task_id`),
  KEY `fk_taskalt_alt_id_idx` (`alternative_id`),
  CONSTRAINT `fk_taskalt_alt_id` FOREIGN KEY (`alternative_id`) REFERENCES `alternative` (`id`),
  CONSTRAINT `fk_taskalt_task_id` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task_criterion`
--

DROP TABLE IF EXISTS `task_criterion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_criterion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `criterion_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_taskcr_task_id_idx` (`task_id`),
  KEY `fk_taskcr_cr_id_idx` (`criterion_id`),
  CONSTRAINT `fk_taskcr_cr_id` FOREIGN KEY (`criterion_id`) REFERENCES `criterion` (`id`),
  CONSTRAINT `fk_taskcr_task_id` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task_data`
--

DROP TABLE IF EXISTS `task_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `criterion_id` int NOT NULL,
  `alternative_id` int NOT NULL,
  `value` varchar(60) NOT NULL,
  PRIMARY KEY (`id`,`task_id`,`criterion_id`,`alternative_id`),
  KEY `fk_task_data_criterion1_idx` (`criterion_id`) /*!80000 INVISIBLE */,
  KEY `fk_task_data_alternative1_idx` (`alternative_id`),
  KEY `fk_task_data_task1_idx` (`task_id`) /*!80000 INVISIBLE */,
  CONSTRAINT `fk_td_alt_id` FOREIGN KEY (`alternative_id`) REFERENCES `alternative` (`id`),
  CONSTRAINT `fk_td_cr_id` FOREIGN KEY (`criterion_id`) REFERENCES `criterion` (`id`),
  CONSTRAINT `fk_td_t_id` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-25 15:40:50
