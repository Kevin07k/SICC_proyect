import bcrypt
from uuid import UUID

from app.config import get_settings
from app.core.sede_router import SedeRouter
from app.db.session import get_connection
from app.exceptions import bad_request, forbidden, not_found
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.usuarios import UsuarioCreate, UsuarioOut, UsuarioUpdate


def _vista_global_usuarios(user: CurrentUser) -> bool:
    settings = get_settings()
    if user.rol_nombre == settings.rol_admin_nombre:
        return True
    if "usuarios.gestionar" in user.permisos:
        return True
    return (
        "reportes.ver" in user.permisos
        and user.id_sede == settings.sede_central_id
    )


def _puede_acceder_usuario(current: CurrentUser, id_sede_objetivo: int) -> bool:
    if _vista_global_usuarios(current):
        return True
    return current.id_sede == id_sede_objetivo


class UsuarioService:
    def __init__(self) -> None:
        self.repo = UsuarioRepository()
        self.router = SedeRouter()
        self.settings = get_settings()

    def list_users(self, user: CurrentUser) -> list[UsuarioOut]:
        engine = self.router.engine_for_sede(user.id_sede)
        dialect = self.router.dialect_for_sede(user.id_sede)
        with get_connection(engine) as conn:
            if _vista_global_usuarios(user):
                rows = self.repo.list_all(conn, dialect)
            else:
                rows = self.repo.list_by_sede(conn, dialect, user.id_sede)
        return [UsuarioOut(**r) for r in rows]

    def get_user(self, current: CurrentUser, user_uuid: UUID) -> UsuarioOut:
        engine = self.router.engine_for_sede(current.id_sede)
        dialect = self.router.dialect_for_sede(current.id_sede)
        with get_connection(engine) as conn:
            row = self.repo.get(conn, dialect, user_uuid)
        if not row:
            raise not_found("Usuario no encontrado")
        if not _puede_acceder_usuario(current, row["id_sede"]):
            raise forbidden("Usuario de otra sede")
        return UsuarioOut(**row)

    def create_user(self, current: CurrentUser, body: UsuarioCreate) -> UsuarioOut:
        target_sede = body.id_sede if body.id_sede is not None else current.id_sede
        if not _vista_global_usuarios(current) and target_sede != current.id_sede:
            raise forbidden("Solo puede crear usuarios de su sede")
        if target_sede not in (
            self.settings.sede_central_id,
            self.settings.sede_secundaria_id,
        ):
            raise bad_request("Sede no válida")

        engine = self.router.engine_for_sede(current.id_sede)
        dialect = self.router.dialect_for_sede(current.id_sede)
        password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
        with get_connection(engine) as conn:
            try:
                row = self.repo.create(
                    conn,
                    dialect,
                    email=body.email,
                    password_hash=password_hash,
                    nombre_completo=body.nombre_completo,
                    id_sede=target_sede,
                    id_rol=body.id_rol,
                )
            except Exception as exc:
                raise bad_request("No se pudo crear usuario (email duplicado?)") from exc
        return UsuarioOut(**row)

    def update_user(
        self, current: CurrentUser, user_uuid: UUID, body: UsuarioUpdate
    ) -> UsuarioOut:
        engine = self.router.engine_for_sede(current.id_sede)
        dialect = self.router.dialect_for_sede(current.id_sede)
        fields: dict = {}
        if body.email is not None:
            fields["email"] = body.email
        if body.nombre_completo is not None:
            fields["nombre_completo"] = body.nombre_completo
        if body.id_rol is not None:
            fields["id_rol"] = body.id_rol
        if body.activo is not None:
            fields["activo"] = body.activo
        if body.password:
            fields["password_hash"] = bcrypt.hashpw(
                body.password.encode(), bcrypt.gensalt()
            ).decode()
        with get_connection(engine) as conn:
            existing = self.repo.get(conn, dialect, user_uuid)
            if not existing:
                raise not_found("Usuario no encontrado")
            if not _puede_acceder_usuario(current, existing["id_sede"]):
                raise forbidden("Usuario de otra sede")
            row = self.repo.update(conn, dialect, user_uuid, fields)
        if not row:
            raise not_found("Usuario no encontrado")
        return UsuarioOut(**row)
