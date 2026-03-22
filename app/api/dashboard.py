# router/dashboard.py
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection  # Usamos Connection

from app.crud import dashboard as crud  # Importamos el nuevo CRUD
from app.core.database import get_session  # La nueva dependencia

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", name="mostrar_dashboard")
async def mostrar_dashboard(
        request: Request,
        conn: Connection = Depends(get_session)  # <--- IMPORTANTE: conn
):
    # Pasamos 'conn', no 'session'
    datos_tipos = crud.get_conteo_incidentes_por_tipo(conn)
    datos_prioridad = crud.get_conteo_incidentes_por_prioridad(conn)

    context = {
        "request": request,
        "datos_tipos": datos_tipos,
        "datos_prioridad": datos_prioridad
    }
    return templates.TemplateResponse("index.html", context)