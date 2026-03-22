USE DB_GestionIncidentes;
GO

-- =============================================
-- Vista: vw_Auditoria_Incidentes_Sede
-- Descripción: Muestra información detallada de los incidentes relacionando estado, 
--              activo afectado, sede a la que pertenece y nivel de criticidad de la misma. 
--              Es útil para auditorías operativas y generación de reportes gerenciales.
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
LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede;
GO

-- =============================================
-- Vista: vw_Incidentes_Criticos_Abiertos
-- Descripción: Filtra y muestra todos los incidentes con nivel de prioridad crítico o alto 
--              que aún no se encuentran cerrados. Facilita la atención prioritaria de casos graves 
--              y el monitoreo de incidentes en sedes afectadas.
-- =============================================
CREATE OR ALTER VIEW vw_Incidentes_Criticos_Abiertos AS
SELECT 
    i.id_incidente,
    i.titulo,
    i.fecha_creacion,
    s.nombre_sede,
    p.nivel AS prioridad
FROM Incidentes i
INNER JOIN cat_Prioridades p ON i.id_prioridad = p.id_prioridad
INNER JOIN cat_Estados e ON i.id_estado = e.id_estado
LEFT JOIN Incidentes_Activos ia ON i.id_incidente = ia.id_incidente
LEFT JOIN Activos a ON ia.id_activo = a.id_activo
LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede
WHERE p.nivel IN ('Alta', 'Crítica') AND e.nombre <> 'Cerrado';
GO

-- =============================================
-- Vista: vw_Top_Activos_Atacados
-- Descripción: Calcula y muestra el conteo total de incidentes reportados por cada activo 
--              (hostname). Útil para identificar qué equipos o servidores están siendo 
--              atacados o comprometidos de forma reiterada.
-- =============================================
CREATE OR ALTER VIEW vw_Top_Activos_Atacados AS
SELECT 
    a.id_activo,
    a.hostname,
    COUNT(ia.id_incidente) AS total_incidentes
FROM Activos a
LEFT JOIN Incidentes_Activos ia ON a.id_activo = ia.id_activo
GROUP BY a.id_activo, a.hostname;
GO

PRINT '>> Vistas Creadas Correctamente.';
GO
