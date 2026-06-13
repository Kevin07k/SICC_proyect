-- Caché de reportes globales (solo PostgreSQL central)
-- Ejecutar: psql -U sicc_admin -d sicc_central -f database/postgres/migrations/04_reportes_cache.sql

CREATE TABLE IF NOT EXISTS reportes_cache (
    id            SERIAL PRIMARY KEY,
    clave         VARCHAR(64) NOT NULL UNIQUE DEFAULT 'global',
    payload       JSONB NOT NULL,
    generated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at    TIMESTAMP NOT NULL,
    duration_ms   INTEGER,
    source_nodes  TEXT[] NOT NULL DEFAULT ARRAY['postgres', 'mysql']
);

CREATE INDEX IF NOT EXISTS idx_reportes_cache_expires ON reportes_cache(expires_at);
