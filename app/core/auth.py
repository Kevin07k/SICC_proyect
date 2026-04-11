from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from functools import wraps

SECRET_KEY = "sicc_secret_key_2026"

CUENTAS = {
    "developer": {
        "password": "dev123",
        "nombre": "Dev Operador",
        "rol": "Developer"
    },
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
