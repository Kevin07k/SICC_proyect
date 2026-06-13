-- Roles y usuarios SQL (PostgreSQL central)
-- Requiere esquema en public (01_schema). Ejecutar como sicc_admin.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sicc_api') THEN
        CREATE ROLE sicc_api LOGIN PASSWORD 'sicc_api_pass_2024';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sicc_reportes') THEN
        CREATE ROLE sicc_reportes LOGIN PASSWORD 'sicc_reportes_pass_2024';
    END IF;
END $$;

-- API: lectura/escritura en public (metadata + operacional Santa Cruz + caché reportes)
GRANT CONNECT ON DATABASE sicc_central TO sicc_api;
GRANT USAGE ON SCHEMA public TO sicc_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sicc_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sicc_api;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sicc_api;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO sicc_api;

-- Reportes: solo lectura en public; FDW se otorga en 05_fdw_mysql
GRANT CONNECT ON DATABASE sicc_central TO sicc_reportes;
GRANT USAGE ON SCHEMA public TO sicc_reportes;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sicc_reportes;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO sicc_reportes;
