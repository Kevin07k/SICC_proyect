USE DB_GestionIncidentes;
GO

-- =============================================
-- Vista: vw_Auditoria_Incidentes_Sede
-- Descripción: Muestra información detallada de los incidentes relacionando estado, 
--              activo afectado, sede a la que pertenece y nivel de criticidad de la misma. 
--              Es útil para auditorías operativas y generación de reportes gerenciales.
-- =============================================
-- =============================================
-- Vista: vw_Auditoria_Incidentes_Sede
-- =============================================
CREATE OR ALTER VIEW vw_Auditoria_Incidentes_Sede AS
SELECT 
    i.id_incidente,
    i.titulo AS titulo_incidente,
    i.fecha_creacion,
    e.nombre AS estado_incidente,
    a.hostname AS activo_afectado,
    a.tipo_activo,
    s.nombre_sede AS sede_afectada,
    s.nivel_criticidad AS criticidad_sede
FROM Incidentes i
INNER JOIN Incidentes_Activos ia ON i.id_incidente = ia.id_incidente
INNER JOIN Activos a ON ia.id_activo = a.id_activo
INNER JOIN cat_Estados e ON i.id_estado = e.id_estado
LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede
WHERE i.eliminado = 0 AND a.eliminado = 0;
GO

-- =============================================
-- Vista: vw_Incidentes_Criticos_Abiertos
-- =============================================
CREATE OR ALTER VIEW vw_Incidentes_Criticos_Abiertos AS
SELECT TOP 50
    i.id_incidente,
    i.titulo,
    i.fecha_creacion,
    ISNULL((
        SELECT STRING_AGG(ISNULL(s.nombre_sede, 'Sin Sede'), ', ')
        FROM Incidentes_Activos ia
        INNER JOIN Activos a ON ia.id_activo = a.id_activo AND a.eliminado = 0
        LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede AND s.eliminado = 0
        WHERE ia.id_incidente = i.id_incidente
    ), 'Sin Activos') AS sedes_afectadas,
    p.nivel AS prioridad
FROM Incidentes i
INNER JOIN cat_Prioridades p ON i.id_prioridad = p.id_prioridad
INNER JOIN cat_Estados e ON i.id_estado = e.id_estado
WHERE p.nivel IN ('Alta', 'Crítica') AND e.nombre <> 'Cerrado' AND i.eliminado = 0
ORDER BY i.fecha_creacion DESC;
GO

-- =============================================
-- Vista: vw_Top_Activos_Atacados
-- =============================================
CREATE OR ALTER VIEW vw_Top_Activos_Atacados AS
SELECT TOP 10
    a.id_activo,
    a.hostname,
    COUNT(ia.id_incidente) AS total_incidentes
FROM Activos a
INNER JOIN Incidentes_Activos ia ON a.id_activo = ia.id_activo
INNER JOIN Incidentes i ON ia.id_incidente = i.id_incidente AND i.eliminado = 0
WHERE a.eliminado = 0
GROUP BY a.id_activo, a.hostname
ORDER BY total_incidentes DESC;
GO

PRINT '>> Vistas Creadas Correctamente.';
GO
