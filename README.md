# SICC — Sistema Integrado de Ciberseguridad y Control

SICC gestiona **incidentes de seguridad** y **activos de TI** en un entorno **multi-sede**: sede central (Santa Cruz) y sucursal (Cochabamba). Cada sede tiene su propia base de datos; la metadata (usuarios, catálogos, roles) se sincroniza entre nodos; los incidentes y activos permanecen **locales** salvo el traslado explícito de activos vía API.

---

## ¿Qué hace el sistema?

| Función | Descripción |
|---------|-------------|
| **Incidentes** | Alta, edición, estados, prioridades, bitácora de investigación |
| **Activos** | Inventario por sede; traslado entre sedes con el mismo UUID |
| **Usuarios y roles** | RBAC; metadata replicada en ambas BDs |
| **Sync** | `POST /sync/manual` — Last-Write-Wins sobre tablas replicadas |
| **Reportes** | Vista global desde PostgreSQL (FDW lectura hacia MySQL) |

---

## ¿Cómo funciona? (vista rápida)

```
Usuario → Frontend (Next.js) → API (FastAPI) → PostgreSQL o MySQL (según sede)
                                    ↓
                         Sync metadata ↔ entre PG y MySQL
```

1. El usuario inicia sesión en la UI; el frontend envía `X-Usuario-UUID` a la API.
2. La API elige **PostgreSQL** (sede 1) o **MySQL** (sede 2) según la sede del usuario.
3. Incidentes y activos se leen/escriben **solo** en la BD de esa sede.
4. Un administrador puede ejecutar **sync** para alinear usuarios y catálogos entre nodos.
5. **Traslado de activo**: la API desactiva en origen e inserta en destino (no es sync).

Diagramas: [`docs/arquitectura.mmd`](docs/arquitectura.mmd), [`docs/distribucion_datos.mmd`](docs/distribucion_datos.mmd).

Detalle técnico: [`docs/system_architecture.md`](docs/system_architecture.md) · Requisitos: [`docs/system_requirements.md`](docs/system_requirements.md).

---

## Estructura del repositorio

Cada carpeta tiene su **README con configuración y uso**. Empieza por la que vayas a tocar:

| Carpeta | Contenido | Documentación |
|---------|-----------|----------------|
| [`database/`](database/) | Compose **PG + MySQL**, DDL, seeds, init, FDW | [**database/README.md**](database/README.md) |
| [`backend/`](backend/) | API REST FastAPI (sync, CRUD, traslado) | [**backend/README.md**](backend/README.md) |
| [`frontend/`](frontend/) | Interfaz Next.js/React | [**frontend/README.md**](frontend/README.md) |
| [`docs/`](docs/) | Arquitectura, requisitos, diagramas E-R, **red/conexiones** | Ver tabla abajo |

---

## Documentación en `docs/`

| Archivo | Para qué |
|---------|----------|
| [system_architecture.md](docs/system_architecture.md) | Arquitectura distribuida, ownership, sync, FDW |
| [system_requirements.md](docs/system_requirements.md) | Requisitos y reglas de negocio |
| [conectividad_red.md](docs/conectividad_red.md) | **Manual de red**: localhost, Docker, BDs en otra máquina |
| [arquitectura.mmd](docs/arquitectura.mmd) | Diagrama general (Mermaid) |
| [distribucion_datos.mmd](docs/distribucion_datos.mmd) | Qué datos van en cada nodo |
| [er_postgres_central.mmd](docs/er_postgres_central.mmd) | Modelo E-R PostgreSQL |
| [er_mysql_cochabamba.mmd](docs/er_mysql_cochabamba.mmd) | Modelo E-R MySQL |

---

## Requisitos

- [Docker](https://docs.docker.com/) y Docker Compose
- Python 3.11+ y [uv](https://docs.astral.sh/uv/) (backend e init de BDs)
- Node.js 20+ (frontend)

---

## Inicio rápido (primera vez)

Orden: **bases de datos → API → frontend**.

```bash
# 1. Bases de datos (database/docker-compose.yml → PostgreSQL + MySQL)
cd database
docker compose build postgres-central   # 1.ª vez: imagen PG con mysql_fdw (no es “solo PG”)
docker compose up -d                    # levanta ambos contenedores
python3 -m venv .venv-init && .venv-init/bin/pip install -r requirements-init.txt
cp .env.example .env                    # opcional: ajustar hosts
.venv-init/bin/python init_databases.py

# 2. API
cd ../backend
cp .env.example .env
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8000

# 3. Frontend
cd ../frontend
cp .env.local.example .env.local
npm install
npm run dev
```

| Recurso | URL |
|---------|-----|
| UI | http://localhost:3000 |
| API (Swagger) | http://localhost:8000/docs |
| Health (PG + MySQL) | http://localhost:8000/health |

**Login demo:** `admin@sicc.com` / `admin123` (ver [frontend/README.md](frontend/README.md)).

---

## ¿BD o API en otra máquina?

No uses solo `localhost`. Sigue el manual:

**[docs/conectividad_red.md](docs/conectividad_red.md)**

Ahí están los escenarios (Docker, IP remota, FDW, CORS, frontend en LAN).

---

## Arranque diario

```bash
cd database && docker compose up -d
cd ../backend && uv run uvicorn app.main:app --reload --port 8000
cd ../frontend && npm run dev
```

---

## Reglas importantes

- Incidentes **solo** en la BD de su sede.
- Activos **no** se sincronizan; traslado vía `POST /activos/{uuid}/transferir`.
- Sync LWW **solo** metadata (usuarios, catálogos, `sync_control`).
- No commitear archivos `.env` (contraseñas).

---

## Solución rápida de problemas

| Problema | Dónde mirar |
|----------|-------------|
| No conecta a PG/MySQL | [docs/conectividad_red.md](docs/conectividad_red.md) |
| Init / FDW / Docker | [database/README.md](database/README.md) |
| 401 / sync / endpoints | [backend/README.md](backend/README.md) |
| UI no carga datos | [frontend/README.md](frontend/README.md) |

---

## Rama y repositorio

Código en GitHub: `Kevin07k/SICC_proyect` — rama **`evil-sister`** (versión distribuida PG + MySQL + API + UI).
