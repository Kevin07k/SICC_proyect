from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.auth import CUENTAS, get_current_user

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", name="mostrar_login")
async def mostrar_login(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "error": None
    })


@router.post("/login", name="procesar_login")
async def procesar_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    cuenta = CUENTAS.get(username.lower())

    if not cuenta or cuenta["password"] != password:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="usuario", value=username.lower(), httponly=True)
    response.set_cookie(key="rol", value=cuenta["rol"], httponly=True)
    response.set_cookie(key="nombre", value=cuenta["nombre"], httponly=True)
    return response


@router.get("/logout", name="procesar_logout")
async def procesar_logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("usuario")
    response.delete_cookie("rol")
    response.delete_cookie("nombre")
    return response
