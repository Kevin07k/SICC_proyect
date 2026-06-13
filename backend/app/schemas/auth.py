from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    uuid: UUID
    email: str
    nombre_completo: str
    id_sede: int
    id_rol: int
    rol_nombre: str
    permisos: list[str]


class CurrentUser(BaseModel):
    uuid: UUID
    email: str
    nombre_completo: str
    id_sede: int
    id_rol: int
    rol_nombre: str
    permisos: list[str]
