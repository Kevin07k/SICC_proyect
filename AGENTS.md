# SICC — Instrucciones para agentes (resumen)

Objetivo: mantener el contexto **mínimo** para no gastar tokens. Detalle en `README.md` y READMEs por carpeta.

Idioma del proyecto: **español** (docs/commits/mensajes) salvo que pidan lo contrario.

---

## TL;DR (arquitectura)

- **PostgreSQL** (Santa Cruz): datos locales + FDW solo lectura hacia MySQL.
- **MySQL** (Cochabamba): datos locales.
- **MongoDB** (una instancia por sede): evidencias, timeline y telemetría; local, sin sync LWW.
- **`backend/`**: FastAPI **solo REST JSON** (sync metadata, traslado de activos, CRUD por sede, routing SQL+Mongo).
- **`frontend/`**: Next.js/React; consume API; **sin acceso directo** a BDs.

---

## Reglas no negociables (RN)

- **RN-02**: Incidentes **solo** en la BD de su sede.
- **RN-04**: No borrar historial; usar baja lógica (`eliminado`).
- **RN-07**: Sync LWW **solo** metadata replicada (`updated_at`).
- **RN-08**: Activos son locales; **no** sync bidireccional.
- **RN-09**: Traslado de activos **solo** vía API: `POST /activos/{uuid}/transferir` (mismo UUID).

Además:
- **Sin JWT**: auth por **sesiones en BD** (`Sesiones`).
- No poner lógica de sync/traslado/RBAC en el frontend.

---

## ¿Qué leer? (mínimo)

- Arquitectura/reglas: `docs/system_architecture.md`, `docs/system_requirements.md`
- Red y hosts (BD remota, Docker): `docs/conectividad_red.md`
- Diagramas: `docs/arquitectura.mmd`, `docs/distribucion_datos.mmd`, `docs/mongo_modelo_documentos.mmd`, `docs/er_*.mmd`

---

## Comandos (ver READMEs por capa)

- Proyecto: `README.md`
- BDs: `database/README.md`
- API: `backend/README.md`
- UI: `frontend/README.md`

**Docker BDs:** `database/docker-compose.yml` levanta **PG, MySQL y Mongo** (`postgres-central`, `mysql-secundaria`, `mongo-santa-cruz`, `mongo-cochabamba`). `build postgres-central` solo construye la imagen PG; `up -d` arranca los cuatro. No inventar rutas bajo `docs/agent/` — no existen; usar `docs/*.md` y READMEs por carpeta.
