from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import bad_request, not_found
from app.repositories.catalogo_repo import CatalogoRepository
from app.schemas.auth import CurrentUser
from app.schemas.catalogos import (
    EstadoOut,
    PrioridadOut,
    SedeOut,
    TipoIncidenteCreate,
    TipoIncidenteOut,
    TipoIncidenteUpdate,
)


class CatalogoService:
    def __init__(self) -> None:
        self.repo = CatalogoRepository()
        self.router = SedeRouter()

    def _conn_dialect(self, user: CurrentUser):
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)  # type: ignore[return-value]
        return engine, dialect

    def _central_conn(self):
        engine = self.router.engine_for_sede(self.router.settings.sede_central_id)
        return engine, "postgres"

    def list_sedes(self, user: CurrentUser) -> list[SedeOut]:
        engine, dialect = self._conn_dialect(user)
        with get_connection(engine) as conn:
            rows = self.repo.list_sedes(conn, dialect)
        return [SedeOut(**r) for r in rows]

    def list_estados(self, user: CurrentUser) -> list[EstadoOut]:
        engine, dialect = self._conn_dialect(user)
        with get_connection(engine) as conn:
            rows = self.repo.list_estados(conn, dialect)
        return [EstadoOut(**r) for r in rows]

    def list_prioridades(self, user: CurrentUser) -> list[PrioridadOut]:
        engine, dialect = self._conn_dialect(user)
        with get_connection(engine) as conn:
            rows = self.repo.list_prioridades(conn, dialect)
        return [PrioridadOut(**r) for r in rows]

    def list_tipos(self, user: CurrentUser) -> list[TipoIncidenteOut]:
        engine, dialect = self._conn_dialect(user)
        with get_connection(engine) as conn:
            rows = self.repo.list_tipos(conn, dialect)
        return [TipoIncidenteOut(**r) for r in rows]

    def list_tipos_gestion(self, _user: CurrentUser) -> list[TipoIncidenteOut]:
        engine, dialect = self._central_conn()
        with get_connection(engine) as conn:
            rows = self.repo.list_tipos(conn, dialect, include_eliminados=True)
        return [TipoIncidenteOut(**r) for r in rows]

    def create_tipo(self, _user: CurrentUser, body: TipoIncidenteCreate) -> TipoIncidenteOut:
        engine, dialect = self._central_conn()
        with get_connection(engine) as conn:
            try:
                row = self.repo.create_tipo(
                    conn, dialect, nombre=body.nombre.strip(), descripcion=body.descripcion
                )
            except Exception as exc:
                raise bad_request("No se pudo crear el tipo (¿nombre duplicado?)") from exc
            conn.commit()
        return TipoIncidenteOut(**row)

    def update_tipo(
        self, _user: CurrentUser, id_tipo: int, body: TipoIncidenteUpdate
    ) -> TipoIncidenteOut:
        fields = body.model_dump(exclude_unset=True)
        if "nombre" in fields and fields["nombre"] is not None:
            fields["nombre"] = fields["nombre"].strip()
        engine, dialect = self._central_conn()
        with get_connection(engine) as conn:
            existing = self.repo.get_tipo(conn, dialect, id_tipo)
            if not existing:
                raise not_found("Tipo de incidente no encontrado")
            try:
                row = self.repo.update_tipo(conn, dialect, id_tipo, fields)
            except Exception as exc:
                raise bad_request("No se pudo actualizar (¿nombre duplicado?)") from exc
            conn.commit()
        if not row:
            raise not_found("Tipo de incidente no encontrado")
        return TipoIncidenteOut(**row)

    def delete_tipo(self, _user: CurrentUser, id_tipo: int) -> None:
        engine, dialect = self._central_conn()
        with get_connection(engine) as conn:
            existing = self.repo.get_tipo(conn, dialect, id_tipo)
            if not existing or existing.get("eliminado"):
                raise not_found("Tipo de incidente no encontrado")
            if self.repo.count_incidentes_por_tipo(conn, dialect, id_tipo) > 0:
                raise bad_request(
                    "No se puede dar de baja: hay incidentes activos con este tipo"
                )
            if not self.repo.soft_delete_tipo(conn, dialect, id_tipo):
                raise not_found("Tipo de incidente no encontrado")
            conn.commit()
