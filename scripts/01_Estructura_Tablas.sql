USE master;
GO

IF EXISTS (SELECT name
FROM sys.databases
WHERE name = 'DB_GestionIncidentes')
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

CREATE TABLE cat_Tipos_Incidente
(
    id_tipo INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(100) NOT NULL UNIQUE,
    descripcion NVARCHAR(500),
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE cat_Prioridades
(
    id_prioridad INT PRIMARY KEY IDENTITY(1,1),
    nivel NVARCHAR(50) NOT NULL UNIQUE,
    valor_orden INT NOT NULL UNIQUE,
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE cat_Estados
(
    id_estado INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(50) NOT NULL UNIQUE,
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE cat_Sedes
(
    id_sede INT PRIMARY KEY IDENTITY(1,1),
    nombre_sede NVARCHAR(100) NOT NULL UNIQUE,
    nivel_criticidad NVARCHAR(50) NOT NULL,
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE Usuarios
(
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    nombre_completo NVARCHAR(200) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    rol NVARCHAR(100) NOT NULL DEFAULT 'Analista',
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE Activos
(
    id_activo INT PRIMARY KEY IDENTITY(1,1),
    hostname NVARCHAR(100) NOT NULL UNIQUE,
    direccion_ip NVARCHAR(45),
    tipo_activo NVARCHAR(100),
    propietario NVARCHAR(200),
    id_sede INT NULL,
    CONSTRAINT FK_Activos_Sede FOREIGN KEY (id_sede) REFERENCES cat_Sedes(id_sede),
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE Incidentes
(
    id_incidente INT PRIMARY KEY IDENTITY(1,1),
    titulo NVARCHAR(255) NOT NULL,
    descripcion_detallada NVARCHAR(MAX) NOT NULL,
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0,
    fecha_cierre DATETIME2 NULL,
    id_tipo INT NOT NULL,
    id_prioridad INT NOT NULL,
    id_estado INT NOT NULL,
    id_usuario_asignado INT NULL,
    CONSTRAINT FK_Incidentes_Tipo FOREIGN KEY (id_tipo) REFERENCES cat_Tipos_Incidente(id_tipo),
    CONSTRAINT FK_Incidentes_Prioridad FOREIGN KEY (id_prioridad) REFERENCES cat_Prioridades(id_prioridad),
    CONSTRAINT FK_Incidentes_Estado FOREIGN KEY (id_estado) REFERENCES cat_Estados(id_estado),
    CONSTRAINT FK_Incidentes_Usuario FOREIGN KEY (id_usuario_asignado) REFERENCES Usuarios(id_usuario)
);

CREATE TABLE Incidentes_Activos
(
    id_incidente_activo INT PRIMARY KEY IDENTITY(1, 1),
    id_incidente INT NOT NULL,
    id_activo INT NOT NULL,
    notas_relacion NVARCHAR(300),
    CONSTRAINT FK_IA_Incidente FOREIGN KEY (id_incidente) REFERENCES Incidentes(id_incidente) ON DELETE CASCADE,
    CONSTRAINT FK_IA_Activo FOREIGN KEY (id_activo) REFERENCES Activos(id_activo) ON DELETE CASCADE,
    CONSTRAINT UQ_Incidente_Activo UNIQUE (id_incidente, id_activo),
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0
);

CREATE TABLE Bitacora_Investigacion
(
    id_bitacora INT PRIMARY KEY IDENTITY(1,1),
    id_incidente INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_entrada DATETIME2 NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    eliminado BIT NOT NULL DEFAULT 0,
    comentario NVARCHAR(MAX) NOT NULL,
    CONSTRAINT FK_Bitacora_Incidente FOREIGN KEY (id_incidente) REFERENCES Incidentes(id_incidente) ON DELETE CASCADE,
    CONSTRAINT FK_Bitacora_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);
PRINT '>> Estructura de Tablas creada.';
GO
