from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IncidenteActivoCreate(BaseModel):
    id_activo: UUID
    notas: str | None = Field(default=None, max_length=300)


class IncidenteActivoOut(BaseModel):
    uuid: UUID
    id_incidente: UUID
    id_activo: UUID
    notas: str | None
    tipo_activo_registrado: str | None
    sede_registrada: str | None
    hostname_registrado: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    hostname_actual: str | None = None
    activo_eliminado: bool | None = None
