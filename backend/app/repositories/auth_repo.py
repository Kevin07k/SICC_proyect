from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


class AuthRepository:
    def find_by_email(self, conn: Connection, dialect: str, email: str) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT u.uuid, u.email, u.password_hash, u.nombre_completo,
                   u.id_sede, u.id_rol, u.activo, r.nombre AS rol_nombre
            FROM {tq("Usuarios", dialect)} u
            JOIN {tq("Roles", dialect)} r ON r.id_rol = u.id_rol
            WHERE u.email = :email AND u.activo = TRUE
            """
        )
        row = conn.execute(sql, {"email": email}).fetchone()
        return row_to_dict(row) if row else None

    def find_by_uuid(self, conn: Connection, dialect: str, user_uuid: UUID) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT u.uuid, u.email, u.nombre_completo, u.id_sede, u.id_rol,
                   u.activo, r.nombre AS rol_nombre
            FROM {tq("Usuarios", dialect)} u
            JOIN {tq("Roles", dialect)} r ON r.id_rol = u.id_rol
            WHERE u.uuid = :uuid AND u.activo = TRUE
            """
        )
        row = conn.execute(sql, {"uuid": str(user_uuid)}).fetchone()
        return row_to_dict(row) if row else None

    def get_permisos(self, conn: Connection, dialect: str, id_rol: int) -> list[str]:
        sql = text(
            f"""
            SELECT p.codigo
            FROM {tq("Permisos", dialect)} p
            JOIN {tq("Roles_Permisos", dialect)} rp ON rp.id_permiso = p.id_permiso
            WHERE rp.id_rol = :id_rol
            ORDER BY p.codigo
            """
        )
        rows = conn.execute(sql, {"id_rol": id_rol}).fetchall()
        return [r[0] for r in rows]

    def find_user_across_engines(
        self, pg_conn: Connection, mysql_conn: Connection, email: str
    ) -> tuple[dict[str, Any], str] | None:
        user = self.find_by_email(pg_conn, "postgres", email)
        if user:
            return user, "postgres"
        user = self.find_by_email(mysql_conn, "mysql", email)
        if user:
            return user, "mysql"
        return None

    def find_uuid_across_engines(
        self, pg_conn: Connection, mysql_conn: Connection, user_uuid: UUID
    ) -> tuple[dict[str, Any], str] | None:
        user = self.find_by_uuid(pg_conn, "postgres", user_uuid)
        if user:
            return user, "postgres"
        user = self.find_by_uuid(mysql_conn, "mysql", user_uuid)
        if user:
            return user, "mysql"
        return None
