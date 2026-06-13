# Requerimientos

## Objetivo del sistema
El sistema tiene como objetivo gestionar incidentes de ciberseguridad en múltiples sedes distribuidas utilizando una arquitectura heterogénea basada en PostgreSQL y MySQL, permitiendo administración centralizada, control de permisos y distribución lógica de datos.
## Problemas que resuelve
Actualmente las sedes manejan incidentes y activos de forma aislada, dificultando la auditoría, trazabilidad y administración global de eventos de ciberseguridad. El sistema permitirá centralizar autenticación y control mientras mantiene operaciones distribuidas por sede.

## Funcionalidades principales

| ID    | Funcionalidad                 |
| ----- | ------------------------------ |
| RF-01 | Login (sesiones locales)       |
| RF-02 | Gestión usuarios               |
| RF-03 | Gestión sedes                  |
| RF-04 | Registrar incidentes           |
| RF-05 | Gestión activos                |
| RF-06 | Cambio de sede del usuario     |
| RF-07 | Auditoría                      |
| RF-08 | RBAC                           |
| RF-09 | Sincronización bidireccional (solo metadata) |
| RF-10 | Traslado de activo entre sedes (FastAPI)     |
| RF-11 | Evidencias, timeline y telemetría en MongoDB por sede (vía FastAPI) |


## Reglas de negocio

| Código | Regla                                |
| ------ | ------------------------------------- |
| RN-01  | Un activo tiene UUID global (conservado en traslado) |
| RN-02  | Un incidente pertenece a una sede y solo existe en su BD |
| RN-03  | Los usuarios solo ven su sede         |
| RN-04  | El historial NO se elimina (traslado = baja lógica en origen) |
| RN-05  | Cambio de sede de activo no genera nuevo UUID |
| RN-06  | Sede autentica usuarios localmente    |
| RN-07  | Metadata replicada sincronizable con LWW via /sync/manual |
| RN-08  | Activos NO se replican; son locales por sede |
| RN-09  | Traslado de activo: FastAPI desactiva en origen e inserta en destino |
| RN-10  | Documentos Mongo son locales por sede; referencian UUIDs SQL de la misma sede |
| RN-11  | MongoDB no participa en sync LWW; no hay réplica de documentos entre sedes |

## Requisitos NO funcionales

| Código | Requisito                   |
| ------ | --------------------------- |
| RNF-01 | Soportar PostgreSQL y MySQL |
| RNF-02 | Soportar múltiples sedes    |
| RNF-03 | Consultas optimizadas       |
| RNF-04 | Integridad distribuida      |
| RNF-05 | MongoDB por sede para datos semi-estructurados complementarios al SQL |
