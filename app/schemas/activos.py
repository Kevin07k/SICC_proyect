from sqlmodel import SQLModel
from typing import Optional

class ActivoCreate(SQLModel):
    hostname: str
    direccion_ip: Optional[str] = None
    tipo_activo: Optional[str] = None
    propietario: Optional[str] = None
    id_sede: Optional[int] = None

class ActivoUpdate(SQLModel):
    hostname: Optional[str] = None
    direccion_ip: Optional[str] = None
    tipo_activo: Optional[str] = None
    propietario: Optional[str] = None
    id_sede: Optional[int] = None
