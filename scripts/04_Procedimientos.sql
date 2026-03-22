USE DB_GestionIncidentes;
GO

-- =============================================
-- Procedimiento: sp_RegistrarIncidenteCompleto
-- Descripción: Registra de manera transaccional un nuevo incidente en la base de datos.
--              Inserta los datos principales (título, descripción, tipo, estado) y opcionalmente
--              lo vincula a un activo afectado en la tabla intermedia (Incidentes_Activos).
-- =============================================
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
        DECLARE @NuevoIncidenteID INT;
        INSERT INTO Incidentes (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
        VALUES (@titulo, @descripcion_detallada, @id_tipo, @id_prioridad, @id_estado, @id_usuario_asignado);
        SET @NuevoIncidenteID = SCOPE_IDENTITY();

        IF @id_activo IS NOT NULL AND @id_activo > 0
        BEGIN
            INSERT INTO Incidentes_Activos (id_incidente, id_activo) VALUES (@NuevoIncidenteID, @id_activo);
        END

        COMMIT TRAN;
        SELECT @NuevoIncidenteID AS id_incidente_generado;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR (@ErrorMessage, 16, 1);
    END CATCH
END;
GO

-- =============================================
-- Procedimiento: sp_CerrarIncidente
-- Descripción: Cambia el estado de un incidente a "Cerrado" registrando la fecha de conclusión.
--              Además, deja un registro automático en la bitácora de investigación detallando
--              la finalización y anotando el comentario final de cierre.
-- =============================================
CREATE OR ALTER PROCEDURE sp_CerrarIncidente
    @id_incidente INT,
    @id_usuario_cierre INT,
    @nota_cierre NVARCHAR(MAX) = 'Incidente cerrado.'
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;
        DECLARE @IdEstadoCerrado INT;
        SELECT @IdEstadoCerrado = id_estado FROM cat_Estados WHERE nombre = 'Cerrado';

        UPDATE Incidentes SET id_estado = @IdEstadoCerrado, fecha_cierre = GETDATE() WHERE id_incidente = @id_incidente;
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario) VALUES (@id_incidente, @id_usuario_cierre, @nota_cierre);

        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR (@Msg, 16, 1);
    END CATCH
END;
GO

-- =============================================
-- Procedimiento: sp_AsignarAnalista
-- Descripción: Permite asignar o reasignar a un usuario en específico (analista) para que 
--              se encargue de la investigación y seguimiento de un incidente abierto.
--              Valida previamente que el usuario exista en el sistema.
-- =============================================
CREATE OR ALTER PROCEDURE sp_AsignarAnalista
    @id_incidente INT,
    @id_usuario INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;
        IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE id_usuario = @id_usuario)
        BEGIN
            RAISERROR ('CRÍTICO: El usuario asignado no existe.', 16, 1);
            RETURN;
        END
        UPDATE Incidentes SET id_usuario_asignado = @id_usuario WHERE id_incidente = @id_incidente;
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR (@Msg, 16, 1);
    END CATCH
END;
GO

PRINT '>> Procedimientos Almacenados Creados Correctamente.';
GO
