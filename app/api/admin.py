from typing import Optional

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection

from app.crud import categorias as crud
from app import schemas
from app.core.database import get_session
from app.core.context import get_base_context

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/categorias", name="mostrar_admin_categorias")
async def mostrar_admin_categorias(
        request: Request,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "categorias")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if context["acceso_denegado"]:
        return templates.TemplateResponse("categorias/categorias_admin.html", context)

    context.update({
        "tipos": crud.get_tipos_incidente(conn),
        "prioridades": crud.get_prioridades(conn),
        "estados": crud.get_estados(conn)
    })
    return templates.TemplateResponse("categorias/categorias_admin.html", context)


@router.get("/tipos/crear", name="mostrar_formulario_crear_tipo")
async def mostrar_formulario_crear_tipo(request: Request):
    context = get_base_context(request, "categorias")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if not context["puede_crear"]:
        context["acceso_denegado"] = True
        return templates.TemplateResponse("categorias/tipo_form.html", context)

    context["tipo"] = None
    return templates.TemplateResponse("categorias/tipo_form.html", context)


@router.post("/tipos/crear", name="procesar_crear_tipo")
async def procesar_crear_tipo(
        conn: Connection = Depends(get_session),
        nombre: str = Form(...),
        descripcion: Optional[str] = Form(None)
):
    tipo_data = schemas.TipoIncidenteCreate(
        nombre=nombre,
        descripcion=descripcion
    )
    crud.crear_tipo_incidente(conn=conn, tipo=tipo_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_admin_categorias"),
        status_code=303
    )


@router.get("/tipos/editar/{tipo_id}", name="mostrar_formulario_editar_tipo")
async def mostrar_formulario_editar_tipo(
        request: Request,
        tipo_id: int,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "categorias")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if not context["puede_editar"]:
        context["acceso_denegado"] = True
        return templates.TemplateResponse("categorias/tipo_form.html", context)

    tipo_encontrado = crud.get_tipo_incidente(conn, tipo_id)
    context["tipo"] = tipo_encontrado
    return templates.TemplateResponse("categorias/tipo_form.html", context)


@router.post("/tipos/editar/{tipo_id}", name="procesar_editar_tipo")
async def procesar_editar_tipo(
        request: Request,
        tipo_id: int,
        conn: Connection = Depends(get_session),
        nombre: str = Form(...),
        descripcion: Optional[str] = Form(None)
):
    tipo_update = schemas.TipoIncidenteUpdate(
        nombre=nombre,
        descripcion=descripcion
    )

    crud.actualizar_tipo_incidente(
        conn=conn,
        tipo_id=tipo_id,
        tipo_update=tipo_update
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_admin_categorias"),
        status_code=303
    )


@router.post("/tipos/eliminar/{tipo_id}", name="procesar_eliminar_tipo")
async def procesar_eliminar_tipo(
        tipo_id: int,
        conn: Connection = Depends(get_session)
):
    crud.eliminar_tipo_incidente(conn=conn, tipo_id=tipo_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_admin_categorias"),
        status_code=303
    )