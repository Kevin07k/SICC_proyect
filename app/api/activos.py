# router/activos.py
# ===================================
# Activos CRUD
# ===================================

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection  # <--- CAMBIO: Connection
from typing import Optional

from app.crud import activos as crud  # Asegúrate de la ruta correcta
from app.crud import categorias as crud_categorias
from app import schemas
from app.core.database import get_session  # <--- CAMBIO: get_session

# --- CONFIGURACIÓN ---
router = APIRouter(
    prefix="/activos",
    tags=["Activos"]
)

templates = Jinja2Templates(directory="app/templates")


# --- RUTAS ---

@router.get("/", name="mostrar_lista_de_activos")
async def mostrar_lista_de_activos(
        request: Request,
        conn: Connection = Depends(get_session)  # <--- CAMBIO: conn
):
    activos = crud.get_activos(conn)

    context = {
        "request": request,
        "activos": activos
    }
    return templates.TemplateResponse("activos/activos_lista.html", context)


# --- Create Activos ---

@router.get("/crear", name="mostrar_formulario_crear_activo")
async def mostrar_formulario_crear_activo(request: Request, conn: Connection = Depends(get_session)):
    context = {
        "request": request,
        "activo": None,
        "sedes": crud_categorias.get_sedes(conn)
    }
    return templates.TemplateResponse("activos/activo_form.html", context)


@router.post("/crear", name="procesar_crear_activo")
async def procesar_crear_activo(
        conn: Connection = Depends(get_session),  # <--- CAMBIO: conn
        hostname: str = Form(...),
        direccion_ip: Optional[str] = Form(None),
        tipo_activo: Optional[str] = Form(None),
        propietario: Optional[str] = Form(None),
        id_sede: Optional[int] = Form(None)
):
    # Creamos el esquema con los datos del formulario
    activo_data = schemas.ActivoCreate(
        hostname=hostname,
        direccion_ip=direccion_ip,
        tipo_activo=tipo_activo,
        propietario=propietario,
        id_sede=id_sede
    )

    # Pasamos 'conn' y el esquema
    crud.crear_activo(conn=conn, activo=activo_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_activos"),
        status_code=303
    )


# --- Edit Activos ---

@router.get("/editar/{activo_id}", name="mostrar_formulario_editar_activo")
async def mostrar_formulario_editar_activo(
        request: Request,
        activo_id: int,
        conn: Connection = Depends(get_session)
):
    # Buscamos por ID
    activo = crud.get_activo(conn, activo_id)

    context = {
        "request": request,
        "activo": activo,
        "sedes": crud_categorias.get_sedes(conn)
    }
    return templates.TemplateResponse("activos/activo_form.html", context)


@router.post("/editar/{activo_id}", name="procesar_editar_activo")
async def procesar_editar_activo(
        request: Request,
        activo_id: int,
        conn: Connection = Depends(get_session),  # <--- CAMBIO: conn
        hostname: str = Form(...),
        direccion_ip: Optional[str] = Form(None),
        tipo_activo: Optional[str] = Form(None),
        propietario: Optional[str] = Form(None),
        id_sede: Optional[int] = Form(None)
):
    # Nota: NO buscamos 'db_activo' aquí. El CRUD lo hace.

    activo_update = schemas.ActivoUpdate(
        hostname=hostname,
        direccion_ip=direccion_ip,
        tipo_activo=tipo_activo,
        propietario=propietario,
        id_sede=id_sede
    )

    crud.actualizar_activo(
        conn=conn,  # Conexión
        activo_id=activo_id,  # ID Entero
        activo_update=activo_update  # Datos nuevos
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_activos"),
        status_code=303
    )


# --- Delete Activo ---
@router.post("/eliminar/{activo_id}", name="procesar_eliminar_activo")
async def procesar_eliminar_activo(
        activo_id: int,
        conn: Connection = Depends(get_session)  # <--- CAMBIO: conn
):
    # Nota: Eliminada la verificación previa 'if db_activo'.
    # Llamamos directo al CRUD.
    crud.eliminar_activo(conn=conn, activo_id=activo_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_activos"),
        status_code=303
    )