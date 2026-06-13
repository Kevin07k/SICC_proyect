-- MySQL: snapshot en Incidentes_Activos
ALTER TABLE Incidentes_Activos
    ADD COLUMN IF NOT EXISTS tipo_activo_registrado VARCHAR(100),
    ADD COLUMN IF NOT EXISTS sede_registrada VARCHAR(100),
    ADD COLUMN IF NOT EXISTS hostname_registrado VARCHAR(100);

-- MySQL 8.0.12+ no tiene IF NOT EXISTS en ADD COLUMN en todas las builds; si falla, omitir columnas existentes.
-- UNIQUE: crear solo si no existe (ajustar manualmente si ya hay duplicados).
-- ALTER TABLE Incidentes_Activos ADD UNIQUE KEY uq_incidente_activo (id_incidente, id_activo);
