from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from functools import wraps
import bcrypt
from sqlalchemy import text

SECRET_KEY = "sicc_secret_key_2026"

# Cuentas hardcodeadas como fallback (DBA siempre tiene acceso)
CUENTAS = {
    "dba": {
        "password": "dba123",
        "nombre": "Admin Sistema",
        "rol": "DBA"
    }
}

PERMISOS_ROL = {
    "DBA": {
        "secciones": ["dashboard", "incidentes", "activos", "sedes", "usuarios", "categorias"],
        "puede_crear": True,
        "puede_editar": True,
        "puede_eliminar": True,
        "puede_ver_reportes": True,
        "descripcion": "Control total del sistema"
    },
    "Developer": {
        "secciones": ["dashboard", "incidentes", "activos"],
        "puede_crear": True,
        "puede_editar": True,
        "puede_eliminar": False,
        "puede_ver_reportes": False,
        "descripcion": "Registra y actualiza incidentes y activos"
    }
}


def hash_password(password: str) -> str:
    """Genera un hash bcrypt de la contraseña."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def authenticate_user(conn, username: str, password: str):
    """
    Autentica un usuario contra la base de datos.
    Primero busca en la BD, luego en el dict CUENTAS como fallback para DBA.
    """
    # 1. Buscar en la base de datos
    query = text("""
        SELECT id_usuario, nombre_completo, email, username, password_hash, rol
        FROM Usuarios
        WHERE username = :username AND eliminado = 0
    """)
    result = conn.execute(query, {"username": username.lower()})
    user = result.mappings().first()

    if user and user["password_hash"]:
        if verify_password(password, user["password_hash"]):
            return {
                "usuario": user["username"],
                "nombre": user["nombre_completo"],
                "rol": user["rol"],
                "id_usuario": user["id_usuario"]
            }
        return None

    # 2. Fallback: Cuentas hardcodeadas (DBA)
    cuenta = CUENTAS.get(username.lower())
    if cuenta and cuenta["password"] == password:
        return {
            "usuario": username.lower(),
            "nombre": cuenta["nombre"],
            "rol": cuenta["rol"]
        }

    return None


def get_current_user(request: Request):
    usuario = request.cookies.get("usuario")
    rol = request.cookies.get("rol")
    nombre = request.cookies.get("nombre")
    if not usuario or not rol:
        return None
    return {"usuario": usuario, "rol": rol, "nombre": nombre}


def require_login(request: Request):
    user = get_current_user(request)
    if not user:
        return None
    return user


def tiene_acceso(rol: str, seccion: str) -> bool:
    permisos = PERMISOS_ROL.get(rol)
    if not permisos:
        return False
    return seccion in permisos["secciones"]


def puede_crear(rol: str) -> bool:
    permisos = PERMISOS_ROL.get(rol, {})
    return permisos.get("puede_crear", False)


def puede_editar(rol: str) -> bool:
    permisos = PERMISOS_ROL.get(rol, {})
    return permisos.get("puede_editar", False)


def puede_eliminar(rol: str) -> bool:
    permisos = PERMISOS_ROL.get(rol, {})
    return permisos.get("puede_eliminar", False)


def puede_ver_reportes(rol: str) -> bool:
    permisos = PERMISOS_ROL.get(rol, {})
    return permisos.get("puede_ver_reportes", False)
