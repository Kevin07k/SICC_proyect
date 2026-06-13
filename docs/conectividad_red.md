# Manual de conectividad y red — SICC

Guía para conectar **PostgreSQL**, **MySQL**, la **API** y el **frontend** cuando dejas de trabajar solo en `localhost` o cuando cada servicio corre en otra máquina.

---

## Quién se conecta a quién

```
┌─────────────┐     HTTP      ┌─────────────┐     TCP       ┌─────────────────┐
│  frontend   │ ────────────► │   backend   │ ────────────► │ PostgreSQL (SC) │
│  (navegador)│               │  (FastAPI)  │ ────────────► │ MySQL (CB)      │
└─────────────┘               └─────────────┘               └────────▲────────┘
                                                                    │ FDW (solo lectura)
                                                                    └──────────────┘
```

| Componente | Archivo de config | Variables clave |
|------------|-------------------|-----------------|
| Init de BDs (`init_databases.py`) | `database/.env` | `PG_HOST`, `MYSQL_HOST`, `MYSQL_FDW_HOST` |
| API | `backend/.env` | `PG_*`, `MYSQL_*`, `CORS_ORIGINS` |
| Frontend | `frontend/.env.local` | `NEXT_PUBLIC_API_URL` |
| FDW (dentro del contenedor PG) | renderizado en init desde `database/.env` | `MYSQL_FDW_HOST` (no es `localhost` del host) |

---

## Archivos Compose en el repo

| Archivo | Qué levanta |
|---------|-------------|
| [`database/docker-compose.yml`](../database/docker-compose.yml) | **PostgreSQL** (`postgres-central`) **y** **MySQL** (`mysql-secundaria`) en `sicc-net` |
| [`docker-compose.yml`](../docker-compose.yml) (raíz) | API (`api`) + frontend (`web`); **no** incluye BDs |
| [`backend/docker-compose.yml`](../backend/docker-compose.yml) | Solo la API |
| [`frontend/docker-compose.yml`](../frontend/docker-compose.yml) | Solo la UI |

`postgres-central` es el **nombre del servicio** PostgreSQL dentro del compose de `database/`, no un compose aparte. Para desarrollo local con BDs en Docker: `cd database && docker compose up -d` (ambos motores).

---

## Puertos por defecto

| Servicio | Puerto | Protocolo |
|----------|--------|-----------|
| PostgreSQL (Santa Cruz) | `5432` | TCP |
| MySQL (Cochabamba) | `3306` | TCP |
| API FastAPI | `8000` | HTTP |
| Frontend Next.js | `3000` | HTTP |

Si cambias puertos en Docker (`ports:` en compose), actualiza **todos** los `.env` afectados.

---

## Escenario 1 — Todo en tu PC (desarrollo local)

**Cuándo:** `database/docker-compose.yml` (PG + MySQL), API y UI en el host.

| Archivo | Valor típico |
|---------|----------------|
| `database/.env` | `PG_HOST=localhost`, `MYSQL_HOST=localhost`, `MYSQL_FDW_HOST=mysql-secundaria` |
| `backend/.env` | `PG_HOST=localhost`, `MYSQL_HOST=localhost` |
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL=http://localhost:8000` |

`MYSQL_FDW_HOST=mysql-secundaria` es el **nombre del servicio Docker** en la red `sicc-net`, no `localhost` (PostgreSQL corre *dentro* del contenedor).

---

## Escenario 2 — API en Docker, BDs en el host

**Cuándo:** `docker compose up` en la raíz (API + web), BDs con `database/docker-compose.yml`.

En `backend/.env` (o el `.env` que monta el contenedor API):

```env
PG_HOST=host.docker.internal
MYSQL_HOST=host.docker.internal
```

En Linux el `backend/docker-compose.yml` y el de la raíz ya incluyen:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

`database/.env` sigue con `localhost` para `init_databases.py` (el script corre en el **host**, no dentro del contenedor API).

---

## Escenario 3 — BDs en servidor remoto (otra máquina o VM)

**Cuándo:** PostgreSQL en `192.168.1.10`, MySQL en `192.168.1.20`, desarrollas desde tu laptop.

### En el servidor de PostgreSQL

- Escuchar en la red: `listen_addresses = '*'` en `postgresql.conf`
- `pg_hba.conf`: permitir tu IP de desarrollo
- Firewall: abrir **5432** solo a IPs de confianza

### En el servidor de MySQL

- `bind-address = 0.0.0.0` (o IP específica)
- Usuario con host `%` o tu IP: `CREATE USER 'sicc_api'@'%' ...`
- Firewall: abrir **3306**

### En tu laptop

`backend/.env`:

```env
PG_HOST=192.168.1.10
PG_PORT=5432
MYSQL_HOST=192.168.1.20
MYSQL_PORT=3306
```

`database/.env` (para init remoto):

```env
PG_HOST=192.168.1.10
MYSQL_HOST=192.168.1.20
```

**FDW:** si PostgreSQL sigue en Docker en la máquina 10, `MYSQL_FDW_HOST` debe ser la IP **vista desde ese contenedor** hacia MySQL (suele ser `192.168.1.20` o el hostname de la VM MySQL), **no** `mysql-secundaria` (ese nombre solo existe en el compose local).

Tras cambiar FDW:

```bash
cd database
.venv-init/bin/python init_databases.py --distribuido --force-fdw
```

### Init desde tu PC contra BDs remotas

1. Red accesible a ambos puertos.
2. Ajustar `database/.env` con IPs reales.
3. Ejecutar `init_databases.py` (usa `sicc_admin` / root según el script).

No ejecutes `docker compose` de BDs en tu laptop si las BDs ya están en servidores remotos.

---

## Escenario 4 — Frontend en otra máquina o acceso desde la red

El navegador llama a la API por URL pública o LAN.

`frontend/.env.local` (build/dev):

```env
NEXT_PUBLIC_API_URL=http://192.168.1.5:8000
```

En `backend/.env`:

```env
CORS_ORIGINS=http://192.168.1.6:3000,http://localhost:3000
```

(`192.168.1.6` = IP donde corre el navegador o el servidor Next.js.)

Si usas Docker para el frontend, la variable debe estar en **build time** (`args` en `docker-compose.yml`) porque `NEXT_PUBLIC_*` se embebe en el bundle.

---

## Escenario 5 — Una sede en otra máquina (solo MySQL remoto)

PostgreSQL local, MySQL en servidor `db-cb.ejemplo`:

| Variable | Valor |
|----------|--------|
| `MYSQL_HOST` | IP/hostname del servidor MySQL |
| `PG_HOST` | `localhost` (si PG sigue local) |
| `MYSQL_FDW_HOST` | misma IP/hostname que `MYSQL_HOST` (visto desde contenedor PG) |

La API enruta incidentes/activos de Cochabamba al motor MySQL; Santa Cruz sigue en PG.

---

## Checklist al cambiar de entorno

1. Copiar `.env.example` → `.env` en `database/` y `backend/`.
2. Actualizar **host, puerto, usuario y contraseña** (nunca commitear `.env`).
3. Probar conectividad:
   ```bash
   # PostgreSQL
   psql -h $PG_HOST -p $PG_PORT -U sicc_api -d sicc_central -c "SELECT 1"
   # MySQL
   mysql -h $MYSQL_HOST -P $MYSQL_PORT -u sicc_api -p sicc_cochabamba -e "SELECT 1"
   # API
   curl -s http://<API_HOST>:8000/health
   ```
4. Si moviste MySQL: reconfigurar FDW (`init_databases.py --distribuido --force-fdw`).
5. Ajustar `CORS_ORIGINS` y `NEXT_PUBLIC_API_URL`.
6. Reiniciar API y frontend tras cambiar `.env`.

---

## Errores frecuentes

| Síntoma | Causa | Solución |
|---------|--------|----------|
| `Connection refused` | Servicio apagado o puerto/firewall | `docker compose ps`, `ss -tlnp`, abrir puerto |
| FDW no ve tablas MySQL | `MYSQL_FDW_HOST` incorrecto | Usar hostname/IP **desde el contenedor PG** |
| API en Docker no llega a BD | `localhost` dentro del contenedor | `host.docker.internal` |
| Login OK en UI pero API falla | `NEXT_PUBLIC_API_URL` mal | Apuntar a IP:puerto real de la API |
| CORS error en navegador | Origen no listado | Añadir URL del frontend a `CORS_ORIGINS` |
| Init OK pero API 401 | API usa `sicc_api`, init con admin | Usuarios creados en `04_usuarios_sql.sql` |

---

## Seguridad

- No subir `.env` a Git (ver `.gitignore`).
- En producción: contraseñas fuertes, usuarios con mínimos privilegios (`sicc_api`, `sicc_fdw_ro`).
- Restringir acceso por firewall/VPN; no exponer 5432/3306 a Internet sin necesidad.
- Rotar credenciales si alguna vez se filtraron en un commit.

---

## Referencias

- BDs e init: [database/README.md](../database/README.md)
- API: [backend/README.md](../backend/README.md)
- UI: [frontend/README.md](../frontend/README.md)
- Arquitectura: [system_architecture.md](system_architecture.md)
