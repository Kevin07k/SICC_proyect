from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ActivoCreate(BaseModel):
    hostname: str = Field(min_length=1, max_length=100)
    direccion_ip: str | None = Field(default=None, max_length=45)
    tipo_activo: str | None = Field(default=None, max_length=100)
    propietario: str | None = Field(default=None, max_length=200)


class ActivoUpdate(BaseModel):
    hostname: str | None = Field(default=None, min_length=1, max_length=100)
    direccion_ip: str | None = None
    tipo_activo: str | None = None
    propietario: str | None = None
    eliminado: bool | None = None


class ActivoTransferirRequest(BaseModel):
    sede_destino_id: int
    motivo: str = Field(min_length=3, max_length=500)


class ActivoTransferirResponse(BaseModel):
    uuid: UUID
    sede_origen_id: int
    sede_destino_id: int
    nodo_origen: str
    nodo_destino: str
    motivo: str


class ActivoOut(BaseModel):
    uuid: UUID
    hostname: str
    direccion_ip: str | None
    tipo_activo: str | None
    propietario: str | None
    id_sede: int
    eliminado: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
