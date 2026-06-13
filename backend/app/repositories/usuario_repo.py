from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


class UsuarioRepository:
    def list_all(self, conn: Connection, dialect: str) -> list[dict[str, Any]]:
        sql = text(
            f"""
            SELECT uuid, email, nombre_completo, id_sede, id_rol, activo,
                   created_at, updated_at
            FROM {tq("Usuarios", dialect)}
            ORDER BY id_sede, nombre_completo
            """
        )
        rows = conn.execute(sql).fetchall()
        return [row_to_dict(r) for r in rows]

    def list_by_sede(self, conn: Connection, dialect: str, id_sede: int) -> list[dict[str, Any]]:
        sql = text(
            f"""
            SELECT uuid, email, nombre_completo, id_sede, id_rol, activo,
                   created_at, updated_at
            FROM {tq("Usuarios", dialect)}
            WHERE id_sede = :id_sede
            ORDER BY nombre_completo
            """
        )
        rows = conn.execute(sql, {"id_sede": id_sede}).fetchall()
        return [row_to_dict(r) for r in rows]

    def get(self, conn: Connection, dialect: str, user_uuid: UUID) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT uuid, email, nombre_completo, id_sede, id_rol, activo,
                   created_at, updated_at
            FROM {tq("Usuarios", dialect)}
            WHERE uuid = :uuid
            """
        )
        row = conn.execute(sql, {"uuid": str(user_uuid)}).fetchone()
        return row_to_dict(row) if row else None

    def create(
        self,
        conn: Connection,
        dialect: str,
        *,
        email: str,
        password_hash: str,
        nombre_completo: str,
        id_sede: int,
        id_rol: int,
    ) -> dict[str, Any]:
        new_uuid = uuid4()
        if dialect == "postgres":
            sql = text(
                f"""
                INSERT INTO {tq("Usuarios", dialect)}
                    (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
                VALUES (:uuid, :email, :password_hash, :nombre, :id_sede, :id_rol)
                RETURNING uuid, email, nombre_completo, id_sede, id_rol, activo,
                          created_at, updated_at
                """
            )
            row = conn.execute(
                sql,
                {
                    "uuid": str(new_uuid),
                    "email": email,
                    "password_hash": password_hash,
                    "nombre": nombre_completo,
                    "id_sede": id_sede,
                    "id_rol": id_rol,
                },
            ).fetchone()
        else:
            sql = text(
                f"""
                INSERT INTO {tq("Usuarios", dialect)}
                    (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
                VALUES (:uuid, :email, :password_hash, :nombre, :id_sede, :id_rol)
                """
            )
            conn.execute(
                sql,
                {
                    "uuid": str(new_uuid),
                    "email": email,
                    "password_hash": password_hash,
                    "nombre": nombre_completo,
                    "id_sede": id_sede,
                    "id_rol": id_rol,
                },
            )
            row = conn.execute(
                text(
                    f"""
                    SELECT uuid, email, nombre_completo, id_sede, id_rol, activo,
                           created_at, updated_at
                    FROM {tq("Usuarios", dialect)} WHERE uuid = :uuid
                    """
                ),
                {"uuid": str(new_uuid)},
            ).fetchone()
        conn.commit()
        return row_to_dict(row)  # type: ignore[arg-type]

    def update(
        self,
        conn: Connection,
        dialect: str,
        user_uuid: UUID,
        fields: dict[str, Any],
    ) -> dict[str, Any] | None:
        sets = []
        params: dict[str, Any] = {"uuid": str(user_uuid)}
        for key, value in fields.items():
            if value is not None:
                sets.append(f"{key} = :{key}")
                params[key] = value
        if not sets:
            return self.get(conn, dialect, user_uuid)
        sql = text(
            f"""
            UPDATE {tq("Usuarios", dialect)}
            SET {", ".join(sets)}
            WHERE uuid = :uuid
            """
        )
        conn.execute(sql, params)
        conn.commit()
        return self.get(conn, dialect, user_uuid)
