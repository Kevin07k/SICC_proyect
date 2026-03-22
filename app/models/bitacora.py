from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .incidentes import Incidentes
    from .usuarios import Usuarios

class Bitacora_Investigacion(SQLModel, table=True):
    __tablename__ = 'Bitacora_Investigacion'

    id_bitacora: Optional[int] = Field(default=None, primary_key=True)

    id_incidente: int = Field(foreign_key="Incidentes.id_incidente")
    id_usuario: int = Field(foreign_key="Usuarios.id_usuario")

    fecha_entrada: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DATETIME2, server_default=func.now(), nullable=False)
    )
    comentario: str = Field(max_length=300, nullable=False)

    incidente: "Incidentes" = Relationship(back_populates="bitacoras")
    usuario: "Usuarios" = Relationship(back_populates="bitacoras")
