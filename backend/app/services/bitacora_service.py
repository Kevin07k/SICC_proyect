from uuid import UUID

from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import not_found
from app.repositories.bitacora_repo import BitacoraRepository
from app.repositories.incidente_repo import IncidenteRepository
from app.schemas.auth import CurrentUser
from app.schemas.bitacora import BitacoraCreate, BitacoraOut


class BitacoraService:
    def __init__(self) -> None:
        self.repo = BitacoraRepository()
        self.incidente_repo = IncidenteRepository()
        self.router = SedeRouter()

    def list_entries(self, user: CurrentUser, incidente_uuid: UUID) -> list[BitacoraOut]:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            inc = self.incidente_repo.get(conn, dialect, incidente_uuid)
            if not inc or inc["id_sede"] != user.id_sede:
                raise not_found("Incidente no encontrado")
            rows = self.repo.list_by_incidente(conn, dialect, incidente_uuid)
        return [BitacoraOut(**r) for r in rows]

    def add_entry(
        self, user: CurrentUser, incidente_uuid: UUID, body: BitacoraCreate
    ) -> BitacoraOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            inc = self.incidente_repo.get(conn, dialect, incidente_uuid)
            if not inc or inc["id_sede"] != user.id_sede:
                raise not_found("Incidente no encontrado")
            row = self.repo.create(
                conn, dialect, incidente_uuid, user.uuid, body.comentario
            )
        return BitacoraOut(**row)
