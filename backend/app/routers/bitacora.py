from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import require_permiso
from app.schemas.auth import CurrentUser
from app.schemas.bitacora import BitacoraCreate, BitacoraOut
from app.services.bitacora_service import BitacoraService

router = APIRouter(prefix="/incidentes", tags=["bitacora"])


def get_service() -> BitacoraService:
    return BitacoraService()


@router.get("/{incidente_uuid}/bitacora", response_model=list[BitacoraOut])
def list_bitacora(
    incidente_uuid: UUID,
    user: CurrentUser = Depends(require_permiso("bitacora.ver")),
    svc: BitacoraService = Depends(get_service),
) -> list[BitacoraOut]:
    return svc.list_entries(user, incidente_uuid)


@router.post("/{incidente_uuid}/bitacora", response_model=BitacoraOut, status_code=201)
def create_bitacora(
    incidente_uuid: UUID,
    body: BitacoraCreate,
    user: CurrentUser = Depends(require_permiso("incidentes.gestionar")),
    svc: BitacoraService = Depends(get_service),
) -> BitacoraOut:
    return svc.add_entry(user, incidente_uuid, body)
