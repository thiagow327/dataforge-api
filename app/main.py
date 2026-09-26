from fastapi import FastAPI

app = FastAPI(
    title="DataForge API",
    description="Componente principal: CRUD de datasets, persistência e proxy para o insight-service.",
    version="0.1.0",
)


@app.get("/health", tags=["infra"])
def health():
    """Healthcheck simples para orquestração e testes."""
    return {"status": "ok", "service": "dataforge-api"}


@app.get("/", tags=["infra"])
def root():
    return {"service": "dataforge-api", "docs": "/docs"}
