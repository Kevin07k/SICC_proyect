from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection
from typing import Optional

from app.crud import usuarios as crud
from app import schemas
from app.core.database import get_session
from app.core.context import get_base_context

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/", name="mostrar_lista_de_usuarios")
async def mostrar_lista_de_usuarios(
        request: Request,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "usuarios")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if context["acceso_denegado"]:
        return templates.TemplateResponse("usuarios/usuarios_lista.html", context)

    usuarios = crud.get_usuarios(conn)
    context["usuarios"] = usuarios
    return templates.TemplateResponse("usuarios/usuarios_lista.html", context)


@router.get("/crear", name="mostrar_formulario_crear_usuario")
async def mostrar_formulario_crear_usuario(request: Request):
    context = get_base_context(request, "usuarios")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if not context["puede_crear"]:
        context["acceso_denegado"] = True
        return templates.TemplateResponse("usuarios/usuario_form.html", context)

    context["usuario"] = None
    return templates.TemplateResponse("usuarios/usuario_form.html", context)


@router.post("/crear", name="procesar_crear_usuario")
async def procesar_crear_usuario(
        conn: Connection = Depends(get_session),
        nombre_completo: str = Form(...),
        email: str = Form(...),
        rol: str = Form(...)
):
    usuario_data = schemas.UsuarioCreate(
        nombre_completo=nombre_completo,
        email=email,
        rol=rol
    )

    crud.crear_usuario(conn=conn, usuario=usuario_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_usuarios"),
        status_code=303
    )


@router.get("/editar/{usuario_id}", name="mostrar_formulario_editar_usuario")
async def mostrar_formulario_editar_usuario(
        request: Request,
        usuario_id: int,
        conn: Connection = Depends(get_session)
):
    context = get_base_context(request, "usuarios")
    if not context:
        return RedirectResponse(url="/login", status_code=303)
    if not context["puede_editar"]:
        context["acceso_denegado"] = True
        return templates.TemplateResponse("usuarios/usuario_form.html", context)

    usuario = crud.get_usuario(conn, usuario_id)
    context["usuario"] = usuario
    return templates.TemplateResponse("usuarios/usuario_form.html", context)


@router.post("/editar/{usuario_id}", name="procesar_editar_usuario")
async def procesar_editar_usuario(
        request: Request,
        usuario_id: int,
        conn: Connection = Depends(get_session),
        nombre_completo: str = Form(...),
        email: str = Form(...),
        rol: str = Form(...)
):
    usuario_update = schemas.UsuarioUpdate(
        nombre_completo=nombre_completo,
        email=email,
        rol=rol
    )

    crud.actualizar_usuario(
        conn=conn,
        usuario_id=usuario_id,
        usuario_update=usuario_update
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_usuarios"),
        status_code=303
    )


@router.post("/usuarios/eliminar/{usuario_id}", name="procesar_eliminar_usuario")
async def procesar_eliminar_usuario(
        usuario_id: int,
        conn: Connection = Depends(get_session)
):
    crud.eliminar_usuario(conn=conn, usuario_id=usuario_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_usuarios"),
        status_code=303
    )