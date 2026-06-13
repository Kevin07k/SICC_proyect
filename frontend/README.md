# Frontend SICC

Interfaz **Next.js 15** + **React** (tema oscuro). Consume **solo** la API REST; no hay conexión directa a PostgreSQL ni MySQL.

Guía global del proyecto: [README.md](../README.md) en la raíz.

---

## Requisitos

- Node.js **20+**
- API FastAPI en ejecución → [backend/README.md](../backend/README.md)
- BDs inicializadas → [database/README.md](../database/README.md)

---

## Configuración

```bash
cd frontend
cp .env.local.example .env.local
npm install
```

| Variable | Uso |
|----------|-----|
| `NEXT_PUBLIC_API_URL` | URL base de la API (ej. `http://localhost:8000`) |
| `NEXT_PUBLIC_ENABLE_DEV_SWITCHER` | `true` → `/dev/switch` y mini-switcher en sidebar |

**Importante:** `NEXT_PUBLIC_*` se incluye en el bundle del navegador. Si la API está en otra máquina o puerto, cambia esta variable y reinicia `npm run dev` (o reconstruye la imagen Docker).

---

## Desarrollo

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000).

Tras cambiar `package.json`:

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Conectividad y red

El frontend **solo** habla con la API por HTTP. No configura hosts de base de datos.

| Escenario | `NEXT_PUBLIC_API_URL` |
|-----------|------------------------|
| Todo en localhost | `http://localhost:8000` |
| API en otra PC de la red | `http://<IP-api>:8000` |
| API detrás de proxy / HTTPS | URL pública del backend |

En el **backend**, añade el origen del frontend a `CORS_ORIGINS` (ver [backend/README.md](../backend/README.md)).

Con Docker en la raíz del repo, la URL suele seguir siendo la del **host** donde publicas el puerto 8000, no el nombre interno del contenedor.

Manual completo: [**docs/conectividad_red.md**](../docs/conectividad_red.md).

---

## Usuarios de prueba (seeds)

Tras `init_databases.py`:

| Email | Contraseña | Rol | Sede |
|-------|------------|-----|------|
| `admin@sicc.com` | `admin123` | Administrador | Santa Cruz |
| `analista.sc@test.sicc` | `test123` | Analista | Santa Cruz |
| `analista.cb@test.sicc` | `test123` | Analista | Cochabamba |
| `dba@test.sicc` | `test123` | DBA | Santa Cruz |

**Acceso rápido:** [http://localhost:3000/dev/switch](http://localhost:3000/dev/switch) (requiere `NEXT_PUBLIC_ENABLE_DEV_SWITCHER=true`).

---

## Docker

Solo frontend:

```bash
docker compose up --build
```

Stack completo (API + UI) desde la raíz del repo:

```bash
cd ..
docker compose up --build
```

Asegúrate de que `NEXT_PUBLIC_API_URL` apunte a donde el **navegador** puede alcanzar la API (normalmente `http://localhost:8000`).

---

## Pruebas

```bash
npm run lint
npm run build
npm run smoke   # requiere API levantada
```

---

## Módulos

| Módulo | Descripción |
|--------|-------------|
| Dashboard | KPIs y gráficas desde la API |
| Incidentes | CRUD, bitácora, filtros en cliente |
| Activos | CRUD y traslado entre sedes |
| Usuarios | Administración de metadata |
| Sync | `/admin/sync` — LWW de tablas replicadas |

Auth: cookie `sicc_uuid` + header `X-Usuario-UUID` hacia la API (sin JWT).

---

## Solución de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| Pantalla vacía / errores de red | `NEXT_PUBLIC_API_URL`, API en `/health` |
| CORS en consola del navegador | `CORS_ORIGINS` en `backend/.env` |
| Login falla | BDs e init; credenciales en tabla anterior |

---

## Documentación relacionada

- [README global](../README.md)
- [Backend / API](../backend/README.md)
- [Bases de datos](../database/README.md)
- [Manual de conectividad y red](../docs/conectividad_red.md)
