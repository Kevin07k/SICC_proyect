from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text, Connection

from app.core.auth import get_current_user, authenticate_user, hash_password, CUENTAS
from app.core.database import get_session

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
    password: str = Form(...),
    conn: Connection = Depends(get_session)
):
    # Autenticar contra la BD (con fallback al dict CUENTAS para DBA)
    user = authenticate_user(conn, username, password)

    if not user:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="usuario", value=user["usuario"], httponly=True)
    response.set_cookie(key="rol", value=user["rol"], httponly=True)
    response.set_cookie(key="nombre", value=user["nombre"], httponly=True)
    return response


@router.get("/register", name="mostrar_registro")
async def mostrar_registro(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "error": None,
        "success": None,
        "form_data": None
    })


@router.post("/register", name="procesar_registro")
async def procesar_registro(
    request: Request,
    nombre_completo: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    conn: Connection = Depends(get_session)
):
    form_data = {
        "nombre_completo": nombre_completo,
        "email": email,
        "username": username
    }

    # Validaciones del lado del servidor
    if len(username.strip()) < 3:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "El nombre de usuario debe tener al menos 3 caracteres.",
            "success": None,
            "form_data": form_data
        })

    if len(password) < 6:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "La contraseña debe tener al menos 6 caracteres.",
            "success": None,
            "form_data": form_data
        })

    if password != confirm_password:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Las contraseñas no coinciden.",
            "success": None,
            "form_data": form_data
        })

    # Verificar username único
    username_clean = username.strip().lower()

    # No permitir nombres de usuario reservados (ej. dba)
    if username_clean in CUENTAS:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": f"El nombre de usuario '{username_clean}' está reservado.",
            "success": None,
            "form_data": form_data
        })

    check_username = text("SELECT COUNT(*) AS cnt FROM Usuarios WHERE username = :username AND eliminado = 0")
    result = conn.execute(check_username, {"username": username_clean})
    if result.mappings().first()["cnt"] > 0:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Ese nombre de usuario ya está en uso.",
            "success": None,
            "form_data": form_data
        })

    # Verificar email único
    check_email = text("SELECT COUNT(*) AS cnt FROM Usuarios WHERE email = :email AND eliminado = 0")
    result = conn.execute(check_email, {"email": email.strip().lower()})
    if result.mappings().first()["cnt"] > 0:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Ese correo electrónico ya está registrado.",
            "success": None,
            "form_data": form_data
        })

    # Crear el usuario con rol Developer
    try:
        password_hash = hash_password(password)

        insert_query = text("""
            INSERT INTO Usuarios (nombre_completo, email, username, password_hash, rol)
            VALUES (:nombre_completo, :email, :username, :password_hash, :rol)
        """)

        conn.execute(insert_query, {
            "nombre_completo": nombre_completo.strip(),
            "email": email.strip().lower(),
            "username": username_clean,
            "password_hash": password_hash,
            "rol": "Developer"
        })
        conn.commit()

        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": None,
            "success": f"¡Cuenta creada exitosamente! Ya puedes iniciar sesión como '{username_clean}'.",
            "form_data": None
        })

    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        if "UNIQUE" in error_msg or "unique" in error_msg:
            return templates.TemplateResponse("auth/register.html", {
                "request": request,
                "error": "El correo electrónico o nombre de usuario ya existe.",
                "success": None,
                "form_data": form_data
            })
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": f"Error al crear la cuenta: {error_msg}",
            "success": None,
            "form_data": form_data
        })


@router.get("/logout", name="procesar_logout")
async def procesar_logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("usuario")
    response.delete_cookie("rol")
    response.delete_cookie("nombre")
    return response
