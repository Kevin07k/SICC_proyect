USE DB_GestionIncidentes;
GO

PRINT '--- 1. Creando Stored Procedure Transaccional ---';
GO

CREATE OR ALTER PROCEDURE sp_RegistrarIncidenteCompleto
    @titulo NVARCHAR(255),
    @descripcion_detallada NVARCHAR(MAX),
    @id_tipo INT,
    @id_prioridad INT,
    @id_estado INT,
    @id_usuario_asignado INT = NULL,
    @id_activo INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRAN;

        -- 1. Insertar el Incidente
        DECLARE @NuevoIncidenteID INT;

        INSERT INTO Incidentes (
            titulo, descripcion_detallada, 
            id_tipo, id_prioridad, id_estado, id_usuario_asignado
        )
        VALUES (
            @titulo, @descripcion_detallada, 
            @id_tipo, @id_prioridad, @id_estado, @id_usuario_asignado
        );

        -- Obtener el ID generado para el nuevo incidente
        SET @NuevoIncidenteID = SCOPE_IDENTITY();

        -- 2. Vincular el Activo afectado (Si se proporcionó uno)
        IF @id_activo IS NOT NULL AND @id_activo > 0
        BEGIN
            INSERT INTO Incidentes_Activos (id_incidente, id_activo)
            VALUES (@NuevoIncidenteID, @id_activo);
        END

        -- 3. Si todo va bien, confirmar la transacción
        COMMIT TRAN;
        
        -- Retornar el ID del nuevo incidente por si el backend lo necesita
        SELECT @NuevoIncidenteID AS id_incidente_generado;

    END TRY
    BEGIN CATCH
        -- En caso de error, deshacer todos los cambios (ROLLBACK)
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;

        -- Relanzar el error para que el Backend (FastAPI) lo pueda capturar
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END;
GO

PRINT '>> SPRINT 2: SP sp_RegistrarIncidenteCompleto creado correctamente.';
GO
