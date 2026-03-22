USE DB_GestionIncidentes;
GO

-- =============================================
-- Índice: IX_Incidentes_FechaCreacion (Non-Clustered)
-- Descripción: 1. Índice para acelerar las búsquedas y ordenamientos por fecha de creación.
--              Permite generar historiales y reportes de forma mucho más eficiente.
-- =============================================
CREATE NONCLUSTERED INDEX IX_Incidentes_FechaCreacion
ON Incidentes(fecha_creacion DESC);
GO

-- =============================================
-- Índice: IX_Activos_IDSede (Non-Clustered)
-- Descripción: 2. Índice para acelerar los filtros al buscar activos pertenecientes a una sede
--              en específico. Incluye el hostname para resolver la consulta sin ir a la tabla principal.
-- =============================================
CREATE NONCLUSTERED INDEX IX_Activos_IDSede
ON Activos(id_sede)
INCLUDE (hostname);
GO

-- =============================================
-- Índice: IX_Incidentes_PrioridadEstado_Soporte (Non-Clustered)
-- Descripción: 3. Índice compuesto robusto para optimizar la vista vw_Incidentes_Criticos_Abiertos.
--              Cubre filtros comunes por prioridad y estado, e incluye columnas adicionales 
--              muy consultadas (título, fecha de creación, analista).
-- =============================================
CREATE NONCLUSTERED INDEX IX_Incidentes_PrioridadEstado_Soporte
ON Incidentes (id_prioridad, id_estado)
INCLUDE (titulo, fecha_creacion, id_usuario_asignado);
GO

-- =============================================
-- Índice: IX_Incidentes_Activos_SoporteGroup (Non-Clustered)
-- Descripción: 4. Índice de cobertura para optimizar agrupaciones como COUNT() utilizadas
--              en vw_Top_Activos_Atacados. Permite contar cuántos incidentes tiene un activo 
--              rápidamente gracias al índice sobre id_activo incluyendo el id_incidente.
-- =============================================
CREATE NONCLUSTERED INDEX IX_Incidentes_Activos_SoporteGroup
ON Incidentes_Activos (id_activo)
INCLUDE (id_incidente);
GO

PRINT '>> Índices Creados Correctamente.';
GO
