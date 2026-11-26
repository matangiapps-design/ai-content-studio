"""MATANGI Core orchestration API.

This first milestone persists projects and job requests. It deliberately does not
claim to execute model/GPU jobs; a worker adapter must be registered separately.
"""
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()
DB_PATH = Path(os.getenv("MATANGI_CORE_DB", "data/matangi_core.sqlite3"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

PRODUCTS = {"content-studio", "musicvision", "seed-vc", "cloudphone"}
TERMINAL_STATES = {"succeeded", "failed", "cancelled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect():
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(project_id),
            product TEXT NOT NULL,
            task TEXT NOT NULL,
            provider TEXT,
            input_json TEXT NOT NULL,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            output_json TEXT,
            error_json TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_matangi_jobs_project_created
            ON jobs(project_id, created_at DESC);
        CREATE TABLE IF NOT EXISTS job_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL REFERENCES jobs(job_id),
            event_type TEXT NOT NULL,
            detail_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)


init_db()


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class JobCreate(BaseModel):
    project_id: str
    product: str
    task: str = Field(min_length=1, max_length=500)
    provider: Optional[str] = None
    input: dict[str, Any] = Field(default_factory=dict)


def project_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def job_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["input"] = json.loads(item.pop("input_json"))
    item["output"] = json.loads(item.pop("output_json")) if item.get("output_json") else None
    item["error"] = json.loads(item.pop("error_json")) if item.get("error_json") else None
    return item


def event(db: sqlite3.Connection, job_id: str, event_type: str, detail: dict[str, Any]) -> None:
    db.execute(
        "INSERT INTO job_events(job_id,event_type,detail_json,created_at) VALUES(?,?,?,?)",
        (job_id, event_type, json.dumps(detail), utc_now()),
    )


@router.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {
        "service": "MATANGI Core",
        "mode": "orchestration-metadata-only",
        "worker_execution": "not-configured",
        "products": {
            product: {"registered": True, "worker_connected": False}
            for product in sorted(PRODUCTS)
        },
        "models": {"qwen": "not-connected"},
        "gpu": {"worker": "not-connected"},
        "billing": {"connected": False},
    }


@router.post("/projects", status_code=201)
def create_project(payload: ProjectCreate) -> dict[str, Any]:
    project_id = f"prj_{uuid.uuid4().hex}"
    now = utc_now()
    with connect() as db:
        db.execute(
            "INSERT INTO projects(project_id,name,description,created_at) VALUES(?,?,?,?)",
            (project_id, payload.name, payload.description, now),
        )
        row = db.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
    return project_dict(row)


@router.get("/projects")
def list_projects(limit: int = Query(default=50, ge=1, le=100)) -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM projects ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [project_dict(row) for row in rows]


@router.get("/projects/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_dict(row)


@router.post("/jobs", status_code=202)
def create_job(payload: JobCreate) -> dict[str, Any]:
    if payload.product not in PRODUCTS:
        raise HTTPException(status_code=422, detail=f"Unsupported product. Choose one of: {', '.join(sorted(PRODUCTS))}")
    job_id = f"job_{uuid.uuid4().hex}"
    now = utc_now()
    with connect() as db:
        project = db.execute(
            "SELECT project_id FROM projects WHERE project_id=?", (payload.project_id,)
        ).fetchone()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        db.execute(
            """INSERT INTO jobs(job_id,project_id,product,task,provider,input_json,state,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (job_id, payload.project_id, payload.product, payload.task, payload.provider,
             json.dumps(payload.input), "queued", now, now),
        )
        event(db, job_id, "job.queued", {"note": "Persisted; waiting for a configured worker adapter."})
        row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    return job_dict(row)


@router.get("/jobs")
def list_jobs(
    project_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[dict[str, Any]]:
    with connect() as db:
        if project_id:
            rows = db.execute(
                "SELECT * FROM jobs WHERE project_id=? ORDER BY created_at DESC LIMIT ?",
                (project_id, limit),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [job_dict(row) for row in rows]


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Job not found")
        events = db.execute(
            "SELECT event_type,detail_json,created_at FROM job_events WHERE job_id=? ORDER BY event_id",
            (job_id,),
        ).fetchall()
    result = job_dict(row)
    result["events"] = [
        {"type": item["event_type"], "detail": json.loads(item["detail_json"]), "created_at": item["created_at"]}
        for item in events
    ]
    return result


@router.post("/jobs/{job_id}/cancel", status_code=202)
def cancel_job(job_id: str) -> dict[str, Any]:
    now = utc_now()
    with connect() as db:
        row = db.execute("SELECT state FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Job not found")
        if row["state"] in TERMINAL_STATES:
            raise HTTPException(status_code=409, detail=f"Job is already {row['state']}")
        db.execute("UPDATE jobs SET state='cancelled',updated_at=? WHERE job_id=?", (now, job_id))
        event(db, job_id, "job.cancelled", {"note": "Cancelled before worker execution is enabled."})
        updated = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    return job_dict(updated)
