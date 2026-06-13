-- SICC PostgreSQL — Transacciones explícitas, bloqueo FOR UPDATE y SP atómico
-- Requiere 06_vistas_procedimientos.sql. Idempotente.

-- ============================================================
-- SP: actualizar propietario con bloqueo pesimista (FOR UPDATE)
-- ============================================================

CREATE OR REPLACE FUNCTION sp_actualizar_propietario_activo(
    p_activo_uuid UUID,
    p_propietario VARCHAR(200)
)
RETURNS TABLE (
    uuid UUID,
    hostname VARCHAR(100),
    propietario VARCHAR(200),
    eliminado BOOLEAN
) AS $$
DECLARE
    v_row RECORD;
BEGIN
    SELECT a.uuid, a.hostname, a.propietario, a.eliminado
    INTO v_row
    FROM Activos a
    WHERE a.uuid = p_activo_uuid
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Activo % no encontrado', p_activo_uuid;
    END IF;

    IF v_row.eliminado THEN
        RAISE EXCEPTION 'Activo % está dado de baja', p_activo_uuid;
    END IF;

    UPDATE Activos
    SET propietario = p_propietario,
        updated_at = CURRENT_TIMESTAMP
    WHERE Activos.uuid = p_activo_uuid;

    RETURN QUERY
    SELECT a.uuid, a.hostname, a.propietario, a.eliminado
    FROM Activos a
    WHERE a.uuid = p_activo_uuid;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION sp_actualizar_propietario_activo(UUID, VARCHAR) TO sicc_api;

-- ============================================================
-- DEMO 1: transacción exitosa con sp_cerrar_incidente (ROLLBACK al final)
-- UUID demo: a1000001-0001-4000-8000-000000000001
-- ============================================================
-- BEGIN;
-- SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- SELECT * FROM sp_cerrar_incidente(
--     'a1000001-0001-4000-8000-000000000001'::uuid,
--     NOW()
-- );
-- ROLLBACK;

-- ============================================================
-- DEMO 2: rollback ante FK inválida (no persiste cambios)
-- ============================================================
-- BEGIN;
-- UPDATE Incidentes SET id_estado = 99999
-- WHERE uuid = 'a1000001-0001-4000-8000-000000000001';
-- ROLLBACK;

-- ============================================================
-- DEMO 3: REPEATABLE READ — conteo estable en la misma transacción
-- Ejecutar SELECT dos veces; en otra sesión INSERT+COMMIT entre medias
-- ============================================================
-- BEGIN;
-- SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- SELECT COUNT(*) AS total_snapshot FROM Incidentes WHERE eliminado = FALSE;
-- -- (otra sesión: insertar incidente y COMMIT)
-- SELECT COUNT(*) AS total_misma_tx FROM Incidentes WHERE eliminado = FALSE;
-- COMMIT;

-- ============================================================
-- DEMO 4: bloqueo pesimista vía SP
-- Activos demo SC: b1000001-0001-4000-8000-000000000001
-- ============================================================
-- BEGIN;
-- SELECT * FROM sp_actualizar_propietario_activo(
--     'b1000001-0001-4000-8000-000000000001'::uuid,
--     'Propietario TX demo'
-- );
-- ROLLBACK;
