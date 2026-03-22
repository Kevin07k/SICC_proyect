# ===================================
# User CRUD
# ===================================

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection  # <--- CAMBIO 1: Importar Connection, no Session

from app.crud import usuarios as crud  # Asegúrate de importar el CRUD correcto
from app import schemas
from app.core.database import get_session  # <--- CAMBIO 2: Importar get_db_connection

# --- CONFIGURACIÓN ---
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

templates = Jinja2Templates(directory="app/templates")


# --- RUTAS ---

@router.get("/", name="mostrar_lista_de_usuarios")
async def mostrar_lista_de_usuarios(
        request: Request,
        conn: Connection = Depends(get_session)  # <--- CAMBIO 3: Usar 'conn'
):
    usuarios = crud.get_usuarios(conn)
    context = {
        "request": request,
        "usuarios": usuarios
    }
    return templates.TemplateResponse("usuarios/usuarios_lista.html", context)


# --- Create User ---

@router.get("/crear", name="mostrar_formulario_crear_usuario")
async def mostrar_formulario_crear_usuario(request: Request):
    context = {
        "request": request,
        "usuario": None
    }
    return templates.TemplateResponse("usuarios/usuario_form.html", context)


@router.post("/crear", name="procesar_crear_usuario")
async def procesar_crear_usuario(
        conn: Connection = Depends(get_session),  # <--- CAMBIO: Dependency
        nombre_completo: str = Form(...),
        email: str = Form(...),
        rol: str = Form(...)
):
    usuario_data = schemas.UsuarioCreate(
        nombre_completo=nombre_completo,
        email=email,
        rol=rol
    )

    # <--- CORRECCIÓN DEL ERROR: Usamos 'conn=conn'
    crud.crear_usuario(conn=conn, usuario=usuario_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_usuarios"),
        status_code=303
    )


# --- Edit User ---

@router.get("/editar/{usuario_id}", name="mostrar_formulario_editar_usuario")
async def mostrar_formulario_editar_usuario(
        request: Request,
        usuario_id: int,
        conn: Connection = Depends(get_session)
):
    usuario = crud.get_usuario(conn, usuario_id)
    context = {
        "request": request,
        "usuario": usuario
    }
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
    # Nota: No necesitamos hacer 'db_usuario = crud.get...' antes.
    # El CRUD de actualizar ya verifica si existe internamente.

    usuario_update = schemas.UsuarioUpdate(
        nombre_completo=nombre_completo,
        email=email,
        rol=rol
    )

    crud.actualizar_usuario(
        conn=conn,  # <--- CORRECCIÓN
        usuario_id=usuario_id,  # <--- CORRECCIÓN: Pasamos el ID directo
        usuario_update=usuario_update
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_usuarios"),
        status_code=303
    )


# --- Delete user ---

@router.post("/usuarios/eliminar/{usuario_id}", name="procesar_eliminar_usuario")
async def procesar_eliminar_usuario(
        usuario_id: int,
        conn: Connection = Depends(get_session)
):
    """
    Elimina un usuario.
    """
    # CORRECCIÓN IMPORTANTE:
    # 1. No buscamos el objeto db_usuario antes.
    # 2. Llamamos a la función pasando 'conn' y 'usuario_id' (entero).

    crud.eliminar_usuario(conn=conn, usuario_id=usuario_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_usuarios"),
        status_code=303
    )