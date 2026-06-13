import bcrypt

from app.config import get_settings
from app.core.sede_router import SedeRouter
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.session import get_connection
from app.exceptions import unauthorized
from app.repositories.auth_repo import AuthRepository
from app.schemas.auth import CurrentUser, LoginRequest, LoginResponse


class AuthService:
    def __init__(self) -> None:
        self.repo = AuthRepository()
        self.settings = get_settings()
        self.router = SedeRouter(self.settings)

    def login(self, body: LoginRequest) -> LoginResponse:
        with get_connection(get_postgres_engine()) as pg_conn, get_connection(
            get_mysql_engine()
        ) as mysql_conn:
            found = self.repo.find_user_across_engines(pg_conn, mysql_conn, body.email)
            if not found:
                raise unauthorized("Credenciales inválidas")
            user, dialect = found
            if not bcrypt.checkpw(
                body.password.encode(),
                user["password_hash"].encode(),
            ):
                raise unauthorized("Credenciales inválidas")
            conn = pg_conn if dialect == "postgres" else mysql_conn
            permisos = self.repo.get_permisos(conn, dialect, user["id_rol"])
            return LoginResponse(
                uuid=user["uuid"],
                email=user["email"],
                nombre_completo=user["nombre_completo"],
                id_sede=user["id_sede"],
                id_rol=user["id_rol"],
                rol_nombre=user["rol_nombre"],
                permisos=permisos,
            )

    def get_user_by_uuid(self, user_uuid) -> CurrentUser | None:
        with get_connection(get_postgres_engine()) as pg_conn, get_connection(
            get_mysql_engine()
        ) as mysql_conn:
            found = self.repo.find_uuid_across_engines(pg_conn, mysql_conn, user_uuid)
            if not found:
                return None
            user, dialect = found
            conn = pg_conn if dialect == "postgres" else mysql_conn
            permisos = self.repo.get_permisos(conn, dialect, user["id_rol"])
            return CurrentUser(
                uuid=user["uuid"],
                email=user["email"],
                nombre_completo=user["nombre_completo"],
                id_sede=user["id_sede"],
                id_rol=user["id_rol"],
                rol_nombre=user["rol_nombre"],
                permisos=permisos,
            )
