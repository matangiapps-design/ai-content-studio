"""Contract tests for the OpenShorts adapter; no external service is contacted."""
import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from server.routers import openshorts


def _client():
    app = FastAPI()
    app.include_router(openshorts.router, prefix="/api/openshorts")
    return TestClient(app)


def test_status_unconfigured(monkeypatch):
    monkeypatch.delenv("OPENSHORTS_API_URL", raising=False)
    response = _client().get("/api/openshorts/status")
    assert response.status_code == 200
    assert response.json()["configured"] is False
    assert response.json()["reachable"] is False


def test_public_host_blocked_by_default(monkeypatch):
    monkeypatch.setenv("OPENSHORTS_API_URL", "https://api.openshorts.app")
    monkeypatch.delenv("OPENSHORTS_ALLOW_HOSTED", raising=False)
    base, _, error = openshorts._service_config()
    assert base == ""
    assert "disabled" in error.lower()


def test_generate_requires_rights_acknowledgement(monkeypatch):
    monkeypatch.setenv("OPENSHORTS_API_URL", "http://openshorts-backend:8000")
    response = _client().post("/api/openshorts/generate", json={
        "url": "https://www.youtube.com/watch?v=abc123",
        "acknowledged": False,
    })
    assert response.status_code == 422
    assert "permission" in response.text.lower()


def test_generate_and_poll_job(monkeypatch):
    monkeypatch.setenv("OPENSHORTS_API_URL", "http://openshorts-backend:8000")
    calls = []

    async def fake_request(method, path, payload=None):
        calls.append((method, path, payload))
        if path == "/api/process":
            return 200, {"job_id": "job_123", "status": "queued"}
        if path == "/api/status/job_123":
            return 200, {
                "status": "completed",
                "logs": ["done"],
                "result": {"clips": [{"title": "Clip 1", "download_url": "https://cdn.example/clip.mp4"}]},
            }
        raise AssertionError(f"Unexpected request: {method} {path}")

    monkeypatch.setattr(openshorts, "_request", fake_request)
    client = _client()
    submitted = client.post("/api/openshorts/generate", json={
        "url": "https://www.youtube.com/watch?v=abc123",
        "acknowledged": True,
        "target_clips": 4,
    })
    assert submitted.status_code == 200
    assert submitted.json()["job_id"] == "job_123"
    assert calls[0][0:2] == ("POST", "/api/process")
    assert calls[0][2]["acknowledged"] is True
    assert calls[0][2]["output_format"] == "vertical"
    assert calls[0][2]["target_clips"] == 4

    polled = client.get("/api/openshorts/jobs/job_123")
    assert polled.status_code == 200
    assert polled.json()["status"] == "completed"
    assert polled.json()["clips"][0]["title"] == "Clip 1"
    assert polled.json()["clips"][0]["matangi_download_path"] == "/api/openshorts/jobs/job_123/clips/0/download"


def test_invalid_job_id_rejected(monkeypatch):
    monkeypatch.setenv("OPENSHORTS_API_URL", "http://openshorts-backend:8000")
    response = _client().get("/api/openshorts/jobs/../../secrets")
    assert response.status_code in {404, 400}


def test_optional_gemini_key_is_forwarded_only_as_header(monkeypatch):
    monkeypatch.setenv("OPENSHORTS_API_KEY", "private-api-token")
    monkeypatch.setenv("OPENSHORTS_GEMINI_API_KEY", "private-gemini-token")
    headers = openshorts._headers()
    assert headers["Authorization"] == "Bearer private-api-token"
    assert headers["X-Gemini-Key"] == "private-gemini-token"
    assert "private-gemini-token" not in str(headers.get("Authorization"))
