-- =============================================================================
-- TEST — Optimización: ANALYZE y EXPLAIN ANALYZE (PostgreSQL)
-- Requiere volumen: apply_benchmark_seed.py (recomendado ~10000+ filas)
-- =============================================================================

\echo '=== Conteo (debe haber miles de filas bench) ==='
SELECT COUNT(*) AS total_incidentes FROM Incidentes;
SELECT COUNT(*) AS bench_incidentes FROM Incidentes WHERE titulo LIKE '[Bench]%';
SELECT COUNT(*) AS filtro_antes_estado1
FROM Incidentes WHERE eliminado = FALSE AND id_estado = 1;
SELECT COUNT(*) AS filtro_despues_sc_estado1
FROM Incidentes WHERE eliminado = FALSE AND id_sede = 1 AND id_estado = 1;

\echo '=== 1) Estadísticas del optimizador ==='
ANALYZE Usuarios;
ANALYZE Incidentes;
ANALYZE Activos;
ANALYZE Incidentes_Activos;
ANALYZE Bitacora_Investigacion;

\echo '=== 2) ANTES — SELECT * sin sede (suele Seq Scan / muchas filas) ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT *
FROM Incidentes
WHERE eliminado = FALSE
  AND id_estado = 1;

\echo '=== 3) DESPUÉS — columnas + id_sede + ORDER BY + LIMIT (índices sede/estado/fecha) ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT uuid, titulo, id_sede, id_estado, created_at
FROM Incidentes
WHERE eliminado = FALSE
  AND id_sede = 1
  AND id_estado = 1
ORDER BY created_at DESC
LIMIT 50;

\echo '=== 4) Vista agregada ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM vw_resumen_incidentes_por_estado
WHERE id_sede = 1;

\echo '=== 5) Índices en Incidentes ==='
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'incidentes'
ORDER BY indexname;

\echo '=== 6) Muestra pg_stats ==='
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename = 'incidentes'
  AND attname IN ('id_sede', 'id_estado', 'created_at')
ORDER BY attname;


SELECT COUNT(*) AS activos_cochabamba
FROM sucursal_cochabamba."Activos";