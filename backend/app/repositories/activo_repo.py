from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.sql_dialect import tq
from app.repositories.base import row_to_dict


class ActivoRepository:
    def list_by_sede(
        self, conn: Connection, dialect: str, id_sede: int, include_eliminados: bool = False
    ) -> list[dict[str, Any]]:
        where = "id_sede = :id_sede"
        if not include_eliminados:
            elim = "FALSE" if dialect == "postgres" else "0"
            where += f" AND eliminado = {elim}"
        sql = text(
            f"""
            SELECT uuid, hostname, direccion_ip, tipo_activo, propietario,
                   id_sede, eliminado, created_at, updated_at
            FROM {tq("Activos", dialect)}
            WHERE {where}
            ORDER BY hostname
            """
        )
        rows = conn.execute(sql, {"id_sede": id_sede}).fetchall()
        return [row_to_dict(r) for r in rows]

    def get(self, conn: Connection, dialect: str, activo_uuid: UUID) -> dict[str, Any] | None:
        sql = text(
            f"""
            SELECT uuid, hostname, direccion_ip, tipo_activo, propietario,
                   id_sede, eliminado, created_at, updated_at
            FROM {tq("Activos", dialect)}
            WHERE uuid = :uuid
            """
        )
        row = conn.execute(sql, {"uuid": str(activo_uuid)}).fetchone()
        return row_to_dict(row) if row else None

    def find_active_in_any_node(
        self,
        pg_conn: Connection,
        mysql_conn: Connection,
        activo_uuid: UUID,
    ) -> tuple[dict[str, Any], str, Connection] | None:
        row = self.get(pg_conn, "postgres", activo_uuid)
        if row and not row.get("eliminado"):
            return row, "postgres", pg_conn
        row = self.get(mysql_conn, "mysql", activo_uuid)
        if row and not row.get("eliminado"):
            return row, "mysql", mysql_conn
        return None

    def create(self, conn: Connection, dialect: str, data: dict[str, Any]) -> dict[str, Any]:
        new_uuid = uuid4()
        params = {"uuid": str(new_uuid), **data}
        if dialect == "postgres":
            sql = text(
                f"""
                INSERT INTO {tq("Activos", dialect)}
                    (uuid, hostname, direccion_ip, tipo_activo, propietario, id_sede)
                VALUES (:uuid, :hostname, :direccion_ip, :tipo_activo, :propietario, :id_sede)
                RETURNING uuid
                """
            )
            conn.execute(sql, params)
        else:
            sql = text(
                f"""
                INSERT INTO {tq("Activos", dialect)}
                    (uuid, hostname, direccion_ip, tipo_activo, propietario, id_sede)
                VALUES (:uuid, :hostname, :direccion_ip, :tipo_activo, :propietario, :id_sede)
                """
            )
            conn.execute(sql, params)
        conn.commit()
        result = self.get(conn, dialect, new_uuid)
        assert result is not None
        return result

    def soft_delete(
        self,
        conn: Connection,
        dialect: str,
        activo_uuid: UUID,
        *,
        auto_commit: bool = True,
    ) -> None:
        elim_val = "TRUE" if dialect == "postgres" else "1"
        sql = text(
            f"""
            UPDATE {tq("Activos", dialect)}
            SET eliminado = {elim_val}
            WHERE uuid = :uuid
            """
        )
        conn.execute(sql, {"uuid": str(activo_uuid)})
        if auto_commit:
            conn.commit()

    def restore(
        self,
        conn: Connection,
        dialect: str,
        activo_uuid: UUID,
        *,
        auto_commit: bool = True,
    ) -> None:
        elim_val = "FALSE" if dialect == "postgres" else "0"
        sql = text(
            f"""
            UPDATE {tq("Activos", dialect)}
            SET eliminado = {elim_val}
            WHERE uuid = :uuid
            """
        )
        conn.execute(sql, {"uuid": str(activo_uuid)})
        if auto_commit:
            conn.commit()

    def insert_transfer(
        self,
        conn: Connection,
        dialect: str,
        activo: dict[str, Any],
        sede_destino_id: int,
        *,
        auto_commit: bool = True,
    ) -> dict[str, Any]:
        params = {
            "uuid": str(activo["uuid"]),
            "hostname": activo["hostname"],
            "direccion_ip": activo.get("direccion_ip"),
            "tipo_activo": activo.get("tipo_activo"),
            "propietario": activo.get("propietario"),
            "id_sede": sede_destino_id,
        }
        elim = "FALSE" if dialect == "postgres" else "0"
        if dialect == "postgres":
            sql = text(
                f"""
                INSERT INTO {tq("Activos", dialect)}
                    (uuid, hostname, direccion_ip, tipo_activo, propietario, id_sede, eliminado)
                VALUES (:uuid, :hostname, :direccion_ip, :tipo_activo, :propietario, :id_sede, {elim})
                ON CONFLICT (uuid) DO UPDATE SET
                    hostname = EXCLUDED.hostname,
                    direccion_ip = EXCLUDED.direccion_ip,
                    tipo_activo = EXCLUDED.tipo_activo,
                    propietario = EXCLUDED.propietario,
                    id_sede = EXCLUDED.id_sede,
                    eliminado = {elim}
                """
            )
        else:
            sql = text(
                f"""
                INSERT INTO {tq("Activos", dialect)}
                    (uuid, hostname, direccion_ip, tipo_activo, propietario, id_sede, eliminado)
                VALUES (:uuid, :hostname, :direccion_ip, :tipo_activo, :propietario, :id_sede, {elim})
                ON DUPLICATE KEY UPDATE
                    hostname = VALUES(hostname),
                    direccion_ip = VALUES(direccion_ip),
                    tipo_activo = VALUES(tipo_activo),
                    propietario = VALUES(propietario),
                    id_sede = VALUES(id_sede),
                    eliminado = {elim}
                """
            )
        conn.execute(sql, params)
        if auto_commit:
            conn.commit()
        result = self.get(conn, dialect, UUID(str(activo["uuid"])))
        assert result is not None
        return result

    def update(
        self,
        conn: Connection,
        dialect: str,
        activo_uuid: UUID,
        fields: dict[str, Any],
    ) -> dict[str, Any] | None:
        sets = []
        params: dict[str, Any] = {"uuid": str(activo_uuid)}
        for key, value in fields.items():
            if value is not None:
                if key == "eliminado" and dialect == "mysql":
                    params[key] = 1 if value else 0
                else:
                    params[key] = value
                sets.append(f"{key} = :{key}")
        if not sets:
            return self.get(conn, dialect, activo_uuid)
        sql = text(
            f"""
            UPDATE {tq("Activos", dialect)}
            SET {", ".join(sets)}
            WHERE uuid = :uuid
            """
        )
        conn.execute(sql, params)
        conn.commit()
        return self.get(conn, dialect, activo_uuid)
