from uuid import UUID

from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import forbidden, not_found
from app.repositories.activo_repo import ActivoRepository
from app.schemas.activos import ActivoCreate, ActivoOut, ActivoUpdate
from app.schemas.auth import CurrentUser


class ActivoService:
    def __init__(self) -> None:
        self.repo = ActivoRepository()
        self.router = SedeRouter()

    def list_activos(self, user: CurrentUser) -> list[ActivoOut]:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            rows = self.repo.list_by_sede(conn, dialect, user.id_sede)
        return [ActivoOut(**r) for r in rows]

    def get_activo(self, user: CurrentUser, activo_uuid: UUID) -> ActivoOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            row = self.repo.get(conn, dialect, activo_uuid)
        if not row:
            raise not_found("Activo no encontrado")
        if row["id_sede"] != user.id_sede and not row.get("eliminado"):
            raise forbidden("Activo de otra sede")
        if row["id_sede"] != user.id_sede:
            raise not_found("Activo no encontrado en su sede")
        return ActivoOut(**row)

    def create_activo(self, user: CurrentUser, body: ActivoCreate) -> ActivoOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        data = {
            "hostname": body.hostname,
            "direccion_ip": body.direccion_ip,
            "tipo_activo": body.tipo_activo,
            "propietario": body.propietario,
            "id_sede": user.id_sede,
        }
        with get_connection(engine) as conn:
            row = self.repo.create(conn, dialect, data)
        return ActivoOut(**row)

    def update_activo(
        self, user: CurrentUser, activo_uuid: UUID, body: ActivoUpdate
    ) -> ActivoOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        fields = body.model_dump(exclude_unset=True)
        with get_connection(engine) as conn:
            existing = self.repo.get(conn, dialect, activo_uuid)
            if not existing or existing["id_sede"] != user.id_sede:
                raise not_found("Activo no encontrado")
            row = self.repo.update(conn, dialect, activo_uuid, fields)
        if not row:
            raise not_found("Activo no encontrado")
        return ActivoOut(**row)
