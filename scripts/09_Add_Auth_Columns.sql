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
SET password_hash = '$2b$12$uxxRjFUjeeSfvjQoMcKt8.6fS7poEheeL9aJuYYLvAN0L6QvDZNLK' 
WHERE password_hash IS NULL;
GO

-- 5. Insertar cuentas de sistema DBA y Developer para el login de la aplicación
IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE username = 'dba')
BEGIN
    INSERT INTO Usuarios (nombre_completo, email, rol, username, password_hash)
    VALUES ('Admin Sistema', 'dba@sicc.com', 'DBA', 'dba', '$2b$12$V2v7tU/nJVy0Z0.yZRmej.k2LONF6C/TMyP5.qH02tnRb0NgeWwmy');
    PRINT '>> Usuario DBA agregado a tabla Usuarios.';
END
GO

IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE username = 'developer')
BEGIN
    INSERT INTO Usuarios (nombre_completo, email, rol, username, password_hash)
    VALUES ('Desarrollador', 'dev@sicc.com', 'Developer', 'developer', '$2b$12$uxxRjFUjeeSfvjQoMcKt8.6fS7poEheeL9aJuYYLvAN0L6QvDZNLK');
    PRINT '>> Usuario Developer agregado a tabla Usuarios.';
END
GO

PRINT '>> Actualizacion de tabla Usuarios completada.';
GO
