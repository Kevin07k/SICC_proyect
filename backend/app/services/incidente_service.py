from uuid import UUID

from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import forbidden, not_found
from app.repositories.incidente_activo_repo import IncidenteActivoRepository
from app.repositories.incidente_repo import IncidenteRepository
from app.schemas.auth import CurrentUser
from app.schemas.incidente_activos import IncidenteActivoOut
from app.schemas.incidentes import IncidenteCreate, IncidenteOut, IncidenteUpdate


class IncidenteService:
    def __init__(self) -> None:
        self.repo = IncidenteRepository()
        self.vinculo_repo = IncidenteActivoRepository()
        self.router = SedeRouter()

    def _to_out(self, row: dict, vinculos: list[dict] | None = None) -> IncidenteOut:
        activos = [IncidenteActivoOut(**v) for v in (vinculos or [])]
        return IncidenteOut(**row, activos_vinculados=activos)

    def list_incidentes(self, user: CurrentUser) -> list[IncidenteOut]:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            rows = self.repo.list_by_sede(conn, dialect, user.id_sede)
        return [IncidenteOut(**r) for r in rows]

    def get_incidente(self, user: CurrentUser, incidente_uuid: UUID) -> IncidenteOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            row = self.repo.get(conn, dialect, incidente_uuid)
            if not row:
                raise not_found("Incidente no encontrado")
            if row["id_sede"] != user.id_sede:
                raise forbidden("Incidente de otra sede")
            vinculos = self.vinculo_repo.list_by_incidente(conn, dialect, incidente_uuid)
        return self._to_out(row, vinculos)

    def create_incidente(self, user: CurrentUser, body: IncidenteCreate) -> IncidenteOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        asignado = body.id_usuario_asignado or user.uuid
        data = {
            "titulo": body.titulo,
            "descripcion": body.descripcion,
            "id_tipo": body.id_tipo,
            "id_prioridad": body.id_prioridad,
            "id_estado": body.id_estado,
            "id_usuario_asignado": asignado,
            "id_sede": user.id_sede,
        }
        with get_connection(engine) as conn:
            row = self.repo.create(conn, dialect, data)
            inc_uuid = UUID(str(row["uuid"]))
            for activo_uuid in body.activos:
                activo = self.vinculo_repo.get_activo_with_sede(conn, dialect, activo_uuid)
                if not activo:
                    raise not_found(f"Activo {activo_uuid} no encontrado")
                if activo["id_sede"] != user.id_sede:
                    raise forbidden("El activo debe pertenecer a la misma sede que el incidente")
                if not self.vinculo_repo.link_exists(conn, dialect, inc_uuid, activo_uuid):
                    self.vinculo_repo.create_link(conn, dialect, inc_uuid, activo, None)
            vinculos = self.vinculo_repo.list_by_incidente(conn, dialect, inc_uuid)
        return self._to_out(row, vinculos)

    def update_incidente(
        self, user: CurrentUser, incidente_uuid: UUID, body: IncidenteUpdate
    ) -> IncidenteOut:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        fields = body.model_dump(exclude_unset=True)
        with get_connection(engine) as conn:
            existing = self.repo.get(conn, dialect, incidente_uuid)
            if not existing:
                raise not_found("Incidente no encontrado")
            if existing["id_sede"] != user.id_sede:
                raise forbidden("Incidente de otra sede")
            row = self.repo.update(conn, dialect, incidente_uuid, fields)
        if not row:
            raise not_found("Incidente no encontrado")
        with get_connection(engine) as conn:
            vinculos = self.vinculo_repo.list_by_incidente(conn, dialect, incidente_uuid)
        return self._to_out(row, vinculos)
