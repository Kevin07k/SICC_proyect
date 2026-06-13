from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BitacoraCreate(BaseModel):
    comentario: str = Field(min_length=1)


class BitacoraOut(BaseModel):
    uuid: UUID
    id_incidente: UUID
    id_usuario: UUID
    comentario: str
    eliminado: bool = False
    created_at: datetime | None = None
    usuario_nombre: str | None = None
