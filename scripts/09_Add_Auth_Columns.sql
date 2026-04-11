USE DB_GestionIncidentes;
GO

-- 1. Agregar columna username si no existe
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Usuarios') AND name = 'username')
BEGIN
    ALTER TABLE Usuarios ADD username NVARCHAR(50) NULL;
    PRINT '>> Columna username agregada.';
END
GO

-- 2. Agregar columna password_hash si no existe
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Usuarios') AND name = 'password_hash')
BEGIN
    ALTER TABLE Usuarios ADD password_hash NVARCHAR(255) NULL;
    PRINT '>> Columna password_hash agregada.';
END
GO

-- 3. Actualizar constraint de unicidad para username
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('Usuarios') AND name = 'UQ_Usuarios_Username')
BEGIN
    -- Los valores nulos de las cuentas dummy previas podrían causar error, se manejan creándolas temporalmente
    UPDATE Usuarios SET username = 'user_' + CAST(id_usuario AS NVARCHAR) WHERE username IS NULL;
    
    ALTER TABLE Usuarios ADD CONSTRAINT UQ_Usuarios_Username UNIQUE (username);
    PRINT '>> Constraint UNIQUE agregado a username.';
END
GO

-- 4. Setear un hash por defecto (bcrypt de 'password') o 'dev123' a las cuentas anteriores
-- password: '$2b$12$Kk0a2Ie7yF5bS6gH2U4i7O2mQZ8sH8wYj6kP9xN3gB4yW4o9c/OEK' (dev123)
UPDATE Usuarios 
SET password_hash = '$2b$12$Kk0a2Ie7yF5bS6gH2U4i7O2mQZ8sH8wYj6kP9xN3gB4yW4o9c/OEK' 
WHERE password_hash IS NULL;
GO

PRINT '>> Actualizacion de tabla Usuarios completada.';
GO
