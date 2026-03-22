# router/incidentes.py

# ===================================
# Incidentes CRUD
# ===================================

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection, text  # <--- CAMBIO: Connection, text
from typing import Optional

from app.crud import incidentes as crud_incidentes  # Asegúrate de importar bien tus CRUDS
from app.crud import categorias as crud_categorias
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
        "tipos": crud_categorias.get_tipos_incidente(conn),
        "prioridades": crud_categorias.get_prioridades(conn),
        "estados": crud_categorias.get_estados(conn),
        "usuarios": crud_usuarios.get_usuarios(conn),
        "activos": crud_activos.get_activos(conn)
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
        id_usuario_asignado: Optional[int] = Form(None),
        id_activo: Optional[int] = Form(None)
):
    # Usamos RAW SQL para llamar al Stored Procedure
    query = text("""
        EXEC sp_RegistrarIncidenteCompleto 
            @titulo = :titulo,
            @descripcion_detallada = :descripcion,
            @id_tipo = :tipo,
            @id_prioridad = :prioridad,
            @id_estado = :estado,
            @id_usuario_asignado = :usuario,
            @id_activo = :activo
    """)
    try:
        conn.execute(query, {
            "titulo": titulo,
            "descripcion": descripcion_detallada,
            "tipo": id_tipo,
            "prioridad": id_prioridad,
            "estado": id_estado,
            "usuario": id_usuario_asignado,
            "activo": id_activo
        })
        conn.commit()  # Aseguramos el entorno SQLAlchemy aunque el SP tenga COMMIT TRAN
    except Exception as e:
        print(f"Error ejecutando SP transaccional: {e}")
        conn.rollback()

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
        "tipos": crud_categorias.get_tipos_incidente(conn),
        "prioridades": crud_categorias.get_prioridades(conn),
        "estados": crud_categorias.get_estados(conn),
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

    # También necesitamos la lista de TODOS los usuarios
    usuarios_para_vincular = crud_usuarios.get_usuarios(conn)

    context = {
        "request": request,
        "incidente": incidente,
        "activos_para_vincular": activos_para_vincular,
        "usuarios_para_vincular": usuarios_para_vincular
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

# ===================================
# SPRINT 1: VISTA DE AUDITORIA GERENCIAL
# ===================================

@router.get("/auditoria/sedes", name="auditoria_incidentes_sedes")
async def auditoria_incidentes_sedes(
        conn: Connection = Depends(get_session)
):
    """
    Endpoint gerencial que consulta EXCLUSIVAMENTE la vista vw_Auditoria_Incidentes_Sede.
    Esto proporciona seguridad lógica al no exponer las tablas base directamente.
    """
    query = text("SELECT * FROM vw_Auditoria_Incidentes_Sede")
    result = conn.execute(query).mappings().fetchall()
    
    # Retornamos los datos directamente como JSON para consumo de frontend/gerencial
    return {"data": [dict(row) for row in result]}

# ===================================
# SPRINT 5: STORED PROCEDURES
# ===================================

@router.post("/detalle/{incidente_id}/cerrar", name="procesar_cerrar_incidente")
async def procesar_cerrar_incidente(
    request: Request,
    incidente_id: int,
    nota_cierre: str = Form("Incidente cerrado de forma automática por interfaz web."),
    conn: Connection = Depends(get_session)
):
    query = text("""
        EXEC sp_CerrarIncidente 
            @id_incidente = :incidente_id, 
            @id_usuario_cierre = 1,
            @nota_cierre = :nota_cierre
    """)
    try:
        conn.execute(query, {
            "incidente_id": incidente_id,
            "nota_cierre": nota_cierre
        })
        conn.commit() 
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
        
    return RedirectResponse(
        url=request.url_for("mostrar_detalle_incidente", incidente_id=incidente_id),
        status_code=303
    )

@router.post("/detalle/{incidente_id}/asignar", name="procesar_asignar_analista")
async def procesar_asignar_analista(
    request: Request,
    incidente_id: int,
    id_usuario: int = Form(...),
    conn: Connection = Depends(get_session)
):
    query = text("""
        EXEC sp_AsignarAnalista 
            @id_incidente = :incidente_id, 
            @id_usuario = :id_usuario
    """)
    try:
        conn.execute(query, {
            "incidente_id": incidente_id,
            "id_usuario": id_usuario
        })
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
        
    return RedirectResponse(
        url=request.url_for("mostrar_detalle_incidente", incidente_id=incidente_id),
        status_code=303
    )