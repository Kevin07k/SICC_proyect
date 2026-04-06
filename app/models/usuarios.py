from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mssql import DATETIME2, BIT
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .incidentes import Incidentes
    from .bitacora import Bitacora_Investigacion

class Usuarios(SQLModel, table=True):
    __tablename__ = 'Usuarios'
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    nombre_completo: str = Field(max_length=200, nullable=False)
    email: str = Field(max_length=255, unique=True, nullable=False)
    rol: str = Field(max_length=100, nullable=False, default='Analista')
    fecha_creacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    fecha_actualizacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    eliminado: bool = Field(default=False, sa_column=Column(BIT, server_default="0", nullable=False))
    incidentes_asignados: List["Incidentes"] = Relationship(back_populates="usuario_asignado")
    bitacoras: List["Bitacora_Investigacion"] = Relationship(back_populates="usuario")
