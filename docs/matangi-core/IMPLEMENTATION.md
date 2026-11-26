# MATANGI Core — first backend milestone

This implementation adds a metadata-only orchestration API inside the existing FastAPI AI Content Studio backend.

## Routes
All routes are under `/api/matangi` and are protected by the existing API-token middleware in `server/main.py`.

- `GET /capabilities`: reports honestly which adapters are not connected.
- `POST /projects`, `GET /projects`, `GET /projects/{project_id}`
- `POST /jobs`, `GET /jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/cancel`

## Persistence
SQLite database at `data/matangi_core.sqlite3` by default. Override with `MATANGI_CORE_DB`. Tables: projects, jobs, job_events.

## Current limitations
- Jobs are persisted in `queued` state only. No model, GPU or product worker is connected.
- No user-level identity/tenant isolation yet; the parent application currently protects API routes with its existing shared token.
- No billing, external storage, webhook or deployment configuration is added.
- This does not alter existing AI Content Studio generation routes.

## Local verification
From the repository root, with existing dependencies installed:

```bash
python -m compileall -q server/routers/matangi_core.py server/main.py
python -m pytest tests/ -q
```

Then start the existing backend with the repository's normal Docker Compose setup and query `/api/matangi/capabilities` using the configured authenticated session.

Do not expose this API publicly until tenant authorization, rate limiting, audit review and worker isolation are implemented.
