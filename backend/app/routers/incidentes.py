from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import require_permiso
from app.schemas.auth import CurrentUser
from app.schemas.incidente_activos import IncidenteActivoCreate, IncidenteActivoOut
from app.schemas.incidentes import IncidenteCreate, IncidenteOut, IncidenteUpdate
from app.services.incidente_activo_service import IncidenteActivoService
from app.services.incidente_service import IncidenteService

router = APIRouter(prefix="/incidentes", tags=["incidentes"])


def get_service() -> IncidenteService:
    return IncidenteService()


def get_vinculo_service() -> IncidenteActivoService:
    return IncidenteActivoService()


@router.get("", response_model=list[IncidenteOut])
def list_incidentes(
    user: CurrentUser = Depends(require_permiso("incidentes.ver")),
    svc: IncidenteService = Depends(get_service),
) -> list[IncidenteOut]:
    return svc.list_incidentes(user)


@router.get("/{incidente_uuid}", response_model=IncidenteOut)
def get_incidente(
    incidente_uuid: UUID,
    user: CurrentUser = Depends(require_permiso("incidentes.ver")),
    svc: IncidenteService = Depends(get_service),
) -> IncidenteOut:
    return svc.get_incidente(user, incidente_uuid)


@router.post("", response_model=IncidenteOut, status_code=201)
def create_incidente(
    body: IncidenteCreate,
    user: CurrentUser = Depends(require_permiso("incidentes.gestionar")),
    svc: IncidenteService = Depends(get_service),
) -> IncidenteOut:
    return svc.create_incidente(user, body)


@router.patch("/{incidente_uuid}", response_model=IncidenteOut)
def update_incidente(
    incidente_uuid: UUID,
    body: IncidenteUpdate,
    user: CurrentUser = Depends(require_permiso("incidentes.gestionar")),
    svc: IncidenteService = Depends(get_service),
) -> IncidenteOut:
    return svc.update_incidente(user, incidente_uuid, body)


@router.get("/{incidente_uuid}/activos", response_model=list[IncidenteActivoOut])
def list_incidente_activos(
    incidente_uuid: UUID,
    user: CurrentUser = Depends(require_permiso("incidentes.ver")),
    svc: IncidenteActivoService = Depends(get_vinculo_service),
) -> list[IncidenteActivoOut]:
    return svc.list_vinculos(user, incidente_uuid)


@router.post(
    "/{incidente_uuid}/activos",
    response_model=IncidenteActivoOut,
    status_code=201,
)
def link_incidente_activo(
    incidente_uuid: UUID,
    body: IncidenteActivoCreate,
    user: CurrentUser = Depends(require_permiso("incidentes.gestionar")),
    svc: IncidenteActivoService = Depends(get_vinculo_service),
) -> IncidenteActivoOut:
    return svc.link_activo(user, incidente_uuid, body)


@router.delete("/{incidente_uuid}/activos/{vinculo_uuid}", status_code=204)
def unlink_incidente_activo(
    incidente_uuid: UUID,
    vinculo_uuid: UUID,
    user: CurrentUser = Depends(require_permiso("incidentes.gestionar")),
    svc: IncidenteActivoService = Depends(get_vinculo_service),
) -> None:
    svc.unlink_activo(user, incidente_uuid, vinculo_uuid)
