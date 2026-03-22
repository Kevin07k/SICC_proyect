from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .incidentes import Incidentes_Activos

class Activos(SQLModel, table=True):
    __tablename__ = 'Activos'
    id_activo: Optional[int] = Field(default=None, primary_key=True)
    hostname: str = Field(max_length=100, unique=True, nullable=False)
    direccion_ip: Optional[str] = Field(default=None, max_length=45)
    tipo_activo: Optional[str] = Field(default=None, max_length=100)
    propietario: Optional[str] = Field(default=None, max_length=200)
    incidentes_links: List["Incidentes_Activos"] = Relationship(back_populates="activo")
