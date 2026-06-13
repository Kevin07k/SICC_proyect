from sqlalchemy.engine import Engine

from pymongo.database import Database

from app.config import Settings, get_settings
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.mongo import get_mongo_cb_db, get_mongo_sc_db
from app.exceptions import bad_request


class SedeRouter:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def engine_for_sede(self, id_sede: int) -> Engine:
        if id_sede == self.settings.sede_central_id:
            return get_postgres_engine()
        if id_sede == self.settings.sede_secundaria_id:
            return get_mysql_engine()
        raise bad_request(f"Sede {id_sede} no configurada")

    def dialect_for_sede(self, id_sede: int) -> str:
        if id_sede == self.settings.sede_central_id:
            return "postgres"
        if id_sede == self.settings.sede_secundaria_id:
            return "mysql"
        raise bad_request(f"Sede {id_sede} no configurada")

    def sede_for_engine(self, engine: Engine) -> int:
        if engine is get_postgres_engine():
            return self.settings.sede_central_id
        if engine is get_mysql_engine():
            return self.settings.sede_secundaria_id
        raise bad_request("Motor de BD desconocido")

    def mongo_db_for_sede(self, id_sede: int) -> Database:
        if id_sede == self.settings.sede_central_id:
            return get_mongo_sc_db()
        if id_sede == self.settings.sede_secundaria_id:
            return get_mongo_cb_db()
        raise bad_request(f"Sede {id_sede} no configurada")


def get_sede_router() -> SedeRouter:
    return SedeRouter()
