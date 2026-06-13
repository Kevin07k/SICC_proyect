-- SICC MySQL — Transacciones explícitas, bloqueo FOR UPDATE y SP atómico
-- Requiere 06_vistas_procedimientos.sql. Usa DELIMITER.

USE sicc_cochabamba;

DROP PROCEDURE IF EXISTS sp_actualizar_propietario_activo;

DELIMITER $$

CREATE PROCEDURE sp_actualizar_propietario_activo(
    IN p_activo_uuid CHAR(36),
    IN p_propietario VARCHAR(200)
)
BEGIN
    DECLARE v_eliminado TINYINT;

    SELECT eliminado INTO v_eliminado
    FROM Activos
    WHERE uuid = p_activo_uuid
    FOR UPDATE;

    IF v_eliminado IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Activo no encontrado';
    END IF;

    IF v_eliminado = 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Activo dado de baja';
    END IF;

    UPDATE Activos
    SET propietario = p_propietario,
        updated_at = CURRENT_TIMESTAMP
    WHERE uuid = p_activo_uuid;

    SELECT uuid, hostname, propietario, eliminado
    FROM Activos
    WHERE uuid = p_activo_uuid;
END$$

DELIMITER ;

GRANT EXECUTE ON PROCEDURE sp_actualizar_propietario_activo TO 'sicc_api'@'%';

-- DEMO 1: CALL sp_cerrar_incidente en transacción + ROLLBACK
-- Incidente demo CB: a2000001-0001-4000-8000-000000000001 (si existe tras apply_demo_seed)
-- START TRANSACTION;
-- SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- CALL sp_cerrar_incidente('a2000001-0001-4000-8000-000000000001', NOW());
-- ROLLBACK;

-- DEMO 2: rollback FK inválida
-- START TRANSACTION;
-- UPDATE Incidentes SET id_estado = 99999 WHERE uuid = 'a2000001-0001-4000-8000-000000000001';
-- ROLLBACK;

-- DEMO 3: REPEATABLE READ
-- START TRANSACTION;
-- SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- SELECT COUNT(*) FROM Incidentes WHERE eliminado = 0;
-- SELECT COUNT(*) FROM Incidentes WHERE eliminado = 0;
-- COMMIT;

-- DEMO 4: bloqueo pesimista
-- Activos demo CB: b2000001-0001-4000-8000-000000000001
-- START TRANSACTION;
-- CALL sp_actualizar_propietario_activo('b2000001-0001-4000-8000-000000000001', 'Propietario TX demo');
-- ROLLBACK;
