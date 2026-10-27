from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_transcription_endpoint_mock():
    response = client.post(
        "/v1/transcriptions",
        files={"file": ("sample.wav", b"fake audio", "audio/wav")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "sample.wav"
    assert "text" in body
    assert "segments" in body
