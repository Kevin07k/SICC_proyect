-- Usuarios SQL de aplicación y FDW (Cochabamba)
-- Ejecutar como root: init_databases.py (setup_distribuido)

CREATE USER IF NOT EXISTS 'sicc_api'@'%' IDENTIFIED BY 'sicc_api_pass_2024';
CREATE USER IF NOT EXISTS 'sicc_fdw_ro'@'%' IDENTIFIED BY 'sicc_fdw_ro_pass_2024';

-- API: metadata replicada + operacional local
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.cat_Sedes TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Roles TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Permisos TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Roles_Permisos TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.cat_Estados TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.cat_Prioridades TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.cat_Tipos_Incidente TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Usuarios TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Sesiones TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE ON sicc_cochabamba.sync_control TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Activos TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Incidentes TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Incidentes_Activos TO 'sicc_api'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sicc_cochabamba.Bitacora_Investigacion TO 'sicc_api'@'%';

-- FDW: solo lectura operacional (sin metadata ni sync)
GRANT SELECT ON sicc_cochabamba.Activos TO 'sicc_fdw_ro'@'%';
GRANT SELECT ON sicc_cochabamba.Incidentes TO 'sicc_fdw_ro'@'%';
GRANT SELECT ON sicc_cochabamba.Incidentes_Activos TO 'sicc_fdw_ro'@'%';
GRANT SELECT ON sicc_cochabamba.Bitacora_Investigacion TO 'sicc_fdw_ro'@'%';

FLUSH PRIVILEGES;
