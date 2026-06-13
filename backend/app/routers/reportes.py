from fastapi import APIRouter, Depends, Query

from app.dependencies import require_central_permiso
from app.schemas.auth import CurrentUser
from app.schemas.reportes import ReporteGlobalResponse
from app.services.reporte_service import ReporteService

router = APIRouter(prefix="/reportes", tags=["reportes"])


def get_service() -> ReporteService:
    return ReporteService()


@router.get("/global", response_model=ReporteGlobalResponse)
def get_reporte_global(
    refresh: bool = Query(False, description="Forzar recálculo ignorando caché vigente"),
    _user: CurrentUser = Depends(require_central_permiso("reportes.ver")),
    svc: ReporteService = Depends(get_service),
) -> ReporteGlobalResponse:
    return svc.get_global(force_refresh=refresh)


@router.post("/global/regenerar", response_model=ReporteGlobalResponse)
def regenerar_reporte_global(
    _user: CurrentUser = Depends(require_central_permiso("reportes.ver")),
    svc: ReporteService = Depends(get_service),
) -> ReporteGlobalResponse:
    return svc.get_global(force_refresh=True)
