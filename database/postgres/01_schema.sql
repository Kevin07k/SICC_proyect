-- SICC — PostgreSQL Central (Santa Cruz)
-- DDL completo: metadata replicada + datos operacionales locales

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- CATÁLOGOS REPLICADOS
-- ============================================================

CREATE TABLE cat_Sedes (
    id_sede          SERIAL PRIMARY KEY,
    nombre_sede      VARCHAR(100) NOT NULL UNIQUE,
    nivel_criticidad VARCHAR(50)  NOT NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado        BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Roles (
    id_rol      SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Permisos (
    id_permiso  SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    codigo      VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Roles_Permisos (
    id_rol     INTEGER NOT NULL REFERENCES Roles(id_rol),
    id_permiso INTEGER NOT NULL REFERENCES Permisos(id_permiso),
    PRIMARY KEY (id_rol, id_permiso)
);

CREATE TABLE cat_Estados (
    id_estado  SERIAL PRIMARY KEY,
    nombre     VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado  BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE cat_Prioridades (
    id_prioridad SERIAL PRIMARY KEY,
    nivel        VARCHAR(50) NOT NULL UNIQUE,
    valor_orden  INTEGER NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado    BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE cat_Tipos_Incidente (
    id_tipo     SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(500),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado   BOOLEAN NOT NULL DEFAULT FALSE
);

-- ============================================================
-- USUARIOS Y SESIONES (REPLICADOS)
-- ============================================================

CREATE TABLE Usuarios (
    uuid            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    id_sede         INTEGER NOT NULL REFERENCES cat_Sedes(id_sede),
    id_rol          INTEGER NOT NULL REFERENCES Roles(id_rol),
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Sesiones (
    token         VARCHAR(255) PRIMARY KEY,
    usuario_uuid  UUID NOT NULL REFERENCES Usuarios(uuid),
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at    TIMESTAMP NOT NULL
);

CREATE TABLE sync_control (
    id          INTEGER PRIMARY KEY DEFAULT 1,
    last_sync   TIMESTAMP NOT NULL DEFAULT '1970-01-01 00:00:00',
    nodo_origen VARCHAR(20) NOT NULL DEFAULT 'postgres',
    CONSTRAINT sync_control_single_row CHECK (id = 1)
);

-- ============================================================
-- DATOS OPERACIONALES LOCALES (Santa Cruz)
-- ============================================================

CREATE TABLE Activos (
    uuid           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostname       VARCHAR(100) NOT NULL,
    direccion_ip   VARCHAR(45),
    tipo_activo    VARCHAR(100),
    propietario    VARCHAR(200),
    id_sede        INTEGER NOT NULL REFERENCES cat_Sedes(id_sede),
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado      BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Incidentes (
    uuid                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo              VARCHAR(255) NOT NULL,
    descripcion         TEXT,
    id_tipo             INTEGER NOT NULL REFERENCES cat_Tipos_Incidente(id_tipo),
    id_prioridad        INTEGER NOT NULL REFERENCES cat_Prioridades(id_prioridad),
    id_estado           INTEGER NOT NULL REFERENCES cat_Estados(id_estado),
    id_usuario_asignado UUID NOT NULL REFERENCES Usuarios(uuid),
    id_sede             INTEGER NOT NULL REFERENCES cat_Sedes(id_sede),
    fecha_cierre        TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado           BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Incidentes_Activos (
    uuid                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_incidente             UUID NOT NULL REFERENCES Incidentes(uuid),
    id_activo                UUID NOT NULL REFERENCES Activos(uuid),
    notas                    VARCHAR(300),
    tipo_activo_registrado   VARCHAR(100),
    sede_registrada          VARCHAR(100),
    hostname_registrado      VARCHAR(100),
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_incidente, id_activo)
);

CREATE TABLE Bitacora_Investigacion (
    uuid          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_incidente  UUID NOT NULL REFERENCES Incidentes(uuid),
    id_usuario    UUID NOT NULL REFERENCES Usuarios(uuid),
    comentario    TEXT,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eliminado     BOOLEAN NOT NULL DEFAULT FALSE
);

-- ============================================================
-- TRIGGERS: updated_at automático
-- ============================================================

CREATE OR REPLACE FUNCTION fn_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cat_sedes_updated_at
    BEFORE UPDATE ON cat_Sedes FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON Roles FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_permisos_updated_at
    BEFORE UPDATE ON Permisos FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_cat_estados_updated_at
    BEFORE UPDATE ON cat_Estados FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_cat_prioridades_updated_at
    BEFORE UPDATE ON cat_Prioridades FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_cat_tipos_incidente_updated_at
    BEFORE UPDATE ON cat_Tipos_Incidente FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_usuarios_updated_at
    BEFORE UPDATE ON Usuarios FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_activos_updated_at
    BEFORE UPDATE ON Activos FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_incidentes_updated_at
    BEFORE UPDATE ON Incidentes FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_incidentes_activos_updated_at
    BEFORE UPDATE ON Incidentes_Activos FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
CREATE TRIGGER trg_bitacora_updated_at
    BEFORE UPDATE ON Bitacora_Investigacion FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

-- ============================================================
-- ÍNDICES
-- ============================================================

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

-- ============================================================
-- CACHÉ REPORTES GLOBALES (solo lectura analítica)
-- ============================================================

CREATE TABLE reportes_cache (
    id            SERIAL PRIMARY KEY,
    clave         VARCHAR(64) NOT NULL UNIQUE DEFAULT 'global',
    payload       JSONB NOT NULL,
    generated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at    TIMESTAMP NOT NULL,
    duration_ms   INTEGER,
    source_nodes  TEXT[] NOT NULL DEFAULT ARRAY['postgres', 'mysql']
);

CREATE INDEX idx_reportes_cache_expires ON reportes_cache(expires_at);
