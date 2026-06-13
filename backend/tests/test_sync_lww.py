"""Sync LWW: el registro con updated_at más reciente prevalece."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text

from app.core.sql_dialect import tq
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.session import get_connection

_HASH = "$2b$12$IGJe7k/OGX4KJzZ8HFc0Cehn9iYldLE.hFOR55rAcdMXicRINlUxm"


@pytest.mark.integration
def test_sync_lww_usuario_wins_newer(client, admin_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    email = "lww_test@sicc.com"
    older = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=5)
    newer = datetime.now(UTC).replace(tzinfo=None)

    # MySQL primero (más antiguo). PG después: el trigger de PG deja updated_at más reciente.
    with get_connection(get_mysql_engine()) as my_conn:
        my_conn.execute(
            text(
                f"""
                INSERT INTO {tq("Usuarios", "mysql")}
                    (uuid, email, password_hash, nombre_completo, id_sede, id_rol,
                     created_at, updated_at)
                VALUES (
                    UUID(), :email, :hash,
                    'LWW MY Old', 1, 1, :c, :u
                )
                ON DUPLICATE KEY UPDATE
                    nombre_completo = 'LWW MY Old',
                    updated_at = :u
                """
            ),
            {"email": email, "hash": _HASH, "c": older, "u": older},
        )
        my_conn.commit()

    with get_connection(get_postgres_engine()) as pg_conn:
        pg_conn.execute(
            text(
                f"""
                INSERT INTO {tq("Usuarios", "postgres")}
                    (uuid, email, password_hash, nombre_completo, id_sede, id_rol,
                     created_at, updated_at)
                VALUES (
                    gen_random_uuid(), :email, :hash,
                    'LWW PG', 1, 1, :c, :u
                )
                ON CONFLICT (email) DO UPDATE SET
                    nombre_completo = 'LWW PG Winner',
                    updated_at = :u
                """
            ),
            {"email": email, "hash": _HASH, "c": newer, "u": newer},
        )
        pg_conn.commit()

    resp = client.post("/sync/manual", headers=admin_headers)
    assert resp.status_code == 200, resp.text

    with get_connection(get_mysql_engine()) as my_conn:
        row = my_conn.execute(
            text(
                f"""
                SELECT nombre_completo FROM {tq("Usuarios", "mysql")}
                WHERE email = :email
                """
            ),
            {"email": email},
        ).fetchone()
    assert row is not None
    assert row[0] == "LWW PG Winner"
