from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


class BitacoraRepository:
    def list_by_incidente(
        self, conn: Connection, dialect: str, incidente_uuid: UUID
    ) -> list[dict[str, Any]]:
        elim = "FALSE" if dialect == "postgres" else "0"
        sql = text(
            f"""
            SELECT b.uuid, b.id_incidente, b.id_usuario, b.comentario, b.eliminado,
                   b.created_at, u.nombre_completo AS usuario_nombre
            FROM {tq("Bitacora_Investigacion", dialect)} b
            JOIN {tq("Usuarios", dialect)} u ON u.uuid = b.id_usuario
            WHERE b.id_incidente = :id_incidente AND b.eliminado = {elim}
            ORDER BY b.created_at ASC
            """
        )
        rows = conn.execute(sql, {"id_incidente": str(incidente_uuid)}).fetchall()
        return [row_to_dict(r) for r in rows]

    def create(
        self,
        conn: Connection,
        dialect: str,
        incidente_uuid: UUID,
        usuario_uuid: UUID,
        comentario: str,
    ) -> dict[str, Any]:
        new_uuid = uuid4()
        params = {
            "uuid": str(new_uuid),
            "id_incidente": str(incidente_uuid),
            "id_usuario": str(usuario_uuid),
            "comentario": comentario,
        }
        if dialect == "postgres":
            sql = text(
                f"""
                INSERT INTO {tq("Bitacora_Investigacion", dialect)}
                    (uuid, id_incidente, id_usuario, comentario)
                VALUES (
                    :uuid,
                    CAST(:id_incidente AS uuid),
                    CAST(:id_usuario AS uuid),
                    :comentario
                )
                """
            )
        else:
            sql = text(
                f"""
                INSERT INTO {tq("Bitacora_Investigacion", dialect)}
                    (uuid, id_incidente, id_usuario, comentario)
                VALUES (:uuid, :id_incidente, :id_usuario, :comentario)
                """
            )
        conn.execute(sql, params)
        conn.commit()
        rows = self.list_by_incidente(conn, dialect, incidente_uuid)
        for row in rows:
            if str(row["uuid"]) == str(new_uuid):
                return row
        return rows[-1]
