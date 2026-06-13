from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import require_any_permiso
from app.schemas.auth import CurrentUser
from app.schemas.mongo import (
    EvidenciaCreate,
    EvidenciaOut,
    TelemetriaCreate,
    TelemetriaOut,
    TimelineEventoCreate,
    TimelineEventoOut,
)
from app.services.mongo_service import MongoDocumentService

incidente_router = APIRouter(prefix="/incidentes", tags=["documentos"])
activo_router = APIRouter(prefix="/activos", tags=["documentos"])

VER_INCIDENTE_DOCS = require_any_permiso("incidentes.ver", "documentos.ver")
GESTIONAR_INCIDENTE_DOCS = require_any_permiso(
    "incidentes.gestionar", "documentos.gestionar"
)
VER_ACTIVO_DOCS = require_any_permiso("activos.ver", "documentos.ver")
GESTIONAR_ACTIVO_DOCS = require_any_permiso("activos.gestionar", "documentos.gestionar")


def get_service() -> MongoDocumentService:
    return MongoDocumentService()


@incidente_router.get("/{incidente_uuid}/evidencias", response_model=list[EvidenciaOut])
def list_evidencias(
    incidente_uuid: UUID,
    user: CurrentUser = Depends(VER_INCIDENTE_DOCS),
    svc: MongoDocumentService = Depends(get_service),
) -> list[EvidenciaOut]:
    return svc.list_evidencias(user, incidente_uuid)


@incidente_router.post(
    "/{incidente_uuid}/evidencias",
    response_model=EvidenciaOut,
    status_code=201,
)
def create_evidencia(
    incidente_uuid: UUID,
    body: EvidenciaCreate,
    user: CurrentUser = Depends(GESTIONAR_INCIDENTE_DOCS),
    svc: MongoDocumentService = Depends(get_service),
) -> EvidenciaOut:
    return svc.add_evidencia(user, incidente_uuid, body)


@incidente_router.get("/{incidente_uuid}/timeline", response_model=list[TimelineEventoOut])
def list_timeline(
    incidente_uuid: UUID,
    user: CurrentUser = Depends(VER_INCIDENTE_DOCS),
    svc: MongoDocumentService = Depends(get_service),
) -> list[TimelineEventoOut]:
    return svc.list_timeline(user, incidente_uuid)


@incidente_router.post(
    "/{incidente_uuid}/timeline",
    response_model=TimelineEventoOut,
    status_code=201,
)
def create_timeline(
    incidente_uuid: UUID,
    body: TimelineEventoCreate,
    user: CurrentUser = Depends(GESTIONAR_INCIDENTE_DOCS),
    svc: MongoDocumentService = Depends(get_service),
) -> TimelineEventoOut:
    return svc.add_timeline(user, incidente_uuid, body)


@activo_router.get("/{activo_uuid}/telemetria", response_model=list[TelemetriaOut])
def list_telemetria(
    activo_uuid: UUID,
    user: CurrentUser = Depends(VER_ACTIVO_DOCS),
    svc: MongoDocumentService = Depends(get_service),
) -> list[TelemetriaOut]:
    return svc.list_telemetria(user, activo_uuid)


@activo_router.post(
    "/{activo_uuid}/telemetria",
    response_model=TelemetriaOut,
    status_code=201,
)
def create_telemetria(
    activo_uuid: UUID,
    body: TelemetriaCreate,
    user: CurrentUser = Depends(GESTIONAR_ACTIVO_DOCS),
    svc: MongoDocumentService = Depends(get_service),
) -> TelemetriaOut:
    return svc.add_telemetria(user, activo_uuid, body)
