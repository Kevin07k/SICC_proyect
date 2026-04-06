# router/dashboard.py
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection, text  # Usamos Connection y text

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
    conteo_criticos = crud.get_conteo_incidentes_criticos(conn)

    context = {
        "request": request,
        "datos_tipos": datos_tipos,
        "datos_prioridad": datos_prioridad,
        "conteo_criticos": conteo_criticos
    }
    return templates.TemplateResponse("index.html", context)

# ===================================
# SPRINT 5: VISTAS ESTADÍSTICAS
# ===================================

@router.get("/vistas/criticos", name="dashboard_incidentes_criticos")
async def dashboard_incidentes_criticos(conn: Connection = Depends(get_session)):
    query = text("SELECT * FROM vw_Incidentes_Criticos_Abiertos")
    result = conn.execute(query).mappings().fetchall()
    return {"data": [dict(r) for r in result]}

@router.get("/vistas/top-activos", name="dashboard_top_activos")
async def dashboard_top_activos(conn: Connection = Depends(get_session)):
    query = text("SELECT * FROM vw_Top_Activos_Atacados")
    result = conn.execute(query).mappings().fetchall()
    return {"data": [dict(r) for r in result]}