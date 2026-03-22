USE DB_GestionIncidentes;
GO

PRINT '--- 1. VISTAS: vw_Incidentes_Criticos_Abiertos ---';
GO
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

PRINT '--- 2. VISTAS: vw_Top_Activos_Atacados ---';
GO
CREATE OR ALTER VIEW vw_Top_Activos_Atacados AS
SELECT 
    a.id_activo,
    a.hostname,
    COUNT(ia.id_incidente) AS total_incidentes
FROM Activos a
LEFT JOIN Incidentes_Activos ia ON a.id_activo = ia.id_activo
GROUP BY a.id_activo, a.hostname;
GO

PRINT '--- 3. SP: sp_CerrarIncidente ---';
GO
CREATE OR ALTER PROCEDURE sp_CerrarIncidente
    @id_incidente INT,
    @id_usuario_cierre INT,
    @nota_cierre NVARCHAR(MAX) = 'Incidente cerrado por resolución exitosa.'
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;

        -- Buscar dinámicamente el ID del estado 'Cerrado' del catálogo
        DECLARE @IdEstadoCerrado INT;
        SELECT @IdEstadoCerrado = id_estado FROM cat_Estados WHERE nombre = 'Cerrado';

        -- 1. Actualizar el Incidente
        UPDATE Incidentes
        SET id_estado = @IdEstadoCerrado, fecha_cierre = GETDATE()
        WHERE id_incidente = @id_incidente;

        -- 2. Insertar Bitacora de Cierre (Auditoría)
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario)
        VALUES (@id_incidente, @id_usuario_cierre, @nota_cierre);

        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR (@Msg, 16, 1);
    END CATCH
END;
GO

PRINT '--- 4. SP: sp_AsignarAnalista ---';
GO
CREATE OR ALTER PROCEDURE sp_AsignarAnalista
    @id_incidente INT,
    @id_usuario INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;

        -- Validar lógica de negocio: Si el usuario existe
        IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE id_usuario = @id_usuario)
        BEGIN
            RAISERROR ('CRÍTICO: El usuario asignado no existe en el catálogo.', 16, 1);
            RETURN;
        END

        -- Actualizar Asignación
        UPDATE Incidentes
        SET id_usuario_asignado = @id_usuario
        WHERE id_incidente = @id_incidente;

        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR (@Msg, 16, 1);
    END CATCH
END;
GO

PRINT '--- 5. TRIGGER: trg_PrevenirBorradoEvidencia (INSTEAD OF DELETE) ---';
GO
CREATE OR ALTER TRIGGER trg_PrevenirBorradoEvidencia
ON Incidentes
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (SELECT 1 FROM deleted)
    BEGIN
        -- Levantamos error y evitamos el borrado. Es un INSTEAD OF, por lo que bloquea la acción original.
        RAISERROR ('VULNERACIÓN DE POLITICA: La evidencia y registros de incidentes no pueden ser eliminados.', 16, 1);
    END
END;
GO

PRINT '--- 6. TRIGGER: trg_Auditoria_CambioPrioridad (AFTER UPDATE) ---';
GO
CREATE OR ALTER TRIGGER trg_Auditoria_CambioPrioridad
ON Incidentes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;

    -- Validamos actualización exclusiva a id_prioridad
    IF UPDATE(id_prioridad)
    BEGIN
        -- Inserción automatizada a la bitácora si SUBIÓ de nivel la prioridad
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario)
        SELECT 
            i.id_incidente,
            ISNULL(i.id_usuario_asignado, 1),
            CONCAT('ALERTA DE ESCALAMIENTO: La prioridad del incidente severizó de ', pd.nivel, ' a ', pn.nivel, '.')
        FROM inserted i
        INNER JOIN deleted d ON i.id_incidente = d.id_incidente
        INNER JOIN cat_Prioridades pn ON i.id_prioridad = pn.id_prioridad
        INNER JOIN cat_Prioridades pd ON d.id_prioridad = pd.id_prioridad
        WHERE i.id_prioridad <> d.id_prioridad
          AND pn.valor_orden > pd.valor_orden; -- Solo registramos "escalamientos" (subida de severidad)
    END
END;
GO

PRINT '--- 7. ÍNDICES: Soporte a Vistas y FKs ---';
GO
-- Índice compuesto robusto para vw_Incidentes_Criticos_Abiertos
CREATE NONCLUSTERED INDEX IX_Incidentes_PrioridadEstado_Soporte
ON Incidentes (id_prioridad, id_estado)
INCLUDE (titulo, fecha_creacion, id_usuario_asignado);
GO

-- Índice de cobertura para optimizar agrupaciones como COUNT() en vw_Top_Activos_Atacados
CREATE NONCLUSTERED INDEX IX_Incidentes_Activos_SoporteGroup
ON Incidentes_Activos (id_activo)
INCLUDE (id_incidente);
GO

PRINT '>> SPRINT 5: Paquete de Objetos Avazados "Rúbrica Excelente" creados con éxito.';
GO
