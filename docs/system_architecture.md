# System Architecture

## Arquitectura General

El sistema implementa una arquitectura distribuida heterogénea basada en múltiples motores de bases de datos con responsabilidades parcialmente autónomas.

La arquitectura está compuesta por:

- un nodo PostgreSQL correspondiente a la sede central,
- un nodo MySQL correspondiente a una sede secundaria,
- un nodo MongoDB por sede (Santa Cruz y Cochabamba) para datos documentales semi-estructurados,
- un backend FastAPI encargado de coordinación, validación lógica, autenticación y routing distribuido.

Cada nodo mantiene autonomía operacional sobre sus propios datos operacionales mientras que los datos de metadata (usuarios, sesiones, catálogos) se replican bidireccionalmente para permitir operación independiente incluso ante fallos de conectividad.

---

## Objetivo Arquitectónico

La arquitectura busca garantizar:

- distribución de datos,
- autonomía parcial de nodos,
- tolerancia a fallos,
- separación de responsabilidades,
- soporte heterogéneo multi-motor,
- consultas distribuidas,
- sincronización controlada,
- escalabilidad futura,
- operación autónoma por sede incluso con nodo central caído.

---

## Arquitectura Distribuida

El sistema se basa en un modelo distribuido híbrido donde cada nodo mantiene ownership de sus datos operacionales y una copia replicada de la metadata del sistema.

---

## PostgreSQL — Nodo Central

PostgreSQL representa la sede central del sistema y además funciona como coordinador global.

## Responsabilidades

- gestión operacional de la sede central,
- almacenamiento de incidentes locales,
- almacenamiento de activos locales,
- bitácoras locales,
- generación de reportes globales,
- analytics,
- consultas federadas hacia MySQL,
- coordinación distribuida,
- almacenamiento de usuarios + sesiones (disponible para autenticación local),
- replicación bidireccional de metadata,
- control de sincronización (sync_control).

## Datos Locales (propios de la sede)

- incidentes de sede central,
- activos de sede central,
- bitácoras de sede central.

## Datos Replicados

- usuarios,
- sesiones,
- catálogos (sedes, roles, permisos, estados, prioridades, tipos de incidente),
- sync_control.

---

## MySQL — Nodo Secundario

MySQL representa una sede secundaria autónoma.

## Responsabilidades

- gestión operacional local,
- almacenamiento de incidentes locales,
- almacenamiento de activos locales,
- bitácoras locales,
- operaciones operacionales locales,
- almacenamiento de usuarios + sesiones (disponible para autenticación local),
- replicación bidireccional de metadata,
- control de sincronización (sync_control).

## Datos Locales (propios de la sede)

- incidentes secundarios,
- activos secundarios,
- bitácoras secundarias.

## Datos Replicados

- usuarios,
- sesiones,
- catálogos (sedes, roles, permisos, estados, prioridades, tipos de incidente),
- sync_control.

---

## MongoDB — Nodo documental por sede

Cada sede dispone de **su propia instancia MongoDB**, co-locada con el motor SQL de esa sede. MongoDB **no reemplaza** PostgreSQL ni MySQL: complementa el modelo relacional almacenando información variable, anidada o de alto volumen que encaja mal en tablas normalizadas.

### Responsabilidades

- evidencias e IoCs asociados a incidentes locales,
- línea de tiempo detallada de investigación (eventos con payloads heterogéneos),
- telemetría y hallazgos de escaneo vinculados a activos locales,
- consultas analíticas sobre documentos (agregaciones, filtros por subcampos, arrays).

### Datos locales (propios de la sede)

| Colección | Vinculación SQL | Contenido típico |
|-----------|-----------------|------------------|
| `evidencias_incidente` | `incidente_uuid` | IoCs (hash, IP, dominio), metadatos de capturas, adjuntos, logs parseados |
| `timeline_eventos` | `incidente_uuid`, `autor_uuid` | Eventos de investigación con esquema flexible por `tipo_evento` |
| `telemetria_activo` | `activo_uuid` | Resultados de escaneo, vulnerabilidades, snapshots de configuración |

Cada instancia usa una base dedicada (`sicc_sc` en Santa Cruz, `sicc_cb` en Cochabamba) con las **mismas colecciones** en ambas sedes (homogeneidad de esquema, fragmentación horizontal por sede).

### Qué NO va en MongoDB

- usuarios, sesiones, catálogos → siguen en SQL replicado con LWW,
- incidentes, activos, bitácoras resumidas → siguen en SQL como fuente de verdad transaccional,
- sync de metadata → **no** pasa por MongoDB.

### Integración con SQL (referencia lógica, no FK cross-engine)

```
Incidente (SQL)  ──incidente_uuid──►  evidencias_incidente (Mongo)
Incidente (SQL)  ──incidente_uuid──►  timeline_eventos (Mongo)
Activo (SQL)     ──activo_uuid──────►  telemetria_activo (Mongo)
Bitacora (SQL)   ──resumen──────────►  timeline_eventos (Mongo, detalle extendido)
```

- FastAPI **valida** que el UUID referenciado exista en el SQL de la **misma sede** antes de insertar en Mongo.
- No hay foreign keys entre motores; la integridad es responsabilidad de la API (igual que en el modelo distribuido SQL actual).
- La bitácora relacional conserva el registro auditable mínimo; Mongo guarda el detalle extenso (payload JSON, arrays de IoCs, etc.).

### Ejemplo de documento — `evidencias_incidente`

```json
{
  "incidente_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "tipo": "ioc",
  "metadata": {
    "fuente": "EDR",
    "severidad_detectada": "alta"
  },
  "iocs": [
    { "tipo": "hash_sha256", "valor": "abc123..." },
    { "tipo": "ip", "valor": "203.0.113.45" }
  ],
  "autor_uuid": "usuario-uuid",
  "created_at": "2026-06-13T10:00:00Z",
  "eliminado": false
}
```

### Routing FastAPI (diseño, sin implementar aún)

| Operación | Destino |
|-----------|---------|
| CRUD incidente/activo/bitácora SQL | PostgreSQL (SC) o MySQL (CB) según sede del usuario |
| Alta/consulta evidencias o timeline | MongoDB de la misma sede |
| `POST /sync/manual` | Solo tablas SQL replicadas |
| `POST /activos/{uuid}/transferir` | Solo SQL; telemetría histórica en Mongo **permanece en la sede origen** |
| Reporte global con evidencias | FastAPI consulta ambos Mongo + FDW SQL; agregación en capa API |

### Consistencia y traslado de activos

- **RN-02** aplica: los documentos de un incidente viven en el Mongo de la sede donde está el incidente SQL.
- En traslado de activo (RN-09): el activo se mueve en SQL; la `telemetria_activo` histórica **no se migra** (coherente con RN-04). Nuevos escaneos en la sede destino usan el mismo `activo_uuid`.
- **Sin sync LWW** entre instancias Mongo: no hay réplica bidireccional de documentos entre sedes.

### Índices recomendados (diseño)

| Colección | Índice | Justificación |
|-----------|--------|---------------|
| `evidencias_incidente` | `{ incidente_uuid: 1, created_at: -1 }` | Listar evidencias de un incidente ordenadas |
| `evidencias_incidente` | `{ "iocs.valor": 1 }` | Búsqueda por IoC concreto |
| `timeline_eventos` | `{ incidente_uuid: 1, created_at: 1 }` | Timeline cronológico |
| `telemetria_activo` | `{ activo_uuid: 1, captured_at: -1 }` | Historial de escaneos por activo |

### Diagrama

Ver `docs/mongo_modelo_documentos.mmd` para el modelo documental y referencias UUID.

---

## Ownership de Datos

Cada nodo es responsable únicamente de sus propios datos operacionales.

Esto significa que:

- PostgreSQL controla los incidentes y activos de la sede central,
- MySQL controla los incidentes y activos de la sede secundaria,
- MongoDB Santa Cruz almacena documentos vinculados a entidades SQL de Santa Cruz,
- MongoDB Cochabamba almacena documentos vinculados a entidades SQL de Cochabamba.

No existe modificación directa de datos operacionales entre nodos, salvo el **traslado explícito de activos** orquestado por FastAPI (ver sección más abajo). Los documentos Mongo **no se replican** entre sedes.

Los datos replicados (usuarios, sesiones, catálogos) existen en ambos nodos y pueden ser modificados en cualquiera de ellos, resolviéndose conflictos mediante la estrategia last-write-wins.

**Importante:** la sincronización bidireccional con last-write-wins **no aplica** a incidentes, activos, bitácoras ni `Incidentes_Activos`. Esas entidades son locales por sede.

---

## Datos Replicados

Los siguientes datos críticos del sistema existen replicados entre PostgreSQL y MySQL.

Esto permite mantener operaciones básicas incluso ante fallos parciales de conectividad.

## Entidades Replicadas

- sedes,
- usuarios,
- sesiones,
- roles,
- permisos,
- estados,
- prioridades,
- tipos de incidente,
- sync_control.

---

## Estrategia de Sincronización Bidireccional

### Principio

Ambos nodos mantienen una copia completa de los datos replicados (usuarios, sesiones, catálogos). Cualquier nodo puede crear, modificar o eliminar estas entidades mientras opera de forma autónoma.

Cuando ambos nodos están en línea, los cambios se sincronizan bidireccionalmente.

### Estrategia de Resolución: Last-Write-Wins por Timestamp

Cada fila replicada tiene un campo `updated_at` de tipo TIMESTAMP. Al sincronizar, se comparan los timestamps de ambas versiones y la más reciente prevalece.

```
Si PG.updated_at > MySQL.updated_at  →  se actualiza MySQL
Si MySQL.updated_at > PG.updated_at  →  se actualiza PG
Si están iguales                      →  no se hace nada
Si existe solo en un nodo            →  se crea en el otro
Si fue eliminado en un nodo          →  se elimina en el otro
  (si el delete tiene timestamp más reciente)
```

### Tabla de Control: sync_control

Ambos nodos tienen una tabla `sync_control` con una sola fila que registra:

```sql
CREATE TABLE sync_control (
    id INTEGER PRIMARY KEY DEFAULT 1,
    last_sync TIMESTAMP NOT NULL,
    nodo_origen VARCHAR(20) NOT NULL
);
```

`last_sync` indica desde qué timestamp se sincronizó la última vez. En cada sincronización, cada nodo envía solo los registros con `updated_at > last_sync`.

### Flujo de Sincronización

```
1. FastAPI consulta sync_control.last_sync en ambos nodos
2. Usa el last_sync más antiguo como punto de partida
3. Consulta en PostgreSQL: "SELECT * FROM usuarios WHERE updated_at > last_sync"
4. Consulta en MySQL: "SELECT * FROM usuarios WHERE updated_at > last_sync"
5. Para cada registro recibido:
   a. Si existe en ambos → comparar updated_at, el más reciente gana
   b. Si solo en uno → insertar en el otro
   c. Si updated_at es igual → omitir
6. Aplica los cambios en el nodo destino mediante FastAPI
7. Actualiza sync_control.last_sync en ambos nodos con NOW()
```

### Disparo de la Sincronización

La sincronización se dispara mediante:

- **Endpoint manual:** `POST /sync/manual` — un administrador (o el evaluador) puede llamarlo en cualquier momento para probar la consistencia.
- **Endpoint /sync/status:** `GET /sync/status` — muestra el estado actual de sincronización y posibles diferencias entre nodos.

### Ejemplo de Operación ante Falla

```
1. PostgreSQL se desconecta
2. Sede secundaria (MySQL) sigue operando normalmente:
   - Crea un nuevo usuario
   - Modifica un incidente local
3. PostgreSQL se reconecta
4. Administrador llama POST /sync/manual
5. FastAPI detecta que MySQL tiene usuarios con updated_at > last_sync
6. FastAPI replica esos usuarios nuevos a PostgreSQL
7. Ambas bases quedan consistentes
```

> La sincronización solo recorre las tablas replicadas listadas en *Entidades Replicadas*. Los incidentes modificados en el paso 2 **no** se copian al otro nodo.

---

## Traslado de activos entre sedes

Los activos son **datos operacionales locales**: el registro vive en la base de datos de la sede donde se gestiona (PostgreSQL para Santa Cruz, MySQL para Cochabamba). **No** se replican mediante `POST /sync/manual`.

Si un activo debe pasar a otra sede (cambio físico o de responsabilidad operativa), FastAPI ejecuta un **traslado orquestado** — no es sync automático ni last-write-wins.

### Reglas

- El activo conserva el **mismo UUID** en la sede destino.
- En la base **origen**: se marca `eliminado = true` (baja lógica; el historial no se borra físicamente, coherente con RN-04).
- En la base **destino**: se inserta un registro nuevo con el mismo UUID, datos actualizados y `id_sede` apuntando a la sede destino.
- Los vínculos `Incidentes_Activos` previos permanecen en la sede origen; no se migran automáticamente.
- El catálogo `sedes` sí está replicado en ambos nodos, por lo que `id_sede` destino es válido en la BD destino.

### Endpoint

`POST /activos/{uuid}/transferir`

**Cuerpo de ejemplo:**

```json
{
  "sede_destino_id": 2,
  "motivo": "Equipo reasignado a sede Cochabamba"
}
```

### Flujo (FastAPI)

```
1. Validar sesión, permisos y que el activo existe en la BD origen (no eliminado)
2. Validar que sede_destino_id existe en cat_Sedes (réplica en ambos nodos)
3. Validar que origen ≠ destino y que origen/destino mapean a PostgreSQL o MySQL según corresponda
4. Verificar que no hay incidentes abiertos vinculados al activo (opcional, regla de negocio)
5. UPDATE en BD origen: eliminado = true, updated_at = NOW()
6. INSERT en BD destino: mismo uuid, campos del activo, id_sede = sede_destino_id, eliminado = false
7. Registrar evento en auditoría / bitácora si aplica
8. Responder 200 con resumen { uuid, sede_origen, sede_destino, nodo_origen, nodo_destino }
```

### Cuándo no usar traslado

- Cambios menores del activo en la **misma** sede: CRUD local normal en la BD de la sede.
- Consultas globales de inventario: usar FDW desde PostgreSQL; no implica copiar filas de activos.

---

## Estrategia de Consultas Distribuidas

PostgreSQL implementa consultas federadas hacia MySQL utilizando mecanismos de integración heterogénea (PostgreSQL FDW).

Esto permite generar reportes globales sin necesidad de replicar completamente los datos operacionales.

Las consultas distribuidas son utilizadas únicamente para:

- reportes globales,
- dashboards,
- analytics,
- consolidación de información.

---

## Estrategia de Reportes Globales

Los reportes globales son construidos desde PostgreSQL combinando:

- datos locales de la sede central,
- datos federados consultados desde MySQL.

Esto permite mantener separación operacional mientras se habilita consolidación analítica global.

---

## Integridad Referencial Distribuida

Las foreign keys dentro de un mismo motor de base de datos se implementan normalmente.

Las relaciones entre entidades replicadas en PostgreSQL y MySQL son validadas mediante lógica implementada en FastAPI.

---

## Estrategia de Identificadores

El sistema utiliza UUID como identificador global distribuido para entidades críticas (usuarios, incidentes, activos).

Esto permite:

- evitar colisiones entre nodos,
- soportar creación distribuida,
- mantener unicidad global,
- facilitar sincronización bidireccional.

---

## Estrategia de Consistencia

La arquitectura utiliza consistencia eventual para la sincronización bidireccional de metadata.

Los datos operacionales permanecen gobernados localmente por cada nodo sin replicación entre sedes.

---

## Tolerancia a Fallos

Cada nodo puede continuar operando parcialmente incluso ante fallos del otro nodo.

## Si PostgreSQL falla

MySQL puede continuar:

- gestionando incidentes locales,
- gestionando activos locales,
- realizando operaciones operacionales,
- **autenticando usuarios localmente** (tiene copia de usuarios + sesiones),
- registrando cambios en metadata (usuarios, catálogos).

Al reconectarse, los cambios hechos durante la caída se sincronizan a PostgreSQL.

## Si MySQL falla

PostgreSQL puede continuar:

- gestionando operaciones de sede central,
- generando reportes parciales,
- realizando operaciones analíticas locales,
- **autenticando usuarios localmente**,
- registrando cambios en metadata.

Al reconectarse, los cambios hechos durante la caída se sincronizan a MySQL.

---

## Backend FastAPI

FastAPI actúa como:

- gateway central,
- coordinador distribuido,
- administrador de autenticación (sin JWT, usando sesiones locales),
- validador lógico,
- administrador de integridad distribuida,
- sistema de routing multi-motor,
- **mediador de sincronización bidireccional** (solo metadata replicada),
- **orquestador de traslado de activos** entre nodos,
- **router multi-motor SQL + NoSQL** hacia el Mongo de la sede correspondiente,
- expositor de endpoints de administración (/sync/manual).

### Endpoints principales

| Endpoint | Descripción |
|----------|-------------|
| POST /auth/login | Autentica contra la BD de la sede correspondiente |
| POST /sync/manual | Sincroniza **solo** tablas replicadas (LWW por `updated_at`) |
| GET /sync/status | Muestra estado de consistencia de metadata entre nodos |
| POST /activos/{uuid}/transferir | Traslado de activo: desactiva en origen, crea en destino (mismo UUID) |
| CRUD por sede | Operaciones locales según la sede del usuario autenticado |
| CRUD documentos NoSQL | Evidencias, timeline y telemetría en MongoDB de la sede (diseño) |

---

## Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Backend | FastAPI |
| Nodo Central SQL | PostgreSQL (Santa Cruz) |
| Nodo Secundario SQL | MySQL (Cochabamba) |
| Nodo documental por sede | MongoDB (`sicc_sc`, `sicc_cb`) |
| Integración Distribuida | PostgreSQL FDW |
| ORM/SQL | SQLAlchemy Core |
| Autenticación | Sesiones locales (token en BD) |
| Identificadores | UUID |
| Arquitectura | Distribuida Heterogénea |
| Consistencia metadata | Eventual (last-write-wins) |
| Consistencia operacional | Local por sede (sin réplica) |
| Traslado de activos | Orquestado por FastAPI (mismo UUID) |
| Sincronización | Bidireccional manual, solo metadata SQL (vía API) |
| Datos NoSQL | Locales por sede; referencia UUID a SQL; sin réplica entre Mongo |
