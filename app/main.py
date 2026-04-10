from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.core.auth import get_current_user

from app.api import dashboard, incidentes, activos, usuarios, admin, bitacora, sedes, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- INICIANDO SISTEMA SICC ---")
    print("Verificando base de datos...")
    print("--- TABLAS LISTAS ---")
    yield
    print("--- APAGANDO SISTEMA ---")

app = FastAPI(
    title="Sistema de Gestión de Incidentes",
    description="Proyecto de Base de Datos II con FastAPI y SQL Server.",
    lifespan=lifespan
)

# --- Montar Archivos Estáticos ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- Middleware de autenticación ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    rutas_publicas = ["/login", "/static", "/docs", "/openapi.json", "/redoc"]
    path = request.url.path

    for ruta in rutas_publicas:
        if path.startswith(ruta):
            return await call_next(request)

    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    request.state.user = user
    response = await call_next(request)
    return response


# --- CONECTAR LAS RUTAS ---
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(incidentes.router)
app.include_router(activos.router)
app.include_router(usuarios.router)
app.include_router(admin.router)
app.include_router(bitacora.router)
app.include_router(sedes.router)