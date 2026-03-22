/*
================================================================================
 PROYECTO:     SICC - Sistema de Gestión de Incidentes de Ciberseguridad
 DOCUMENTO:    Script de Base de Datos (DDL y DML)
 MOTOR:        Microsoft SQL Server 2019/2022
 AUTOR:        Brandon Kevin Mamani Roque
 FECHA:        Diciembre 2025
================================================================================
*/

USE master;
GO

-- =============================================================================
-- 1. GESTIÓN DE LA BASE DE DATOS
-- =============================================================================

-- Si la base de datos existe, la eliminamos para reiniciar el entorno (Clean Install)
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'DB_GestionIncidentes')
BEGIN
    ALTER DATABASE DB_GestionIncidentes SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE DB_GestionIncidentes;
    PRINT '>> Base de datos anterior eliminada.';
END
GO

CREATE DATABASE DB_GestionIncidentes;
GO

USE DB_GestionIncidentes;
PRINT '>> Base de datos DB_GestionIncidentes creada y seleccionada.';
GO

-- =============================================================================
-- 2. DDL - DATA DEFINITION LANGUAGE (Creación de Tablas)
-- =============================================================================

/* 2.1. TABLAS CATÁLOGO (Independientes) */

CREATE TABLE cat_Tipos_Incidente (
    id_tipo INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(100) NOT NULL UNIQUE,
    descripcion NVARCHAR(500)
);

CREATE TABLE cat_Prioridades (
    id_prioridad INT PRIMARY KEY IDENTITY(1,1),
    nivel NVARCHAR(50) NOT NULL UNIQUE,
    valor_orden INT NOT NULL UNIQUE -- Para ordenar (1=Baja ... 4=Crítica)
);

CREATE TABLE cat_Estados (
    id_estado INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(50) NOT NULL UNIQUE
);

/* 2.2. TABLAS DE ENTIDADES (Contexto) */

CREATE TABLE Usuarios (
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    nombre_completo NVARCHAR(200) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    rol NVARCHAR(100) NOT NULL DEFAULT 'Analista'
);

CREATE TABLE Activos (
    id_activo INT PRIMARY KEY IDENTITY(1,1),
    hostname NVARCHAR(100) NOT NULL UNIQUE,
    direccion_ip NVARCHAR(45),
    tipo_activo NVARCHAR(100), -- Coincide con schema Python
    propietario NVARCHAR(200)  -- Coincide con schema Python
);

/* 2.3. TABLA CENTRAL (Hechos) */

CREATE TABLE Incidentes (
    id_incidente INT PRIMARY KEY IDENTITY(1,1),
    titulo NVARCHAR(255) NOT NULL,
    descripcion_detallada NVARCHAR(MAX) NOT NULL,
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_cierre DATETIME2 NULL,

    -- Llaves Foráneas
    id_tipo INT NOT NULL,
    id_prioridad INT NOT NULL,
    id_estado INT NOT NULL,
    id_usuario_asignado INT NULL,

    -- Restricciones de Integridad Referencial
    CONSTRAINT FK_Incidentes_Tipo FOREIGN KEY (id_tipo) REFERENCES cat_Tipos_Incidente(id_tipo),
    CONSTRAINT FK_Incidentes_Prioridad FOREIGN KEY (id_prioridad) REFERENCES cat_Prioridades(id_prioridad),
    CONSTRAINT FK_Incidentes_Estado FOREIGN KEY (id_estado) REFERENCES cat_Estados(id_estado),
    CONSTRAINT FK_Incidentes_Usuario FOREIGN KEY (id_usuario_asignado) REFERENCES Usuarios(id_usuario)
);

/* 2.4. TABLAS DE RELACIÓN Y DETALLE (Dependientes) */

-- Tabla Intermedia N:M (Un incidente afecta muchos activos, un activo tiene muchos incidentes)
CREATE TABLE Incidentes_Activos (
    id_incidente_activo INT PRIMARY KEY IDENTITY(1, 1),
    id_incidente INT NOT NULL,
    id_activo INT NOT NULL,
    notas_relacion NVARCHAR(300),

    CONSTRAINT FK_IA_Incidente FOREIGN KEY (id_incidente) REFERENCES Incidentes(id_incidente) ON DELETE CASCADE,
    CONSTRAINT FK_IA_Activo FOREIGN KEY (id_activo) REFERENCES Activos(id_activo) ON DELETE CASCADE,

    -- Restricción Única: Evita vincular el mismo activo dos veces al mismo incidente
    CONSTRAINT UQ_Incidente_Activo UNIQUE (id_incidente, id_activo)
);

-- Tabla de Historial / Auditoría
CREATE TABLE Bitacora_Investigacion (
    id_bitacora INT PRIMARY KEY IDENTITY(1,1),
    id_incidente INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_entrada DATETIME2 NOT NULL DEFAULT GETDATE(), -- Coincide con Python 'fecha_entrada'
    comentario NVARCHAR(MAX) NOT NULL,

    CONSTRAINT FK_Bitacora_Incidente FOREIGN KEY (id_incidente) REFERENCES Incidentes(id_incidente) ON DELETE CASCADE,
    CONSTRAINT FK_Bitacora_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

PRINT '>> Tablas creadas correctamente.';
GO

-- 3. CARGA DE CATÁLOGOS (Datos obligatorios)

INSERT INTO cat_Prioridades (nivel, valor_orden) VALUES
('Baja', 1), ('Media', 2), ('Alta', 3), ('Crítica', 4);

INSERT INTO cat_Estados (nombre) VALUES
('Nuevo'), ('En Investigación'), ('Contenido'), ('Erradicado'), ('Cerrado'), ('Falso Positivo');

INSERT INTO cat_Tipos_Incidente (nombre, descripcion) VALUES
('Phishing', 'Ingeniería social vía correo electrónico.'),
('Malware', 'Software malicioso (virus, ransomware, troyano).'),
('Acceso No Autorizado', 'Inicio de sesión desde fuente desconocida.'),
('Denegación de Servicio (DoS)', 'Ataque de sobrecarga.'),
('Exfiltración de Datos', 'Fuga de información sensible.');

-- Usuario Administrador Inicial
INSERT INTO Usuarios (nombre_completo, email, rol) VALUES
('Admin Sistema', 'admin@sicc.com', 'Administrador');

PRINT '>> Estructura creada y catálogos cargados correctamente.';
GO