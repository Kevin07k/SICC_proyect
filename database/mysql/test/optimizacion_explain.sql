-- =============================================================================
-- TEST — Optimización: ANALYZE y EXPLAIN (MySQL 8+)
-- Requiere volumen: apply_benchmark_seed.py (recomendado ~10000+ filas)
-- =============================================================================

USE sicc_cochabamba;

SELECT '=== Conteo (miles de filas bench) ===' AS paso;
SELECT COUNT(*) AS total_incidentes FROM Incidentes;
SELECT COUNT(*) AS bench_incidentes FROM Incidentes WHERE titulo LIKE '[Bench]%';
SELECT COUNT(*) AS filtro_antes_estado1
FROM Incidentes WHERE eliminado = 0 AND id_estado = 1;
SELECT COUNT(*) AS filtro_despues_cb_estado1
FROM Incidentes WHERE eliminado = 0 AND id_sede = 2 AND id_estado = 1;

-- 1) Estadísticas
ANALYZE TABLE Usuarios, Incidentes, Activos, Incidentes_Activos, Bitacora_Investigacion;

-- 2) ANTES — sin filtro de sede (type ALL o muchas filas examinadas)
EXPLAIN ANALYZE
SELECT *
FROM Incidentes
WHERE eliminado = 0
  AND id_estado = 1;

-- 3) DESPUÉS — sede Cochabamba (2) + columnas + LIMIT
EXPLAIN ANALYZE
SELECT uuid, titulo, id_sede, id_estado, created_at
FROM Incidentes
WHERE eliminado = 0
  AND id_sede = 2
  AND id_estado = 1
ORDER BY created_at DESC
LIMIT 50;

-- 4) Vista agregada
EXPLAIN ANALYZE
SELECT * FROM vw_resumen_incidentes_por_estado
WHERE id_sede = 2;

-- 5) Índices
SHOW INDEX FROM Incidentes;
