-- Parcial II - Programacion Computacional III
-- Base de datos: parcial-2  (MariaDB en XAMPP)
-- Importar desde phpMyAdmin (pestaña SQL / Importar)

CREATE DATABASE IF NOT EXISTS `parcial-2`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `parcial-2`;

CREATE TABLE IF NOT EXISTS `usuarios_usss102024` (
  `idUsuario` int(10) NOT NULL AUTO_INCREMENT,
  `usuario`   char(35) NOT NULL,
  `clave`     char(35) NOT NULL,
  `nombre`    char(85) NOT NULL,
  `direccion` char(100) NOT NULL,
  `telefono`  char(9) NOT NULL,
  PRIMARY KEY (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Usuario inicial para poder entrar al login la primera vez (admin / admin123)
INSERT INTO `usuarios_usss102024` (`usuario`, `clave`, `nombre`, `direccion`, `telefono`)
SELECT 'admin', 'admin123', 'Administrador', 'Usulutan', '7000-0000' FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `usuarios_usss102024` WHERE `usuario` = 'admin');
