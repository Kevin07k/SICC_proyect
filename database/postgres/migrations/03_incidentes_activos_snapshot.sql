-- Migración: snapshot histórico en Incidentes_Activos (BDs ya existentes)
-- PostgreSQL (sicc_central)
ALTER TABLE Incidentes_Activos ADD COLUMN IF NOT EXISTS tipo_activo_registrado VARCHAR(100);
ALTER TABLE Incidentes_Activos ADD COLUMN IF NOT EXISTS sede_registrada VARCHAR(100);
ALTER TABLE Incidentes_Activos ADD COLUMN IF NOT EXISTS hostname_registrado VARCHAR(100);
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'incidentes_activos_id_incidente_id_activo_key'
    ) THEN
        ALTER TABLE Incidentes_Activos ADD UNIQUE (id_incidente, id_activo);
    END IF;
END $$;

-- MySQL: ver database/mysql/migrations/03_incidentes_activos_snapshot.sql
