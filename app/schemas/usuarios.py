from sqlmodel import SQLModel
from typing import Optional

class UsuarioCreate(SQLModel):
    nombre_completo: str
    email: str
    rol: str = 'Analista'

class UsuarioUpdate(SQLModel):
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None
