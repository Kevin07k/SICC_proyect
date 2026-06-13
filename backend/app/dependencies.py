from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.engine import Connection

from app.config import Settings, get_settings
from app.core.sede_router import SedeRouter, get_sede_router
from app.db.session import get_connection
from app.exceptions import forbidden, unauthorized
from app.schemas.auth import CurrentUser
from app.services.auth_service import AuthService


def get_auth_service() -> AuthService:
    return AuthService()


async def get_current_user(
    x_usuario_uuid: Annotated[str | None, Header(alias="X-Usuario-UUID")] = None,
    auth: AuthService = Depends(get_auth_service),
) -> CurrentUser:
    if not x_usuario_uuid:
        raise unauthorized("Header X-Usuario-UUID requerido")
    try:
        user_uuid = UUID(x_usuario_uuid)
    except ValueError as exc:
        raise unauthorized("UUID inválido") from exc
    user = auth.get_user_by_uuid(user_uuid)
    if not user:
        raise unauthorized("Usuario no encontrado o inactivo")
    return user


def require_permiso(codigo: str) -> Callable:
    async def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.rol_nombre == "Administrador":
            return user
        if codigo not in user.permisos:
            raise forbidden(f"Permiso requerido: {codigo}")
        return user

    return _checker


def require_any_permiso(*codigos: str) -> Callable:
    async def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.rol_nombre == "Administrador":
            return user
        if any(c in user.permisos for c in codigos):
            return user
        raise forbidden(f"Permiso requerido: uno de {', '.join(codigos)}")

    return _checker


def _assert_sede_central(user: CurrentUser, settings: Settings) -> None:
    if user.id_sede != settings.sede_central_id:
        raise forbidden("Operación disponible solo en sede central (Santa Cruz)")


def require_sede_central() -> Callable:
    async def _checker(
        user: CurrentUser = Depends(get_current_user),
        settings: Settings = Depends(get_settings),
    ) -> CurrentUser:
        _assert_sede_central(user, settings)
        return user

    return _checker


def require_central_permiso(codigo: str) -> Callable:
    """Permiso de aplicación + usuario de la sede central."""

    async def _checker(
        user: CurrentUser = Depends(require_permiso(codigo)),
        settings: Settings = Depends(get_settings),
    ) -> CurrentUser:
        _assert_sede_central(user, settings)
        return user

    return _checker


def get_db_for_user(
    user: CurrentUser = Depends(get_current_user),
    router: SedeRouter = Depends(get_sede_router),
) -> Connection:
    engine = router.engine_for_sede(user.id_sede)
    with get_connection(engine) as conn:
        yield conn


def get_postgres_conn(
    router: SedeRouter = Depends(get_sede_router),
) -> Connection:
    engine = router.engine_for_sede(router.settings.sede_central_id)
    with get_connection(engine) as conn:
        yield conn


def get_mysql_conn(
    router: SedeRouter = Depends(get_sede_router),
) -> Connection:
    engine = router.engine_for_sede(router.settings.sede_secundaria_id)
    with get_connection(engine) as conn:
        yield conn
