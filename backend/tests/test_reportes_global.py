"""Reportes globales con caché en PostgreSQL."""

import pytest

from app.db.engines import get_postgres_engine
from app.db.session import get_connection
from sqlalchemy import text


@pytest.fixture
def admin_headers(client, integration_enabled) -> dict[str, str]:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    resp = client.post(
        "/auth/login",
        json={"email": "admin@sicc.com", "password": "admin123"},
    )
    assert resp.status_code == 200
    return {"X-Usuario-UUID": resp.json()["uuid"]}


@pytest.fixture
def dba_central_headers(client, integration_enabled) -> dict[str, str]:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    resp = client.post(
        "/auth/login",
        json={"email": "dba@test.sicc", "password": "test123"},
    )
    assert resp.status_code == 200
    return {"X-Usuario-UUID": resp.json()["uuid"]}


@pytest.fixture
def dba_cb_headers(client, integration_enabled) -> dict[str, str]:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    resp = client.post(
        "/auth/login",
        json={"email": "dba.cb@test.sicc", "password": "test123"},
    )
    assert resp.status_code == 200
    return {"X-Usuario-UUID": resp.json()["uuid"]}


def _ensure_reportes_cache_table() -> None:
    with get_connection(get_postgres_engine()) as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS reportes_cache (
                    id SERIAL PRIMARY KEY,
                    clave VARCHAR(64) NOT NULL UNIQUE DEFAULT 'global',
                    payload JSONB NOT NULL,
                    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    duration_ms INTEGER,
                    source_nodes TEXT[] NOT NULL DEFAULT ARRAY['postgres', 'mysql']
                )
                """
            )
        )
        conn.commit()


@pytest.mark.integration
def test_reporte_global_admin(client, admin_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    _ensure_reportes_cache_table()

    resp = client.get("/reportes/global", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "payload" in data
    assert len(data["payload"]["sedes"]) == 2
    assert data["ttl_seconds"] > 0

    resp2 = client.get("/reportes/global", headers=admin_headers)
    assert resp2.status_code == 200
    assert resp2.json()["from_cache"] is True


@pytest.mark.integration
def test_reporte_global_dba_central(client, dba_central_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    _ensure_reportes_cache_table()

    resp = client.get("/reportes/global", headers=dba_central_headers)
    assert resp.status_code == 200


@pytest.mark.integration
def test_reporte_global_denegado_cochabamba_dba(
    client, dba_cb_headers, integration_enabled
) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    _ensure_reportes_cache_table()

    resp = client.get("/reportes/global", headers=dba_cb_headers)
    assert resp.status_code == 403


@pytest.mark.integration
def test_usuarios_vista_global_denegado_cochabamba(
    client, dba_cb_headers, integration_enabled
) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    resp = client.get("/usuarios", headers=dba_cb_headers)
    assert resp.status_code == 200
    users = resp.json()
    sedes = {u["id_sede"] for u in users}
    assert all(s == 2 for s in sedes) or len(sedes) <= 1
