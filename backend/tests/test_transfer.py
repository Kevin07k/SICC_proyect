"""Traslado de activo: origen eliminado, destino con mismo UUID activo."""

import pytest


@pytest.mark.integration
def test_transfer_activo_cross_db(client, admin_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    create = client.post(
        "/activos",
        headers=admin_headers,
        json={
            "hostname": "srv-transfer-test",
            "direccion_ip": "10.0.0.99",
            "tipo_activo": "servidor",
            "propietario": "IT",
        },
    )
    assert create.status_code == 201, create.text
    activo_uuid = create.json()["uuid"]
    assert create.json()["id_sede"] == 1

    transfer = client.post(
        f"/activos/{activo_uuid}/transferir",
        headers=admin_headers,
        json={"sede_destino_id": 2, "motivo": "Prueba traslado a Cochabamba"},
    )
    assert transfer.status_code == 200, transfer.text
    data = transfer.json()
    assert data["sede_destino_id"] == 2
    assert data["nodo_destino"] == "mysql"

    list_cb = client.get("/activos", headers=admin_headers)
    assert list_cb.status_code == 200
    uuids_cb = [a["uuid"] for a in list_cb.json()]
    assert activo_uuid not in uuids_cb
