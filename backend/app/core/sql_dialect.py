"""Helpers de nombres de tabla/columna según motor."""

from typing import Literal

DialectKind = Literal["postgres", "mysql"]

# Mapeo lógico → nombre físico por motor
TABLES: dict[str, dict[DialectKind, str]] = {
    "cat_Sedes": {"postgres": "cat_sedes", "mysql": "cat_Sedes"},
    "Roles": {"postgres": "roles", "mysql": "Roles"},
    "Permisos": {"postgres": "permisos", "mysql": "Permisos"},
    "Roles_Permisos": {"postgres": "roles_permisos", "mysql": "Roles_Permisos"},
    "cat_Estados": {"postgres": "cat_estados", "mysql": "cat_Estados"},
    "cat_Prioridades": {"postgres": "cat_prioridades", "mysql": "cat_Prioridades"},
    "cat_Tipos_Incidente": {"postgres": "cat_tipos_incidente", "mysql": "cat_Tipos_Incidente"},
    "Usuarios": {"postgres": "usuarios", "mysql": "Usuarios"},
    "Sesiones": {"postgres": "sesiones", "mysql": "Sesiones"},
    "sync_control": {"postgres": "sync_control", "mysql": "sync_control"},
    "Activos": {"postgres": "activos", "mysql": "Activos"},
    "Incidentes": {"postgres": "incidentes", "mysql": "Incidentes"},
    "Incidentes_Activos": {"postgres": "incidentes_activos", "mysql": "Incidentes_Activos"},
    "Bitacora_Investigacion": {
        "postgres": "bitacora_investigacion",
        "mysql": "Bitacora_Investigacion",
    },
}


def t(logical: str, dialect: DialectKind) -> str:
    return TABLES[logical][dialect]


def q_ident(name: str, dialect: DialectKind) -> str:
    if dialect == "postgres":
        return f'"{name}"'
    return f"`{name}`"


def tq(logical: str, dialect: DialectKind) -> str:
    physical = t(logical, dialect)
    return q_ident(physical, dialect)
