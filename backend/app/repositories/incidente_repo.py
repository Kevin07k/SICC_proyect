from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


class IncidenteRepository:
    def list_by_sede(self, conn: Connection, dialect: str, id_sede: int) -> list[dict[str, Any]]:
        sql = text(
            f"""
            SELECT i.uuid, i.titulo, i.descripcion, i.id_tipo, i.id_prioridad, i.id_estado,
                   i.id_usuario_asignado, i.id_sede, i.fecha_cierre, i.eliminado,
                   i.created_at, i.updated_at,
                   t.nombre AS tipo_nombre, p.nivel AS prioridad_nivel, e.nombre AS estado_nombre
            FROM {tq("Incidentes", dialect)} i
            JOIN {tq("cat_Tipos_Incidente", dialect)} t ON t.id_tipo = i.id_tipo
            JOIN {tq("cat_Prioridades", dialect)} p ON p.id_prioridad = i.id_prioridad
            JOIN {tq("cat_Estados", dialect)} e ON e.id_estado = i.id_estado
            WHERE i.id_sede = :id_sede AND i.eliminado = FALSE
            ORDER BY i.created_at DESC
            """
        )
        rows = conn.execute(sql, {"id_sede": id_sede}).fetchall()
        return [row_to_dict(r) for r in rows]

    def get(self, conn: Connection, dialect: str, incidente_uuid: UUID) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT i.uuid, i.titulo, i.descripcion, i.id_tipo, i.id_prioridad, i.id_estado,
                   i.id_usuario_asignado, i.id_sede, i.fecha_cierre, i.eliminado,
                   i.created_at, i.updated_at,
                   t.nombre AS tipo_nombre, p.nivel AS prioridad_nivel, e.nombre AS estado_nombre
            FROM {tq("Incidentes", dialect)} i
            JOIN {tq("cat_Tipos_Incidente", dialect)} t ON t.id_tipo = i.id_tipo
            JOIN {tq("cat_Prioridades", dialect)} p ON p.id_prioridad = i.id_prioridad
            JOIN {tq("cat_Estados", dialect)} e ON e.id_estado = i.id_estado
            WHERE i.uuid = :uuid
            """
        )
        row = conn.execute(sql, {"uuid": str(incidente_uuid)}).fetchone()
        return row_to_dict(row) if row else None

    def create(
        self,
        conn: Connection,
        dialect: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        new_uuid = uuid4()
        params = {
            "uuid": str(new_uuid),
            **data,
            "uuid_user": str(data["id_usuario_asignado"]),
        }
        if dialect == "postgres":
            sql = text(
                f"""
                INSERT INTO {tq("Incidentes", dialect)}
                    (uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
                     id_usuario_asignado, id_sede)
                VALUES
                    (:uuid, :titulo, :descripcion, :id_tipo, :id_prioridad, :id_estado,
                     CAST(:uuid_user AS uuid), :id_sede)
                """
            )
            conn.execute(sql, params)
        else:
            sql = text(
                f"""
                INSERT INTO {tq("Incidentes", dialect)}
                    (uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
                     id_usuario_asignado, id_sede)
                VALUES
                    (:uuid, :titulo, :descripcion, :id_tipo, :id_prioridad, :id_estado,
                     :uuid_user, :id_sede)
                """
            )
            conn.execute(sql, params)
        conn.commit()
        result = self.get(conn, dialect, new_uuid)
        assert result is not None
        return result

    def update(
        self,
        conn: Connection,
        dialect: str,
        incidente_uuid: UUID,
        fields: dict[str, Any],
    ) -> dict[str, Any] | None:
        sets = []
        params: dict[str, Any] = {"uuid": str(incidente_uuid)}
        for key, value in fields.items():
            if value is not None:
                col = key
                if key == "id_usuario_asignado":
                    col = "id_usuario_asignado"
                    params["id_usuario_asignado"] = str(value)
                    sets.append(f"{col} = :id_usuario_asignado")
                else:
                    sets.append(f"{col} = :{key}")
                    params[key] = value
        if not sets:
            return self.get(conn, dialect, incidente_uuid)
        sql = text(
            f"""
            UPDATE {tq("Incidentes", dialect)}
            SET {", ".join(sets)}
            WHERE uuid = :uuid
            """
        )
        conn.execute(sql, params)
        conn.commit()
        return self.get(conn, dialect, incidente_uuid)
