import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_api_schema():
    """Verify that the ask endpoint exists and returns 422 if empty payload."""
    response = client.post("/api/v1/ask", json={})
    assert response.status_code == 422  # Unprocessable Entity (missing fields)

def test_swagger_ui_available():
    """Verify that the Swagger UI is available."""
    response = client.get("/docs")
    assert response.status_code == 200
