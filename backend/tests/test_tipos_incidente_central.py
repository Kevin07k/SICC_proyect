"""CRUD tipos de incidente — solo sede central."""

import pytest


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
def analista_cb_headers(client, integration_enabled) -> dict[str, str]:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    resp = client.post(
        "/auth/login",
        json={"email": "analista.cb@test.sicc", "password": "test123"},
    )
    assert resp.status_code == 200
    return {"X-Usuario-UUID": resp.json()["uuid"]}


@pytest.mark.integration
def test_tipos_gestion_solo_central(client, admin_headers, analista_cb_headers) -> None:
    resp_cb = client.get("/catalogos/tipos-incidente/gestion", headers=analista_cb_headers)
    assert resp_cb.status_code == 403

    resp_admin = client.get("/catalogos/tipos-incidente/gestion", headers=admin_headers)
    assert resp_admin.status_code == 200


@pytest.mark.integration
def test_tipos_list_publico_para_formularios(client, analista_cb_headers) -> None:
    resp = client.get("/catalogos/tipos-incidente", headers=analista_cb_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
