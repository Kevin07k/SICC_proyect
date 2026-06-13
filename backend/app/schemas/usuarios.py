from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nombre_completo: str = Field(min_length=2, max_length=200)
    id_rol: int
    id_sede: int | None = Field(
        default=None,
        description="Sede del usuario; por defecto la del operador. Admin/DBA pueden asignar otra.",
    )


class UsuarioUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6)
    nombre_completo: str | None = None
    id_rol: int | None = None
    activo: bool | None = None


class UsuarioOut(BaseModel):
    uuid: UUID
    email: str
    nombre_completo: str
    id_sede: int
    id_rol: int
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
