from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "LegalEase"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_demo_without_key():
    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",
            "parties": "Alice (Disclosing Party), Bob (Receiving Party)",
            "terms": "Keep information confidential; 30 day termination notice",
            "dates": "September 30, 2026",
            "language": "English",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_type"] == "NDA"
    assert len(data["content"]) > 100
