from sqlmodel import SQLModel
from typing import Optional

class BitacoraCreate(SQLModel):
    id_incidente: int
    id_usuario: int
    comentario: str

class BitacoraUpdate(SQLModel):
    comentario: str
