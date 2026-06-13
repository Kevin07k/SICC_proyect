"""Sync no debe propagar incidentes operacionales."""

import pytest
from sqlalchemy import text

from app.core.sql_dialect import tq
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.session import get_connection


@pytest.mark.integration
def test_sync_does_not_copy_incidentes(client, admin_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    titulo = "INC-SYNC-TEST-ONLY-PG"

    with get_connection(get_postgres_engine()) as pg_conn:
        pg_conn.execute(
            text(
                f"""
                INSERT INTO {tq("Incidentes", "postgres")}
                    (uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
                     id_usuario_asignado, id_sede)
                SELECT gen_random_uuid(), :titulo, 'test', 1, 1, 1, u.uuid, 1
                FROM {tq("Usuarios", "postgres")} u
                WHERE u.email = 'admin@sicc.com'
                LIMIT 1
                """
            ),
            {"titulo": titulo},
        )
        pg_conn.commit()

    client.post("/sync/manual", headers=admin_headers)

    with get_connection(get_mysql_engine()) as my_conn:
        count = my_conn.execute(
            text(
                f"""
                SELECT COUNT(*) FROM {tq("Incidentes", "mysql")}
                WHERE titulo = :titulo
                """
            ),
            {"titulo": titulo},
        ).scalar()
    assert count == 0
