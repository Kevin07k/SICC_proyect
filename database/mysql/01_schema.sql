-- SICC — MySQL Secundaria (Cochabamba)
-- DDL completo: metadata replicada + datos operacionales locales

CREATE DATABASE IF NOT EXISTS sicc_cochabamba
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sicc_cochabamba;

CREATE TABLE cat_Sedes (
    id_sede          INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sede      VARCHAR(100) NOT NULL UNIQUE,
    nivel_criticidad VARCHAR(50)  NOT NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado        TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE Roles (
    id_rol      INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE Permisos (
    id_permiso  INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    codigo      VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE Roles_Permisos (
    id_rol     INT NOT NULL,
    id_permiso INT NOT NULL,
    PRIMARY KEY (id_rol, id_permiso),
    FOREIGN KEY (id_rol)     REFERENCES Roles(id_rol),
    FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso)
) ENGINE=InnoDB;

CREATE TABLE cat_Estados (
    id_estado  INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado  TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE cat_Prioridades (
    id_prioridad INT AUTO_INCREMENT PRIMARY KEY,
    nivel        VARCHAR(50) NOT NULL UNIQUE,
    valor_orden  INT NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado    TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE cat_Tipos_Incidente (
    id_tipo     INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(500),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado   TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE Usuarios (
    uuid            CHAR(36) PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    id_sede         INT NOT NULL,
    id_rol          INT NOT NULL,
    activo          TINYINT(1) NOT NULL DEFAULT 1,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_sede) REFERENCES cat_Sedes(id_sede),
    FOREIGN KEY (id_rol)  REFERENCES Roles(id_rol)
) ENGINE=InnoDB;

CREATE TABLE Sesiones (
    token         VARCHAR(255) PRIMARY KEY,
    usuario_uuid  CHAR(36) NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at    TIMESTAMP NOT NULL,
    FOREIGN KEY (usuario_uuid) REFERENCES Usuarios(uuid)
) ENGINE=InnoDB;

CREATE TABLE sync_control (
    id          INT PRIMARY KEY DEFAULT 1,
    last_sync   TIMESTAMP NOT NULL DEFAULT '1970-01-01 00:00:01',
    nodo_origen VARCHAR(20) NOT NULL DEFAULT 'mysql',
    CONSTRAINT sync_control_single_row CHECK (id = 1)
) ENGINE=InnoDB;

CREATE TABLE Activos (
    uuid           CHAR(36) PRIMARY KEY,
    hostname       VARCHAR(100) NOT NULL,
    direccion_ip   VARCHAR(45),
    tipo_activo    VARCHAR(100),
    propietario    VARCHAR(200),
    id_sede        INT NOT NULL,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado      TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_sede) REFERENCES cat_Sedes(id_sede)
) ENGINE=InnoDB;

CREATE TABLE Incidentes (
    uuid                CHAR(36) PRIMARY KEY,
    titulo              VARCHAR(255) NOT NULL,
    descripcion         TEXT,
    id_tipo             INT NOT NULL,
    id_prioridad        INT NOT NULL,
    id_estado           INT NOT NULL,
    id_usuario_asignado CHAR(36) NOT NULL,
    id_sede             INT NOT NULL,
    fecha_cierre        TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado           TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_tipo)              REFERENCES cat_Tipos_Incidente(id_tipo),
    FOREIGN KEY (id_prioridad)         REFERENCES cat_Prioridades(id_prioridad),
    FOREIGN KEY (id_estado)            REFERENCES cat_Estados(id_estado),
    FOREIGN KEY (id_usuario_asignado)  REFERENCES Usuarios(uuid),
    FOREIGN KEY (id_sede)              REFERENCES cat_Sedes(id_sede)
) ENGINE=InnoDB;

CREATE TABLE Incidentes_Activos (
    uuid                     CHAR(36) PRIMARY KEY,
    id_incidente             CHAR(36) NOT NULL,
    id_activo                CHAR(36) NOT NULL,
    notas                    VARCHAR(300),
    tipo_activo_registrado   VARCHAR(100),
    sede_registrada          VARCHAR(100),
    hostname_registrado      VARCHAR(100),
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_incidente_activo (id_incidente, id_activo),
    FOREIGN KEY (id_incidente) REFERENCES Incidentes(uuid),
    FOREIGN KEY (id_activo)    REFERENCES Activos(uuid)
) ENGINE=InnoDB;

CREATE TABLE Bitacora_Investigacion (
    uuid          CHAR(36) PRIMARY KEY,
    id_incidente  CHAR(36) NOT NULL,
    id_usuario    CHAR(36) NOT NULL,
    comentario    TEXT,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado     TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_incidente) REFERENCES Incidentes(uuid),
    FOREIGN KEY (id_usuario)   REFERENCES Usuarios(uuid)
) ENGINE=InnoDB;

CREATE INDEX idx_usuarios_email ON Usuarios(email);
CREATE INDEX idx_usuarios_id_sede ON Usuarios(id_sede);
CREATE INDEX idx_sesiones_usuario ON Sesiones(usuario_uuid);
CREATE INDEX idx_sesiones_expires ON Sesiones(expires_at);
CREATE INDEX idx_incidentes_sede ON Incidentes(id_sede);
CREATE INDEX idx_incidentes_estado ON Incidentes(id_estado);
CREATE INDEX idx_incidentes_prioridad ON Incidentes(id_prioridad);
CREATE INDEX idx_incidentes_asignado ON Incidentes(id_usuario_asignado);
CREATE INDEX idx_incidentes_fecha ON Incidentes(created_at);
CREATE INDEX idx_activos_sede ON Activos(id_sede);
CREATE INDEX idx_activos_hostname ON Activos(hostname);
CREATE INDEX idx_activos_eliminado ON Activos(eliminado);
CREATE INDEX idx_incidentes_activos_incidente ON Incidentes_Activos(id_incidente);
CREATE INDEX idx_incidentes_activos_activo ON Incidentes_Activos(id_activo);
CREATE INDEX idx_bitacora_incidente ON Bitacora_Investigacion(id_incidente);
CREATE INDEX idx_bitacora_usuario ON Bitacora_Investigacion(id_usuario);
