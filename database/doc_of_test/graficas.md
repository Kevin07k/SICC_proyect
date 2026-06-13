# Evidencia — optimización (PostgreSQL + MySQL)

Carga previa: `apply_benchmark_seed.py`  
> **ANALYZE** / **ANALYZE TABLE** se ejecutan en los scripts pero no se capturan (en DataGrip no muestran grilla útil).

---

# PostgreSQL — Santa Cruz

Script: [`postgres/test/optimizacion_explain.sql`](../postgres/test/optimizacion_explain.sql)

## 1. Conteos

| Métrica | Resultado |
|---------|-----------|
| Total incidentes | **14 024** |
| Benchmark `[Bench]%` | **14 000** |
| Filtro ANTES (`id_estado = 1`) | **2 355** |
| Filtro DESPUÉS (`id_sede = 1` + `id_estado = 1`) | **1 688** |

### 1.1 Total de incidentes

![total_incidentes](./optimizacion/postgres/conteo/01_total_incidentes.png)

### 1.2 Incidentes benchmark

![bench_incidentes](./optimizacion/postgres/conteo/02_bench_incidentes.png)

### 1.3 Filtro consulta ANTES

![filtro_antes](./optimizacion/postgres/conteo/03_filtro_antes_estado1.png)

### 1.4 Filtro consulta DESPUÉS

![filtro_despues](./optimizacion/postgres/conteo/04_filtro_despues_sc_estado1.png)

El filtro con **sede** reduce filas candidatas (2 355 → 1 688) antes del `EXPLAIN`.

---

## 2. EXPLAIN — sin optimizar vs con optimización

| | Sin optimizar | Con optimización |
|---|---------------|------------------|
| Consulta | `SELECT *` solo `id_estado = 1` | Columnas + `id_sede = 1` + `ORDER BY` + `LIMIT 50` |
| Plan | Bitmap Index Scan (`idx_incidentes_estado`) | Index Scan Backward (`idx_incidentes_fecha`) + `Limit` |
| Tiempo ejecución | **~1,56 ms** | **~0,14 ms** |
| Filas devueltas | 2 355 | 50 |

### 2.1 Sin optimizar (consulta ANTES)

![explain sin optimizar](./optimizacion/postgres/explain/sin_optimizar.png)

### 2.2 Con optimización (consulta DESPUÉS)

![explain con optimizacion](./optimizacion/postgres/explain/con_optimizacion.png)

---

## 3. Vista agregada

`vw_resumen_incidentes_por_estado` — usa `idx_incidentes_sede`; tiempo ejecución **~6,94 ms**.

![vista resumen](./optimizacion/postgres/vistas/vistas.png)

---

## 4. Índices en `Incidentes`

`idx_incidentes_sede`, `idx_incidentes_estado`, `idx_incidentes_fecha`, `idx_incidentes_prioridad`, `idx_incidentes_asignado`, PK `uuid`.

![indices incidentes](./optimizacion/postgres/indices/indices.png)

---

## 5. Estadísticas (`pg_stats`)

Columnas clave del optimizador tras `ANALYZE`: `id_sede`, `id_estado`, `created_at`.

![pg_stats](./optimizacion/postgres/pg_stats/stats.png)

---

# MySQL — Cochabamba

Script: [`mysql/test/optimizacion_explain.sql`](../mysql/test/optimizacion_explain.sql)  
Consulta optimizada con **`id_sede = 2`**.

## 1. Conteos

| Métrica | Resultado |
|---------|-----------|
| Total incidentes | **14 005** |
| Benchmark `[Bench]%` | **14 000** |
| Filtro ANTES (`id_estado = 1`) | **2 336** |
| Filtro DESPUÉS (`id_sede = 2` + `id_estado = 1`) | **1 669** |

### 1.1 Total de incidentes

![mysql total](./optimizacion/mysql/conteo/01_total_incidentes.png)

### 1.2 Incidentes benchmark

![mysql bench](./optimizacion/mysql/conteo/02_brench_incidentes.png)

### 1.3 Filtro consulta ANTES

![mysql antes](./optimizacion/mysql/conteo/03_filtro_antes_estado1.png)

### 1.4 Filtro consulta DESPUÉS (sede Cochabamba)

![mysql despues](./optimizacion/mysql/conteo/04_filtro_despues_cb_estado1.png)

El filtro con **sede** reduce filas candidatas (2 336 → 1 669).

---

## 2. EXPLAIN — sin filtro de sede vs con optimización

| | Sin filtro sede | Con optimización |
|---|-----------------|------------------|
| Consulta | `SELECT *` solo `id_estado = 1` | Columnas + `id_sede = 2` + `ORDER BY` + `LIMIT 50` |
| Plan | Index lookup (`idx_incidentes_estado`) + Filter | Index scan reverse (`idx_incidentes_fecha`) + Filter + `Limit 50` |
| Tiempo (actual) | **~8,67 ms** | **~2,06 ms** |
| Filas devueltas | 2 336 | 50 |

### 2.1 Sin filtro de sede (consulta ANTES)

![mysql explain sin sede](./optimizacion/mysql/explain/01_sin_filtro_sede.png)

### 2.2 Con filtro sede + LIMIT (consulta DESPUÉS)

![mysql explain con filtro](./optimizacion/mysql/explain/02_con_filtro.png)

---

## 3. Vista agregada

`vw_resumen_incidentes_por_estado` — `idx_incidentes_sede` (`id_sede = 2`); tiempo **~72,3 ms**.

![mysql vista](./optimizacion/mysql/vistas/vistas.png)

---

## 4. Índices en `Incidentes`

`idx_incidentes_sede`, `idx_incidentes_estado`, `idx_incidentes_fecha`, `idx_incidentes_prioridad`, `idx_incidentes_asignado`, PK `uuid`.

![mysql indices](./optimizacion/mysql/indices/indices.png)
