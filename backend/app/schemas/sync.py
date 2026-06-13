from datetime import datetime

from pydantic import BaseModel


class SyncManualResponse(BaseModel):
    last_sync: datetime
    tablas_procesadas: list[str]
    registros_aplicados: int


class SyncTableStatus(BaseModel):
    tabla: str
    pendientes_postgres: int
    pendientes_mysql: int


class SyncStatusResponse(BaseModel):
    last_sync_postgres: datetime | None
    last_sync_mysql: datetime | None
    effective_last_sync: datetime | None
    tablas: list[SyncTableStatus]
