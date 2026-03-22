from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .incidentes import Incidentes

class cat_Tipos_Incidente(SQLModel, table=True):
    __tablename__ = 'cat_Tipos_Incidente'
    id_tipo: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    incidentes: List["Incidentes"] = Relationship(back_populates="tipo")

class cat_Prioridades(SQLModel, table=True):
    __tablename__ = 'cat_Prioridades'
    id_prioridad: Optional[int] = Field(default=None, primary_key=True)
    nivel: str = Field(max_length=50, unique=True, nullable=False)
    valor_orden: int = Field(unique=True, nullable=False)
    incidentes: List["Incidentes"] = Relationship(back_populates="prioridad")

class cat_Estados(SQLModel, table=True):
    __tablename__ = 'cat_Estados'
    id_estado: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50, unique=True, nullable=False)
    incidentes: List["Incidentes"] = Relationship(back_populates="estado")
