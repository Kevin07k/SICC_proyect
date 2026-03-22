from sqlmodel import SQLModel
from typing import Optional

class TipoIncidenteCreate(SQLModel):
    nombre: str
    descripcion: Optional[str] = None

class PrioridadCreate(SQLModel):
    nivel: str
    valor_orden: int

class EstadoCreate(SQLModel):
    nombre: str

class TipoIncidenteUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
