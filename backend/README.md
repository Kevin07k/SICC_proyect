# Backend SICC (API)

**FastAPI** expone solo **REST JSON**: autenticación simplificada (práctica local), CRUD por sede, sincronización de metadata (LWW) y traslado de activos entre PostgreSQL y MySQL.

La UI está en [`../frontend/`](../frontend/) (Next.js). **No** incluye plantillas HTML ni acceso directo a BDs desde el navegador.

Guía global del proyecto: [README.md](../README.md) en la raíz.

---

## Qué hay en esta carpeta

```
backend/
├── app/
│   ├── main.py           # FastAPI, CORS, routers
│   ├── config.py         # Settings (.env)
│   ├── dependencies.py # Auth X-Usuario-UUID, RBAC
│   ├── routers/          # HTTP: auth, sync, incidentes, activos, …
│   ├── services/         # Lógica de negocio
│   ├── repositories/     # SQLAlchemy Core
│   ├── db/               # Engines PG + MySQL
│   └── core/             # SedeRouter, tablas replicadas
├── tests/                # pytest (integración con BDs)
├── Dockerfile            # Imagen solo API
├── docker-compose.yml    # API en Docker (BDs aparte)
├── .env.example
└── pyproject.toml        # uv / dependencias
```

---

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL y MySQL en ejecución → ver [database/README.md](../database/README.md)

---

## Inicio rápido

### Prerrequisito: bases de datos listas

```bash
cd ../database
docker compose up -d
.venv-init/bin/python init_databases.py   # ver database/README.md
```

### 1. Configurar entorno

```bash
cd backend
cp .env.example .env
# Valores por defecto apuntan a localhost; ajustar si cambiaste credenciales
```

### 2. Instalar y arrancar

```bash
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8000
```

| Recurso | URL |
|---------|-----|
| Swagger / OpenAPI | http://localhost:8000/docs |
| Health (ping PG + MySQL) | http://localhost:8000/health |

---

## Autenticación (modo práctica local)

Sin JWT ni tabla `Sesiones` en esta versión.

| Paso | Acción |
|------|--------|
| 1 | `POST /auth/login` con `email` y `password` |
| 2 | Guardar el `uuid` de la respuesta |
| 3 | Enviar header `X-Usuario-UUID: <uuid>` en todas las rutas protegidas |

### Credenciales demo

| Campo    | Valor            |
|----------|------------------|
| Email    | `admin@sicc.com` |
| Password | `admin123`       |

### Ejemplos curl

```bash
# Login
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sicc.com","password":"admin123"}'

# Usuario actual (reemplazar UUID)
export UUID="<uuid-del-login>"
curl -s http://localhost:8000/auth/me -H "X-Usuario-UUID: $UUID"

# Listar incidentes de la sede del usuario
curl -s http://localhost:8000/incidentes -H "X-Usuario-UUID: $UUID"

# Sincronizar metadata entre nodos (requiere permiso sync.ejecutar)
curl -s -X POST http://localhost:8000/sync/manual -H "X-Usuario-UUID: $UUID"

# Estado de sync
curl -s http://localhost:8000/sync/status -H "X-Usuario-UUID: $UUID"
```

---

## Routing por sede

La API elige el motor según el `id_sede` del usuario autenticado:

| `id_sede` | Sede | Base de datos |
|-----------|------|----------------|
| 1 | Santa Cruz (central) | PostgreSQL `sicc_central` |
| 2 | Cochabamba | MySQL `sicc_cochabamba` |

Configurable en `.env`: `SEDE_CENTRAL_ID`, `SEDE_SECUNDARIA_ID`.

---

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado PG + MySQL |
| `POST` | `/auth/login` | Login |
| `GET` | `/auth/me` | Perfil + permisos |
| `POST` | `/sync/manual` | Sync LWW de metadata |
| `GET` | `/sync/status` | Pendientes de sincronizar |
| `GET/POST/PATCH` | `/incidentes` | CRUD local por sede |
| `GET/POST/PATCH` | `/activos` | CRUD local por sede |
| `POST` | `/activos/{uuid}/transferir` | Traslado cross-DB (mismo UUID) |
| `GET/POST` | `/incidentes/{uuid}/bitacora` | Bitácora de investigación |
| `GET/POST/PATCH` | `/usuarios` | Usuarios replicados; vista global con `reportes.ver` o Admin |
| `GET` | `/reportes/global` | Reporte global (caché PG, TTL configurable) |
| `POST` | `/reportes/global/regenerar` | Forzar recálculo del reporte |
| `GET` | `/catalogos/sedes`, `/estados`, `/prioridades`, `/tipos-incidente` | Catálogos |

RBAC: permisos por código (`incidentes.ver`, `activos.gestionar`, `sync.ejecutar`, …). El rol **Administrador** tiene bypass.

---

## Arquitectura de capas

```
HTTP  →  routers/  →  services/  →  repositories/  →  SQL (Core)
                              ↓
                        SedeRouter
                    PG (sede 1) | MySQL (sede 2)
```

### Reglas de negocio implementadas

| Regla | Comportamiento en API |
|-------|------------------------|
| RN-03 | CRUD filtrado por `id_sede` del usuario |
| RN-04 | Baja lógica (`eliminado=true`), sin DELETE físico de historial |
| RN-07 | Sync solo tablas replicadas |
| RN-08 | Activos no entran en `/sync/manual` |
| RN-09 | Traslado solo vía `POST /activos/{uuid}/transferir` |

---

## Variables de entorno

```bash
cp .env.example .env
```

| Variable | Uso |
|----------|-----|
| `PG_*`, `MYSQL_*` | Conexión a ambos motores (usuario **`sicc_api`**, no `sicc_admin`) |
| `CORS_ORIGINS` | Orígenes del frontend permitidos por la API |
| `SEDE_CENTRAL_ID` / `SEDE_SECUNDARIA_ID` | Mapeo sede → motor |
| `REPORTES_CACHE_TTL_SECONDS` | Caché del reporte global en PG |

La API **no** usa `MYSQL_FDW_*`; el FDW lo configura `database/init_databases.py`.

---

## Conectividad y red

| Escenario | `PG_HOST` / `MYSQL_HOST` |
|-----------|---------------------------|
| API en el host, BDs en Docker (puertos publicados) | `localhost` |
| API en Docker, BDs en el host | `host.docker.internal` |
| BDs en servidores remotos | IP o hostname de cada servidor |

También actualiza `CORS_ORIGINS` si el frontend no corre en `localhost:3000`.

Guía paso a paso (firewall, FDW, frontend en LAN): [**docs/conectividad_red.md**](../docs/conectividad_red.md).

---

## Docker (solo API)

Las BDs **no** van en este compose. Usa `database/docker-compose.yml` (servicios `postgres-central` **y** `mysql-secundaria`).

```bash
# 1. BDs (PG + MySQL) en Docker
cd ../database
docker compose build postgres-central   # 1.ª vez: imagen PG con mysql_fdw
docker compose up -d                    # levanta ambos contenedores
.venv-init/bin/python init_databases.py

# 2. API en contenedor
cd ../backend
cp .env.example .env
```

Editar `.env` para Docker en Linux:

```env
PG_HOST=host.docker.internal
MYSQL_HOST=host.docker.internal
```

```bash
docker compose up --build
# API en http://localhost:8000
```

El `docker-compose.yml` incluye `extra_hosts: host.docker.internal:host-gateway` para alcanzar las BDs del host.

---

## Desarrollo y calidad

```bash
# Tests (integración requiere PG + MySQL arriba e inicializados)
uv run pytest -v
uv run pytest tests/test_health.py -v

# Linter
uv run ruff check app tests

# Recargar al editar
uv run uvicorn app.main:app --reload --port 8000
```

Marcador `@pytest.mark.integration` en tests que necesitan ambas BDs.

---

## Flujos típicos

### Alta de incidente (analista sede central)

1. Login → obtener `uuid`.
2. `POST /incidentes` con `X-Usuario-UUID` y datos del incidente.
3. El registro se guarda solo en PostgreSQL.

### Traslado de activo a Cochabamba

1. Crear activo en sede origen (`POST /activos`).
2. `POST /activos/{uuid}/transferir` con `{"sede_destino_id": 2, "motivo": "..."}`.
3. Origen: `eliminado=true`; destino: mismo UUID activo en MySQL.

### Alinear metadata tras trabajar offline en MySQL

1. `POST /sync/manual` (usuario con permiso `sync.ejecutar`).
2. Verificar con `GET /sync/status`.

---

## Solución de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| `401` en rutas protegidas | Header `X-Usuario-UUID` presente y válido |
| `403` en sync | Rol con permiso `sync.ejecutar` o Administrador |
| `/health` con `postgres: false` | `cd database && docker compose ps` |
| Login incorrecto | BDs inicializadas; password `admin123`; hash en seeds |
| API Docker no conecta | `PG_HOST` / `MYSQL_HOST` = `host.docker.internal` |
| Tablas PG en minúsculas | Normal en PostgreSQL; el código usa mapeo en `app/core/sql_dialect.py` |

---

## Documentación relacionada

- [README global](../README.md)
- [Bases de datos](../database/README.md)
- [Frontend](../frontend/README.md)
- [Manual de conectividad y red](../docs/conectividad_red.md)
- [Arquitectura](../docs/system_architecture.md)
- [Requisitos](../docs/system_requirements.md)
