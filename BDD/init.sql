-- --------------------------------------------------------
-- Host:                         192.168.1.55
-- Versión del servidor:         10.3.21-MariaDB - Source distribution
-- SO del servidor:              Linux
-- HeidiSQL Versión:             11.1.0.6116
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para modelos3d
CREATE DATABASE IF NOT EXISTS `modelos3d` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `modelos3d`;

-- Volcando estructura para tabla modelos3d.enlaces
CREATE TABLE IF NOT EXISTS `enlaces` (
  `ID` int(20) NOT NULL AUTO_INCREMENT,
  `ID_MODELO` int(20) NOT NULL,
  `ID_WEB` int(11) DEFAULT NULL,
  `ENLACE` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Índice 4` (`ENLACE`),
  KEY `Índice 2` (`ID_MODELO`),
  KEY `Índice 3` (`ID_WEB`),
  CONSTRAINT `FK__modelos` FOREIGN KEY (`ID_MODELO`) REFERENCES `modelos` (`ID`),
  CONSTRAINT `FK_enlaces_webs_enlaces` FOREIGN KEY (`ID_WEB`) REFERENCES `webs_enlaces` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla modelos3d.etiquetas
CREATE TABLE IF NOT EXISTS `etiquetas` (
  `ID` int(20) NOT NULL AUTO_INCREMENT,
  `ETIQUETA` varchar(60) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Índice 2` (`ETIQUETA`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla modelos3d.modelos
CREATE TABLE IF NOT EXISTS `modelos` (
  `ID` int(20) NOT NULL AUTO_INCREMENT,
  `NOMBRE` varchar(60) NOT NULL,
  `IMG` varchar(60) DEFAULT NULL,
  `FECHA_INS` date NOT NULL DEFAULT current_timestamp(),
  `PATH_DRIVE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Índice 2` (`NOMBRE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla modelos3d.modelo_x_etiqueta
CREATE TABLE IF NOT EXISTS `modelo_x_etiqueta` (
  `ID_MODELO` int(20) NOT NULL,
  `ID_EQTIQUETA` int(20) NOT NULL,
  PRIMARY KEY (`ID_EQTIQUETA`,`ID_MODELO`),
  KEY `Índice 1` (`ID_MODELO`),
  KEY `Índice 2` (`ID_EQTIQUETA`),
  CONSTRAINT `FK_modelo_x_etiqueta_etiquetas` FOREIGN KEY (`ID_EQTIQUETA`) REFERENCES `etiquetas` (`ID`),
  CONSTRAINT `FK_modelo_x_etiqueta_modelos` FOREIGN KEY (`ID_MODELO`) REFERENCES `modelos` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla modelos3d.webs_enlaces
CREATE TABLE IF NOT EXISTS `webs_enlaces` (
  `ID` int(20) NOT NULL AUTO_INCREMENT,
  `WEB` varchar(60) DEFAULT NULL,
  `NOMBRE` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Índice 2` (`NOMBRE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- La exportación de datos fue deseleccionada.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
