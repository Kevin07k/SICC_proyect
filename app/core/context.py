from fastapi import Request
from fastapi.responses import RedirectResponse
from app.core.auth import get_current_user, PERMISOS_ROL, tiene_acceso


def get_base_context(request: Request, seccion: str = ""):
    user = get_current_user(request)
    if not user:
        return None

    rol = user["rol"]
    permisos = PERMISOS_ROL.get(rol, {})
    secciones = permisos.get("secciones", [])

    context = {
        "request": request,
        "usuario_actual": user,
        "secciones_permitidas": secciones,
        "puede_crear": permisos.get("puede_crear", False),
        "puede_editar": permisos.get("puede_editar", False),
        "puede_eliminar": permisos.get("puede_eliminar", False),
        "puede_ver_reportes": permisos.get("puede_ver_reportes", False),
        "acceso_denegado": False
    }

    if seccion and not tiene_acceso(rol, seccion):
        context["acceso_denegado"] = True

    return context
