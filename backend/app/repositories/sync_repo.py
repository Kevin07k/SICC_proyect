from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.replicated_tables import ReplicatedTable
from app.core.sql_dialect import tq


# Columnas a sincronizar por tabla lógica (sin omitir PK)
SYNC_COLUMNS: dict[str, list[str]] = {
    "cat_Sedes": [
        "id_sede",
        "nombre_sede",
        "nivel_criticidad",
        "created_at",
        "updated_at",
        "eliminado",
    ],
    "Roles": ["id_rol", "nombre", "descripcion", "created_at", "updated_at"],
    "Permisos": ["id_permiso", "nombre", "codigo", "descripcion", "created_at", "updated_at"],
    "Roles_Permisos": ["id_rol", "id_permiso"],
    "cat_Estados": ["id_estado", "nombre", "created_at", "updated_at", "eliminado"],
    "cat_Prioridades": [
        "id_prioridad",
        "nivel",
        "valor_orden",
        "created_at",
        "updated_at",
        "eliminado",
    ],
    "cat_Tipos_Incidente": [
        "id_tipo",
        "nombre",
        "descripcion",
        "created_at",
        "updated_at",
        "eliminado",
    ],
    "Usuarios": [
        "uuid",
        "email",
        "password_hash",
        "nombre_completo",
        "id_sede",
        "id_rol",
        "activo",
        "created_at",
        "updated_at",
    ],
    "sync_control": ["id", "last_sync", "nodo_origen"],
}


class SyncRepository:
    def get_last_sync(self, conn: Connection, dialect: str) -> datetime:
        sql = text(f"SELECT last_sync FROM {tq('sync_control', dialect)} WHERE id = 1")
        row = conn.execute(sql).fetchone()
        if row:
            return row[0]
        return datetime(1970, 1, 1)

    def set_last_sync(self, conn: Connection, dialect: str, ts: datetime, nodo: str) -> None:
        if dialect == "postgres":
            sql = text(
                f"""
                UPDATE {tq('sync_control', dialect)}
                SET last_sync = :ts, nodo_origen = :nodo
                WHERE id = 1
                """
            )
        else:
            sql = text(
                f"""
                UPDATE {tq('sync_control', dialect)}
                SET last_sync = :ts, nodo_origen = :nodo
                WHERE id = 1
                """
            )
        conn.execute(sql, {"ts": ts, "nodo": nodo})
        conn.commit()

    def fetch_changes(
        self,
        conn: Connection,
        dialect: str,
        table: ReplicatedTable,
        since: datetime,
    ) -> list[dict[str, Any]]:
        cols = SYNC_COLUMNS[table.logical_name]
        col_list = ", ".join(cols)
        tbl = tq(table.logical_name, dialect)
        if table.skip_updated_at_filter:
            sql = text(f"SELECT {col_list} FROM {tbl}")
            rows = conn.execute(sql).fetchall()
        else:
            sql = text(f"SELECT {col_list} FROM {tbl} WHERE updated_at > :since")
            rows = conn.execute(sql, {"since": since}).fetchall()
        return [dict(zip(cols, row, strict=True)) for row in rows]

    def fetch_by_pk(
        self,
        conn: Connection,
        dialect: str,
        table: ReplicatedTable,
        pk_values: dict[str, Any],
    ) -> dict[str, Any] | None:
        cols = SYNC_COLUMNS[table.logical_name]
        col_list = ", ".join(cols)
        tbl = tq(table.logical_name, dialect)
        where = " AND ".join(f"{k} = :{k}" for k in table.pk_columns)
        params = {k: pk_values[k] for k in table.pk_columns}
        if "uuid" in params:
            params["uuid"] = str(params["uuid"])
        sql = text(f"SELECT {col_list} FROM {tbl} WHERE {where}")
        row = conn.execute(sql, params).fetchone()
        if not row:
            return None
        return dict(zip(cols, row, strict=True))

    def fetch_by_email(
        self, conn: Connection, dialect: str, email: str
    ) -> dict[str, Any] | None:
        cols = SYNC_COLUMNS["Usuarios"]
        col_list = ", ".join(cols)
        tbl = tq("Usuarios", dialect)
        sql = text(f"SELECT {col_list} FROM {tbl} WHERE email = :email")
        row = conn.execute(sql, {"email": email}).fetchone()
        if not row:
            return None
        return dict(zip(cols, row, strict=True))

    def upsert_row(
        self,
        conn: Connection,
        dialect: str,
        table: ReplicatedTable,
        row: dict[str, Any],
    ) -> None:
        cols = SYNC_COLUMNS[table.logical_name]
        tbl = tq(table.logical_name, dialect)
        if table.logical_name == "Roles_Permisos":
            if dialect == "postgres":
                sql = text(
                    f"""
                    INSERT INTO {tbl} (id_rol, id_permiso) VALUES (:id_rol, :id_permiso)
                    ON CONFLICT (id_rol, id_permiso) DO NOTHING
                    """
                )
            else:
                sql = text(
                    f"""
                    INSERT IGNORE INTO {tbl} (id_rol, id_permiso)
                    VALUES (:id_rol, :id_permiso)
                    """
                )
            conn.execute(sql, row)
            conn.commit()
            return

        pk_cols = table.pk_columns
        non_pk = [c for c in cols if c not in pk_cols]
        if dialect == "postgres":
            row = dict(row)
            if table.logical_name == "Usuarios":
                row["uuid"] = str(row["uuid"])
            if "eliminado" in row and not isinstance(row["eliminado"], bool):
                row["eliminado"] = bool(row["eliminado"])
            if "activo" in row and not isinstance(row["activo"], bool):
                row["activo"] = bool(row["activo"])
            placeholders = ", ".join(f":{c}" for c in cols)
            updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in non_pk)
            pk = ", ".join(pk_cols)
            if table.logical_name == "Usuarios":
                conflict_col = "email"
            else:
                conflict_col = pk
            sql = text(
                f"""
                INSERT INTO {tbl} ({", ".join(cols)})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_col}) DO UPDATE SET {updates}
                """
            )
        else:
            row = dict(row)
            if table.logical_name == "sync_control":
                last_sync = row.get("last_sync")
                if isinstance(last_sync, datetime) and last_sync < datetime(1970, 1, 1, 0, 0, 1):
                    row["last_sync"] = datetime(1970, 1, 1, 0, 0, 1)
            if "uuid" in row:
                row["uuid"] = str(row["uuid"])
            if "eliminado" in row and isinstance(row["eliminado"], bool):
                row["eliminado"] = 1 if row["eliminado"] else 0
            if "activo" in row and isinstance(row["activo"], bool):
                row["activo"] = 1 if row["activo"] else 0
            placeholders = ", ".join(f":{c}" for c in cols)
            updates = ", ".join(f"{c} = VALUES({c})" for c in non_pk)
            sql = text(
                f"""
                INSERT INTO {tbl} ({", ".join(cols)})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {updates}
                """
            )
        conn.execute(sql, row)
        conn.commit()

    def count_pending(
        self, conn: Connection, dialect: str, table: ReplicatedTable, since: datetime
    ) -> int:
        tbl = tq(table.logical_name, dialect)
        if table.skip_updated_at_filter:
            return 0
        sql = text(f"SELECT COUNT(*) FROM {tbl} WHERE updated_at > :since")
        return int(conn.execute(sql, {"since": since}).scalar() or 0)
