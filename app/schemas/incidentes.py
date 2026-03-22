from sqlmodel import SQLModel
from typing import Optional

class IncidenteCreate(SQLModel):
    titulo: str
    descripcion_detallada: str
    id_tipo: int
    id_prioridad: int
    id_estado: int
    id_usuario_asignado: Optional[int] = None

class IncidenteUpdate(SQLModel):
    titulo: Optional[str] = None
    descripcion_detallada: Optional[str] = None
    id_tipo: Optional[int] = None
    id_prioridad: Optional[int] = None
    id_estado: Optional[int] = None
    id_usuario_asignado: Optional[int] = None

class IncidenteActivoCreate(SQLModel):
    id_incidente: int
    id_activo: int
    notas_relacion: Optional[str] = None
