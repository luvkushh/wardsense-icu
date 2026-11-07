"""FastAPI integration tests for SiteSense endpoints."""
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_rfis_count"] >= 6


def test_list_rfis_endpoint():
    response = client.get("/api/rfis")
    assert response.status_code == 200
    data = response.json()
    assert "rfis" in data
    assert len(data["rfis"]) >= 6


def test_query_endpoint():
    payload = {
        "question": "Can I core drill through the floor at Level 3 Grid B-4?",
        "level": "Level 3",
        "grid_location": "Grid B-4"
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CRITICAL_STOP_WORK"
    assert data["rework_cost_prevented"] >= 180000.00


def test_benchmarks_endpoint():
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert len(data["benchmarks"]) >= 3
