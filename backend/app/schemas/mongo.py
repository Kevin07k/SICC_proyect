from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenciaOut(BaseModel):
    id: str
    incidente_uuid: UUID
    tipo: str
    metadata: dict[str, Any] | None = None
    iocs: list[dict[str, Any]] | None = None
    lineas: list[str] | None = None
    autor_uuid: UUID
    created_at: datetime
    eliminado: bool = False


class EvidenciaCreate(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=50)
    metadata: dict[str, Any] | None = None
    iocs: list[dict[str, Any]] | None = None
    lineas: list[str] | None = None


class TimelineEventoOut(BaseModel):
    id: str
    incidente_uuid: UUID
    tipo_evento: str
    payload: dict[str, Any] = Field(default_factory=dict)
    autor_uuid: UUID
    created_at: datetime
    eliminado: bool = False


class TimelineEventoCreate(BaseModel):
    tipo_evento: str = Field(..., min_length=1, max_length=80)
    payload: dict[str, Any] = Field(default_factory=dict)


class TelemetriaOut(BaseModel):
    id: str
    activo_uuid: UUID
    tipo_escaneo: str
    captured_at: datetime
    hallazgos: list[dict[str, Any]] | None = None
    snapshot: dict[str, Any] | None = None
    eliminado: bool = False


class TelemetriaCreate(BaseModel):
    tipo_escaneo: str = Field(..., min_length=1, max_length=80)
    hallazgos: list[dict[str, Any]] | None = None
    snapshot: dict[str, Any] | None = None
