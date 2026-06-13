"""Vínculo incidente–activo con snapshot histórico."""

import pytest


@pytest.mark.integration
def test_incidente_activo_snapshot_persiste(client, admin_headers, integration_enabled) -> None:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")

    activo = client.post(
        "/activos",
        headers=admin_headers,
        json={
            "hostname": "snap-test-host",
            "tipo_activo": "servidor",
            "id_sede": 1,
        },
    )
    assert activo.status_code == 201, activo.text
    activo_uuid = activo.json()["uuid"]
    tipo_original = activo.json()["tipo_activo"]

    incidente = client.post(
        "/incidentes",
        headers=admin_headers,
        json={
            "titulo": "Incidente snapshot activo",
            "id_tipo": 1,
            "id_prioridad": 1,
            "id_estado": 1,
            "activos": [activo_uuid],
        },
    )
    assert incidente.status_code == 201, incidente.text
    inc_uuid = incidente.json()["uuid"]
    vinculos = incidente.json().get("activos_vinculados") or []
    assert len(vinculos) == 1
    assert vinculos[0]["tipo_activo_registrado"] == tipo_original
    assert vinculos[0]["hostname_registrado"] == "snap-test-host"
    assert vinculos[0]["sede_registrada"]

    patch = client.patch(
        f"/activos/{activo_uuid}",
        headers=admin_headers,
        json={"tipo_activo": "workstation-cambiado"},
    )
    assert patch.status_code == 200, patch.text

    lista = client.get(f"/incidentes/{inc_uuid}/activos", headers=admin_headers)
    assert lista.status_code == 200
    row = lista.json()[0]
    assert row["tipo_activo_registrado"] == tipo_original
    assert row["tipo_activo_registrado"] != "workstation-cambiado"
