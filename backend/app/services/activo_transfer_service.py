from uuid import UUID

from app.config import get_settings
from app.core.sede_router import SedeRouter
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.session import db_transaction, get_connection
from app.exceptions import bad_request, not_found
from app.repositories.activo_repo import ActivoRepository
from app.repositories.catalogo_repo import CatalogoRepository
from app.schemas.activos import ActivoTransferirRequest, ActivoTransferirResponse
from app.schemas.auth import CurrentUser


class ActivoTransferService:
    def __init__(self) -> None:
        self.activo_repo = ActivoRepository()
        self.catalogo_repo = CatalogoRepository()
        self.router = SedeRouter()
        self.settings = get_settings()

    def transferir(
        self,
        user: CurrentUser,
        activo_uuid: UUID,
        body: ActivoTransferirRequest,
    ) -> ActivoTransferirResponse:
        if body.sede_destino_id == user.id_sede:
            raise bad_request("La sede destino debe ser distinta a la actual del activo")

        with get_connection(get_postgres_engine()) as pg_conn, get_connection(
            get_mysql_engine()
        ) as mysql_conn:
            found = self.activo_repo.find_active_in_any_node(pg_conn, mysql_conn, activo_uuid)
            if not found:
                raise not_found("Activo no encontrado o ya transferido")
            activo, origen_dialect, origen_conn = found
            sede_origen = activo["id_sede"]

            dest_engine = self.router.engine_for_sede(body.sede_destino_id)
            dest_dialect = self.router.dialect_for_sede(body.sede_destino_id)
            if origen_dialect == dest_dialect and sede_origen == body.sede_destino_id:
                raise bad_request("El activo ya pertenece a esa sede")

            with get_connection(dest_engine) as dest_conn:
                sede = self.catalogo_repo.get_sede(dest_conn, dest_dialect, body.sede_destino_id)
                if not sede or sede.get("eliminado"):
                    raise bad_request("Sede destino inválida")

                try:
                    # Transacción en origen: baja lógica sin commit hasta confirmar destino
                    with db_transaction(origen_conn):
                        self.activo_repo.soft_delete(
                            origen_conn,
                            origen_dialect,
                            activo_uuid,
                            auto_commit=False,
                        )
                        with db_transaction(dest_conn):
                            self.activo_repo.insert_transfer(
                                dest_conn,
                                dest_dialect,
                                activo,
                                body.sede_destino_id,
                                auto_commit=False,
                            )
                except Exception as exc:
                    raise bad_request(f"Error en traslado: {exc}") from exc

        nodo_map = {
            self.settings.sede_central_id: "postgres",
            self.settings.sede_secundaria_id: "mysql",
        }
        return ActivoTransferirResponse(
            uuid=activo_uuid,
            sede_origen_id=sede_origen,
            sede_destino_id=body.sede_destino_id,
            nodo_origen=nodo_map.get(sede_origen, origen_dialect),
            nodo_destino=nodo_map.get(body.sede_destino_id, dest_dialect),
            motivo=body.motivo,
        )
