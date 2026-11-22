from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from cloudx.config import settings
from cloudx.guardian import Guardian
from cloudx.memory import EventMemory
from cloudx.providers import HiggsfieldProvider
from cloudx.repair_agent import RepairAgent

app = FastAPI(title="CloudX Brain", version="0.3.0")
guardian = Guardian(settings.github_token)
memory = EventMemory()
higgsfield = HiggsfieldProvider(settings.higgsfield_api_key_id, settings.higgsfield_api_key_secret)
repair_agent = RepairAgent()

class HiggsfieldGeneration(BaseModel):
    model_path: str = Field(min_length=3, max_length=180)
    input: dict
    idempotency_key: str | None = Field(default=None, max_length=128)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "cloudx-brain", "version": "0.3.0"}

@app.get("/agents")
async def agents():
    return {"agents": [
        {"id": "guardian", "status": "ready", "role": "monitor_repositories_ci_and_services"},
        {"id": "repair-agent", "status": "ready", "role": "diagnose_and_propose_approval_gated_repairs"},
        {"id": "memory", "status": "ready", "role": "persist_operational_events"},
        {"id": "higgsfield", "status": "ready" if higgsfield.configured else "needs_credentials", "role": "image_and_video_generation"},
        {"id": "model-router", "status": "planned", "role": "select_best_model"},
        {"id": "gpu-manager", "status": "planned", "role": "manage_local_and_cloud_compute"},
    ]}

@app.get("/providers/higgsfield")
async def provider_status():
    return higgsfield.info()

@app.post("/higgsfield/requests")
async def create_higgsfield_request(request: HiggsfieldGeneration):
    if not request.input:
        raise HTTPException(status_code=422, detail="The model input object cannot be empty.")
    try:
        result = await higgsfield.submit(request.model_path, request.input, request.idempotency_key)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Higgsfield request failed: {type(exc).__name__}")

@app.get("/higgsfield/requests/{request_id}")
async def get_higgsfield_request(request_id: str):
    try:
        return await higgsfield.status(request_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Higgsfield status request failed: {type(exc).__name__}")

@app.get("/guardian/scan")
async def scan():
    report = await guardian.scan(settings.repositories, settings.health_urls)
    memory.record(report["checked_at"], "guardian_scan", report)
    report["repair_plans"] = repair_agent.plan(report["findings"])
    return report

@app.get("/memory/recent")
async def recent_memory(limit: int = Query(default=30, ge=1, le=200)):
    return {"events": memory.recent(limit)}
