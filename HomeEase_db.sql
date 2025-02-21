/*
SQLyog Community v13.1.1 (64 bit)
MySQL - 5.5.29 : Database - homeease
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`homeease` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `homeease`;

/*Table structure for table `bookings` */

DROP TABLE IF EXISTS `bookings`;

CREATE TABLE `bookings` (
  `booking_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `provider_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `status` enum('Pending','Accepted','Rejected','Completed','Paid') NOT NULL DEFAULT 'Pending',
  `booking_time` datetime DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `user_id` (`user_id`),
  KEY `provider_id` (`provider_id`),
  KEY `service_id` (`service_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`provider_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

/*Data for the table `bookings` */

insert  into `bookings`(`booking_id`,`user_id`,`provider_id`,`service_id`,`status`,`booking_time`) values 
(1,2,1,1,'Paid',NULL),
(2,2,1,1,'Paid',NULL),
(3,2,1,2,'Paid',NULL),
(4,2,1,3,'Paid',NULL),
(5,2,1,1,'Paid',NULL),
(6,3,1,3,'Paid',NULL),
(9,2,1,2,'Paid',NULL),
(10,3,5,4,'Paid',NULL);

/*Table structure for table `feedback` */

DROP TABLE IF EXISTS `feedback`;

CREATE TABLE `feedback` (
  `feedback_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `provider_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `comments` text NOT NULL,
  `feedback_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`feedback_id`),
  KEY `booking_id` (`booking_id`),
  KEY `user_id` (`user_id`),
  KEY `provider_id` (`provider_id`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `feedback_ibfk_3` FOREIGN KEY (`provider_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `feedback` */

insert  into `feedback`(`feedback_id`,`booking_id`,`user_id`,`provider_id`,`rating`,`comments`,`feedback_date`) values 
(1,1,2,1,4,'good','2025-02-14 13:32:35'),
(2,6,3,1,2,'sadf','2025-02-14 14:17:14'),
(3,10,3,5,4,'very good work','2025-02-14 23:35:18');

/*Table structure for table `payments` */

DROP TABLE IF EXISTS `payments`;

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `provider_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_method` enum('Credit Card','Debit Card','Net Banking','UPI') NOT NULL,
  `payment_status` enum('Pending','Completed','Failed') DEFAULT 'Pending',
  `card_number` varchar(16) DEFAULT NULL,
  `expiry_date` varchar(5) DEFAULT NULL,
  `cvv` varchar(4) DEFAULT NULL,
  `upi_id` varchar(50) DEFAULT NULL,
  `payment_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`),
  KEY `booking_id` (`booking_id`),
  KEY `provider_id` (`provider_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`provider_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

/*Data for the table `payments` */

insert  into `payments`(`payment_id`,`booking_id`,`provider_id`,`user_id`,`amount`,`payment_method`,`payment_status`,`card_number`,`expiry_date`,`cvv`,`upi_id`,`payment_date`) values 
(1,4,1,2,6000.00,'Credit Card','Completed',NULL,NULL,NULL,NULL,'2025-02-14 12:29:49'),
(2,5,1,2,7000.00,'Credit Card','Completed',NULL,NULL,NULL,NULL,'2025-02-14 13:38:41'),
(3,6,1,3,6000.00,'Credit Card','Completed',NULL,NULL,NULL,NULL,'2025-02-14 14:16:54'),
(4,9,1,2,8000.00,'UPI','Completed',NULL,NULL,NULL,NULL,'2025-02-14 19:06:56'),
(5,10,5,3,4000.00,'Debit Card','Completed',NULL,NULL,NULL,NULL,'2025-02-14 23:34:16');

/*Table structure for table `services` */

DROP TABLE IF EXISTS `services`;

CREATE TABLE `services` (
  `service_id` int(11) NOT NULL AUTO_INCREMENT,
  `provider_id` int(11) DEFAULT NULL,
  `service_name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `availability` enum('Available','Unavailable') NOT NULL DEFAULT 'Available',
  `description` text,
  PRIMARY KEY (`service_id`),
  KEY `provider_id` (`provider_id`),
  CONSTRAINT `services_ibfk_1` FOREIGN KEY (`provider_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

/*Data for the table `services` */

insert  into `services`(`service_id`,`provider_id`,`service_name`,`price`,`availability`,`description`) values 
(1,1,'plumbing',7000.00,'Available',NULL),
(2,1,'Electrical Repair',8000.00,'Available',NULL),
(3,1,'Home Cleaning',6000.00,'Available','Deep cleaning, carpet washing, and dusting.'),
(4,5,'Painting ',4000.00,'Available','Painting Service');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `address` text NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('Admin','User','ServiceProvider','VerifiedServiceProvider') NOT NULL DEFAULT 'User',
  `certification` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

/*Data for the table `users` */

insert  into `users`(`user_id`,`full_name`,`email`,`phone`,`address`,`password`,`role`,`certification`) values 
(1,'venkat','venkat@gmail.com','9999999999','hyderabad','venkat','VerifiedServiceProvider',NULL),
(2,'aravind','aravind@gmail.com','9876789876','hyd','aravind','User',NULL),
(3,'raju','raju@gmail.com','8787676565','hyderabad','raju','User',NULL),
(4,'ramu','ramu@gmail.com','7678767898','vizag','ramu','VerifiedServiceProvider','static/uploads/flo1234.jpg'),
(5,'ravi','ravi@gmail.com','9876787678','hyd','ravi','VerifiedServiceProvider','static/uploads/flo1234.jpg');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
