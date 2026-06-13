from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.incidente_activos import IncidenteActivoOut


class IncidenteCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=255)
    descripcion: str | None = None
    id_tipo: int
    id_prioridad: int
    id_estado: int
    id_usuario_asignado: UUID | None = None
    activos: list[UUID] = Field(default_factory=list)


class IncidenteUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=255)
    descripcion: str | None = None
    id_tipo: int | None = None
    id_prioridad: int | None = None
    id_estado: int | None = None
    id_usuario_asignado: UUID | None = None
    fecha_cierre: datetime | None = None
    eliminado: bool | None = None


class IncidenteOut(BaseModel):
    uuid: UUID
    titulo: str
    descripcion: str | None
    id_tipo: int
    id_prioridad: int
    id_estado: int
    id_usuario_asignado: UUID
    id_sede: int
    fecha_cierre: datetime | None
    eliminado: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    tipo_nombre: str | None = None
    prioridad_nivel: str | None = None
    estado_nombre: str | None = None
    activos_vinculados: list[IncidenteActivoOut] = Field(default_factory=list)
