# SICC — Bases de Datos

Nodos de la arquitectura distribuida: **PostgreSQL** (sede central, Santa Cruz) y **MySQL** (sucursal Cochabamba).

Guía global del proyecto: [README.md](../README.md) en la raíz.

---

## Docker Compose: un archivo, dos servicios

El stack de bases de datos es **`database/docker-compose.yml`**. Ese compose levanta **PostgreSQL, MySQL y dos MongoDB** en la red `sicc-net`:

| Servicio en compose | Contenedor | Motor | Puerto en el host |
|---------------------|------------|-------|-------------------|
| `postgres-central` | `sicc-postgres-central` | PostgreSQL 16 + `mysql_fdw` | `5432` |
| `mysql-secundaria` | `sicc-mysql-secundaria` | MySQL 8.0 | `3306` |
| `mongo-santa-cruz` | `sicc-mongo-santa-cruz` | MongoDB 7.0.14 | `27017` |
| `mongo-cochabamba` | `sicc-mongo-cochabamba` | MongoDB 7.0.14 | `27018` |

Comandos habituales (desde `database/`):

```bash
docker compose build postgres-central   # solo 1.ª vez: imagen PG con mysql_fdw
docker compose up -d                    # arranca PG, MySQL y Mongo
docker compose ps                       # todos deben estar healthy
```

**No confundir nombres:**

- `postgres-central` es el **servicio** PostgreSQL dentro del compose, no el nombre del archivo ni “el compose entero”.
- `docker compose build postgres-central` **no** levanta solo PostgreSQL para desarrollo: construye la imagen custom; `up -d` sigue levantando **los dos** servicios.
- El `docker-compose.yml` de la **raíz** del repo es otro archivo: API + frontend (`api`, `web`), **sin** bases de datos. Las BDs siempre van con el compose de esta carpeta.

---

## Qué hay en esta carpeta

Bajo `database/` hay carpetas de SQL (**`postgres/`**, **`mysql/`**) y Mongo (**`mongo/santa_cruz`**, **`mongo/cochabamba`**) más scripts de operación en la raíz.

| Archivo / carpeta | Uso |
|-------------------|-----|
| `docker-compose.yml` | Stack **PG + MySQL + Mongo** en `sicc-net` |
| `postgres/Dockerfile` | PostgreSQL 16 + extensión `mysql_fdw` |
| [`postgres/README.md`](postgres/README.md) | Guía del nodo central (qué hace cada SQL) |
| `postgres/` | SQL PostgreSQL: schema, seed, usuarios, FDW, migraciones, pruebas |
| `postgres/01_schema.sql` | DDL sede central |
| `postgres/06_vistas_procedimientos.sql` | Vistas y funciones SP (rúbrica SQL) |
| `postgres/07_transacciones.sql` | SP con FOR UPDATE, demos de aislamiento |
| `scripts/simular_deadlock.py` | Simulación automática de deadlock |
| `postgres/02_seed.sql` | Catálogos + usuario admin (PG) |
| `postgres/04_usuarios_sql.sql` | Roles `sicc_api`, `sicc_reportes` |
| `postgres/05_fdw_mysql.sql.template` | FDW hacia MySQL (renderizado por init) |
| `postgres/migrations/` | ALTER para BDs ya existentes (PG) |
| `postgres/test/` | SQL de prueba (FDW, sync LWW) |
| [`mysql/README.md`](mysql/README.md) | Guía del nodo Cochabamba (qué hace cada SQL) |
| `mysql/` | SQL MySQL: schema, seed, usuarios, migraciones |
| `mysql/01_schema.sql` | DDL sede secundaria |
| `mysql/06_vistas_procedimientos.sql` | Vistas, SP y triggers MySQL |
| `mysql/02_seed.sql` | Catálogos + usuario admin (MySQL) |
| `mysql/04_usuarios_sql.sql` | `sicc_api`, `sicc_fdw_ro` (lectura FDW) |
| `mysql/migrations/` | ALTER para BDs ya existentes (MySQL) |
| [`mongo/README.md`](mongo/README.md) | Guía MongoDB por sede (init + seed demo) |
| `mongo/santa_cruz/` | Init `sicc_sc` (colecciones, índices, seed) |
| `mongo/cochabamba/` | Init `sicc_cb` (colecciones, índices, seed) |
| `init_databases.py` | **Init idempotente** + usuarios SQL + FDW |
| `requirements-init.txt` | Dependencias del script de init |
| `.env.example` | Variables init/FDW (`MYSQL_FDW_HOST`, etc.) |

> El montaje en `docker-entrypoint-initdb.d` solo ejecuta SQL en el **primer** arranque con volumen nuevo. Si los contenedores ya existían vacíos sin scripts, usa `init_databases.py`.

---

## Credenciales por defecto

### Bootstrap (solo init / migraciones)

| Nodo | User | Password |
|------|------|----------|
| PostgreSQL | `sicc_admin` | `sicc_pg_pass_2024` |
| MySQL | `sicc_admin` | `sicc_mysql_pass_2024` |
| MySQL root | `root` | `sicc_root_pass_2024` |
| MongoDB root (init) | `sicc_mongo_admin` | `sicc_mongo_pass_2024` |
| MongoDB API (futuro) | `sicc_mongo_api` | `sicc_mongo_api_pass_2024` |

### API FastAPI (`backend/.env`)

| Nodo | User | Password |
|------|------|----------|
| PostgreSQL | `sicc_api` | `sicc_api_pass_2024` |
| MySQL | `sicc_api` | `sicc_api_pass_2024` |

### FDW (PostgreSQL lee MySQL)

| Uso | User | Password |
|-----|------|----------|
| Mapping FDW | `sicc_fdw_ro` | `sicc_fdw_ro_pass_2024` |

Host del servidor FDW dentro de Docker: `mysql-secundaria` (ver `database/.env.example`).

**Si MySQL está en otra máquina o IP:** cambia `MYSQL_FDW_HOST` a la dirección **vista desde el contenedor PostgreSQL**, no desde tu laptop. Guía completa: [**docs/conectividad_red.md**](../docs/conectividad_red.md).

---

## Conectividad y red

| Variable (`database/.env`) | Quién la usa | Valor típico (local) |
|----------------------------|--------------|----------------------|
| `PG_HOST` / `MYSQL_HOST` | `init_databases.py` (corre en el **host**) | `localhost` |
| `MONGO_SC_HOST` / `MONGO_CB_HOST` | Conexión Mongo desde el **host** | `localhost` (`27017` / `27018`) |
| `MYSQL_FDW_HOST` | FDW dentro del contenedor **postgres-central** | `mysql-secundaria` (nombre del servicio Docker) |

Copia la plantilla:

```bash
cp .env.example .env
```

Escenarios (BD remota, API en Docker, firewall): [**docs/conectividad_red.md**](../docs/conectividad_red.md).

---

## Inicio rápido

### 1. Levantar contenedores (PG + MySQL)

```bash
cd database
docker compose build postgres-central   # 1.ª vez: build de la imagen PG (mysql_fdw)
docker compose up -d                    # levanta postgres-central y mysql-secundaria
docker compose ps                       # ambos deben estar healthy
```

### 2. Inicializar esquema y datos

```bash
# Entorno virtual (recomendado en Arch/Linux)
python3 -m venv .venv-init
.venv-init/bin/pip install -r requirements-init.txt
.venv-init/bin/python init_databases.py
```

Salida esperada:

```
Inicializando PostgreSQL...
OK postgres
Inicializando MySQL...
OK mysql

Listo. Usuario demo: admin@sicc.com / admin123
```

### Datos demo (5 activos + 5 incidentes por sede)

```bash
python apply_demo_seed.py
# o tras init completo:
python init_databases.py --demo
```

Santa Cruz → PostgreSQL · Cochabamba → MySQL. Ver [`postgres/test/README.md`](postgres/test/README.md) para SQL **TEST** de sincronización.

Si el esquema ya existe:

```
SKIP postgres (esquema ya existe; usa --force para re-ejecutar)
```

### 3. Siguiente paso: API

```bash
cd ../backend
cp .env.example .env
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8000
```

Ver [backend/README.md](../backend/README.md).

---

## Script `init_databases.py`

### Comportamiento

- Ejecuta en orden: `postgres/01` → `02` → `mysql/01` → `02`, luego **usuarios SQL + FDW** (`04` / `05`).
- **Idempotente:** si ya existe la tabla `cat_Sedes`, omite ese nodo.
- Usa `psql` / `mysql` CLI si están instalados; si no, fallback con `psycopg` + `pymysql`.

### Opciones

```bash
python init_databases.py              # schema + seed + usuarios + FDW
python init_databases.py --only postgres
python init_databases.py --only mysql
python init_databases.py --distribuido  # solo usuarios SQL y FDW (BD ya con tablas)
python init_databases.py --force-fdw  # reimportar tablas foráneas de Cochabamba
python init_databases.py --skip-distribuido
python init_databases.py --academico    # solo vistas, SP y triggers (06)
python init_databases.py --skip-academico # omitir 06 tras init normal
python init_databases.py --force      # re-ejecutar aunque exista esquema (puede fallar con datos)
python init_databases.py --benchmark  # +10000 incidentes bench por nodo (EXPLAIN)
python init_databases.py --benchmark 15000 --only mysql
.venv-init/bin/python apply_benchmark_seed.py              # solo carga bench
.venv-init/bin/python apply_benchmark_seed.py --clear      # borrar filas [Bench]%
```

### Optimización (EXPLAIN)

Tras `--benchmark`, ejecutar en DataGrip o CLI:

- `postgres/test/optimizacion_explain.sql` (Santa Cruz, `id_sede = 1`)
- `mysql/test/optimizacion_explain.sql` (Cochabamba, `id_sede = 2`)

La carga bench incluye ~40% filas de la **otra** sede para que el plan **ANTES** (sin `id_sede`) examine más filas que el **DESPUÉS**.

### BDs ya existentes (migrar a FDW)

```bash
docker compose build postgres-central
docker compose up -d
.venv-init/bin/python init_databases.py --distribuido
# backend/.env: PG_USER y MYSQL_USER = sicc_api
```

### Variables de entorno

```bash
cp .env.example .env
```

| Variable | Descripción |
|----------|-------------|
| `PG_*`, `MYSQL_*` | Conexión del script de init (usuario `sicc_admin`) |
| `MYSQL_FDW_HOST` | Host de MySQL **desde el contenedor PG** (FDW) |
| `MYSQL_FDW_USER` / `MYSQL_FDW_PASSWORD` | Usuario solo lectura para FDW |

Si las BDs están en otra IP, edita `PG_HOST` y `MYSQL_HOST` antes de `init_databases.py`. Tras mover MySQL, ejecuta `--distribuido --force-fdw`.

---

## Usuarios de prueba (seed)

UUIDs **fijos** en ambos nodos (PostgreSQL y MySQL) para sync y switcher `/dev/switch` del frontend:

| UUID | Email | Password | Rol | Sede |
|------|-------|----------|-----|------|
| `11111111-1111-1111-1111-111111111101` | `admin@sicc.com` | `admin123` | Administrador | Santa Cruz (1) |
| `11111111-1111-1111-1111-111111111102` | `analista.sc@test.sicc` | `test123` | Analista | Santa Cruz (1) |
| `11111111-1111-1111-1111-111111111103` | `analista.cb@test.sicc` | `test123` | Analista | Cochabamba (2) |
| `11111111-1111-1111-1111-111111111104` | `dba@test.sicc` | `test123` | DBA | Santa Cruz (1) |

Si ya tenías BDs con UUID aleatorio del admin, re-ejecuta `init_databases.py` desde cero o actualiza manualmente los UUID en `Usuarios`.

Para regenerar el hash bcrypt:

```bash
cd ../backend
uv run python -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())"
# Actualizar postgres/02_seed.sql y mysql/02_seed.sql con el nuevo hash
```

---

## Operación diaria

```bash
# Arrancar
docker compose up -d

# Logs
docker compose logs -f
docker compose logs -f postgres-central
docker compose logs -f mysql-secundaria

# Parar (datos en volúmenes)
docker compose down

# Parar y borrar TODO (requiere init de nuevo)
docker compose down -v
docker compose up -d
.venv-init/bin/python init_databases.py
```

---

## Modelo de datos (resumen)

| Tipo | Tablas | ¿Sync LWW? |
|------|--------|------------|
| Replicadas | `cat_Sedes`, `Roles`, `Permisos`, `Roles_Permisos`, `cat_Estados`, `cat_Prioridades`, `cat_Tipos_Incidente`, `Usuarios`, `Sesiones`, `sync_control` | Sí, vía API `POST /sync/manual` |
| Locales por sede | `Activos`, `Incidentes`, `Incidentes_Activos`, `Bitacora_Investigacion` | No |

Mapeo sede → motor (usado por la API):

| `id_sede` | Sede | Motor |
|-----------|------|--------|
| 1 | Sede Central - Santa Cruz | PostgreSQL |
| 2 | Sucursal Cochabamba | MySQL |

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `Connection refused` en init MySQL | Contenedor aún no listo | `docker compose ps`, esperar `healthy`, reintentar |
| `SKIP postgres` pero tablas vacías | Detección por metadatos inconsistente | `init_databases.py --force` o `docker compose down -v` y de nuevo |
| SQL falla en PG 16 | Triggers usan `EXECUTE FUNCTION` | Usar imagen `postgres:16-alpine` del compose |
| Datos viejos / corruptos | Volumen persistente | `docker compose down -v` y reiniciar flujo completo |
| Login `admin@sicc.com` → 401 | Admin creado a mano o hash distinto al seed | `docker compose down -v`, `init_databases.py`, o restaurar UUID/hash del seed |
| MySQL sin `Incidentes` / `sync_control` | Init de Docker cortó en `sync_control` (timestamp `1970-01-01 00:00:00` inválido en MySQL 8) | `docker compose down -v`, `up -d`, `init_databases.py` (schema ya corregido: `00:00:01`) |
| `POST /sync/manual` → 500 | BDs desalineadas o bug ya corregido en API | Verificar tablas en ambos nodos; `cd backend && uv run pytest -v` |
| FDW / `extension mysql_fdw` no existe | Imagen antigua `postgres:16-alpine` | `docker compose build postgres-central && up -d`; `init_databases.py --distribuido --force-fdw` |
| FDW no conecta a MySQL | Host FDW incorrecto | Dentro de Docker usar `MYSQL_FDW_HOST=mysql-secundaria`; probar `postgres/test/fdw_smoke.sql` |
| `user mapping not found for sicc_admin` | Init corre como `sicc_admin` sin mapping FDW | `init_databases.py --distribuido --force-fdw` |
| `user mapping not found for sicc_api` | API/reportes usan `sicc_api` sin mapping FDW | Igual: `--force-fdw` (template incluye mapping para `sicc_api`) |
| API 401/500 tras migrar usuarios | `.env` sigue con `sicc_admin` | `PG_USER`/`MYSQL_USER`=`sicc_api`; o `init_databases.py --distribuido` |
| Falta snapshot en `Incidentes_Activos` | BD creada antes de columnas snapshot | Ver `postgres/migrations/03_incidentes_activos_snapshot.sql` y `mysql/migrations/03_incidentes_activos_snapshot.sql` |

---

## Documentación relacionada

- [README global](../README.md)
- [Manual de conectividad y red](../docs/conectividad_red.md)
- [Backend / API](../backend/README.md)
- [Frontend](../frontend/README.md)
- [Arquitectura](../docs/system_architecture.md)
- [Requisitos](../docs/system_requirements.md)
- [E-R PostgreSQL](../docs/er_postgres_central.mmd) · [E-R MySQL](../docs/er_mysql_cochabamba.mmd)
