"""Tablas de metadata replicadas (sync LWW). Sin Sesiones en práctica local."""

from dataclasses import dataclass
from typing import Literal

DialectKind = Literal["postgres", "mysql"]


@dataclass(frozen=True)
class ReplicatedTable:
    logical_name: str
    pg_name: str
    mysql_name: str
    pk_columns: tuple[str, ...]
    has_eliminado: bool = False
    skip_updated_at_filter: bool = False


REPLICATED_TABLES: list[ReplicatedTable] = [
    ReplicatedTable("cat_Sedes", "cat_sedes", "cat_Sedes", ("id_sede",), True),
    ReplicatedTable("Roles", "roles", "Roles", ("id_rol",)),
    ReplicatedTable("Permisos", "permisos", "Permisos", ("id_permiso",)),
    ReplicatedTable(
        "Roles_Permisos",
        "roles_permisos",
        "Roles_Permisos",
        ("id_rol", "id_permiso"),
        skip_updated_at_filter=True,
    ),
    ReplicatedTable("cat_Estados", "cat_estados", "cat_Estados", ("id_estado",), True),
    ReplicatedTable("cat_Prioridades", "cat_prioridades", "cat_Prioridades", ("id_prioridad",), True),
    ReplicatedTable(
        "cat_Tipos_Incidente",
        "cat_tipos_incidente",
        "cat_Tipos_Incidente",
        ("id_tipo",),
        True,
    ),
    ReplicatedTable("Usuarios", "usuarios", "Usuarios", ("uuid",)),
    ReplicatedTable("sync_control", "sync_control", "sync_control", ("id",), skip_updated_at_filter=True),
]


def table_name(table: ReplicatedTable, dialect: DialectKind) -> str:
    return table.pg_name if dialect == "postgres" else table.mysql_name
