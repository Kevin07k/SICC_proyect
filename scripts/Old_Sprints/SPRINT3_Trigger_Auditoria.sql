USE DB_GestionIncidentes;
GO

PRINT '--- 1. Creando Trigger de Auditoría de Estados ---';
GO

CREATE OR ALTER TRIGGER trg_AuditoriaEstadoIncidente
ON Incidentes
AFTER UPDATE
AS
BEGIN
    -- Evitar que el trigger devuelva mensajes de filas afectadas que confundan a la app/ORM
    SET NOCOUNT ON;

    -- Validar si realmente se hizo una actualización y no es un update vacío
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;

    -- Comprobar específicamente si la columna id_estado fue modificada
    -- Usamos UPDATE() que es más óptimo, y luego verificamos que los valores sean distintos
    IF UPDATE(id_estado)
    BEGIN
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario)
        SELECT 
            i.id_incidente,
            -- En un entorno real, trataríamos de capturar el ID del usuario actual.
            -- Dejamos temporalmente el usuario asignado del incidente (o el sistema/admin: 1)
            ISNULL(i.id_usuario_asignado, 1),
            CONCAT(
                'Cambio Automático de Estado detectado: ', 
                ed.nombre, ' -> ', en.nombre, '.'
            )
        FROM inserted i
        INNER JOIN deleted d ON i.id_incidente = d.id_incidente
        INNER JOIN cat_Estados ed ON d.id_estado = ed.id_estado -- Estado Viejo
        INNER JOIN cat_Estados en ON i.id_estado = en.id_estado -- Estado Nuevo
        WHERE i.id_estado <> d.id_estado; -- Solo insertar si realmente es diferente el ID
    END
END;
GO

PRINT '>> SPRINT 3: Trigger trg_AuditoriaEstadoIncidente creado correctamente.';
GO
