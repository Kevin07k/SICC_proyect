from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection

from app.crud import bitacora as crud
from app import schemas
from app.core.database import get_session

# --- CONFIGURACIÓN ---
router = APIRouter(
    prefix="/bitacora",
    tags=["Bitacora"]
)

templates = Jinja2Templates(directory="app/templates")


# ==========================================
#             EDITAR BITACORA
# ==========================================

@router.get("/editar/{bitacora_id}", name="mostrar_formulario_editar_bitacora")
async def mostrar_formulario_editar_bitacora(
        request: Request,
        bitacora_id: int,
        conn: Connection = Depends(get_session)
):
    bitacora = crud.get_bitacora(conn, bitacora_id)
    context = {
        "request": request,
        "bitacora": bitacora
    }
    return templates.TemplateResponse("incidentes/bitacora_form.html", context)


@router.post("/editar/{bitacora_id}", name="procesar_editar_bitacora")
async def procesar_editar_bitacora(
        request: Request,  # <--- IMPORTANTE: Necesitamos 'request' para redirigir a otro router
        bitacora_id: int,
        conn: Connection = Depends(get_session),
        comentario: str = Form(...)
):
    # 1. Obtenemos la bitácora actual para saber el ID del incidente padre
    db_bitacora = crud.get_bitacora(conn, bitacora_id)

    # En SQL Puro es un diccionario, accedemos con corchetes
    id_incidente_padre = db_bitacora['id_incidente']

    # 2. Actualizamos
    update_data = schemas.BitacoraUpdate(comentario=comentario)
    crud.actualizar_bitacora(
        conn=conn,
        bitacora_id=bitacora_id,
        bitacora_update=update_data
    )

    # 3. Redirigimos usando request.url_for (Busca en TODA la app)
    return RedirectResponse(
        url=request.url_for("mostrar_detalle_incidente", incidente_id=id_incidente_padre),
        status_code=303
    )


# ==========================================
#            ELIMINAR BITACORA
# ==========================================

@router.post("/eliminar/{bitacora_id}", name="procesar_eliminar_bitacora")
async def procesar_eliminar_bitacora(
        request: Request,  # <--- IMPORTANTE: Agregado aquí también
        bitacora_id: int,
        conn: Connection = Depends(get_session)
):
    # 1. Recuperamos para saber a dónde volver
    db_bitacora = crud.get_bitacora(conn, bitacora_id)

    if db_bitacora:
        id_incidente_padre = db_bitacora['id_incidente']

        # 2. Eliminamos
        crud.eliminar_bitacora(conn=conn, bitacora_id=bitacora_id)

        # 3. Redirigimos al detalle del incidente
        return RedirectResponse(
            url=request.url_for("mostrar_detalle_incidente", incidente_id=id_incidente_padre),
            status_code=303
        )

    # Si algo falla, volvemos a la lista general
    return RedirectResponse(
        url=request.url_for("mostrar_lista_de_incidentes"),
        status_code=303
    )