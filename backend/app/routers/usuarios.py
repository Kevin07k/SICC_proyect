from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import require_permiso
from app.schemas.auth import CurrentUser
from app.schemas.usuarios import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def get_service() -> UsuarioService:
    return UsuarioService()


@router.get("", response_model=list[UsuarioOut])
def list_usuarios(
    user: CurrentUser = Depends(require_permiso("usuarios.ver")),
    svc: UsuarioService = Depends(get_service),
) -> list[UsuarioOut]:
    return svc.list_users(user)


@router.get("/{user_uuid}", response_model=UsuarioOut)
def get_usuario(
    user_uuid: UUID,
    user: CurrentUser = Depends(require_permiso("usuarios.ver")),
    svc: UsuarioService = Depends(get_service),
) -> UsuarioOut:
    return svc.get_user(user, user_uuid)


@router.post("", response_model=UsuarioOut, status_code=201)
def create_usuario(
    body: UsuarioCreate,
    user: CurrentUser = Depends(require_permiso("usuarios.gestionar")),
    svc: UsuarioService = Depends(get_service),
) -> UsuarioOut:
    return svc.create_user(user, body)


@router.patch("/{user_uuid}", response_model=UsuarioOut)
def update_usuario(
    user_uuid: UUID,
    body: UsuarioUpdate,
    user: CurrentUser = Depends(require_permiso("usuarios.gestionar")),
    svc: UsuarioService = Depends(get_service),
) -> UsuarioOut:
    return svc.update_user(user, user_uuid, body)
