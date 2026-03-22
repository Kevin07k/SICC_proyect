# router/sedes.py
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection
from typing import Optional

from app.crud import sedes as crud
from app import schemas
from app.core.database import get_session

router = APIRouter(prefix="/sedes", tags=["Sedes"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", name="mostrar_lista_de_sedes")
async def mostrar_lista_de_sedes(request: Request, conn: Connection = Depends(get_session)):
    sedes = crud.get_sedes(conn)
    return templates.TemplateResponse("sedes/sedes_lista.html", {"request": request, "sedes": sedes})

@router.get("/crear", name="mostrar_formulario_crear_sede")
async def mostrar_formulario_crear_sede(request: Request):
    return templates.TemplateResponse("sedes/sede_form.html", {"request": request, "sede": None})

@router.post("/crear", name="procesar_crear_sede")
async def procesar_crear_sede(
    conn: Connection = Depends(get_session),
    nombre_sede: str = Form(...),
    nivel_criticidad: str = Form(...)
):
    sede_data = schemas.SedeCreate(nombre_sede=nombre_sede, nivel_criticidad=nivel_criticidad)
    crud.crear_sede(conn, sede_data)
    return RedirectResponse(url=router.url_path_for("mostrar_lista_de_sedes"), status_code=303)

@router.get("/editar/{sede_id}", name="mostrar_formulario_editar_sede")
async def mostrar_formulario_editar_sede(request: Request, sede_id: int, conn: Connection = Depends(get_session)):
    sede = crud.get_sede(conn, sede_id)
    return templates.TemplateResponse("sedes/sede_form.html", {"request": request, "sede": sede})

@router.post("/editar/{sede_id}", name="procesar_editar_sede")
async def procesar_editar_sede(
    sede_id: int,
    conn: Connection = Depends(get_session),
    nombre_sede: str = Form(...),
    nivel_criticidad: str = Form(...)
):
    sede_update = schemas.SedeUpdate(nombre_sede=nombre_sede, nivel_criticidad=nivel_criticidad)
    crud.actualizar_sede(conn, sede_id, sede_update)
    return RedirectResponse(url=router.url_path_for("mostrar_lista_de_sedes"), status_code=303)

@router.post("/eliminar/{sede_id}", name="procesar_eliminar_sede")
async def procesar_eliminar_sede(sede_id: int, conn: Connection = Depends(get_session)):
    crud.eliminar_sede(conn, sede_id)
    return RedirectResponse(url=router.url_path_for("mostrar_lista_de_sedes"), status_code=303)
