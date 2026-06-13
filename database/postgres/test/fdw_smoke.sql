-- Prueba manual FDW (PostgreSQL central, usuario sicc_api)
--
-- Sin psql en el host (solo Docker):
--   cd database
--   docker compose exec -T postgres-central \
--     psql -U sicc_api -d sicc_central -f - < postgres/test/fdw_smoke.sql
--
-- Con psql local:
--   psql -h localhost -U sicc_api -d sicc_central -f database/postgres/test/fdw_smoke.sql

SELECT foreign_table_schema, foreign_table_name
FROM information_schema.foreign_tables
WHERE foreign_table_schema = 'sucursal_cochabamba'
ORDER BY foreign_table_name;

SELECT COUNT(*) AS activos_cochabamba
FROM sucursal_cochabamba."Activos";

SELECT COUNT(*) AS incidentes_cochabamba
FROM sucursal_cochabamba."Incidentes";
