"""Transacciones: context manager y traslado sin commit prematuro."""

from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.db.session import db_transaction
from app.repositories.activo_repo import ActivoRepository
from app.schemas.activos import ActivoTransferirRequest
from app.schemas.auth import CurrentUser
from app.services.activo_transfer_service import ActivoTransferService


def test_soft_delete_supports_deferred_commit() -> None:
    conn = MagicMock()
    repo = ActivoRepository()
    uid = UUID("b1000001-0001-4000-8000-000000000001")
    repo.soft_delete(conn, "postgres", uid, auto_commit=False)
    conn.execute.assert_called_once()
    conn.commit.assert_not_called()


def test_transfer_calls_repo_without_autocommit(monkeypatch: pytest.MonkeyPatch) -> None:
    activo = {
        "uuid": "b1000001-0001-4000-8000-000000000001",
        "hostname": "h1",
        "id_sede": 1,
        "eliminado": False,
    }
    svc = ActivoTransferService()
    monkeypatch.setattr(
        svc.activo_repo,
        "find_active_in_any_node",
        lambda *_a, **_k: (activo, "postgres", MagicMock()),
    )
    monkeypatch.setattr(
        svc.catalogo_repo,
        "get_sede",
        lambda *_a, **_k: {"id_sede": 2, "eliminado": False},
    )
    soft_calls: list[bool] = []
    insert_calls: list[bool] = []

    def _soft(*_a, auto_commit: bool = True, **_k) -> None:
        soft_calls.append(auto_commit)

    def _insert(*_a, auto_commit: bool = True, **_k) -> dict:
        insert_calls.append(auto_commit)
        return activo

    monkeypatch.setattr(svc.activo_repo, "soft_delete", _soft)
    monkeypatch.setattr(svc.activo_repo, "insert_transfer", _insert)
    monkeypatch.setattr(
        "app.services.activo_transfer_service.get_connection",
        lambda *_a, **_k: MagicMock(__enter__=lambda s: s, __exit__=lambda *a: None),
    )
    monkeypatch.setattr(
        "app.services.activo_transfer_service.db_transaction",
        lambda *_a, **_k: MagicMock(__enter__=lambda s: s, __exit__=lambda *a: None),
    )
    monkeypatch.setattr(
        "app.services.activo_transfer_service.get_postgres_engine",
        lambda: MagicMock(),
    )
    monkeypatch.setattr(
        "app.services.activo_transfer_service.get_mysql_engine",
        lambda: MagicMock(),
    )

    user = CurrentUser(
        uuid=UUID("11111111-1111-1111-1111-111111111101"),
        email="admin@sicc.com",
        nombre_completo="Admin",
        id_sede=1,
        id_rol=1,
        rol_nombre="Administrador",
        permisos=["*"],
    )
    svc.transferir(
        user,
        UUID(activo["uuid"]),
        ActivoTransferirRequest(sede_destino_id=2, motivo="test"),
    )

    assert soft_calls == [False]
    assert insert_calls == [False]


def test_db_transaction_sets_isolation() -> None:
    conn = MagicMock()
    begin_cm = MagicMock()
    conn.begin.return_value = begin_cm

    with db_transaction(conn, isolation_level="READ COMMITTED"):
        pass

    conn.begin.assert_called_once()
    conn.execute.assert_called_once()
    sql_arg = conn.execute.call_args[0][0]
    assert "READ COMMITTED" in str(sql_arg)
