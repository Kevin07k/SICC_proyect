import json
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.repositories.base import row_to_dict


class ReporteRepository:
    def fdw_cochabamba_ready(self, conn: Connection) -> bool:
        sql = text(
            """
            SELECT 1 FROM information_schema.foreign_tables
            WHERE foreign_table_schema = 'sucursal_cochabamba'
              AND foreign_table_name ILIKE 'activos'
            LIMIT 1
            """
        )
        return conn.execute(sql).fetchone() is not None

    def get_cache(self, conn: Connection, clave: str = "global") -> dict[str, Any] | None:
        sql = text(
            """
            SELECT clave, payload, generated_at, expires_at, duration_ms, source_nodes
            FROM reportes_cache
            WHERE clave = :clave
            """
        )
        row = conn.execute(sql, {"clave": clave}).fetchone()
        return row_to_dict(row) if row else None

    def upsert_cache(
        self,
        conn: Connection,
        *,
        clave: str,
        payload: dict[str, Any],
        generated_at: datetime,
        expires_at: datetime,
        duration_ms: int,
    ) -> None:
        sql = text(
            """
            INSERT INTO reportes_cache (clave, payload, generated_at, expires_at, duration_ms)
            VALUES (:clave, CAST(:payload AS jsonb), :generated_at, :expires_at, :duration_ms)
            ON CONFLICT (clave) DO UPDATE SET
                payload = EXCLUDED.payload,
                generated_at = EXCLUDED.generated_at,
                expires_at = EXCLUDED.expires_at,
                duration_ms = EXCLUDED.duration_ms
            """
        )
        conn.execute(
            sql,
            {
                "clave": clave,
                "payload": json.dumps(payload),
                "generated_at": generated_at,
                "expires_at": expires_at,
                "duration_ms": duration_ms,
            },
        )
        conn.commit()

    def aggregate_sede(
        self, conn: Connection, dialect: str, id_sede: int, nombre_sede: str, nodo: str
    ) -> dict[str, Any]:
        elim_inc = "FALSE" if dialect == "postgres" else "0"
        elim_act = elim_inc
        sql = text(
            f"""
            SELECT
                COUNT(*) AS incidentes_total,
                SUM(CASE WHEN i.eliminado = {elim_inc} AND e.nombre NOT IN ('Cerrado', 'Falso Positivo')
                    THEN 1 ELSE 0 END) AS incidentes_abiertos
            FROM Incidentes i
            JOIN cat_Estados e ON e.id_estado = i.id_estado
            WHERE i.id_sede = :id_sede
            """
        )
        inc = conn.execute(sql, {"id_sede": id_sede}).fetchone()
        sql_act = text(
            f"""
            SELECT
                COUNT(*) AS activos_total,
                SUM(CASE WHEN eliminado = {elim_act} THEN 1 ELSE 0 END) AS activos_activos
            FROM Activos
            WHERE id_sede = :id_sede
            """
        )
        act = conn.execute(sql_act, {"id_sede": id_sede}).fetchone()
        return {
            "id_sede": id_sede,
            "nombre_sede": nombre_sede,
            "incidentes_total": int(inc[0] or 0) if inc else 0,
            "incidentes_abiertos": int(inc[1] or 0) if inc else 0,
            "activos_total": int(act[0] or 0) if act else 0,
            "activos_activos": int(act[1] or 0) if act else 0,
            "nodo": nodo,
        }

    def aggregate_global_counts(
        self, conn: Connection, dialect: str, id_sede: int
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        elim = "FALSE" if dialect == "postgres" else "0"
        by_estado = text(
            f"""
            SELECT e.nombre AS nombre, COUNT(*) AS cantidad
            FROM Incidentes i
            JOIN cat_Estados e ON e.id_estado = i.id_estado
            WHERE i.id_sede = :id_sede AND i.eliminado = {elim}
            GROUP BY e.nombre
            ORDER BY cantidad DESC
            """
        )
        by_prioridad = text(
            f"""
            SELECT p.nivel AS nombre, COUNT(*) AS cantidad
            FROM Incidentes i
            JOIN cat_Prioridades p ON p.id_prioridad = i.id_prioridad
            WHERE i.id_sede = :id_sede AND i.eliminado = {elim}
            GROUP BY p.nivel
            ORDER BY cantidad DESC
            """
        )
        estados = [
            {"nombre": r[0], "cantidad": int(r[1])}
            for r in conn.execute(by_estado, {"id_sede": id_sede}).fetchall()
        ]
        prioridades = [
            {"nombre": r[0], "cantidad": int(r[1])}
            for r in conn.execute(by_prioridad, {"id_sede": id_sede}).fetchall()
        ]
        return estados, prioridades

    def aggregate_sede_fdw(
        self,
        conn: Connection,
        id_sede: int,
        nombre_sede: str,
        nodo: str = "mysql_fdw",
    ) -> dict[str, Any]:
        """Métricas de Cochabamba vía esquema sucursal_cochabamba (mysql_fdw)."""
        sql = text(
            """
            SELECT
                COUNT(*) AS incidentes_total,
                SUM(
                    CASE
                        WHEN i.eliminado = 0
                         AND e.nombre NOT IN ('Cerrado', 'Falso Positivo')
                        THEN 1 ELSE 0
                    END
                ) AS incidentes_abiertos
            FROM sucursal_cochabamba."Incidentes" i
            JOIN cat_Estados e ON e.id_estado = i.id_estado
            WHERE i.id_sede = :id_sede
            """
        )
        inc = conn.execute(sql, {"id_sede": id_sede}).fetchone()
        sql_act = text(
            """
            SELECT
                COUNT(*) AS activos_total,
                SUM(CASE WHEN a.eliminado = 0 THEN 1 ELSE 0 END) AS activos_activos
            FROM sucursal_cochabamba."Activos" a
            WHERE a.id_sede = :id_sede
            """
        )
        act = conn.execute(sql_act, {"id_sede": id_sede}).fetchone()
        return {
            "id_sede": id_sede,
            "nombre_sede": nombre_sede,
            "incidentes_total": int(inc[0] or 0) if inc else 0,
            "incidentes_abiertos": int(inc[1] or 0) if inc else 0,
            "activos_total": int(act[0] or 0) if act else 0,
            "activos_activos": int(act[1] or 0) if act else 0,
            "nodo": nodo,
        }

    def aggregate_global_counts_fdw(
        self, conn: Connection, id_sede: int
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        by_estado = text(
            """
            SELECT e.nombre AS nombre, COUNT(*) AS cantidad
            FROM sucursal_cochabamba."Incidentes" i
            JOIN cat_Estados e ON e.id_estado = i.id_estado
            WHERE i.id_sede = :id_sede AND i.eliminado = 0
            GROUP BY e.nombre
            ORDER BY cantidad DESC
            """
        )
        by_prioridad = text(
            """
            SELECT p.nivel AS nombre, COUNT(*) AS cantidad
            FROM sucursal_cochabamba."Incidentes" i
            JOIN cat_Prioridades p ON p.id_prioridad = i.id_prioridad
            WHERE i.id_sede = :id_sede AND i.eliminado = 0
            GROUP BY p.nivel
            ORDER BY cantidad DESC
            """
        )
        estados = [
            {"nombre": r[0], "cantidad": int(r[1])}
            for r in conn.execute(by_estado, {"id_sede": id_sede}).fetchall()
        ]
        prioridades = [
            {"nombre": r[0], "cantidad": int(r[1])}
            for r in conn.execute(by_prioridad, {"id_sede": id_sede}).fetchall()
        ]
        return estados, prioridades
