from datetime import datetime

from pydantic import BaseModel, Field


class SedeOut(BaseModel):
    id_sede: int
    nombre_sede: str
    nivel_criticidad: str
    eliminado: bool = False


class EstadoOut(BaseModel):
    id_estado: int
    nombre: str
    eliminado: bool = False


class PrioridadOut(BaseModel):
    id_prioridad: int
    nivel: str
    valor_orden: int
    eliminado: bool = False


class TipoIncidenteOut(BaseModel):
    id_tipo: int
    nombre: str
    descripcion: str | None = None
    eliminado: bool = False


class TipoIncidenteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str | None = Field(None, max_length=500)


class TipoIncidenteUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100)
    descripcion: str | None = Field(None, max_length=500)


class CatalogoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    nivel: str | None = None
    valor_orden: int | None = None
    nivel_criticidad: str | None = None
