from fastapi import APIRouter, Depends, Response

from app.dependencies import get_current_user, require_central_permiso
from app.schemas.auth import CurrentUser
from app.schemas.catalogos import (
    EstadoOut,
    PrioridadOut,
    SedeOut,
    TipoIncidenteCreate,
    TipoIncidenteOut,
    TipoIncidenteUpdate,
)
from app.services.catalogo_service import CatalogoService

router = APIRouter(prefix="/catalogos", tags=["catalogos"])


def get_service() -> CatalogoService:
    return CatalogoService()


@router.get("/sedes", response_model=list[SedeOut])
def list_sedes(
    user: CurrentUser = Depends(get_current_user),
    svc: CatalogoService = Depends(get_service),
) -> list[SedeOut]:
    return svc.list_sedes(user)


@router.get("/estados", response_model=list[EstadoOut])
def list_estados(
    user: CurrentUser = Depends(get_current_user),
    svc: CatalogoService = Depends(get_service),
) -> list[EstadoOut]:
    return svc.list_estados(user)


@router.get("/prioridades", response_model=list[PrioridadOut])
def list_prioridades(
    user: CurrentUser = Depends(get_current_user),
    svc: CatalogoService = Depends(get_service),
) -> list[PrioridadOut]:
    return svc.list_prioridades(user)


@router.get("/tipos-incidente", response_model=list[TipoIncidenteOut])
def list_tipos(
    user: CurrentUser = Depends(get_current_user),
    svc: CatalogoService = Depends(get_service),
) -> list[TipoIncidenteOut]:
    """Lista activos para formularios de incidentes (cualquier sede autenticada)."""
    return svc.list_tipos(user)


@router.get(
    "/tipos-incidente/gestion",
    response_model=list[TipoIncidenteOut],
)
def list_tipos_gestion(
    _user: CurrentUser = Depends(require_central_permiso("catalogos.gestionar")),
    svc: CatalogoService = Depends(get_service),
) -> list[TipoIncidenteOut]:
    """Administración central: incluye tipos dados de baja."""
    return svc.list_tipos_gestion(_user)


@router.post(
    "/tipos-incidente",
    response_model=TipoIncidenteOut,
    status_code=201,
)
def create_tipo(
    body: TipoIncidenteCreate,
    user: CurrentUser = Depends(require_central_permiso("catalogos.gestionar")),
    svc: CatalogoService = Depends(get_service),
) -> TipoIncidenteOut:
    return svc.create_tipo(user, body)


@router.patch("/tipos-incidente/{id_tipo}", response_model=TipoIncidenteOut)
def update_tipo(
    id_tipo: int,
    body: TipoIncidenteUpdate,
    user: CurrentUser = Depends(require_central_permiso("catalogos.gestionar")),
    svc: CatalogoService = Depends(get_service),
) -> TipoIncidenteOut:
    return svc.update_tipo(user, id_tipo, body)


@router.delete("/tipos-incidente/{id_tipo}", status_code=204)
def delete_tipo(
    id_tipo: int,
    user: CurrentUser = Depends(require_central_permiso("catalogos.gestionar")),
    svc: CatalogoService = Depends(get_service),
) -> Response:
    svc.delete_tipo(user, id_tipo)
    return Response(status_code=204)
