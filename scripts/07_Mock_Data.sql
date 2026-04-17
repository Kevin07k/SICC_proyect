USE DB_GestionIncidentes;
GO

SET NOCOUNT ON;

PRINT '>> Iniciando carga masiva de Mock Data (Activos, Incidentes, Relaciones)...';

-- ===============================================
-- 1. Poblar Activos (50,000 registros)
-- ===============================================
DECLARE @i INT = 1;
DECLARE @id_sede INT;
DECLARE @hostname NVARCHAR(255);
DECLARE @ip NVARCHAR(50);
DECLARE @tipo NVARCHAR(100);

BEGIN TRAN;
WHILE @i <= 50000
BEGIN
    SET @id_sede = (ABS(CHECKSUM(NEWID())) % 3) + 1; -- Asume 3 sedes (1, 2, 3)
    SET @hostname = 'SRV-' + CAST(@id_sede AS VARCHAR) + '-' + RIGHT('00000' + CAST(@i AS VARCHAR), 6);
    SET @ip = '10.' + CAST(@id_sede AS VARCHAR) + '.' + CAST((ABS(CHECKSUM(NEWID())) % 255) AS VARCHAR) + '.' + CAST((ABS(CHECKSUM(NEWID())) % 255) AS VARCHAR);
    SET @tipo = CHOOSE((ABS(CHECKSUM(NEWID())) % 4) + 1, 'Servidor', 'Workstation', 'Router', 'Firewall');
    
    INSERT INTO Activos (hostname, direccion_ip, tipo_activo, propietario, id_sede)
    VALUES (@hostname, @ip, @tipo, 'IT Dept', @id_sede);
    
    IF @i % 10000 = 0
    BEGIN
        COMMIT TRAN;
        BEGIN TRAN;
    END
    
    SET @i = @i + 1;
END;
COMMIT TRAN;
PRINT '>> Activos insertados.';

-- ===============================================
-- 2. Poblar Incidentes (350,000 registros)
-- ===============================================
SET @i = 1;
DECLARE @id_tipo INT;
DECLARE @id_prioridad INT;
DECLARE @id_estado INT;
DECLARE @id_usuario INT;
DECLARE @titulo NVARCHAR(200);

BEGIN TRAN;
WHILE @i <= 350000
BEGIN
    SET @id_tipo = (ABS(CHECKSUM(NEWID())) % 5) + 1; -- 5 tipos (1 al 5)
    SET @id_prioridad = (ABS(CHECKSUM(NEWID())) % 4) + 1; -- 4 prioridades (1 al 4)
    SET @id_estado = (ABS(CHECKSUM(NEWID())) % 6) + 1; -- 6 estados (1 al 6)
    SET @id_usuario = 1; -- 1 usuario administrador por defecto
    
    SET @titulo = CHOOSE(@id_tipo, 
        'Intento de Phishing detectado', 
        'Infección por Malware en host', 
        'Login fallido múltiple (Fuerza Bruta)', 
        'Ataque DoS desde red externa', 
        'Carga inusual de archivos sensibles') + ' #' + RIGHT('000000' + CAST(@i AS VARCHAR), 6);
    
    INSERT INTO Incidentes (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
    VALUES (@titulo, 'Descripción generada automáticamente para pruebas de volumen en el sistema SICC. Revisar telemetría.', @id_tipo, @id_prioridad, @id_estado, @id_usuario);
    
    IF @i % 10000 = 0
    BEGIN
        COMMIT TRAN;
        BEGIN TRAN;
    END
    
    SET @i = @i + 1;
END;
COMMIT TRAN;
PRINT '>> Incidentes insertados.';

-- ===============================================
-- 3. Vincular Activos e Incidentes (100,000 registros)
-- ===============================================
SET @i = 1;
DECLARE @id_incidente INT;
DECLARE @id_activo INT;

BEGIN TRAN;
WHILE @i <= 100000
BEGIN
    SET @id_incidente = (ABS(CHECKSUM(NEWID())) % 350000) + 1;
    SET @id_activo = (ABS(CHECKSUM(NEWID())) % 50000) + 1;
    
    BEGIN TRY
        INSERT INTO Incidentes_Activos (id_incidente, id_activo, notas_relacion)
        VALUES (@id_incidente, @id_activo, 'Activo afectado directamente durante el incidente según la telemetría.');
    END TRY
    BEGIN CATCH
        -- Ignorar error de duplicado
    END CATCH
    
    IF @i % 10000 = 0
    BEGIN
        COMMIT TRAN;
        BEGIN TRAN;
    END
    
    SET @i = @i + 1;
END;
COMMIT TRAN;
PRINT '>> Relaciones insertadas.';

PRINT '>> Operación Finalizada con éxito. Dashboard listo con ~500k registros.';
GO
