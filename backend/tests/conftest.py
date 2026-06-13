import os

import pytest
from fastapi.testclient import TestClient

from app.db.engines import get_mysql_engine, get_postgres_engine, ping_engine
from app.main import app


def _dbs_available() -> bool:
    return ping_engine(get_postgres_engine()) and ping_engine(get_mysql_engine())


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def integration_enabled() -> bool:
    return os.getenv("SICC_RUN_INTEGRATION", "1") == "1" and _dbs_available()


@pytest.fixture
def admin_headers(client: TestClient, integration_enabled: bool) -> dict[str, str]:
    if not integration_enabled:
        pytest.skip("BDs no disponibles")
    resp = client.post(
        "/auth/login",
        json={"email": "admin@sicc.com", "password": "admin123"},
    )
    assert resp.status_code == 200, resp.text
    uuid = resp.json()["uuid"]
    return {"X-Usuario-UUID": uuid}
