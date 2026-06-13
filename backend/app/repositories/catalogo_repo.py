from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


def _eliminado_false(dialect: str) -> str:
    return "FALSE" if dialect == "postgres" else "0"


def _eliminado_true(dialect: str) -> str:
    return "TRUE" if dialect == "postgres" else "1"


class CatalogoRepository:
    def list_sedes(self, conn: Connection, dialect: str) -> list[dict[str, Any]]:
        sql = text(
            f"""
            SELECT id_sede, nombre_sede, nivel_criticidad, eliminado
            FROM {tq("cat_Sedes", dialect)}
            WHERE eliminado = {_eliminado_false(dialect)}
            ORDER BY id_sede
            """
        )
        return [row_to_dict(r) for r in conn.execute(sql).fetchall()]

    def list_estados(self, conn: Connection, dialect: str) -> list[dict[str, Any]]:
        sql = text(
            f"""
            SELECT id_estado, nombre, eliminado
            FROM {tq("cat_Estados", dialect)}
            WHERE eliminado = {_eliminado_false(dialect)}
            ORDER BY id_estado
            """
        )
        return [row_to_dict(r) for r in conn.execute(sql).fetchall()]

    def list_prioridades(self, conn: Connection, dialect: str) -> list[dict[str, Any]]:
        sql = text(
            f"""
            SELECT id_prioridad, nivel, valor_orden, eliminado
            FROM {tq("cat_Prioridades", dialect)}
            WHERE eliminado = {_eliminado_false(dialect)}
            ORDER BY valor_orden
            """
        )
        return [row_to_dict(r) for r in conn.execute(sql).fetchall()]

    def list_tipos(
        self, conn: Connection, dialect: str, *, include_eliminados: bool = False
    ) -> list[dict[str, Any]]:
        where = ""
        if not include_eliminados:
            where = f"WHERE eliminado = {_eliminado_false(dialect)}"
        sql = text(
            f"""
            SELECT id_tipo, nombre, descripcion, eliminado
            FROM {tq("cat_Tipos_Incidente", dialect)}
            {where}
            ORDER BY nombre
            """
        )
        return [row_to_dict(r) for r in conn.execute(sql).fetchall()]

    def get_tipo(self, conn: Connection, dialect: str, id_tipo: int) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT id_tipo, nombre, descripcion, eliminado
            FROM {tq("cat_Tipos_Incidente", dialect)}
            WHERE id_tipo = :id
            """
        )
        row = conn.execute(sql, {"id": id_tipo}).fetchone()
        return row_to_dict(row) if row else None

    def count_incidentes_por_tipo(
        self, conn: Connection, dialect: str, id_tipo: int
    ) -> int:
        elim = _eliminado_false(dialect)
        sql = text(
            f"""
            SELECT COUNT(*) FROM {tq("Incidentes", dialect)}
            WHERE id_tipo = :id_tipo AND eliminado = {elim}
            """
        )
        row = conn.execute(sql, {"id_tipo": id_tipo}).fetchone()
        return int(row[0] or 0) if row else 0

    def create_tipo(
        self, conn: Connection, dialect: str, *, nombre: str, descripcion: str | None
    ) -> dict[str, Any]:
        if dialect == "postgres":
            sql = text(
                f"""
                INSERT INTO {tq("cat_Tipos_Incidente", dialect)} (nombre, descripcion)
                VALUES (:nombre, :descripcion)
                RETURNING id_tipo, nombre, descripcion, eliminado
                """
            )
            row = conn.execute(sql, {"nombre": nombre, "descripcion": descripcion}).fetchone()
            return row_to_dict(row)

        sql = text(
            f"""
            INSERT INTO {tq("cat_Tipos_Incidente", dialect)} (nombre, descripcion)
            VALUES (:nombre, :descripcion)
            """
        )
        result = conn.execute(sql, {"nombre": nombre, "descripcion": descripcion})
        id_tipo = result.lastrowid
        row = self.get_tipo(conn, dialect, int(id_tipo))
        return row or {}

    def update_tipo(
        self,
        conn: Connection,
        dialect: str,
        id_tipo: int,
        fields: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not fields:
            return self.get_tipo(conn, dialect, id_tipo)
        sets = ", ".join(f"{k} = :{k}" for k in fields)
        params = {**fields, "id": id_tipo}
        if dialect == "postgres":
            sql = text(
                f"""
                UPDATE {tq("cat_Tipos_Incidente", dialect)}
                SET {sets}, updated_at = CURRENT_TIMESTAMP
                WHERE id_tipo = :id
                RETURNING id_tipo, nombre, descripcion, eliminado
                """
            )
            row = conn.execute(sql, params).fetchone()
            return row_to_dict(row) if row else None

        sql = text(
            f"""
            UPDATE {tq("cat_Tipos_Incidente", dialect)}
            SET {sets}
            WHERE id_tipo = :id
            """
        )
        conn.execute(sql, params)
        return self.get_tipo(conn, dialect, id_tipo)

    def soft_delete_tipo(self, conn: Connection, dialect: str, id_tipo: int) -> bool:
        elim = _eliminado_true(dialect)
        if dialect == "postgres":
            sql = text(
                f"""
                UPDATE {tq("cat_Tipos_Incidente", dialect)}
                SET eliminado = {elim}, updated_at = CURRENT_TIMESTAMP
                WHERE id_tipo = :id AND eliminado = {_eliminado_false(dialect)}
                RETURNING id_tipo
                """
            )
            row = conn.execute(sql, {"id": id_tipo}).fetchone()
            return row is not None

        sql = text(
            f"""
            UPDATE {tq("cat_Tipos_Incidente", dialect)}
            SET eliminado = {elim}
            WHERE id_tipo = :id AND eliminado = {_eliminado_false(dialect)}
            """
        )
        result = conn.execute(sql, {"id": id_tipo})
        return result.rowcount > 0

    def get_sede(self, conn: Connection, dialect: str, id_sede: int) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT id_sede, nombre_sede, nivel_criticidad, eliminado
            FROM {tq("cat_Sedes", dialect)}
            WHERE id_sede = :id
            """
        )
        row = conn.execute(sql, {"id": id_sede}).fetchone()
        return row_to_dict(row) if row else None
