# ===================================
# Admin CRUD
# ===================================

from typing import Optional

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection  # <--- CAMBIO: Usamos Connection, no Session

from app.crud import catalogos as crud  # Asegúrate de importar el CRUD correcto
from app import schemas
from app.core.database import get_session  # <--- CAMBIO: La nueva dependencia

# --- CONFIGURACIÓN ---
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

templates = Jinja2Templates(directory="app/templates")


# --- RUTAS ---

@router.get("/catalogos", name="mostrar_admin_catalogos")
async def mostrar_admin_catalogos(
        request: Request,
        conn: Connection = Depends(get_session)  # <--- CAMBIO: conn
):
    context = {
        "request": request,
        "tipos": crud.get_tipos_incidente(conn),
        "prioridades": crud.get_prioridades(conn),
        "estados": crud.get_estados(conn)
    }
    return templates.TemplateResponse("catalogos/catalogos_admin.html", context)


# --- CREAR TIPO ---

@router.get("/tipos/crear", name="mostrar_formulario_crear_tipo")
async def mostrar_formulario_crear_tipo(request: Request):
    context = {
        "request": request,
        "tipo": None
    }
    return templates.TemplateResponse("catalogos/tipo_form.html", context)


@router.post("/tipos/crear", name="procesar_crear_tipo")
async def procesar_crear_tipo(
        conn: Connection = Depends(get_session),  # <--- CAMBIO
        nombre: str = Form(...),
        descripcion: Optional[str] = Form(None)
):
    tipo_data = schemas.TipoIncidenteCreate(
        nombre=nombre,
        descripcion=descripcion
    )
    # Pasamos 'conn' en lugar de 'session'
    crud.crear_tipo_incidente(conn=conn, tipo=tipo_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_admin_catalogos"),
        status_code=303
    )


# --- EDITAR TIPO ---

@router.get("/tipos/editar/{tipo_id}", name="mostrar_formulario_editar_tipo")
async def mostrar_formulario_editar_tipo(
        request: Request,
        tipo_id: int,
        conn: Connection = Depends(get_session)
):
    # Aquí buscamos por ID para llenar el formulario
    tipo_encontrado = crud.get_tipo_incidente(conn, tipo_id)

    context = {
        "request": request,
        "tipo": tipo_encontrado
    }
    return templates.TemplateResponse("catalogos/tipo_form.html", context)


@router.post("/tipos/editar/{tipo_id}", name="procesar_editar_tipo")
async def procesar_editar_tipo(
        request: Request,
        tipo_id: int,
        conn: Connection = Depends(get_session),
        nombre: str = Form(...),
        descripcion: Optional[str] = Form(None)
):
    # Ya no necesitamos buscar 'db_tipo' antes.
    # Creamos el esquema de actualización directo.
    tipo_update = schemas.TipoIncidenteUpdate(
        nombre=nombre,
        descripcion=descripcion
    )

    crud.actualizar_tipo_incidente(
        conn=conn,  # Conexión
        tipo_id=tipo_id,  # ID (entero)
        tipo_update=tipo_update  # Datos nuevos
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_admin_catalogos"),
        status_code=303
    )


# --- ELIMINAR TIPO ---

@router.post("/tipos/eliminar/{tipo_id}", name="procesar_eliminar_tipo")
async def procesar_eliminar_tipo(
        tipo_id: int,
        conn: Connection = Depends(get_session)
):
    """
    Elimina un Tipo de Incidente.
    """
    # Simplificado: El CRUD ya verifica si existe o no dentro de su lógica.
    # Solo llamamos a la función de eliminar pasando el ID.
    crud.eliminar_tipo_incidente(conn=conn, tipo_id=tipo_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_admin_catalogos"),
        status_code=303
    )