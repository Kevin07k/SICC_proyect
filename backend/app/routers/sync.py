from fastapi import APIRouter, Depends

from app.dependencies import require_permiso
from app.schemas.auth import CurrentUser
from app.schemas.sync import SyncManualResponse, SyncStatusResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


def get_service() -> SyncService:
    return SyncService()


@router.post("/manual", response_model=SyncManualResponse)
def sync_manual(
    user: CurrentUser = Depends(require_permiso("sync.ejecutar")),
    svc: SyncService = Depends(get_service),
) -> SyncManualResponse:
    return svc.run_manual_sync()


@router.get("/status", response_model=SyncStatusResponse)
def sync_status(
    user: CurrentUser = Depends(require_permiso("sync.ejecutar")),
    svc: SyncService = Depends(get_service),
) -> SyncStatusResponse:
    return svc.get_status()
