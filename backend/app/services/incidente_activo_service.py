from uuid import UUID

from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import bad_request, forbidden, not_found
from app.repositories.incidente_activo_repo import IncidenteActivoRepository
from app.repositories.incidente_repo import IncidenteRepository
from app.schemas.auth import CurrentUser
from app.schemas.incidente_activos import IncidenteActivoCreate, IncidenteActivoOut


class IncidenteActivoService:
    def __init__(self) -> None:
        self.repo = IncidenteActivoRepository()
        self.incidente_repo = IncidenteRepository()
        self.router = SedeRouter()

    def _require_incidente(self, user: CurrentUser, incidente_uuid: UUID, conn, dialect: str):
        row = self.incidente_repo.get(conn, dialect, incidente_uuid)
        if not row:
            raise not_found("Incidente no encontrado")
        if row["id_sede"] != user.id_sede:
            raise forbidden("Incidente de otra sede")
        return row

    def list_vinculos(self, user: CurrentUser, incidente_uuid: UUID) -> list[IncidenteActivoOut]:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            self._require_incidente(user, incidente_uuid, conn, dialect)
            rows = self.repo.list_by_incidente(conn, dialect, incidente_uuid)
        return [IncidenteActivoOut(**r) for r in rows]

    def link_activo(
        self, user: CurrentUser, incidente_uuid: UUID, body: IncidenteActivoCreate
    ) -> IncidenteActivoOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            incidente = self._require_incidente(user, incidente_uuid, conn, dialect)
            if self.repo.link_exists(conn, dialect, incidente_uuid, body.id_activo):
                raise bad_request("El activo ya está vinculado a este incidente")
            activo = self.repo.get_activo_with_sede(conn, dialect, body.id_activo)
            if not activo:
                raise not_found("Activo no encontrado o dado de baja")
            if activo["id_sede"] != incidente["id_sede"]:
                raise forbidden("El activo debe pertenecer a la misma sede que el incidente")
            row = self.repo.create_link(
                conn, dialect, incidente_uuid, activo, body.notas
            )
        return IncidenteActivoOut(**row)

    def unlink_activo(
        self, user: CurrentUser, incidente_uuid: UUID, vinculo_uuid: UUID
    ) -> None:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            self._require_incidente(user, incidente_uuid, conn, dialect)
            link = self.repo.get_by_uuid(conn, dialect, vinculo_uuid)
            if not link or str(link["id_incidente"]) != str(incidente_uuid):
                raise not_found("Vínculo no encontrado")
            self.repo.delete_link(conn, dialect, vinculo_uuid)
