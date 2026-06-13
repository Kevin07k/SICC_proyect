from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


class IncidenteActivoRepository:
    def list_by_incidente(
        self, conn: Connection, dialect: str, incidente_uuid: UUID
    ) -> list[dict[str, Any]]:
        elim_expr = "a.eliminado" if dialect == "postgres" else "a.eliminado"
        sql = text(
            f"""
            SELECT ia.uuid, ia.id_incidente, ia.id_activo, ia.notas,
                   ia.tipo_activo_registrado, ia.sede_registrada, ia.hostname_registrado,
                   ia.created_at, ia.updated_at,
                   a.hostname AS hostname_actual, {elim_expr} AS activo_eliminado
            FROM {tq("Incidentes_Activos", dialect)} ia
            LEFT JOIN {tq("Activos", dialect)} a ON a.uuid = ia.id_activo
            WHERE ia.id_incidente = :id_incidente
            ORDER BY ia.created_at ASC
            """
        )
        rows = conn.execute(sql, {"id_incidente": str(incidente_uuid)}).fetchall()
        return [row_to_dict(r) for r in rows]

    def get_activo_with_sede(
        self, conn: Connection, dialect: str, activo_uuid: UUID
    ) -> dict[str, Any] | None:
        elim = "FALSE" if dialect == "postgres" else "0"
        sql = text(
            f"""
            SELECT a.uuid, a.hostname, a.tipo_activo, a.id_sede, a.eliminado,
                   s.nombre_sede AS sede_nombre
            FROM {tq("Activos", dialect)} a
            JOIN {tq("cat_Sedes", dialect)} s ON s.id_sede = a.id_sede
            WHERE a.uuid = :uuid AND a.eliminado = {elim}
            """
        )
        row = conn.execute(sql, {"uuid": str(activo_uuid)}).fetchone()
        return row_to_dict(row) if row else None

    def link_exists(
        self, conn: Connection, dialect: str, incidente_uuid: UUID, activo_uuid: UUID
    ) -> bool:
        sql = text(
            f"""
            SELECT 1 FROM {tq("Incidentes_Activos", dialect)}
            WHERE id_incidente = :id_incidente AND id_activo = :id_activo
            """
        )
        row = conn.execute(
            sql,
            {"id_incidente": str(incidente_uuid), "id_activo": str(activo_uuid)},
        ).fetchone()
        return row is not None

    def create_link(
        self,
        conn: Connection,
        dialect: str,
        incidente_uuid: UUID,
        activo: dict[str, Any],
        notas: str | None,
    ) -> dict[str, Any]:
        link_uuid = uuid4()
        params = {
            "uuid": str(link_uuid),
            "id_incidente": str(incidente_uuid),
            "id_activo": str(activo["uuid"]),
            "notas": notas,
            "tipo_activo_registrado": activo.get("tipo_activo"),
            "sede_registrada": activo.get("sede_nombre"),
            "hostname_registrado": activo.get("hostname"),
        }
        sql = text(
            f"""
            INSERT INTO {tq("Incidentes_Activos", dialect)}
                (uuid, id_incidente, id_activo, notas,
                 tipo_activo_registrado, sede_registrada, hostname_registrado)
            VALUES
                (:uuid, :id_incidente, :id_activo, :notas,
                 :tipo_activo_registrado, :sede_registrada, :hostname_registrado)
            """
        )
        conn.execute(sql, params)
        conn.commit()
        row = self.get_by_uuid(conn, dialect, link_uuid)
        if not row:
            raise RuntimeError("Vínculo incidente-activo no encontrado tras insert")
        return row

    def get_by_uuid(
        self, conn: Connection, dialect: str, link_uuid: UUID
    ) -> dict[str, Any] | None:
        elim_expr = "a.eliminado" if dialect == "postgres" else "a.eliminado"
        sql = text(
            f"""
            SELECT ia.uuid, ia.id_incidente, ia.id_activo, ia.notas,
                   ia.tipo_activo_registrado, ia.sede_registrada, ia.hostname_registrado,
                   ia.created_at, ia.updated_at,
                   a.hostname AS hostname_actual, {elim_expr} AS activo_eliminado
            FROM {tq("Incidentes_Activos", dialect)} ia
            LEFT JOIN {tq("Activos", dialect)} a ON a.uuid = ia.id_activo
            WHERE ia.uuid = :uuid
            """
        )
        row = conn.execute(sql, {"uuid": str(link_uuid)}).fetchone()
        return row_to_dict(row) if row else None

    def delete_link(self, conn: Connection, dialect: str, link_uuid: UUID) -> bool:
        sql = text(
            f"""
            DELETE FROM {tq("Incidentes_Activos", dialect)}
            WHERE uuid = :uuid
            """
        )
        result = conn.execute(sql, {"uuid": str(link_uuid)})
        conn.commit()
        return result.rowcount > 0
