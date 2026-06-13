from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "postgres" in data
    assert "mysql" in data
    assert "mongo_sc" in data
    assert "mongo_cb" in data
