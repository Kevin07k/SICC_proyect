from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SedeMetricas(BaseModel):
    id_sede: int
    nombre_sede: str
    incidentes_total: int
    incidentes_abiertos: int
    activos_total: int
    activos_activos: int
    nodo: str


class ConteoItem(BaseModel):
    nombre: str
    cantidad: int


class ReporteGlobalPayload(BaseModel):
    sedes: list[SedeMetricas]
    incidentes_por_estado: list[ConteoItem]
    incidentes_por_prioridad: list[ConteoItem]
    totales: dict[str, int]


class ReporteGlobalResponse(BaseModel):
    from_cache: bool
    generated_at: datetime
    expires_at: datetime
    ttl_seconds: int
    duration_ms: int | None = None
    payload: ReporteGlobalPayload


class ReporteCacheMeta(BaseModel):
    clave: str = "global"
    generated_at: datetime
    expires_at: datetime
    duration_ms: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
