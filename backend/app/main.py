from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    activos,
    auth,
    bitacora,
    catalogos,
    health,
    incidentes,
    mongo_documentos,
    reportes,
    sync,
    usuarios,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"{settings.app_name} iniciado")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="API REST SICC — ciberseguridad multi-sede",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(sync.router)
    app.include_router(catalogos.router)
    app.include_router(usuarios.router)
    app.include_router(incidentes.router)
    app.include_router(bitacora.router)
    app.include_router(activos.router)
    app.include_router(mongo_documentos.incidente_router)
    app.include_router(mongo_documentos.activo_router)
    app.include_router(reportes.router)
    return app


app = create_app()
