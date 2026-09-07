import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.database.seed import seed_database

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_list_invoices():
    with TestClient(app) as client:
        response = client.get("/api/invoices")
        assert response.status_code == 200
        invoices = response.json()
        assert isinstance(invoices, list)
        assert len(invoices) >= 4  # Benchmark invoices

def test_analytics_dashboard():
    with TestClient(app) as client:
        response = client.get("/api/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "charts" in data
        assert data["kpis"]["total_invoices"] >= 4

def test_agents_overview():
    with TestClient(app) as client:
        response = client.get("/api/agents/overview")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) == 10  # All 10 specialized agents

def test_ai_chat():
    with TestClient(app) as client:
        response = client.post("/api/ai/chat", json={"role": "user", "content": "What is the status of invoices?"})
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "tools_used" in data
