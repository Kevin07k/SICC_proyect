"""RN-03: usuario solo opera datos de su sede."""

import pytest


@pytest.fixture
def analista_cb_headers(client, integration_enabled) -> dict[str, str]:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    resp = client.post(
        "/auth/login",
        json={"email": "analista.cb@test.sicc", "password": "test123"},
    )
    assert resp.status_code == 200, resp.text
    return {"X-Usuario-UUID": resp.json()["uuid"]}


@pytest.mark.integration
def test_incidentes_scoped_by_sede_admin_santa_cruz(client, admin_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    resp = client.get("/incidentes", headers=admin_headers)
    assert resp.status_code == 200
    for inc in resp.json():
        assert inc["id_sede"] == 1


@pytest.mark.integration
def test_incidentes_scoped_by_sede_cochabamba(client, analista_cb_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    resp = client.get("/incidentes", headers=analista_cb_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1, "Cochabamba debe tener incidentes demo en MySQL"
    for inc in data:
        assert inc["id_sede"] == 2
