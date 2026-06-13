from fastapi import APIRouter

from app.db.engines import get_mysql_engine, get_postgres_engine, ping_engine
from app.db.mongo import get_mongo_cb_db, get_mongo_sc_db, ping_mongo_db
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    pg_ok = ping_engine(get_postgres_engine())
    my_ok = ping_engine(get_mysql_engine())
    mongo_sc_ok = ping_mongo_db(get_mongo_sc_db())
    mongo_cb_ok = ping_mongo_db(get_mongo_cb_db())
    all_ok = pg_ok and my_ok and mongo_sc_ok and mongo_cb_ok
    status = "ok" if all_ok else "degraded"
    return HealthResponse(
        status=status,
        postgres=pg_ok,
        mysql=my_ok,
        mongo_sc=mongo_sc_ok,
        mongo_cb=mongo_cb_ok,
    )
