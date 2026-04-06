from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, NVARCHAR, UniqueConstraint
from sqlalchemy.dialects.mssql import DATETIME2, BIT
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .categorias import cat_Tipos_Incidente, cat_Prioridades, cat_Estados
    from .usuarios import Usuarios
    from .activos import Activos
    from .bitacora import Bitacora_Investigacion

class Incidentes(SQLModel, table=True):
    __tablename__ = 'Incidentes'

    id_incidente: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=255, nullable=False)
    descripcion_detallada: str = Field(sa_column=Column(NVARCHAR, nullable=False))
    
    fecha_creacion: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DATETIME2, server_default=func.now(), nullable=False)
    )
    fecha_actualizacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    eliminado: bool = Field(default=False, sa_column=Column(BIT, server_default="0", nullable=False))
    fecha_cierre: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2))

    id_tipo: int = Field(foreign_key="cat_Tipos_Incidente.id_tipo")
    id_prioridad: int = Field(foreign_key="cat_Prioridades.id_prioridad")
    id_estado: int = Field(foreign_key="cat_Estados.id_estado")
    id_usuario_asignado: Optional[int] = Field(default=None, foreign_key="Usuarios.id_usuario")

    tipo: "cat_Tipos_Incidente" = Relationship(back_populates="incidentes")
    prioridad: "cat_Prioridades" = Relationship(back_populates="incidentes")
    estado: "cat_Estados" = Relationship(back_populates="incidentes")
    usuario_asignado: Optional["Usuarios"] = Relationship(back_populates="incidentes_asignados")
    
    bitacoras: List["Bitacora_Investigacion"] = Relationship(back_populates="incidente")
    activos_links: List["Incidentes_Activos"] = Relationship(back_populates="incidente")

class Incidentes_Activos(SQLModel, table=True):
    __tablename__ = 'Incidentes_Activos'

    id_incidente_activo: Optional[int] = Field(default=None, primary_key=True)

    id_incidente: int = Field(foreign_key="Incidentes.id_incidente")
    id_activo: int = Field(foreign_key="Activos.id_activo")

    notas_relacion: Optional[str] = Field(default=None, max_length=300)
    fecha_creacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    fecha_actualizacion: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME2, server_default=func.now(), nullable=False))
    eliminado: bool = Field(default=False, sa_column=Column(BIT, server_default="0", nullable=False))

    incidente: "Incidentes" = Relationship(back_populates="activos_links")
    activo: "Activos" = Relationship(back_populates="incidentes_links")

    __table_args__ = (
        UniqueConstraint("id_incidente", "id_activo", name="UQ_Incidente_Activo"),
    )
