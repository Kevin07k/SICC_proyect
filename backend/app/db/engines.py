from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import get_settings


@lru_cache
def get_postgres_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.postgres_url,
        pool_pre_ping=True,
        pool_size=5,
    )


@lru_cache
def get_mysql_engine() -> Engine:
    settings = get_settings()
    connect_args: dict = {}
    if not settings.mysql_ssl:
        connect_args["ssl"] = False
    return create_engine(
        settings.mysql_url,
        pool_pre_ping=True,
        pool_size=5,
        connect_args=connect_args,
    )


def ping_engine(engine: Engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
