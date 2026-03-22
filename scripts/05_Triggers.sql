USE DB_GestionIncidentes;
GO

-- =============================================
-- Trigger: trg_AuditoriaEstadoIncidente
-- Descripción: Trigger AFTER UPDATE que registra automáticamente en la bitácora de 
--              investigación cualquier cambio en el estado de un incidente 
--              (ej. de "Abierto" a "En proceso"). Asegura trazabilidad y auditoría.
-- =============================================
CREATE OR ALTER TRIGGER trg_AuditoriaEstadoIncidente
ON Incidentes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;
    IF UPDATE(id_estado)
    BEGIN
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario)
        SELECT 
            i.id_incidente,
            ISNULL(i.id_usuario_asignado, 1),
            CONCAT('Cambio Automático de Estado detectado: ', ed.nombre, ' -> ', en.nombre, '.')
        FROM inserted i
        INNER JOIN deleted d ON i.id_incidente = d.id_incidente
        INNER JOIN cat_Estados ed ON d.id_estado = ed.id_estado
        INNER JOIN cat_Estados en ON i.id_estado = en.id_estado
        WHERE i.id_estado <> d.id_estado;
    END
END;
GO

-- =============================================
-- Trigger: trg_PrevenirBorradoEvidencia
-- Descripción: Trigger INSTEAD OF DELETE que bloquea cualquier intento de eliminar 
--              registros de la tabla Incidentes. Garantiza el cumplimiento de políticas 
--              de ciberseguridad al evitar la destrucción de evidencia de ataques.
-- =============================================
CREATE OR ALTER TRIGGER trg_PrevenirBorradoEvidencia
ON Incidentes
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (SELECT 1 FROM deleted)
    BEGIN
        RAISERROR ('VULNERACIÓN DE POLITICA: La evidencia y registros de incidentes no pueden ser eliminados.', 16, 1);
    END
END;
GO

-- =============================================
-- Trigger: trg_Auditoria_CambioPrioridad
-- Descripción: Trigger AFTER UPDATE que genera una alerta automática en la bitácora 
--              (escalamiento) cada vez que la prioridad de un incidente incrementa a 
--              un nivel de mayor severidad, alertando a los analistas involucrados.
-- =============================================
CREATE OR ALTER TRIGGER trg_Auditoria_CambioPrioridad
ON Incidentes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;
    IF UPDATE(id_prioridad)
    BEGIN
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario)
        SELECT 
            i.id_incidente,
            ISNULL(i.id_usuario_asignado, 1),
            CONCAT('ALERTA DE ESCALAMIENTO: La prioridad del incidente severizó de ', pd.nivel, ' a ', pn.nivel, '.')
        FROM inserted i
        INNER JOIN deleted d ON i.id_incidente = d.id_incidente
        INNER JOIN cat_Prioridades pn ON i.id_prioridad = pn.id_prioridad
        INNER JOIN cat_Prioridades pd ON d.id_prioridad = pd.id_prioridad
        WHERE i.id_prioridad <> d.id_prioridad AND pn.valor_orden > pd.valor_orden;
    END
END;
GO

PRINT '>> Triggers DDL Creados Correctamente.';
GO
