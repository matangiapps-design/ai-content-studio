import importlib
from fastapi import FastAPI
from fastapi.testclient import TestClient


def make_client(tmp_path, monkeypatch):
    import server.routers.matangi_core as core
    monkeypatch.setattr(core, "DB_PATH", tmp_path / "matangi_test.sqlite3")
    core.init_db()
    app = FastAPI()
    app.include_router(core.router, prefix="/api/matangi")
    return TestClient(app)


def test_project_job_lifecycle_persists_and_cancels(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    project_response = client.post(
        "/api/matangi/projects",
        json={"name": "Test project", "description": "Integration test"},
    )
    assert project_response.status_code == 201
    project = project_response.json()

    job_response = client.post(
        "/api/matangi/jobs",
        json={
            "project_id": project["project_id"],
            "product": "content-studio",
            "task": "Create a test storyboard",
            "input": {"format": "9:16"},
        },
    )
    assert job_response.status_code == 202
    job = job_response.json()
    assert job["state"] == "queued"
    assert job["input"] == {"format": "9:16"}

    fetched = client.get(f"/api/matangi/jobs/{job['job_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["events"][0]["type"] == "job.queued"

    cancelled = client.post(f"/api/matangi/jobs/{job['job_id']}/cancel")
    assert cancelled.status_code == 202
    assert cancelled.json()["state"] == "cancelled"


def test_job_rejects_unknown_product(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    project = client.post("/api/matangi/projects", json={"name": "Project"}).json()

    response = client.post(
        "/api/matangi/jobs",
        json={
            "project_id": project["project_id"],
            "product": "unknown-product",
            "task": "Run unsupported product",
            "input": {},
        },
    )
    assert response.status_code == 422


def test_job_requires_existing_project(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    response = client.post(
        "/api/matangi/jobs",
        json={
            "project_id": "missing",
            "product": "musicvision",
            "task": "Render video",
            "input": {},
        },
    )
    assert response.status_code == 404
