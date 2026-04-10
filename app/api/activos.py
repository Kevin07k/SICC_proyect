from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection
from typing import Optional

from app.crud import activos as crud
from app.crud import categorias as crud_categorias
from app import schemas
from app.core.database import get_session
from app.core.context import get_base_context

router = APIRouter(
    prefix="/activos",
    tags=["Activos"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/", name="mostrar_lista_de_activos")
async def mostrar_lista_de_activos(
        request: Request,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "activos")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if context["acceso_denegado"]:
        return templates.TemplateResponse("activos/activos_lista.html", context)

    activos = crud.get_activos(conn)
    context["activos"] = activos
    return templates.TemplateResponse("activos/activos_lista.html", context)


@router.get("/crear", name="mostrar_formulario_crear_activo")
async def mostrar_formulario_crear_activo(request: Request, conn: Connection = Depends(get_session)):
    context = get_base_context(request, "activos")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if not context["puede_crear"]:
        context["acceso_denegado"] = True
        return templates.TemplateResponse("activos/activo_form.html", context)

    context.update({
        "activo": None,
        "sedes": crud_categorias.get_sedes(conn)
    })
    return templates.TemplateResponse("activos/activo_form.html", context)


@router.post("/crear", name="procesar_crear_activo")
async def procesar_crear_activo(
        conn: Connection = Depends(get_session),
        hostname: str = Form(...),
        direccion_ip: Optional[str] = Form(None),
        tipo_activo: Optional[str] = Form(None),
        propietario: Optional[str] = Form(None),
        id_sede: Optional[int] = Form(None)
):
    activo_data = schemas.ActivoCreate(
        hostname=hostname,
        direccion_ip=direccion_ip,
        tipo_activo=tipo_activo,
        propietario=propietario,
        id_sede=id_sede
    )

    crud.crear_activo(conn=conn, activo=activo_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_activos"),
        status_code=303
    )


@router.get("/editar/{activo_id}", name="mostrar_formulario_editar_activo")
async def mostrar_formulario_editar_activo(
        request: Request,
        activo_id: int,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "activos")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if not context["puede_editar"]:
        context["acceso_denegado"] = True
        return templates.TemplateResponse("activos/activo_form.html", context)

    activo = crud.get_activo(conn, activo_id)
    context.update({
        "activo": activo,
        "sedes": crud_categorias.get_sedes(conn)
    })
    return templates.TemplateResponse("activos/activo_form.html", context)


@router.post("/editar/{activo_id}", name="procesar_editar_activo")
async def procesar_editar_activo(
        request: Request,
        activo_id: int,
        conn: Connection = Depends(get_session),
        hostname: str = Form(...),
        direccion_ip: Optional[str] = Form(None),
        tipo_activo: Optional[str] = Form(None),
        propietario: Optional[str] = Form(None),
        id_sede: Optional[int] = Form(None)
):
    activo_update = schemas.ActivoUpdate(
        hostname=hostname,
        direccion_ip=direccion_ip,
        tipo_activo=tipo_activo,
        propietario=propietario,
        id_sede=id_sede
    )

    crud.actualizar_activo(
        conn=conn,
        activo_id=activo_id,
        activo_update=activo_update
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_activos"),
        status_code=303
    )


@router.post("/eliminar/{activo_id}", name="procesar_eliminar_activo")
async def procesar_eliminar_activo(
        activo_id: int,
        conn: Connection = Depends(get_session)
):
    crud.eliminar_activo(conn=conn, activo_id=activo_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_activos"),
        status_code=303
    )