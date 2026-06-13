from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.config import Settings, get_settings


def _mongo_uri(host: str, port: int, user: str, password: str, db: str) -> str:
    return (
        f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource=admin"
    )


@lru_cache
def get_mongo_sc_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(
        _mongo_uri(
            settings.mongo_sc_host,
            settings.mongo_sc_port,
            settings.mongo_sc_user,
            settings.mongo_sc_password,
            settings.mongo_sc_db,
        ),
        serverSelectionTimeoutMS=3000,
    )


@lru_cache
def get_mongo_cb_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(
        _mongo_uri(
            settings.mongo_cb_host,
            settings.mongo_cb_port,
            settings.mongo_cb_user,
            settings.mongo_cb_password,
            settings.mongo_cb_db,
        ),
        serverSelectionTimeoutMS=3000,
    )


def get_mongo_sc_db() -> Database:
    settings = get_settings()
    return get_mongo_sc_client()[settings.mongo_sc_db]


def get_mongo_cb_db() -> Database:
    settings = get_settings()
    return get_mongo_cb_client()[settings.mongo_cb_db]


def ping_mongo_db(db: Database) -> bool:
    try:
        db.command("ping")
        return True
    except PyMongoError:
        return False
