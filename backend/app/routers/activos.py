from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import require_permiso
from app.schemas.activos import (
    ActivoCreate,
    ActivoOut,
    ActivoTransferirRequest,
    ActivoTransferirResponse,
    ActivoUpdate,
)
from app.schemas.auth import CurrentUser
from app.services.activo_service import ActivoService
from app.services.activo_transfer_service import ActivoTransferService

router = APIRouter(prefix="/activos", tags=["activos"])


def get_service() -> ActivoService:
    return ActivoService()


def get_transfer_service() -> ActivoTransferService:
    return ActivoTransferService()


@router.get("", response_model=list[ActivoOut])
def list_activos(
    user: CurrentUser = Depends(require_permiso("activos.ver")),
    svc: ActivoService = Depends(get_service),
) -> list[ActivoOut]:
    return svc.list_activos(user)


@router.get("/{activo_uuid}", response_model=ActivoOut)
def get_activo(
    activo_uuid: UUID,
    user: CurrentUser = Depends(require_permiso("activos.ver")),
    svc: ActivoService = Depends(get_service),
) -> ActivoOut:
    return svc.get_activo(user, activo_uuid)


@router.post("", response_model=ActivoOut, status_code=201)
def create_activo(
    body: ActivoCreate,
    user: CurrentUser = Depends(require_permiso("activos.gestionar")),
    svc: ActivoService = Depends(get_service),
) -> ActivoOut:
    return svc.create_activo(user, body)


@router.patch("/{activo_uuid}", response_model=ActivoOut)
def update_activo(
    activo_uuid: UUID,
    body: ActivoUpdate,
    user: CurrentUser = Depends(require_permiso("activos.gestionar")),
    svc: ActivoService = Depends(get_service),
) -> ActivoOut:
    return svc.update_activo(user, activo_uuid, body)


@router.post("/{activo_uuid}/transferir", response_model=ActivoTransferirResponse)
def transferir_activo(
    activo_uuid: UUID,
    body: ActivoTransferirRequest,
    user: CurrentUser = Depends(require_permiso("activos.gestionar")),
    svc: ActivoTransferService = Depends(get_transfer_service),
) -> ActivoTransferirResponse:
    return svc.transferir(user, activo_uuid, body)
