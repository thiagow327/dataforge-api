import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, get_db
from app.routers import datasets as datasets_router


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    # Evita chamada de rede ao insight-service durante os testes
    monkeypatch.setattr(
        datasets_router,
        "request_analysis",
        lambda dataset_id, records: {"dataset_id": dataset_id, "summary": "ok", "n": len(records)},
    )
    # TestClient sem `with` para não disparar o lifespan (que conectaria no Postgres)
    yield TestClient(main.app)
    main.app.dependency_overrides.clear()


PAYLOAD = {
    "name": "Vendas Teste",
    "description": "amostra",
    "records": [
        {"data": "2026-03-01", "produto": "Notebook", "cep": "01310-100", "valor": 3299},
        {"data": "2026-03-02", "produto": "Mouse", "cep": None, "valor": 49},
    ],
}


def test_crud_completo(client):
    # POST
    resp = client.post("/datasets", json=PAYLOAD)
    assert resp.status_code == 201
    ds = resp.json()
    assert ds["record_count"] == 2
    ds_id = ds["id"]

    # GET lista
    resp = client.get("/datasets")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    # GET detalhe
    assert client.get(f"/datasets/{ds_id}").status_code == 200

    # PUT
    resp = client.put(f"/datasets/{ds_id}", json={"description": "nova"})
    assert resp.json()["description"] == "nova"

    # DELETE + 404
    assert client.delete(f"/datasets/{ds_id}").status_code == 204
    assert client.get(f"/datasets/{ds_id}").status_code == 404


def test_get_inexistente_404(client):
    assert client.get("/datasets/999").status_code == 404


def test_analyze_e_insights(client):
    ds_id = client.post("/datasets", json=PAYLOAD).json()["id"]

    # analyze (insight-service mockado) → persiste
    resp = client.post(f"/datasets/{ds_id}/analyze")
    assert resp.status_code == 200
    assert resp.json()["result"]["summary"] == "ok"

    # insights persistidos
    resp = client.get(f"/datasets/{ds_id}/insights")
    assert resp.status_code == 200
    assert resp.json()["result"]["n"] == 2


def test_insights_sem_analise_404(client):
    ds_id = client.post("/datasets", json=PAYLOAD).json()["id"]
    assert client.get(f"/datasets/{ds_id}/insights").status_code == 404
