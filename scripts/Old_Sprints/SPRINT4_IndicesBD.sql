USE DB_GestionIncidentes;
GO

PRINT '--- 1. Creando Índices No Agrupados (Non-Clustered Indexes) ---';

-- Índice para acelerar las búsquedas y ordenamientos por fecha de creación (muy común en el listado principal)
CREATE NONCLUSTERED INDEX IX_Incidentes_FechaCreacion
ON Incidentes(fecha_creacion DESC);
GO

-- Índice para acelerar los JOINs y filtros cuando buscamos activos por su sede (SPRINT 1)
-- Incluimos el hostname para consultas ligeras (Covering Index)
CREATE NONCLUSTERED INDEX IX_Activos_IDSede
ON Activos(id_sede)
INCLUDE (hostname);
GO

PRINT '>> SPRINT 4: Índices IX_Incidentes_FechaCreacion y IX_Activos_IDSede creados correctamente.';
GO
