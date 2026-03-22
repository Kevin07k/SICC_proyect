# router/incidentes.py

# ===================================
# Incidentes CRUD
# ===================================

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection  # <--- CAMBIO: Connection
from typing import Optional

from app.crud import incidentes as crud_incidentes  # Asegúrate de importar bien tus CRUDS
from app.crud import catalogos as crud_catalogos
from app.crud import usuarios as crud_usuarios
from app.crud import activos as crud_activos
from app.crud import bitacora as crud_bitacora

from app import schemas
from app.core.database import get_session  # <--- CAMBIO: Nueva dependencia

# --- CONFIGURACIÓN ---
router = APIRouter(
    prefix="/incidentes",
    tags=["Incidentes"]
)

templates = Jinja2Templates(directory="app/templates")


# --- RUTAS ---

@router.get("/", name="mostrar_lista_de_incidentes")
async def mostrar_lista_de_incidentes(
        request: Request,
        conn: Connection = Depends(get_session)  # <--- CAMBIO: conn
):
    incidentes = crud_incidentes.get_incidentes(conn)
    context = {
        "request": request,
        "incidentes": incidentes
    }
    return templates.TemplateResponse("incidentes/incidentes_lista.html", context)


# --- Create Incident ---

@router.get("/crear", name="mostrar_formulario_crear_incidente")
async def mostrar_formulario_crear_incidente(
        request: Request,
        conn: Connection = Depends(get_session)
):
    context = {
        "request": request,
        "incidente": None,
        "tipos": crud_catalogos.get_tipos_incidente(conn),
        "prioridades": crud_catalogos.get_prioridades(conn),
        "estados": crud_catalogos.get_estados(conn),
        "usuarios": crud_usuarios.get_usuarios(conn)
    }

    return templates.TemplateResponse("incidentes/incidente_form.html", context)


@router.post("/crear", name="procesar_crear_incidente")
async def procesar_crear_incidente(
        request: Request,
        conn: Connection = Depends(get_session),  # <--- CAMBIO: conn
        titulo: str = Form(...),
        descripcion_detallada: str = Form(...),
        id_tipo: int = Form(...),
        id_prioridad: int = Form(...),
        id_estado: int = Form(...),
        id_usuario_asignado: Optional[int] = Form(None)
):
    incidente_data = schemas.IncidenteCreate(
        titulo=titulo,
        descripcion_detallada=descripcion_detallada,
        id_tipo=id_tipo,
        id_prioridad=id_prioridad,
        id_estado=id_estado,
        id_usuario_asignado=id_usuario_asignado
    )
    # Llamamos al CRUD pasando 'conn'
    crud_incidentes.crear_incidente(conn=conn, incidente=incidente_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_incidentes"),
        status_code=303
    )


# --- Edit Incident ---

@router.get("/editar/{incidente_id}", name="mostrar_formulario_editar_incidente")
async def mostrar_formulario_editar_incidente(
        request: Request,
        incidente_id: int,
        conn: Connection = Depends(get_session)
):
    context = {
        "request": request,
        "incidente": crud_incidentes.get_incidente(conn, incidente_id),
        "tipos": crud_catalogos.get_tipos_incidente(conn),
        "prioridades": crud_catalogos.get_prioridades(conn),
        "estados": crud_catalogos.get_estados(conn),
        "usuarios": crud_usuarios.get_usuarios(conn)
    }
    return templates.TemplateResponse("incidentes/incidente_form.html", context)


@router.post("/editar/{incidente_id}", name="procesar_editar_incidente")
async def procesar_editar_incidente(
        request: Request,
        incidente_id: int,
        conn: Connection = Depends(get_session),
        titulo: str = Form(...),
        descripcion_detallada: str = Form(...),
        id_tipo: int = Form(...),
        id_prioridad: int = Form(...),
        id_estado: int = Form(...),
        id_usuario_asignado: Optional[int] = Form(None)
):
    # Nota: No buscamos 'db_incidente' aquí. El CRUD lo hace.

    incidente_update = schemas.IncidenteUpdate(
        titulo=titulo,
        descripcion_detallada=descripcion_detallada,
        id_tipo=id_tipo,
        id_prioridad=id_prioridad,
        id_estado=id_estado,
        id_usuario_asignado=id_usuario_asignado
    )

    crud_incidentes.actualizar_incidente(
        conn=conn,  # Conexión
        incidente_id=incidente_id,  # ID Entero
        incidente_update=incidente_update
    )

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_incidentes"),
        status_code=303
    )


# --- Delete Incident ---

@router.post("/eliminar/{incidente_id}", name="procesar_eliminar_incidente")
async def procesar_eliminar_incidente(
        incidente_id: int,
        conn: Connection = Depends(get_session)
):
    """
    Elimina un incidente por su ID.
    """
    # CORRECCIÓN: Llamamos directo pasando ID y Conexión
    crud_incidentes.eliminar_incidente(conn=conn, incidente_id=incidente_id)

    return RedirectResponse(
        url=router.url_path_for("mostrar_lista_de_incidentes"),
        status_code=303
    )


# ===================================
# PÁGINA DE DETALLE DEL INCIDENTE
# ===================================


@router.get("/detalle/{incidente_id}", name="mostrar_detalle_incidente")
async def mostrar_detalle_incidente(
        request: Request,
        incidente_id: int,
        conn: Connection = Depends(get_session)
):
    """
    Muestra la página de detalle (expediente) de un solo incidente.
    """
    # Usamos la función del CRUD que carga todos los detalles
    incidente = crud_incidentes.get_incidente_con_detalles(conn, incidente_id)

    # También necesitamos la lista de TODOS los activos (para el menú de vincular)
    activos_para_vincular = crud_activos.get_activos(conn)

    context = {
        "request": request,
        "incidente": incidente,
        "activos_para_vincular": activos_para_vincular
    }
    return templates.TemplateResponse("incidentes/incidente_detalle.html", context)


@router.post("/detalle/{incidente_id}/add_comentario", name="procesar_nuevo_comentario")
async def procesar_nuevo_comentario(
        incidente_id: int,
        conn: Connection = Depends(get_session),
        comentario: str = Form(...)
):
    # En un app real usarías el usuario logueado. Aquí simulamos el ID 1 (Admin).
    bitacora_data = schemas.BitacoraCreate(
        id_incidente=incidente_id,
        id_usuario=1,
        comentario=comentario
    )

    # CORRECCIÓN: Pasamos 'conn'
    crud_bitacora.crear_bitacora(conn=conn, bitacora=bitacora_data)

    return RedirectResponse(
        url=router.url_path_for("mostrar_detalle_incidente", incidente_id=incidente_id),
        status_code=303
    )


@router.post("/detalle/{incidente_id}/link_activo", name="procesar_vincular_activo")
async def procesar_vincular_activo(
        incidente_id: int,
        conn: Connection = Depends(get_session),
        id_activo: int = Form(...)
):
    """
    Vincula un activo existente a este incidente.
    """
    vinculo_data = schemas.IncidenteActivoCreate(
        id_incidente=incidente_id,
        id_activo=id_activo
    )
    try:
        # CORRECCIÓN: Pasamos 'conn'
        crud_incidentes.crear_incidente_activo(conn=conn, vinculo=vinculo_data)
    except Exception as e:
        print(f"Error o duplicado al vincular: {e}")
        # conn.rollback() # Ya lo hace el CRUD si falla

    return RedirectResponse(
        url=router.url_path_for("mostrar_detalle_incidente", incidente_id=incidente_id),
        status_code=303
    )



@router.post("/detalle/{incidente_id}/unlink_activo", name="procesar_desvincular_activo")
async def procesar_desvincular_activo(
        request: Request,
        incidente_id: int,
        conn: Connection = Depends(get_session),
        id_activo: int = Form(...) # Recibimos el ID del activo a quitar
):
    """
    Rompe el vínculo entre el incidente y el activo.
    """
    crud_incidentes.eliminar_vinculo_incidente_activo(
        conn=conn,
        incidente_id=incidente_id,
        activo_id=id_activo
    )

    # Redirigimos al mismo detalle para ver el cambio
    return RedirectResponse(
        url=request.url_for("mostrar_detalle_incidente", incidente_id=incidente_id),
        status_code=303
    )