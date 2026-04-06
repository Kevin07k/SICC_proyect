from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mssql import DATETIME2, BIT
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .incidentes import Incidentes_Activos

class Activos(SQLModel, table=True):
    __tablename__ = 'Activos'
    id_activo: Optional[int] = Field(default=None, primary_key=True)
    hostname: str = Field(max_length=100, unique=True, nullable=False)
    direccion_ip: Optional[str] = Field(default=None, max_length=45)
    tipo_activo: Optional[str] = Field(default=None, max_length=100)
    propietario: Optional[str] = Field(default=None, max_length=200)
    id_sede: Optional[int] = Field(default=None, foreign_key="cat_Sedes.id_sede")
    fecha_creacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    fecha_actualizacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    eliminado: bool = Field(default=False, sa_column=Column(BIT, server_default="0", nullable=False))
    incidentes_links: List["Incidentes_Activos"] = Relationship(back_populates="activo")
