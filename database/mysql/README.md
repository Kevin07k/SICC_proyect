# MySQL — Sucursal Cochabamba

Base de datos **local** de la sucursal (`id_sede = 2`). Guarda incidentes y activos de Cochabamba y replica **metadata** (usuarios, catálogos, `sync_control`) con la central vía API — no con scripts SQL entre nodos.

Guía general (Docker, credenciales, troubleshooting): [../README.md](../README.md).

---

## ¿Qué hace cada archivo?

| Archivo | ¿Cuándo? | Descripción |
|---------|----------|-------------|
| `01_schema.sql` | Primera vez | Tablas, índices y triggers del nodo secundario (misma lógica de negocio que PG, sintaxis MySQL). |
| `02_seed.sql` | Tras el schema | Catálogos, roles, permisos y usuarios de prueba (mismos UUID que en PostgreSQL para sync). |
| `03_seed_demo_operacional.sql` | Opcional (dev) | 5 activos + 5 incidentes en **Cochabamba**. No usar en producción. |
| `04_usuarios_sql.sql` | Tras 01–02 | `sicc_api` (API) y `sicc_fdw_ro` (solo lectura para FDW desde PostgreSQL). Requiere usuario **root** en el init. |
| `06_vistas_procedimientos.sql` | Tras 04 | Vistas, procedimientos `sp_*`, triggers `updated_at`. Init o `--academico`. |
| `07_transacciones.sql` | Tras 06 | `sp_actualizar_propietario_activo`, demos transaccionales. |
| `migrations/*.sql` | BD ya existente | Cambios puntuales si tu BD se creó antes de una actualización del schema. |

---

## Inicio rápido (recomendado)

Desde la carpeta `database/`:

```bash
docker compose up -d
python3 -m venv .venv-init && .venv-init/bin/pip install -r requirements-init.txt
.venv-init/bin/python init_databases.py
```

Eso aplica `01` → `02` en MySQL y, en el mismo flujo, usuarios (`04` con root) + FDW en PostgreSQL. Datos demo opcionales:

```bash
.venv-init/bin/python apply_demo_seed.py
```

Conexión por defecto: host `localhost`, puerto `3306`, BD `sicc_cochabamba`, usuario bootstrap `sicc_admin` / `sicc_mysql_pass_2024`. La API usa `sicc_api`.

---

## Ejecutar SQL a mano

```bash
cd ../database
mysql -h localhost -P 3306 -u sicc_admin -psicc_mysql_pass_2024 sicc_cochabamba < mysql/01_schema.sql
mysql -h localhost -P 3306 -u sicc_admin -psicc_mysql_pass_2024 sicc_cochabamba < mysql/02_seed.sql
```

`04_usuarios_sql.sql` suele ejecutarse como root (crea usuarios):

```bash
mysql -h localhost -P 3306 -u root -psicc_root_pass_2024 sicc_cochabamba < mysql/04_usuarios_sql.sql
```

O con el contenedor:

```bash
docker compose exec -T mysql-secundaria \
  mysql -u sicc_admin -psicc_mysql_pass_2024 sicc_cochabamba < mysql/02_seed.sql
```

---

## Migraciones (`migrations/`)

Solo si tu BD **ya existía** y no tienes los cambios del schema actual:

| Script | Para qué |
|--------|----------|
| `03_incidentes_activos_snapshot.sql` | Columnas snapshot en `Incidentes_Activos`. |
| `05_usuario_dba_cochabamba.sql` | Usuario DBA de prueba en metadata (MySQL). |

El equivalente en PostgreSQL está en [`../postgres/migrations/`](../postgres/migrations/).

---

## Datos en este nodo

| Tipo | Ejemplos | Sync LWW |
|------|----------|----------|
| Replicadas | `Usuarios`, `Sesiones`, catálogos, `sync_control` | Sí (`POST /sync/manual`) |
| Locales | `Incidentes`, `Activos`, `Bitacora_Investigacion` | No — solo Cochabamba |

**No** replicar activos entre sedes con sync: el traslado es `POST /activos/{uuid}/transferir` en la API.

PostgreSQL **lee** tablas operacionales de aquí vía FDW (`sicc_fdw_ro`), no las escribe.

---

## Usuarios de prueba (Cochabamba)

| Email | Password | Rol |
|-------|----------|-----|
| `admin@sicc.com` | `admin123` | Administrador (ambas sedes) |
| `analista.cb@test.sicc` | `test123` | Analista |
| `dba.cb@test.sicc` | `test123` | DBA (reportes) |

Los incidentes demo llevan prefijo `[Demo CB]` en el título.

Pruebas de sync (comentarios PG + MySQL): [`../postgres/test/sync_metadata_test.sql`](../postgres/test/sync_metadata_test.sql).

---

## Documentación del proyecto

- [README global](../../README.md)
- [Bases de datos](../README.md)
- [Diagrama E-R MySQL](../../docs/er_mysql_cochabamba.mmd)
- [Conectividad y red](../../docs/conectividad_red.md)
- [Arquitectura](../../docs/system_architecture.md)
- [Backend / API](../../backend/README.md)
