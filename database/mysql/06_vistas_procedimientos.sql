-- SICC MySQL — Vistas, procedimientos almacenados y triggers (idempotente)
-- Requiere cliente mysql con soporte DELIMITER si se ejecuta a mano.
-- init_databases.py usa el CLI mysql cuando el archivo contiene DELIMITER.

USE sicc_cochabamba;

-- Triggers con binary log (MySQL 8): requiere root o --log-bin-trust-function-creators=1
SET GLOBAL log_bin_trust_function_creators = 1;

-- ============================================================
-- TRIGGERS updated_at (paridad con PostgreSQL)
-- ============================================================

DROP TRIGGER IF EXISTS trg_cat_sedes_updated_at;
DROP TRIGGER IF EXISTS trg_roles_updated_at;
DROP TRIGGER IF EXISTS trg_permisos_updated_at;
DROP TRIGGER IF EXISTS trg_cat_estados_updated_at;
DROP TRIGGER IF EXISTS trg_cat_prioridades_updated_at;
DROP TRIGGER IF EXISTS trg_cat_tipos_incidente_updated_at;
DROP TRIGGER IF EXISTS trg_usuarios_updated_at;
DROP TRIGGER IF EXISTS trg_activos_updated_at;
DROP TRIGGER IF EXISTS trg_incidentes_updated_at;
DROP TRIGGER IF EXISTS trg_incidentes_activos_updated_at;
DROP TRIGGER IF EXISTS trg_bitacora_updated_at;

DELIMITER $$

CREATE TRIGGER trg_cat_sedes_updated_at
BEFORE UPDATE ON cat_Sedes
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_roles_updated_at
BEFORE UPDATE ON Roles
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_permisos_updated_at
BEFORE UPDATE ON Permisos
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_cat_estados_updated_at
BEFORE UPDATE ON cat_Estados
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_cat_prioridades_updated_at
BEFORE UPDATE ON cat_Prioridades
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_cat_tipos_incidente_updated_at
BEFORE UPDATE ON cat_Tipos_Incidente
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_usuarios_updated_at
BEFORE UPDATE ON Usuarios
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_activos_updated_at
BEFORE UPDATE ON Activos
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_incidentes_updated_at
BEFORE UPDATE ON Incidentes
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_incidentes_activos_updated_at
BEFORE UPDATE ON Incidentes_Activos
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER trg_bitacora_updated_at
BEFORE UPDATE ON Bitacora_Investigacion
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

DELIMITER ;

-- ============================================================
-- VISTAS
-- ============================================================

CREATE OR REPLACE VIEW vw_incidentes_detalle AS
SELECT
    i.uuid,
    i.titulo,
    i.descripcion,
    i.id_sede,
    s.nombre_sede,
    e.nombre AS estado,
    p.nivel AS prioridad,
    t.nombre AS tipo_incidente,
    u.nombre_completo AS analista_asignado,
    i.fecha_cierre,
    i.created_at,
    i.updated_at,
    i.eliminado
FROM Incidentes i
JOIN cat_Sedes s ON s.id_sede = i.id_sede
JOIN cat_Estados e ON e.id_estado = i.id_estado
JOIN cat_Prioridades p ON p.id_prioridad = i.id_prioridad
JOIN cat_Tipos_Incidente t ON t.id_tipo = i.id_tipo
JOIN Usuarios u ON u.uuid = i.id_usuario_asignado
WHERE i.eliminado = 0;

CREATE OR REPLACE VIEW vw_incidentes_activos_vinculados AS
SELECT
    ia.uuid AS vinculo_uuid,
    i.uuid AS incidente_uuid,
    i.titulo AS incidente_titulo,
    a.uuid AS activo_uuid,
    a.hostname,
    a.direccion_ip,
    ia.notas,
    ia.tipo_activo_registrado,
    ia.sede_registrada,
    ia.hostname_registrado,
    ia.created_at AS vinculado_en
FROM Incidentes_Activos ia
JOIN Incidentes i ON i.uuid = ia.id_incidente AND i.eliminado = 0
JOIN Activos a ON a.uuid = ia.id_activo AND a.eliminado = 0;

CREATE OR REPLACE VIEW vw_resumen_incidentes_por_estado AS
SELECT
    i.id_sede,
    s.nombre_sede,
    e.nombre AS estado,
    COUNT(*) AS total_incidentes
FROM Incidentes i
JOIN cat_Sedes s ON s.id_sede = i.id_sede
JOIN cat_Estados e ON e.id_estado = i.id_estado
WHERE i.eliminado = 0
GROUP BY i.id_sede, s.nombre_sede, e.nombre, e.id_estado
ORDER BY i.id_sede, e.id_estado;

-- ============================================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================================

DROP PROCEDURE IF EXISTS sp_cerrar_incidente;
DROP PROCEDURE IF EXISTS sp_resumen_operacional_sede;

DELIMITER $$

CREATE PROCEDURE sp_cerrar_incidente(
    IN p_incidente_uuid CHAR(36),
    IN p_fecha_cierre TIMESTAMP
)
BEGIN
    DECLARE v_estado_cerrado INT;
    DECLARE v_fecha TIMESTAMP;

    SELECT id_estado INTO v_estado_cerrado
    FROM cat_Estados
    WHERE nombre = 'Cerrado' AND eliminado = 0
    LIMIT 1;

    IF v_estado_cerrado IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No existe estado Cerrado en cat_Estados';
    END IF;

    SET v_fecha = COALESCE(p_fecha_cierre, CURRENT_TIMESTAMP);

    UPDATE Incidentes
    SET id_estado = v_estado_cerrado,
        fecha_cierre = v_fecha,
        updated_at = CURRENT_TIMESTAMP
    WHERE uuid = p_incidente_uuid
      AND eliminado = 0;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Incidente no encontrado o ya eliminado';
    END IF;

    SELECT uuid, titulo, fecha_cierre, id_estado
    FROM Incidentes
    WHERE uuid = p_incidente_uuid;
END$$

CREATE PROCEDURE sp_resumen_operacional_sede(IN p_id_sede INT)
BEGIN
    SELECT 'incidentes_activos' AS metrica, COUNT(*) AS valor
    FROM Incidentes
    WHERE id_sede = p_id_sede AND eliminado = 0
    UNION ALL
    SELECT 'activos_activos', COUNT(*)
    FROM Activos
    WHERE id_sede = p_id_sede AND eliminado = 0
    UNION ALL
    SELECT 'vinculos_incidente_activo', COUNT(*)
    FROM Incidentes_Activos ia
    JOIN Incidentes i ON i.uuid = ia.id_incidente
    WHERE i.id_sede = p_id_sede AND i.eliminado = 0;
END$$

DELIMITER ;

GRANT SELECT ON vw_incidentes_detalle TO 'sicc_api'@'%';
GRANT SELECT ON vw_incidentes_activos_vinculados TO 'sicc_api'@'%';
GRANT SELECT ON vw_resumen_incidentes_por_estado TO 'sicc_api'@'%';
GRANT EXECUTE ON PROCEDURE sp_cerrar_incidente TO 'sicc_api'@'%';
GRANT EXECUTE ON PROCEDURE sp_resumen_operacional_sede TO 'sicc_api'@'%';
