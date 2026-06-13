# Scripts de prueba (PostgreSQL)

SQL de **laboratorio** — no forman parte del arranque normal.

Documentación completa del nodo: [../README.md](../README.md).

## Archivos

| Archivo | Uso |
|---------|-----|
| `fdw_smoke.sql` | Comprobar FDW (`sucursal_cochabamba`) tras `init_databases.py`. |
| `sync_metadata_test.sql` | Ejemplos comentados para sync LWW (PG y MySQL). |
| `optimizacion_explain.sql` | `ANALYZE` y `EXPLAIN ANALYZE` (requiere `apply_benchmark_seed.py` antes). |
| `transacciones_concurrencia.sql` | Índice a demos en `07_transacciones.sql`. |
| `deadlock_demo.sql` | Deadlock manual (2 terminales, UUIDs demo). |

Requiere `--academico` (06+07). Deadlock automático: `python scripts/simular_deadlock.py`.

Ver también: [`../07_transacciones.sql`](../07_transacciones.sql), [`../../README.md`](../../README.md).

## FDW

```bash
cd ../../database
PGPASSWORD=sicc_api_pass_2024 docker compose exec -T postgres-central \
  psql -U sicc_api -d sicc_central -f - < postgres/test/fdw_smoke.sql
```

Reconfigurar FDW: `python init_databases.py --distribuido --force-fdw`

## Demo y sync

- Demo operacional: `python apply_demo_seed.py` (usa `../03_seed_demo_operacional.sql`).
- Sync: descomentar un bloque en `sync_metadata_test.sql`, ejecutar en un nodo, luego `POST /sync/manual` desde la API.
