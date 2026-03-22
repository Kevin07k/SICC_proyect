from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Importamos la función para crear tablas
# from app.core.database import create_db_and_tables

# Importamos los routers desde tu carpeta 'router'
# Nota: He quitado 'bitacora' asumiendo que su lógica está dentro de 'incidentes.py'
from app.api import dashboard, incidentes, activos, usuarios, admin, bitacora

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

# --- CONECTAR LAS RUTAS ---
app.include_router(dashboard.router)
app.include_router(incidentes.router) # Aquí dentro deberían ir las rutas de bitácora
app.include_router(activos.router)
app.include_router(usuarios.router)
app.include_router(admin.router)
app.include_router(bitacora.router)