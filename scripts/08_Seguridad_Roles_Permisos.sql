USE DB_GestionIncidentes;
GO

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
GO

IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_vendedor' AND type = 'R')
    DROP ROLE rol_vendedor;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_gerente' AND type = 'R')
    DROP ROLE rol_gerente;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'rol_dba' AND type = 'R')
    DROP ROLE rol_dba;
GO

PRINT '>> Limpieza de roles y usuarios previos completada.';
GO

USE master;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_vendedor')
    CREATE LOGIN login_vendedor WITH PASSWORD = 'V3nd3d0r$SICC_2026!', DEFAULT_DATABASE = DB_GestionIncidentes;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_gerente')
    CREATE LOGIN login_gerente WITH PASSWORD = 'G3r3nt3$SICC_2026!', DEFAULT_DATABASE = DB_GestionIncidentes;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_dba')
    CREATE LOGIN login_dba WITH PASSWORD = 'Db4Adm1n$SICC_2026!', DEFAULT_DATABASE = DB_GestionIncidentes;

PRINT '>> Logins de servidor creados.';
GO

USE DB_GestionIncidentes;
GO

CREATE ROLE rol_vendedor;
CREATE ROLE rol_gerente;
CREATE ROLE rol_dba;

PRINT '>> Roles de base de datos creados.';
GO

CREATE USER usr_vendedor FOR LOGIN login_vendedor;
CREATE USER usr_gerente FOR LOGIN login_gerente;
CREATE USER usr_dba FOR LOGIN login_dba;

ALTER ROLE rol_vendedor ADD MEMBER usr_vendedor;
ALTER ROLE rol_gerente ADD MEMBER usr_gerente;
ALTER ROLE rol_dba ADD MEMBER usr_dba;

PRINT '>> Usuarios creados y asignados a sus roles.';
GO

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

PRINT '>> Permisos de ROL_DBA configurados (control total).';
GO

GRANT SELECT, INSERT, UPDATE ON Incidentes TO rol_vendedor;
GRANT SELECT, INSERT ON Incidentes_Activos TO rol_vendedor;
GRANT SELECT, INSERT ON Bitacora_Investigacion TO rol_vendedor;

DENY DELETE ON Incidentes TO rol_vendedor;
DENY DELETE ON Incidentes_Activos TO rol_vendedor;
DENY DELETE ON Bitacora_Investigacion TO rol_vendedor;
DENY UPDATE ON Bitacora_Investigacion TO rol_vendedor;

GRANT SELECT ON Activos TO rol_vendedor;
GRANT SELECT ON Usuarios TO rol_vendedor;
DENY INSERT, UPDATE, DELETE ON Activos TO rol_vendedor;
DENY INSERT, UPDATE, DELETE ON Usuarios TO rol_vendedor;

GRANT SELECT ON cat_Tipos_Incidente TO rol_vendedor;
GRANT SELECT ON cat_Prioridades TO rol_vendedor;
GRANT SELECT ON cat_Estados TO rol_vendedor;
GRANT SELECT ON cat_Sedes TO rol_vendedor;
DENY INSERT, UPDATE, DELETE ON cat_Tipos_Incidente TO rol_vendedor;
DENY INSERT, UPDATE, DELETE ON cat_Prioridades TO rol_vendedor;
DENY INSERT, UPDATE, DELETE ON cat_Estados TO rol_vendedor;
DENY INSERT, UPDATE, DELETE ON cat_Sedes TO rol_vendedor;

DENY SELECT ON vw_Auditoria_Incidentes_Sede TO rol_vendedor;
DENY SELECT ON vw_Incidentes_Criticos_Abiertos TO rol_vendedor;
DENY SELECT ON vw_Top_Activos_Atacados TO rol_vendedor;

GRANT EXECUTE ON sp_RegistrarIncidenteCompleto TO rol_vendedor;
DENY EXECUTE ON sp_CerrarIncidente TO rol_vendedor;
DENY EXECUTE ON sp_AsignarAnalista TO rol_vendedor;

PRINT '>> Permisos de ROL_VENDEDOR configurados (insertar y actualizar ciertas tablas).';
GO

GRANT SELECT ON Incidentes TO rol_gerente;
GRANT SELECT ON Incidentes_Activos TO rol_gerente;
GRANT SELECT ON Bitacora_Investigacion TO rol_gerente;
GRANT SELECT ON Activos TO rol_gerente;
GRANT SELECT ON Usuarios TO rol_gerente;
GRANT SELECT ON cat_Tipos_Incidente TO rol_gerente;
GRANT SELECT ON cat_Prioridades TO rol_gerente;
GRANT SELECT ON cat_Estados TO rol_gerente;
GRANT SELECT ON cat_Sedes TO rol_gerente;

DENY INSERT, UPDATE, DELETE ON Incidentes TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON Incidentes_Activos TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON Bitacora_Investigacion TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON Activos TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON Usuarios TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON cat_Tipos_Incidente TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON cat_Prioridades TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON cat_Estados TO rol_gerente;
DENY INSERT, UPDATE, DELETE ON cat_Sedes TO rol_gerente;

GRANT SELECT ON vw_Auditoria_Incidentes_Sede TO rol_gerente;
GRANT SELECT ON vw_Incidentes_Criticos_Abiertos TO rol_gerente;
GRANT SELECT ON vw_Top_Activos_Atacados TO rol_gerente;

DENY EXECUTE ON sp_RegistrarIncidenteCompleto TO rol_gerente;
DENY EXECUTE ON sp_CerrarIncidente TO rol_gerente;
DENY EXECUTE ON sp_AsignarAnalista TO rol_gerente;

PRINT '>> Permisos de ROL_GERENTE configurados (solo consulta de reportes).';
GO

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
