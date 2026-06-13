# PostgreSQL — Sede central (Santa Cruz)

Base de datos **local** de la sede central (`id_sede = 1`). También aloja catálogos **replicados** (sync LWW vía API) y el esquema **FDW** para leer Cochabamba sin copiar datos operacionales.

Guía general (Docker, credenciales, troubleshooting): [../README.md](../README.md).

---

## ¿Qué hace cada archivo?

| Archivo | ¿Cuándo? | Descripción |
|---------|----------|-------------|
| `01_schema.sql` | Primera vez | Tablas, índices, triggers. Incluye metadata replicada + datos locales (incidentes, activos, bitácora) + `reportes_cache`. |
| `02_seed.sql` | Tras el schema | Catálogos, roles, permisos y usuarios de prueba (UUID fijos para sync y dev switcher). |
| `03_seed_demo_operacional.sql` | Opcional (dev) | 5 activos + 5 incidentes en **Santa Cruz**. No usar en producción. |
| `04_usuarios_sql.sql` | Tras 01–02 | Roles `sicc_api` (API) y `sicc_reportes`. Lo ejecuta `init_databases.py`. |
| `05_fdw_mysql.sql.template` | Tras 04 | Plantilla FDW hacia MySQL. **No ejecutar a mano**: el init sustituye `__MYSQL_FDW_*__` y genera el SQL. |
| `06_vistas_procedimientos.sql` | Tras 04 | Vistas, funciones `sp_*` y permisos. Lo ejecuta `init_databases.py` (o `--academico`). |
| `07_transacciones.sql` | Tras 06 | `sp_actualizar_propietario_activo` (`FOR UPDATE`), demos de aislamiento. |
| `Dockerfile` | Build Docker | Imagen PG 16 con extensión `mysql_fdw`. |
| `migrations/*.sql` | BD ya existente | Cambios puntuales si creaste la BD antes de una actualización del schema. |
| `test/*.sql` | Solo laboratorio | Pruebas FDW y sync; no forman parte del arranque normal. |

---

## Inicio rápido (recomendado)

Desde la carpeta `database/`:

```bash
# Desde database/: levanta PG y MySQL (no solo postgres-central)
docker compose up -d
python3 -m venv .venv-init && .venv-init/bin/pip install -r requirements-init.txt
.venv-init/bin/python init_databases.py
```

Eso aplica, en orden: `01` → `02` → usuarios (`04`) → FDW (`05` renderizado). Luego, si quieres datos demo:

```bash
.venv-init/bin/python apply_demo_seed.py
# o: init_databases.py --demo
```

Conexión por defecto: host `localhost`, puerto `5432`, BD `sicc_central`, usuario bootstrap `sicc_admin` / `sicc_pg_pass_2024`. La API usa `sicc_api` (ver `../README.md`).

---

## Ejecutar SQL a mano

```bash
cd ../database
PGPASSWORD=sicc_pg_pass_2024 psql -h localhost -U sicc_admin -d sicc_central -f postgres/01_schema.sql
```

O con el contenedor:

```bash
docker compose exec -T postgres-central \
  psql -U sicc_admin -d sicc_central -f - < postgres/02_seed.sql
```

---

## Migraciones (`migrations/`)

Solo si tu BD **ya existía** y te falta algo que el `01_schema.sql` nuevo ya trae integrado:

| Script | Para qué |
|--------|----------|
| `03_incidentes_activos_snapshot.sql` | Columnas snapshot en `Incidentes_Activos`. |
| `04_reportes_cache.sql` | Tabla `reportes_cache` (si no está en tu schema). |
| `05_usuario_dba_cochabamba.sql` | Usuario DBA de prueba en metadata (PG). |

MySQL tiene sus propios scripts en [`../mysql/migrations/`](../mysql/migrations/).

---

## FDW (lectura de Cochabamba)

- Esquema foráneo: `sucursal_cochabamba` (tablas importadas desde MySQL).
- Configuración: `05_fdw_mysql.sql.template` + variables en `database/.env` (`MYSQL_FDW_HOST=mysql-secundaria` dentro de Docker).
- Reimportar tablas: `python init_databases.py --distribuido --force-fdw`
- Comprobar: [`test/fdw_smoke.sql`](test/fdw_smoke.sql) (instrucciones en [`test/README.md`](test/README.md)).

---

## Datos en este nodo

| Tipo | Ejemplos | Sync LWW |
|------|----------|----------|
| Replicadas | `Usuarios`, `Sesiones`, catálogos, `sync_control` | Sí (`POST /sync/manual`) |
| Locales | `Incidentes`, `Activos`, `Bitacora_Investigacion` | No — solo Santa Cruz |

Los incidentes de **Cochabamba** viven en MySQL, no aquí.

---

## Pruebas (`test/`)

- `fdw_smoke.sql` — verifica que FDW ve tablas de Cochabamba.
- `sync_metadata_test.sql` — ejemplos comentados para probar sync LWW.
- `deadlock_demo.sql` — deadlock en dos terminales (UUIDs demo).
- `../scripts/simular_deadlock.py` — simulación automática de deadlock.

Detalle: [test/README.md](test/README.md).

---

## Documentación del proyecto

- [README global](../../README.md)
- [Bases de datos](../README.md)
- [Diagrama E-R PostgreSQL](../../docs/er_postgres_central.mmd)
- [Conectividad y FDW](../../docs/conectividad_red.md)
- [Arquitectura](../../docs/system_architecture.md)
- [Backend / API](../../backend/README.md)
