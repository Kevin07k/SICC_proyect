-- SICC PostgreSQL — Vistas, funciones/procedimientos y triggers (idempotente)
-- Ejecutado tras 01_schema + 02_seed por init_databases.py

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
WHERE i.eliminado = FALSE;

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
JOIN Incidentes i ON i.uuid = ia.id_incidente AND i.eliminado = FALSE
JOIN Activos a ON a.uuid = ia.id_activo AND a.eliminado = FALSE;

CREATE OR REPLACE VIEW vw_resumen_incidentes_por_estado AS
SELECT
    i.id_sede,
    s.nombre_sede,
    e.nombre AS estado,
    COUNT(*)::INTEGER AS total_incidentes
FROM Incidentes i
JOIN cat_Sedes s ON s.id_sede = i.id_sede
JOIN cat_Estados e ON e.id_estado = i.id_estado
WHERE i.eliminado = FALSE
GROUP BY i.id_sede, s.nombre_sede, e.nombre, e.id_estado
ORDER BY i.id_sede, e.id_estado;

-- ============================================================
-- FUNCIÓN / PROCEDIMIENTO: cierre de incidente
-- ============================================================

CREATE OR REPLACE FUNCTION sp_cerrar_incidente(
    p_incidente_uuid UUID,
    p_fecha_cierre TIMESTAMP DEFAULT NULL
)
RETURNS TABLE (
    incidente_uuid UUID,
    titulo VARCHAR(255),
    fecha_cierre TIMESTAMP,
    id_estado INTEGER
) AS $$
DECLARE
    v_estado_cerrado INTEGER;
    v_fecha TIMESTAMP;
BEGIN
    SELECT id_estado INTO v_estado_cerrado
    FROM cat_Estados
    WHERE nombre = 'Cerrado' AND eliminado = FALSE
    LIMIT 1;

    IF v_estado_cerrado IS NULL THEN
        RAISE EXCEPTION 'No existe estado Cerrado en cat_Estados';
    END IF;

    v_fecha := COALESCE(p_fecha_cierre, CURRENT_TIMESTAMP);

    UPDATE Incidentes
    SET id_estado = v_estado_cerrado,
        fecha_cierre = v_fecha,
        updated_at = CURRENT_TIMESTAMP
    WHERE uuid = p_incidente_uuid
      AND eliminado = FALSE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Incidente % no encontrado o ya eliminado', p_incidente_uuid;
    END IF;

    RETURN QUERY
    SELECT i.uuid, i.titulo, i.fecha_cierre, i.id_estado
    FROM Incidentes i
    WHERE i.uuid = p_incidente_uuid;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- PROCEDIMIENTO: resumen por sede (para reportes locales)
-- ============================================================

CREATE OR REPLACE FUNCTION sp_resumen_operacional_sede(p_id_sede INTEGER)
RETURNS TABLE (
    metrica TEXT,
    valor BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'incidentes_activos'::TEXT, COUNT(*)
    FROM Incidentes
    WHERE id_sede = p_id_sede AND eliminado = FALSE
    UNION ALL
    SELECT 'activos_activos'::TEXT, COUNT(*)
    FROM Activos
    WHERE id_sede = p_id_sede AND eliminado = FALSE
    UNION ALL
    SELECT 'vinculos_incidente_activo'::TEXT, COUNT(*)
    FROM Incidentes_Activos ia
    JOIN Incidentes i ON i.uuid = ia.id_incidente
    WHERE i.id_sede = p_id_sede AND i.eliminado = FALSE;
END;
$$ LANGUAGE plpgsql;

-- Permisos de lectura para API y reportes
GRANT SELECT ON vw_incidentes_detalle TO sicc_api, sicc_reportes;
GRANT SELECT ON vw_incidentes_activos_vinculados TO sicc_api, sicc_reportes;
GRANT SELECT ON vw_resumen_incidentes_por_estado TO sicc_api, sicc_reportes;
GRANT EXECUTE ON FUNCTION sp_cerrar_incidente(UUID, TIMESTAMP) TO sicc_api;
GRANT EXECUTE ON FUNCTION sp_resumen_operacional_sede(INTEGER) TO sicc_api, sicc_reportes;
