from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 — registra os modelos no metadata
from app.database import Base, engine
from app.routers import datasets


@asynccontextmanager
async def lifespan(app: FastAPI):
    # MVP: cria as tabelas na subida. (Migrações com Alembic ficam para depois.)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DataForge API",
    description="Componente principal: CRUD de datasets, persistência e proxy para o insight-service.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(datasets.router)


@app.get("/health", tags=["infra"])
def health():
    """Healthcheck simples para orquestração e testes."""
    return {"status": "ok", "service": "dataforge-api"}


@app.get("/", tags=["infra"])
def root():
    return {"service": "dataforge-api", "docs": "/docs"}
