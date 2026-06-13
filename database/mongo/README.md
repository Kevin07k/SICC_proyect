# MongoDB — Documentos por sede

Una instancia MongoDB **por sede**: Santa Cruz (`sicc_sc`) y Cochabamba (`sicc_cb`). Complementa PostgreSQL/MySQL con evidencias, timeline y telemetría vinculadas por UUID.

Guía general (Docker, credenciales): [../README.md](../README.md).

---

## ¿Qué hace cada archivo?

| Carpeta / archivo | Sede | Descripción |
|-------------------|------|-------------|
| `santa_cruz/01_init.js` | Santa Cruz | Colecciones, índices y usuario `sicc_mongo_api` en `sicc_sc`. |
| `santa_cruz/02_seed.js` | Santa Cruz | **5 incidentes + 5 activos** demo con evidencias, timeline y telemetría. |
| `cochabamba/01_init.js` | Cochabamba | Colecciones, índices y usuario `sicc_mongo_api` en `sicc_cb`. |
| `cochabamba/02_seed.js` | Cochabamba | **5 incidentes + 5 activos** demo (misma cobertura que SC). |
| [`test/`](test/) | Ambas | Scripts mongosh de muestra y consultas para defensa (sin lógica JS). |

---

## Colecciones (ambas sedes)

| Colección | Vinculación SQL | Uso |
|-----------|-----------------|-----|
| `evidencias_incidente` | `incidente_uuid` | IoCs, logs, adjuntos |
| `timeline_eventos` | `incidente_uuid` | Eventos de investigación |
| `telemetria_activo` | `activo_uuid` | Escaneos y snapshots |

---

## Inicio rápido

Desde `database/`:

```bash
docker compose up -d
```

Servicios Mongo:

| Servicio compose | Contenedor | BD | Puerto host |
|------------------|------------|-----|-------------|
| `mongo-santa-cruz` | `sicc-mongo-santa-cruz` | `sicc_sc` | `27017` |
| `mongo-cochabamba` | `sicc-mongo-cochabamba` | `sicc_cb` | `27018` |

Los scripts `.js` en `/docker-entrypoint-initdb.d` solo corren en el **primer** arranque con volumen nuevo.

Para **completar** el seed tras actualizar `02_seed.js` (sin borrar volúmenes):

```bash
cd database
.venv-init/bin/python apply_mongo_demo_seed.py
```

Reset total Mongo + SQL:

```bash
docker compose down -v && docker compose up -d
.venv-init/bin/python init_databases.py
.venv-init/bin/python apply_demo_seed.py
```

---

## Documentos por sede (seed completo)

| Colección | Por sede | Notas |
|-----------|----------|--------|
| `evidencias_incidente` | ≥ 5 | Al menos 1 por incidente demo |
| `timeline_eventos` | ≥ 5 | Al menos 1 por incidente demo |
| `telemetria_activo` | 5 | 1 por activo demo |
| **Total aprox.** | **~15–20** | SC + CB ≈ 30–40 docs en el sistema |

---

## Conexión manual (desde el host)

Santa Cruz:

```bash
mongosh "mongodb://sicc_mongo_api:sicc_mongo_api_pass_2024@localhost:27017/sicc_sc?authSource=admin"
```

Cochabamba:

```bash
mongosh "mongodb://sicc_mongo_api:sicc_mongo_api_pass_2024@localhost:27018/sicc_cb?authSource=admin"
```

Consultas de ejemplo:

```javascript
db.evidencias_incidente.find({ incidente_uuid: 'a1000001-0001-4000-8000-000000000001' })
db.timeline_eventos.find({ incidente_uuid: 'a1000001-0001-4000-8000-000000000002' }).sort({ created_at: 1 })
db.telemetria_activo.find({ 'hallazgos.severidad': 'alta' })
```

---

## Credenciales por defecto

| Uso | User | Password |
|-----|------|----------|
| Bootstrap (root, init) | `sicc_mongo_admin` | `sicc_mongo_pass_2024` |
| API (futuro) | `sicc_mongo_api` | `sicc_mongo_api_pass_2024` |

Variables en `database/.env.example` y `backend/.env.example`.

---

## Documentación del proyecto

- [Arquitectura MongoDB](../../docs/system_architecture.md)
- [Modelo documental](../../docs/mongo_modelo_documentos.mmd)
