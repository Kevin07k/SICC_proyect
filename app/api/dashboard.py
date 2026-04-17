from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection, text

from app.crud import dashboard as crud
from app.core.database import get_session
from app.core.context import get_base_context

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", name="mostrar_dashboard")
async def mostrar_dashboard(
        request: Request,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "dashboard")
    if not context:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=303)

    if context["acceso_denegado"]:
        return templates.TemplateResponse("index.html", context)

    datos_tipos = crud.get_conteo_incidentes_por_tipo(conn)
    datos_prioridad = crud.get_conteo_incidentes_por_prioridad(conn)
    conteo_criticos = crud.get_conteo_incidentes_criticos(conn)
    
    # Obtener datos de las vistas para el dashboard
    datos_top_activos = conn.execute(text("SELECT * FROM vw_Top_Activos_Atacados")).mappings().fetchall()
    datos_criticos = conn.execute(text("SELECT * FROM vw_Incidentes_Criticos_Abiertos")).mappings().fetchall()

    context.update({
        "datos_tipos": datos_tipos,
        "datos_prioridad": datos_prioridad,
        "conteo_criticos": conteo_criticos,
        "datos_top_activos": [dict(r) for r in datos_top_activos],
        "datos_criticos": [dict(r) for r in datos_criticos]
    })
    return templates.TemplateResponse("index.html", context)


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