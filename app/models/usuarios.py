from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .incidentes import Incidentes
    from .bitacora import Bitacora_Investigacion

class Usuarios(SQLModel, table=True):
    __tablename__ = 'Usuarios'
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    nombre_completo: str = Field(max_length=200, nullable=False)
    email: str = Field(max_length=255, unique=True, nullable=False)
    rol: str = Field(max_length=100, nullable=False, default='Analista')
    incidentes_asignados: List["Incidentes"] = Relationship(back_populates="usuario_asignado")
    bitacoras: List["Bitacora_Investigacion"] = Relationship(back_populates="usuario")
