from collections.abc import Generator
from contextlib import contextmanager
from typing import Literal

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

IsolationLevel = Literal[
    "READ UNCOMMITTED",
    "READ COMMITTED",
    "REPEATABLE READ",
    "SERIALIZABLE",
]


@contextmanager
def get_connection(engine: Engine) -> Generator[Connection, None, None]:
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


def connection_dep(engine: Engine) -> Generator[Connection, None, None]:
    with get_connection(engine) as conn:
        yield conn


@contextmanager
def db_transaction(
    conn: Connection,
    *,
    isolation_level: IsolationLevel | None = None,
) -> Generator[Connection, None, None]:
    """
    Unidad de trabajo ACID en un solo motor.
    Si isolation_level se indica, debe ser la primera sentencia de la transacción.
    """
    with conn.begin():
        if isolation_level is not None:
            conn.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
        yield conn


@contextmanager
def db_transaction_read_committed(conn: Connection) -> Generator[Connection, None, None]:
    with db_transaction(conn, isolation_level="READ COMMITTED"):
        yield conn


@contextmanager
def db_transaction_repeatable_read(conn: Connection) -> Generator[Connection, None, None]:
    with db_transaction(conn, isolation_level="REPEATABLE READ"):
        yield conn
