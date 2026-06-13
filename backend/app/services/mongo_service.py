from datetime import UTC, datetime
from uuid import UUID

from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import not_found
from app.repositories.activo_repo import ActivoRepository
from app.repositories.incidente_repo import IncidenteRepository
from app.repositories.mongo_repo import MongoDocumentRepository
from app.schemas.auth import CurrentUser
from app.schemas.mongo import (
    EvidenciaCreate,
    EvidenciaOut,
    TelemetriaCreate,
    TelemetriaOut,
    TimelineEventoCreate,
    TimelineEventoOut,
)


class MongoDocumentService:
    def __init__(self) -> None:
        self.repo = MongoDocumentRepository()
        self.incidente_repo = IncidenteRepository()
        self.activo_repo = ActivoRepository()
        self.router = SedeRouter()

    def _assert_incidente_local(self, user: CurrentUser, incidente_uuid: UUID) -> None:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            inc = self.incidente_repo.get(conn, dialect, incidente_uuid)
            if not inc or inc["id_sede"] != user.id_sede:
                raise not_found("Incidente no encontrado")

    def _assert_activo_local(self, user: CurrentUser, activo_uuid: UUID) -> None:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            act = self.activo_repo.get(conn, dialect, activo_uuid)
            if not act or act["id_sede"] != user.id_sede or act.get("eliminado"):
                raise not_found("Activo no encontrado")

    def list_evidencias(self, user: CurrentUser, incidente_uuid: UUID) -> list[EvidenciaOut]:
        self._assert_incidente_local(user, incidente_uuid)
        db = self.router.mongo_db_for_sede(user.id_sede)
        rows = self.repo.list_evidencias(db, incidente_uuid)
        return [EvidenciaOut(**r) for r in rows]

    def _auto_log_payload(self, body: EvidenciaCreate, evidencia_id: str) -> dict:
        ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        detalle = ""
        if body.iocs:
            detalle = f" ({len(body.iocs)} IoC(s))"
        elif body.lineas:
            detalle = f" ({len(body.lineas)} línea(s))"
        return {
            "tipo": "log",
            "metadata": {
                "automatico": True,
                "evidencia_ref": evidencia_id,
                "tipo_origen": body.tipo,
            },
            "lineas": [f"{ts} Evidencia tipo {body.tipo} registrada{detalle}"],
        }

    def add_evidencia(
        self, user: CurrentUser, incidente_uuid: UUID, body: EvidenciaCreate
    ) -> EvidenciaOut:
        self._assert_incidente_local(user, incidente_uuid)
        db = self.router.mongo_db_for_sede(user.id_sede)
        row = self.repo.create_evidencia(
            db,
            incidente_uuid,
            user.uuid,
            body.model_dump(exclude_none=True),
        )
        if body.tipo != "log":
            self.repo.create_evidencia(
                db,
                incidente_uuid,
                user.uuid,
                self._auto_log_payload(body, row["id"]),
            )
        return EvidenciaOut(**row)

    def list_timeline(self, user: CurrentUser, incidente_uuid: UUID) -> list[TimelineEventoOut]:
        self._assert_incidente_local(user, incidente_uuid)
        db = self.router.mongo_db_for_sede(user.id_sede)
        rows = self.repo.list_timeline(db, incidente_uuid)
        return [TimelineEventoOut(**r) for r in rows]

    def add_timeline(
        self, user: CurrentUser, incidente_uuid: UUID, body: TimelineEventoCreate
    ) -> TimelineEventoOut:
        self._assert_incidente_local(user, incidente_uuid)
        db = self.router.mongo_db_for_sede(user.id_sede)
        row = self.repo.create_timeline(
            db,
            incidente_uuid,
            user.uuid,
            body.model_dump(exclude_none=True),
        )
        return TimelineEventoOut(**row)

    def list_telemetria(self, user: CurrentUser, activo_uuid: UUID) -> list[TelemetriaOut]:
        self._assert_activo_local(user, activo_uuid)
        db = self.router.mongo_db_for_sede(user.id_sede)
        rows = self.repo.list_telemetria(db, activo_uuid)
        return [TelemetriaOut(**r) for r in rows]

    def add_telemetria(
        self, user: CurrentUser, activo_uuid: UUID, body: TelemetriaCreate
    ) -> TelemetriaOut:
        self._assert_activo_local(user, activo_uuid)
        db = self.router.mongo_db_for_sede(user.id_sede)
        row = self.repo.create_telemetria(
            db,
            activo_uuid,
            body.model_dump(exclude_none=True),
        )
        return TelemetriaOut(**row)
