-- Esquema de la base de datos de Auto-Python.
-- Los datos incluidos son ficticios y sirven como ejemplo.

CREATE DATABASE IF NOT EXISTS `db_labelprint`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE `db_labelprint`;

-- --------------------------------------------------------
-- Tablas
-- --------------------------------------------------------

CREATE TABLE `catClientes` (
  `IdCliente` tinyint(5) NOT NULL AUTO_INCREMENT,
  `cCliente` varchar(45) DEFAULT NULL,
  `bActivo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`IdCliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `catModelos` (
  `IdModelo` tinyint(5) NOT NULL AUTO_INCREMENT,
  `cModelo` varchar(45) DEFAULT NULL,
  `IdCliente` tinyint(5) NOT NULL,
  `bActivo` tinyint(1) DEFAULT 1,
  `cPlantilla` varchar(150) NOT NULL,
  `cEstilo` varchar(150) NOT NULL,
  PRIMARY KEY (`IdModelo`),
  KEY `index2` (`IdCliente`),
  KEY `index3` (`bActivo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `catNumerosParte` (
  `IdNP` int(11) NOT NULL AUTO_INCREMENT,
  `IdModelo` tinyint(5) DEFAULT NULL,
  `cNumeroParte` varchar(45) DEFAULT NULL,
  `cCodigoBarras1` varchar(45) DEFAULT NULL,
  `cCodigoBarras2` varchar(45) DEFAULT NULL,
  `cCodigoBarras3` varchar(45) DEFAULT NULL,
  `bActivo` tinyint(1) DEFAULT 1,
  `cCBLectura` varchar(50) NOT NULL,
  `iStdPack` int(11) NOT NULL,
  PRIMARY KEY (`IdNP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `catParametros` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `cNombre` varchar(50) NOT NULL,
  `iPinIn` int(11) NOT NULL,
  `iPinout` int(11) NOT NULL,
  `iPrintDelay` int(11) NOT NULL,
  `bEscaner` tinyint(1) NOT NULL DEFAULT 0,
  `bBoton` tinyint(1) NOT NULL DEFAULT 0,
  `bPrintRack` tinyint(1) NOT NULL DEFAULT 0,
  `iHorasProduccion` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `catSupervisor` (
  `Id` tinyint(3) NOT NULL AUTO_INCREMENT,
  `cUsuario` varchar(50) NOT NULL,
  `cPassword` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `mvPiezas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cNumeroParte` varchar(45) DEFAULT NULL,
  `cCBLectura` varchar(50) DEFAULT NULL,
  `iCantidad` int(11) DEFAULT NULL,
  `iProduccion` int(11) DEFAULT NULL,
  `dFinProd` timestamp NULL DEFAULT NULL,
  `dIniProd` timestamp NOT NULL DEFAULT current_timestamp(),
  `IdStatus` tinyint(4) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Datos de ejemplo
-- --------------------------------------------------------

INSERT INTO `catClientes` (`IdCliente`, `cCliente`, `bActivo`) VALUES
  (1, 'Cliente Demo', 1);

INSERT INTO `catModelos`
  (`IdModelo`, `cModelo`, `IdCliente`, `bActivo`, `cPlantilla`, `cEstilo`)
VALUES
  (1, 'Modelo Base', 1, 1,
   'templates/standard_template.html',
   'styles/standard_style.css');

INSERT INTO `catNumerosParte`
  (`IdNP`, `IdModelo`, `cNumeroParte`, `cCodigoBarras1`, `cCodigoBarras2`,
   `cCodigoBarras3`, `bActivo`, `cCBLectura`, `iStdPack`)
VALUES
  (1, 1, 'PN-1001', 'DEMO-A-01', 'DEMO-A-02', '', 1, 'DEMO-0001', 10);

INSERT INTO `catParametros`
  (`Id`, `cNombre`, `iPinIn`, `iPinout`, `iPrintDelay`, `bEscaner`,
   `bBoton`, `bPrintRack`, `iHorasProduccion`)
VALUES
  (1, 'CELDA DEMO', 18, 0, 10, 1, 0, 0, 2);

INSERT INTO `catSupervisor` (`Id`, `cUsuario`, `cPassword`) VALUES
  (1, 'supervisor', 'demo1234');

INSERT INTO `mvPiezas`
  (`id`, `cNumeroParte`, `cCBLectura`, `iCantidad`, `iProduccion`,
   `dFinProd`, `dIniProd`, `IdStatus`)
VALUES
  (1, 'PN-1001', 'DEMO-0001', 0, 10, NULL, '2024-01-15 08:00:00', 1);

-- --------------------------------------------------------
-- Procedimientos almacenados
-- --------------------------------------------------------

DELIMITER $$

DROP PROCEDURE IF EXISTS `spClientes`$$
CREATE PROCEDURE `spClientes` (
  IN `cAccion` VARCHAR(45),
  IN `vIdCliente` TINYINT(5),
  IN `vcCliente` VARCHAR(45),
  IN `vbActivo` TINYINT(1)
) MODIFIES SQL DATA
BEGIN
  IF cAccion = 'I' THEN
    START TRANSACTION;
      INSERT INTO catClientes (cCliente) VALUES (vcCliente);
      SELECT LAST_INSERT_ID();
    COMMIT;
  ELSEIF cAccion = 'E' THEN
    START TRANSACTION;
      UPDATE catClientes
      SET cCliente = vcCliente,
          bActivo = vbActivo
      WHERE IdCliente = vIdCliente;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'C1' THEN
    SELECT IdCliente, cCliente FROM catClientes WHERE bActivo = 1;
  ELSEIF cAccion = 'C2' THEN
    SELECT IdCliente, cCliente FROM catClientes WHERE IdCliente = vIdCliente;
  ELSEIF cAccion = 'C3' THEN
    SELECT IdCliente, cCliente, bActivo,
           CASE
             WHEN bActivo = 1 THEN 'Activo'
             WHEN bActivo = 0 THEN 'InActivo'
           END AS tActivo
    FROM catClientes
    ORDER BY cCliente ASC;
  END IF;
END$$

DROP PROCEDURE IF EXISTS `spModelos`$$
CREATE PROCEDURE `spModelos` (
  IN `cAccion` VARCHAR(45),
  IN `vIdModelo` TINYINT(5),
  IN `vcModelo` VARCHAR(45),
  IN `vIdCliente` TINYINT(5),
  IN `vbActivo` TINYINT(1),
  IN `vcPlantilla` VARCHAR(150),
  IN `vcEstilo` VARCHAR(150)
) MODIFIES SQL DATA
BEGIN
  IF cAccion = 'I' THEN
    START TRANSACTION;
      INSERT INTO catModelos (cModelo, IdCliente, cPlantilla, cEstilo)
      VALUES (vcModelo, vIdCliente, vcPlantilla, vcEstilo);
      SELECT LAST_INSERT_ID();
    COMMIT;
  ELSEIF cAccion = 'E' THEN
    START TRANSACTION;
      UPDATE catModelos
      SET cModelo = vcModelo,
          IdCliente = vIdCliente,
          bActivo = vbActivo,
          cPlantilla = vcPlantilla,
          cEstilo = vcEstilo
      WHERE IdModelo = vIdModelo;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'C1' THEN
    SELECT C.IdCliente, C.cCliente, M.IdModelo, M.cModelo, M.cPlantilla, M.cEstilo
    FROM catClientes C
    INNER JOIN catModelos M ON C.IdCliente = M.IdCliente
    WHERE C.bActivo = 1 AND M.bActivo = 1;
  ELSEIF cAccion = 'C2' THEN
    SELECT C.IdCliente, C.cCliente, M.IdModelo, M.cModelo, M.cPlantilla, M.cEstilo
    FROM catClientes C
    INNER JOIN catModelos M ON C.IdCliente = M.IdCliente
    WHERE C.IdCliente = vIdCliente;
  ELSEIF cAccion = 'C3' THEN
    SELECT C.IdCliente, C.cCliente, M.IdModelo, M.cModelo, M.cPlantilla, M.cEstilo
    FROM catClientes C
    INNER JOIN catModelos M ON C.IdCliente = M.IdCliente
    WHERE M.IdModelo = vIdModelo;
  ELSEIF cAccion = 'C4' THEN
    SELECT C.IdCliente, C.cCliente, M.IdModelo, M.cModelo, M.bActivo,
           CASE
             WHEN M.bActivo = 1 THEN 'Activo'
             WHEN M.bActivo = 0 THEN 'InActivo'
           END AS tActivo,
           M.cPlantilla, M.cEstilo
    FROM catClientes C
    INNER JOIN catModelos M ON C.IdCliente = M.IdCliente
    ORDER BY C.cCliente ASC, M.cModelo ASC;
  END IF;
END$$

DROP PROCEDURE IF EXISTS `spNP`$$
CREATE PROCEDURE `spNP` (
  IN `cAccion` VARCHAR(45),
  IN `vIdNP` INT(11),
  IN `vIdModelo` TINYINT(5),
  IN `vcNumeroParte` VARCHAR(45),
  IN `vCB1` VARCHAR(45),
  IN `vCB2` VARCHAR(45),
  IN `vCB3` VARCHAR(45),
  IN `vbActivo` TINYINT(1),
  IN `vcCBLectura` VARCHAR(50),
  IN `viStdPack` INT(11)
) MODIFIES SQL DATA
BEGIN
  IF cAccion = 'I' THEN
    START TRANSACTION;
      INSERT INTO catNumerosParte
        (IdModelo, cNumeroParte, cCodigoBarras1, cCodigoBarras2,
         cCodigoBarras3, cCBLectura, iStdPack)
      VALUES
        (vIdModelo, vcNumeroParte, vCB1, vCB2, vCB3, vcCBLectura, viStdPack);
      SELECT LAST_INSERT_ID();
    COMMIT;
  ELSEIF cAccion = 'E' THEN
    START TRANSACTION;
      UPDATE catNumerosParte
      SET IdModelo = vIdModelo,
          cNumeroParte = vcNumeroParte,
          cCodigoBarras1 = vCB1,
          cCodigoBarras2 = vCB2,
          cCodigoBarras3 = vCB3,
          cCBLectura = vcCBLectura,
          iStdPack = viStdPack,
          bActivo = vbActivo
      WHERE IdNP = vIdNP;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'C1' THEN
    SELECT IdNP, cNumeroParte, cCodigoBarras1, cCodigoBarras2,
           cCodigoBarras3, cCBLectura, iStdPack
    FROM catNumerosParte
    WHERE IdModelo = vIdModelo AND bActivo = 1;
  ELSEIF cAccion = 'C2' THEN
    SELECT IdNP, cNumeroParte, cCodigoBarras1, cCodigoBarras2,
           cCodigoBarras3, cCBLectura, iStdPack
    FROM catNumerosParte
    WHERE IdNP = vIdNP;
  ELSEIF cAccion = 'C3' THEN
    SELECT C.IdCliente, C.cCliente, M.IdModelo, M.cModelo, NP.IdNP,
           NP.cNumeroParte, NP.cCodigoBarras1, NP.cCodigoBarras2,
           NP.cCodigoBarras3, 0 AS lineas, NP.bActivo,
           CASE
             WHEN NP.bActivo = 1 THEN 'Activo'
             WHEN NP.bActivo = 0 THEN 'InActivo'
           END AS tActivo,
           NP.cCBLectura, NP.iStdPack
    FROM catNumerosParte NP
    INNER JOIN catModelos M ON NP.IdModelo = M.IdModelo
    INNER JOIN catClientes C ON M.IdCliente = C.IdCliente
    ORDER BY C.cCliente DESC, M.cModelo DESC, NP.cNumeroParte DESC;
  ELSEIF cAccion = 'C4' THEN
    SELECT C.IdCliente, C.cCliente, M.IdModelo, M.cModelo, NP.IdNP,
           NP.cNumeroParte, NP.cCodigoBarras1, NP.cCodigoBarras2,
           NP.cCodigoBarras3, 0 AS lineas, NP.bActivo,
           CASE
             WHEN NP.bActivo = 1 THEN 'Activo'
             WHEN NP.bActivo = 0 THEN 'InActivo'
           END AS tActivo,
           NP.cCBLectura, NP.iStdPack
    FROM catNumerosParte NP
    INNER JOIN catModelos M ON NP.IdModelo = M.IdModelo
    INNER JOIN catClientes C ON M.IdCliente = C.IdCliente
    WHERE NP.cCBLectura = vcCBLectura;
  END IF;
END$$

DROP PROCEDURE IF EXISTS `spParametros`$$
CREATE PROCEDURE `spParametros` (
  IN `Nombre` VARCHAR(50),
  IN `iIn` INT,
  IN `iOut` INT,
  IN `iDelay` INT,
  IN `iEscaner` TINYINT(1),
  IN `iBoton` TINYINT(1),
  IN `cAccion` VARCHAR(45),
  IN `iPrintRack` INT(1),
  IN `iHoras` INT
) NO SQL
BEGIN
  IF cAccion = 'E' THEN
    START TRANSACTION;
      UPDATE catParametros
      SET cNombre = Nombre,
          iPinIn = iIn,
          iPinout = iOut,
          iPrintDelay = iDelay,
          bEscaner = iEscaner,
          bBoton = iBoton,
          bPrintRack = iPrintRack,
          iHorasProduccion = iHoras
      WHERE Id = 1;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'C1' THEN
    SELECT cNombre, iPinIn, iPinout, iPrintDelay, bEscaner, bBoton,
           bPrintRack, iHorasProduccion
    FROM catParametros
    WHERE Id = 1;
  END IF;
END$$

DROP PROCEDURE IF EXISTS `spPiezas`$$
CREATE PROCEDURE `spPiezas` (
  IN `cAccion` VARCHAR(45),
  IN `vcNumeroParte` VARCHAR(45),
  IN `vcCBLectura` VARCHAR(50),
  IN `viCantidad` INT(11),
  IN `viProduccion` INT(11),
  IN `vid` INT(11)
) MODIFIES SQL DATA
BEGIN
  IF cAccion = 'I' THEN
    START TRANSACTION;
      INSERT INTO mvPiezas (cNumeroParte, cCBLectura, iCantidad, iProduccion)
      VALUES (vcNumeroParte, vcCBLectura, viCantidad, viProduccion);
      SELECT LAST_INSERT_ID();
    COMMIT;
  ELSEIF cAccion = 'CE' THEN
    START TRANSACTION;
      UPDATE mvPiezas
      SET dFinProd = CURRENT_TIMESTAMP(), IdStatus = 3
      WHERE id = vid;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'CP' THEN
    START TRANSACTION;
      UPDATE mvPiezas
      SET dFinProd = CURRENT_TIMESTAMP(), IdStatus = 2
      WHERE id = vid;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'CL' THEN
    START TRANSACTION;
      UPDATE mvPiezas
      SET iCantidad = 0, iProduccion = 0
      WHERE id = vid;
      SELECT 1;
    COMMIT;
  ELSEIF cAccion = 'C1' THEN
    SELECT id, dFinProd, TIMESTAMPDIFF(HOUR, dIniProd, NOW()) AS Horas,
           iCantidad, iProduccion
    FROM mvPiezas
    WHERE cCBLectura = vcCBLectura AND IdStatus = 1;
  ELSEIF cAccion = 'C2' THEN
    SELECT id, dFinProd, TIMESTAMPDIFF(HOUR, dFinProd, NOW()) AS Horas,
           iCantidad, iProduccion
    FROM mvPiezas
    WHERE cCBLectura = vcCBLectura AND IdStatus = 2;
  ELSEIF cAccion = 'AD' THEN
    START TRANSACTION;
      UPDATE mvPiezas SET iCantidad = iCantidad + 1 WHERE id = vid;
      SELECT iCantidad FROM mvPiezas WHERE id = vid;
    COMMIT;
  ELSEIF cAccion = 'LE' THEN
    START TRANSACTION;
      UPDATE mvPiezas SET iCantidad = iCantidad - viCantidad WHERE id = vid;
      SELECT iCantidad FROM mvPiezas WHERE id = vid;
    COMMIT;
  END IF;
END$$

DROP PROCEDURE IF EXISTS `spSupervisor`$$
CREATE PROCEDURE `spSupervisor` (
  IN `usuario` VARCHAR(50),
  IN `clave` VARCHAR(50)
) NO SQL
BEGIN
  SELECT Id FROM catSupervisor
  WHERE cUsuario = usuario AND cPassword = clave;
END$$

DELIMITER ;
