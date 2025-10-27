-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 27-10-2025 a las 21:48:12
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sistema_votacion`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administradores`
--

CREATE TABLE `administradores` (
  `id` int(11) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `administradores`
--

INSERT INTO `administradores` (`id`, `usuario`, `nombre`, `password_hash`, `fecha_creacion`) VALUES
(2, 'admin', 'Administrador', 'pbkdf2:sha256:600000$tpHyXiQMk3UUjiez$bd6972e7dcf5eed5fc753703af74558c62b2a39bd6fbb6502450ba47e9862106', '2025-10-27 20:44:03');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `candidatos`
--

CREATE TABLE `candidatos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `partido` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyectos`
--

CREATE TABLE `proyectos` (
  `id` int(11) NOT NULL,
  `nombre_proyecto` varchar(200) NOT NULL,
  `curso` varchar(20) NOT NULL,
  `ciclo` varchar(30) DEFAULT NULL,
  `materia` varchar(100) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `integrantes` text NOT NULL,
  `descripcion` text DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_creacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proyectos`
--

INSERT INTO `proyectos` (`id`, `nombre_proyecto`, `curso`, `ciclo`, `materia`, `categoria`, `integrantes`, `descripcion`, `activo`, `fecha_creacion`) VALUES
(245, 'Navidad Ecológica', '1°A', 'Ciclo Básico', 'Catequesis', 'Catequesis', 'COTIGNOLA, Francisco Bautista, GRAUSO, Julian Valentín', NULL, 1, '2025-10-27 20:20:18'),
(246, 'Proyecto Sociales', '1°A', 'Ciclo Básico', 'Sociales', 'Ciencias Sociales', 'FLORENTIN PEREIRA, Aaron Ezequiel', NULL, 1, '2025-10-27 20:20:18'),
(247, 'Auto dragster + semáforo', '1°A', 'Ciclo Básico', 'Robótica', 'Robótica', 'MONTESANO, Sofía Isabella, PINTO, Ema Rocío', NULL, 1, '2025-10-27 20:20:18'),
(248, 'Proyectos Sociales', '1°A', 'Ciclo Básico', 'Sociales', 'Ciencias Sociales', 'MURIEL MARTINEZ, Máximo Fernando', NULL, 1, '2025-10-27 20:20:18'),
(249, 'Proyectos Procedimientos I', '1°B', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'FUENTES, Thiago Gustavo, GOMEZ, Nicole Emilce', NULL, 1, '2025-10-27 20:20:18'),
(250, 'Muestra de arte', '1°B', 'Ciclo Básico', 'Educación Artística Visual', 'Otros', 'LOPEZ BUSNELLI, Mateo Sebastian, PACHECO, Bianca Luna', NULL, 1, '2025-10-27 20:20:18'),
(251, 'Robótica', '1°B', 'Ciclo Básico', 'Robótica', 'Robótica', 'PERALTA CABRERA, Iñaki Gastón', NULL, 1, '2025-10-27 20:20:18'),
(252, 'Juegos policiales', '2°A', 'Ciclo Básico', 'Prácticas Del Lenguaje', 'Literatura', 'BARRAZA, Ian Alexis, PERALTA, Bruno Nicolas', NULL, 1, '2025-10-27 20:20:18'),
(253, 'Muestra de arte', '2°A', 'Ciclo Básico', 'Educación Artística Visual', 'Otros', 'COPELLI, Martina, LESCANO, Pia Aylen', NULL, 1, '2025-10-27 20:20:18'),
(254, 'Banco Plegable en madera', '2°A', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'DEL CAMPO SALAZAR, Santino, GOCHI SAVAN, Luz Marianela', NULL, 1, '2025-10-27 20:20:18'),
(255, 'Organizador de madera', '2°A', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'PEREYRA, Jazmín Emily, POMAZON OBREGON, Milenka Allison, VINCIGUERRA ALTIERI, Dante', NULL, 1, '2025-10-27 20:20:18'),
(256, 'Libros poetas', '2°A', 'Ciclo Básico', 'Prácticas Del Lenguaje', 'Literatura', 'ROMERO, Mateo Eliel', NULL, 1, '2025-10-27 20:20:18'),
(257, 'Juegos matemáticos', '2°B', 'Ciclo Básico', 'Matemática', 'Matemática', 'ARANDA CRISTALDO, Jonathan Gaston, OROZCO, Gonzalo Benjamín', NULL, 1, '2025-10-27 20:20:18'),
(258, 'Repisa perchero', '2°B', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'BAEZ ALCARAS, Alejo', NULL, 1, '2025-10-27 20:20:18'),
(259, 'Ciudad inteligente', '2°B', 'Ciclo Básico', 'Robótica', 'Robótica', 'BOGGINI, Valentin Ezequiel, CHAVEZ RAMIREZ, Steven Benjamín', NULL, 1, '2025-10-27 20:20:18'),
(260, 'Banquito', '2°B', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'CARPIO, Santiago Nicolás', NULL, 1, '2025-10-27 20:20:18'),
(261, 'Mesa plegable', '2°B', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'SANCHEZ GONZALEZ, Santiago Ariel', NULL, 1, '2025-10-27 20:20:18'),
(262, 'Velador', '2°B', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'TOLABA, Ian Gabriel', NULL, 1, '2025-10-27 20:20:18'),
(263, 'Teatro', '3°A', 'Ciclo Básico', 'Literatura', 'Literatura', 'BENITEZ, Ernesto Benjamín, DUARTE, Franco, GARCIA LOPEZ, Bianca Belén, JUSTINIANO, Benjamin Ariel, NUÑEZ, Selene Noemí, RAMIREZ MAIDANA, Franco Valentín', NULL, 1, '2025-10-27 20:20:18'),
(264, 'La revolución Industrial', '3°A', 'Ciclo Básico', 'Historia', 'Ciencias Sociales', 'FIGUEROA BARRIENTOS, Lautaro', NULL, 1, '2025-10-27 20:20:18'),
(265, 'Muestra de arte', '3°A', 'Ciclo Básico', 'Educación Artística Visual', 'Otros', 'FIORENZA, Bianca Sofía, LANZAVECCHIA, Kiara', NULL, 1, '2025-10-27 20:20:18'),
(266, 'Soldadura con estaño y eléctrica', '3°A', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'DURE, Thiago, ORQUERA, Nicolas', NULL, 1, '2025-10-27 20:20:18'),
(267, 'Parque de atracciones', '3°B', 'Ciclo Básico', 'Procedimientos Técnicos', 'Procedimientos Técnicos', 'ALANI, Nazareno Samuel, SUAREZ YBAÑEZ, Mateo Nehuen', NULL, 1, '2025-10-27 20:20:18'),
(268, 'Ciudad inteligente', '3°B', 'Ciclo Básico', 'Robótica', 'Robótica', 'BARROS DEHN, Joaquín David, QUISBERT ALVAREZ, Ian Gael', NULL, 1, '2025-10-27 20:20:18'),
(269, 'Muestra de arte', '3°B', 'Ciclo Básico', 'Educación Artística Visual', 'Otros', 'COENCE FRANCO, Iara Candela, LUNA SANTILLAN, Mía Zoe', NULL, 1, '2025-10-27 20:20:18'),
(270, 'La Revolución Industrial', '3°B', 'Ciclo Básico', 'Historia', 'Ciencias Sociales', 'KOSICAR, Joaquín Esteban', NULL, 1, '2025-10-27 20:20:18'),
(271, 'Invisible (Enfoque 2)', '3°B', 'Ciclo Básico', 'Prácticas Del Lenguaje', 'Literatura', 'LOPEZ, Mía Jeanette, ORONOZ AGUIRRE, Julieta Melina', NULL, 1, '2025-10-27 20:20:18'),
(272, 'Invisible (Enfoque 1)', '3°B', 'Ciclo Básico', 'Prácticas Del Lenguaje', 'Literatura', 'MACHADO, Martina Oriana, RODAS AGUILAR, Sol Milagros', NULL, 1, '2025-10-27 20:20:18'),
(273, 'Virus letal y Guerra de memes', '4°A', 'Ciclo Superior', 'Laboratorio De Programación I', 'Programación', 'ALZO, Ayelen Julieta, BRACAMONTE, Zoe Berenice, GARAY, Cintia Irina', NULL, 1, '2025-10-27 20:20:18'),
(274, 'Service remoto', '4°A', 'Ciclo Superior', 'Laboratorio De Sistemas Operativos I', 'Hardware', 'BARRERA, Natan Donato, ESQUIVEL VILLALBA, Lisandro Román, VALDES BUFFA, Brenda Morena', NULL, 1, '2025-10-27 20:20:18'),
(275, 'Aplicaciones 4°A', '4°A', 'Ciclo Superior', 'Laboratorio De Aplicaciones', 'Otros', 'CARDOZO, Uziel Feliciano, MONZON, Samira Geraldine', NULL, 1, '2025-10-27 20:20:18'),
(276, 'Odisea', '4°A', 'Ciclo Superior', 'Literatura', 'Literatura', 'JUAREZ, Iván Lautaro Benjamín, LUYO FLORES, Ariana Angelina', NULL, 1, '2025-10-27 20:20:18'),
(277, 'Audicam', '4°A', 'Ciclo Superior', 'Laboratorio De Programación I', 'Programación', 'QUEIROT, Martin, VERON, Bautista', NULL, 1, '2025-10-27 20:20:18'),
(278, 'Modding', '4°B', 'Ciclo Superior', 'Laboratorio De Hardware I', 'Hardware', 'CORREA, Dante, IZAGUIRRE, Nahuel Agostino, ROMERO, Santiago Hernán', NULL, 1, '2025-10-27 20:20:18'),
(279, 'Armado y Desarmado de Laptop', '4°B', 'Ciclo Superior', 'Laboratorio De Hardware I', 'Hardware', 'FIGUEROA, Alma Sofia', NULL, 1, '2025-10-27 20:20:18'),
(280, 'Juegos la odisea', '4°B', 'Ciclo Superior', 'Literatura', 'Literatura', 'GIMENEZ, Ambar, SILVA NUÑEZ, Melanie Lujan', NULL, 1, '2025-10-27 20:20:18'),
(281, 'Programas y misceláneos 4°B', '4°B', 'Ciclo Superior', 'Laboratorio De Programación I', 'Programación', 'MINACIAN, Gonzalo David, MUNIZAGA, Sebastian Leonel', NULL, 1, '2025-10-27 20:20:18'),
(282, 'El idiomático', '4°B', 'Ciclo Superior', 'Laboratorio De Programación I', 'Programación', 'PALACIOS, Mauro', NULL, 1, '2025-10-27 20:20:18'),
(283, 'Service remoto', '4°B', 'Ciclo Superior', 'Laboratorio De Sistemas Operativos I', 'Hardware', 'SILVA, Uma Aymee, URDAPILLETA, Facundo Nehuen', NULL, 1, '2025-10-27 20:20:18'),
(284, 'Astrum Deus', '4°B', 'Ciclo Superior', 'Laboratorio De Programación I', 'Programación', 'ZOLOAGA, Facundo Alejo', NULL, 1, '2025-10-27 20:20:18'),
(285, 'Casa Domótica', '5°U', 'Ciclo Superior', 'Laboratorio De Sistemas Operativos Ii', 'Hardware', 'ACOSTA, Ramiro Javier, ARAUJO, Rocco Martin, ARIAS, Pablo Gabriel, BARRETO, Jerónimo Valentin, BENITEZ GOMEZ, Esteban Eliam, CRESPO BARREIRA, Fatima Anabella, DI PAOLA, Emiliano Agustín, ESCUDERO, Sofía Irina, ORTIZ, Ignacio Dario, PALACIOS, Lucas Benjamín, RODRIGUEZ, Ambar Candela, SANMARTIN VELAZCO, Ignacio Ariel, SANTILLI, Morena', NULL, 1, '2025-10-27 20:20:18'),
(286, 'Proyectos con Visual Basic', '5°U', 'Ciclo Superior', 'Laboratorio De Sistemas Operativos Ii', 'Hardware', 'GARCIA LOPEZ, Lucero Madelaine, RUIZ, Kevin Emir', NULL, 1, '2025-10-27 20:20:18'),
(287, 'Juegos el principito', '5°U', 'Ciclo Superior', 'Literatura', 'Literatura', 'GUTIERREZ AMARILLA, Lara Martina', NULL, 1, '2025-10-27 20:20:18'),
(288, 'Programación y servidores con Python', '5°U', 'Ciclo Superior', 'Laboratorio De Programación Ii', 'Programación', 'IRALA ALMEIDA, Julian, TIRIGALL CORZO, Carlos Javier', NULL, 1, '2025-10-27 20:20:18'),
(289, 'Programación y servidores con Php', '5°U', 'Ciclo Superior', 'Laboratorio De Programación Ii', 'Programación', 'PUGLIELLI, Alfredo Mateo, VERGARA, Agustina', NULL, 1, '2025-10-27 20:20:18'),
(290, 'Sistema de votación', '5°U', 'Ciclo Superior', 'Laboratorio De Programación Ii', 'Programación', 'SEGOVIA, Cristian Gonzalo', NULL, 1, '2025-10-27 20:20:18'),
(291, 'Noct-Air', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'ALARCON AGUIRRE, Gonzalo Adrián, CALDERON, Maxima Nicole', NULL, 1, '2025-10-27 20:20:18'),
(292, 'Facetel', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'ALVAREZ CIGNONI, Agustin, VALENZUELA, Thomas Santino', NULL, 1, '2025-10-27 20:20:18'),
(293, 'Hyperion', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'BILLORDO, Emiliano Gabriel, GALEANO DIAS, Lautaro Gabriel', NULL, 1, '2025-10-27 20:20:18'),
(294, 'PCPC', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'BORDON, Eva Aime, RODRIGUEZ, Joaquín Elías', NULL, 1, '2025-10-27 20:20:18'),
(295, 'SPWM', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'DUARTE, Santiago Gael, FARFAN, Alex Agustin Fabrizio', NULL, 1, '2025-10-27 20:20:18'),
(296, 'Sign Language Translator', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'MENDEZ, Cristal Jazmin, VILARIÑO MILIN, Victorio', NULL, 1, '2025-10-27 20:20:18'),
(297, 'SIA', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'MOREYRA, Mariano Ezequiel, ZELARAYAN MORALES, Joaquin Alessandro', NULL, 1, '2025-10-27 20:20:18'),
(298, 'Glov', '6°U', 'Ciclo Superior', 'Laboratorio De Hardware / So Iii', 'Hardware', 'SUAREZ, Alan Nicolás, VAZQUEZ, Lucas Valentín', NULL, 1, '2025-10-27 20:20:18'),
(299, 'Rehilo', '7°U', 'Ciclo Superior', 'Proyecto, Diseño E Implementación De Sistemas Computacionales', 'Otros', 'ARGUELLO COLOMBRES, Leylen Abril Alanis, BOGADO MERELES, Micaela Luján, GOMEZ SAUCEDO, Demian Alejandro', NULL, 1, '2025-10-27 20:20:18'),
(300, 'Contacho', '7°U', 'Ciclo Superior', 'Proyecto, Diseño E Implementación De Sistemas Computacionales', 'Otros', 'CAVALLO, Thomas Martín, LUCIO, Juan Pablo, MAURIN, Santiago Alberto', NULL, 1, '2025-10-27 20:20:18'),
(301, 'Telefonía IP', '7°U', 'Ciclo Superior', 'Redes', 'Otros', 'LUQUE, Agustín Nehuel, SANCHEZ PAMPA, Melanie', NULL, 1, '2025-10-27 20:20:18');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `votos`
--

CREATE TABLE `votos` (
  `id` int(11) NOT NULL,
  `proyecto_id` int(11) NOT NULL,
  `fecha_voto` datetime DEFAULT NULL,
  `ip_address` varchar(45) NOT NULL,
  `user_agent` text NOT NULL,
  `hash_voto` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administradores`
--
ALTER TABLE `administradores`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario` (`usuario`);

--
-- Indices de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `proyectos`
--
ALTER TABLE `proyectos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_proyecto_nombre` (`nombre_proyecto`),
  ADD KEY `idx_proyectos_categoria` (`categoria`),
  ADD KEY `idx_proyectos_curso` (`curso`),
  ADD KEY `idx_proyectos_ciclo` (`ciclo`),
  ADD KEY `idx_proyectos_activo` (`activo`),
  ADD KEY `idx_proyectos_nombre_curso` (`nombre_proyecto`(100),`curso`);

--
-- Indices de la tabla `votos`
--
ALTER TABLE `votos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_votos_hash_voto` (`hash_voto`),
  ADD KEY `votos_ibfk_1` (`proyecto_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `administradores`
--
ALTER TABLE `administradores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `proyectos`
--
ALTER TABLE `proyectos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=302;

--
-- AUTO_INCREMENT de la tabla `votos`
--
ALTER TABLE `votos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `votos`
--
ALTER TABLE `votos`
  ADD CONSTRAINT `votos_ibfk_1` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
