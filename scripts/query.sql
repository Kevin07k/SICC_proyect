USE DB_GestionIncidentes

SELECT *
FROM Incidentes



USE DB_GestionIncidentes;
GO
SET STATISTICS IO, TIME ON;
GO

-- =======================================================
-- LIMPIEZA DE CACHÉ (Para prueba justa - Cold Cache)
-- =======================================================
DBCC FREEPROCCACHE;   -- Limpia el caché de planes de ejecución
DBCC DROPCLEANBUFFERS; -- Limpia el caché de datos en memoria (buffer pool)
GO

-- Prueba SIN Índice (Forzando escaneo completo)
SELECT TOP 50 id_incidente, titulo, fecha_creacion, id_prioridad, id_estado
FROM Incidentes WITH (INDEX(0))
WHERE id_prioridad IN (1, 2) AND id_estado <> 4 AND eliminado = 0
ORDER BY fecha_creacion DESC;
GO

-- =======================================================
-- LIMPIEZA DE CACHÉ (Para prueba justa - Cold Cache)
-- =======================================================
DBCC FREEPROCCACHE;
DBCC DROPCLEANBUFFERS;
GO

-- Prueba CON Índice (Usando IX_Incidentes_PrioridadEstado_Soporte)
SELECT TOP 50 id_incidente, titulo, fecha_creacion, id_prioridad, id_estado
FROM Incidentes
WHERE id_prioridad IN (1, 2) AND id_estado <> 4 AND eliminado = 0
ORDER BY fecha_creacion DESC;

SET STATISTICS IO, TIME OFF;
GO

----------------------------------------------------

SELECT TOP 20 * FROM vw_Auditoria_Incidentes_Sede;


SELECT * FROM vw_Incidentes_Criticos_Abiertos;


----------------------------------------------------

DECLARE @NuevoID INT;
EXEC sp_RegistrarIncidenteCompleto 
    @titulo = 'Falla de conexión en el servidor principal',
    @descripcion_detallada = 'No hay ping al servidor desde la VLAN 20.',
    @id_tipo = 1,
    @id_prioridad = 1, -- Alta
    @id_estado = 1, -- Abierto
    @id_usuario_asignado = 1, -- Usamos el ID 1 (el administrador por defecto)
    @id_activo = 3; -- ID de activo opcional


-- Cierra el incidente ID 1 (Cambia al ID generado en el paso anterior)
EXEC sp_CerrarIncidente 
    @id_incidente = 1,
    @id_usuario_cierre = 1,
    @nota_cierre = 'Servidor reiniciado, conexión restablecida con éxito.';

-- Verificando que se cambió el estado y se registró en la bitácora
SELECT id_incidente, id_estado, fecha_cierre FROM Incidentes WHERE id_incidente = 1;
SELECT * FROM Bitacora_Investigacion WHERE id_incidente = 1;