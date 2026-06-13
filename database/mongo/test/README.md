# MongoDB — test / defensa

Scripts mongosh sin lógica JS. Requiere seed demo (`02_seed.js` o `apply_mongo_demo_seed.py`).

## Conectar

```bash
# Santa Cruz
mongosh "mongodb://sicc_mongo_api:sicc_mongo_api_pass_2024@localhost:27017/sicc_sc?authSource=admin"

# Cochabamba
mongosh "mongodb://sicc_mongo_api:sicc_mongo_api_pass_2024@localhost:27018/sicc_cb?authSource=admin"
```

## Ejecutar

```bash
cd database

mongosh "mongodb://sicc_mongo_api:sicc_mongo_api_pass_2024@localhost:27017/sicc_sc?authSource=admin" \
  --file mongo/test/01_muestra_datos_demo.js

mongosh "mongodb://sicc_mongo_api:sicc_mongo_api_pass_2024@localhost:27017/sicc_sc?authSource=admin" \
  --file mongo/test/02_consultas_api_y_indices.js
```

## 2 casos para la presentación (`01_muestra_datos_demo.js`)

| Caso | UUID | Qué es | Web |
|------|------|--------|-----|
| 1 — Phishing | `a1000001-0001-4000-8000-000000000001` | IoCs + log + timeline | `/incidentes/a1000001-0001-4000-8000-000000000001` |
| 2 — Escaneo vuln. alta | `b1000001-0001-4000-8000-000000000003` | Telemetría sc-ws-01 | `/activos/b1000001-0001-4000-8000-000000000003` |

## Archivos

- `01_muestra_datos_demo.js` — consultar los 2 casos del seed (phishing + activo vuln. alta)
- `02_consultas_api_y_indices.js` — finds de la API + explain de índices
- `03_insertar_casos_defensa.js` — **2 inserts listos** para ejecutar tú en la defensa (no inserta solo)

### Inserts en defensa (`03_insertar_casos_defensa.js`)

| # | Dónde | UUID en SQL/Mongo | Qué inserta |
|---|-------|-------------------|-------------|
| 1 | Incidente phishing | `a1000001-0001-4000-8000-000000000001` | Evidencia IoC (IP `203.0.113.99` + dominio) |
| 2 | Activo sc-ws-01 | `b1000001-0001-4000-8000-000000000003` | Telemetría con hallazgo severidad `alta` |

Descomenta el bloque en mongosh, pega y ejecuta. Luego abre la web o haz `find` para mostrar el documento nuevo.
