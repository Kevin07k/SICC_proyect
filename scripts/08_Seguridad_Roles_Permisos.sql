USE DB_GestionIncidentes;
GO

-- ========================================
-- LIMPIEZA DE ROLES Y USUARIOS PREVIOS
-- ========================================

IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'usr_vendedor')
BEGIN
    ALTER ROLE rol_vendedor DROP MEMBER usr_vendedor;
    DROP USER usr_vendedor;
END
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'usr_gerente')
BEGIN
    ALTER ROLE rol_gerente DROP MEMBER usr_gerente;
    DROP USER usr_gerente;
END
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'usr_dba')
BEGIN
    ALTER ROLE rol_dba DROP MEMBER usr_dba;
    DROP USER usr_dba;
END
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'usr_developer')
BEGIN
    ALTER ROLE rol_developer DROP MEMBER usr_developer;
    DROP USER usr_developer;
END
GO

IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_vendedor' AND type = 'R')
    DROP ROLE rol_vendedor;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_gerente' AND type = 'R')
    DROP ROLE rol_gerente;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_dba' AND type = 'R')
    DROP ROLE rol_dba;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_developer' AND type = 'R')
    DROP ROLE rol_developer;
GO

PRINT '>> Limpieza de roles y usuarios previos completada.';
GO

-- ========================================
-- CREAR LOGINS DE SERVIDOR
-- ========================================

USE master;
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_vendedor')
    DROP LOGIN login_vendedor;
IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_gerente')
    DROP LOGIN login_gerente;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_developer')
    CREATE LOGIN login_developer WITH PASSWORD = 'D3v3l0p3r$SICC_2026!', DEFAULT_DATABASE = DB_GestionIncidentes;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_dba')
    CREATE LOGIN login_dba WITH PASSWORD = 'Db4Adm1n$SICC_2026!', DEFAULT_DATABASE = DB_GestionIncidentes;

PRINT '>> Logins de servidor creados (developer, dba).';
GO

-- ========================================
-- CREAR ROLES DE BASE DE DATOS
-- ========================================

USE DB_GestionIncidentes;
GO

CREATE ROLE rol_developer;
CREATE ROLE rol_dba;

PRINT '>> Roles de base de datos creados (rol_developer, rol_dba).';
GO

-- ========================================
-- CREAR USUARIOS Y ASIGNAR A ROLES
-- ========================================

CREATE USER usr_developer FOR LOGIN login_developer;
CREATE USER usr_dba FOR LOGIN login_dba;

ALTER ROLE rol_developer ADD MEMBER usr_developer;
ALTER ROLE rol_dba ADD MEMBER usr_dba;

PRINT '>> Usuarios creados y asignados a sus roles.';
GO

-- ========================================
-- PERMISOS ROL_DBA (ADMIN - Control Total)
-- ========================================

ALTER ROLE db_owner ADD MEMBER usr_dba;

GRANT SELECT, INSERT, UPDATE, DELETE ON Incidentes TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON Incidentes_Activos TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON Bitacora_Investigacion TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON Activos TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON Usuarios TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON cat_Tipos_Incidente TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON cat_Prioridades TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON cat_Estados TO rol_dba;
GRANT SELECT, INSERT, UPDATE, DELETE ON cat_Sedes TO rol_dba;

GRANT SELECT ON vw_Auditoria_Incidentes_Sede TO rol_dba;
GRANT SELECT ON vw_Incidentes_Criticos_Abiertos TO rol_dba;
GRANT SELECT ON vw_Top_Activos_Atacados TO rol_dba;

GRANT EXECUTE ON sp_RegistrarIncidenteCompleto TO rol_dba;
GRANT EXECUTE ON sp_CerrarIncidente TO rol_dba;
GRANT EXECUTE ON sp_AsignarAnalista TO rol_dba;

PRINT '>> Permisos de ROL_DBA configurados (control total del sistema).';
GO

-- ========================================
-- PERMISOS ROL_DEVELOPER
-- Puede: INSERT/UPDATE en Incidentes, Activos, Bitacora
-- No puede: DELETE, ni acceder a reportes/vistas
-- ========================================

GRANT SELECT, INSERT, UPDATE ON Incidentes TO rol_developer;
GRANT SELECT, INSERT ON Incidentes_Activos TO rol_developer;
GRANT SELECT, INSERT ON Bitacora_Investigacion TO rol_developer;

DENY DELETE ON Incidentes TO rol_developer;
DENY DELETE ON Incidentes_Activos TO rol_developer;
DENY DELETE ON Bitacora_Investigacion TO rol_developer;
DENY UPDATE ON Bitacora_Investigacion TO rol_developer;

GRANT SELECT ON Activos TO rol_developer;
GRANT SELECT, INSERT, UPDATE ON Activos TO rol_developer;
DENY DELETE ON Activos TO rol_developer;

GRANT SELECT ON Usuarios TO rol_developer;
DENY INSERT, UPDATE, DELETE ON Usuarios TO rol_developer;

GRANT SELECT ON cat_Tipos_Incidente TO rol_developer;
GRANT SELECT ON cat_Prioridades TO rol_developer;
GRANT SELECT ON cat_Estados TO rol_developer;
GRANT SELECT ON cat_Sedes TO rol_developer;
DENY INSERT, UPDATE, DELETE ON cat_Tipos_Incidente TO rol_developer;
DENY INSERT, UPDATE, DELETE ON cat_Prioridades TO rol_developer;
DENY INSERT, UPDATE, DELETE ON cat_Estados TO rol_developer;
DENY INSERT, UPDATE, DELETE ON cat_Sedes TO rol_developer;

DENY SELECT ON vw_Auditoria_Incidentes_Sede TO rol_developer;
DENY SELECT ON vw_Incidentes_Criticos_Abiertos TO rol_developer;
DENY SELECT ON vw_Top_Activos_Atacados TO rol_developer;

GRANT EXECUTE ON sp_RegistrarIncidenteCompleto TO rol_developer;
DENY EXECUTE ON sp_CerrarIncidente TO rol_developer;
DENY EXECUTE ON sp_AsignarAnalista TO rol_developer;

PRINT '>> Permisos de ROL_DEVELOPER configurados (insertar y actualizar incidentes/activos).';
GO

-- ========================================
-- RESUMEN DE SEGURIDAD
-- ========================================

PRINT '========================================';
PRINT '   RESUMEN DE SEGURIDAD IMPLEMENTADA';
PRINT '========================================';

SELECT 
    dp.name AS nombre_rol,
    dp.type_desc AS tipo,
    dp.create_date AS fecha_creacion
FROM sys.database_principals dp
WHERE dp.type = 'R' 
  AND dp.name LIKE 'rol_%';
GO

SELECT 
    u.name AS usuario,
    r.name AS rol_asignado
FROM sys.database_role_members rm
INNER JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
INNER JOIN sys.database_principals u ON rm.member_principal_id = u.principal_id
WHERE r.name LIKE 'rol_%';
GO

SELECT 
    dp.name AS rol,
    perm.permission_name AS permiso,
    perm.state_desc AS tipo_permiso,
    OBJECT_NAME(perm.major_id) AS objeto
FROM sys.database_permissions perm
INNER JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
WHERE dp.name LIKE 'rol_%'
ORDER BY dp.name, OBJECT_NAME(perm.major_id), perm.permission_name;
GO

PRINT '>> Script de Seguridad ejecutado correctamente.';
GO