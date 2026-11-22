from fastapi import FastAPI
from cloudx.config import settings
from cloudx.guardian import Guardian
from cloudx.providers import HiggsfieldProvider

app = FastAPI(title="CloudX Brain", version="0.1.0")
guardian = Guardian(settings.github_token)
higgsfield = HiggsfieldProvider(settings.higgsfield_api_key, settings.higgsfield_base_url)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "cloudx-brain"}

@app.get("/agents")
async def agents():
    return {"agents": [
        {"id": "guardian", "status": "ready", "role": "observe_and_diagnose"},
        {"id": "repair-planner", "status": "planned", "role": "propose_safe_repairs"},
        {"id": "model-router", "status": "planned", "role": "select_best_model"},
        {"id": "gpu-manager", "status": "planned", "role": "manage_local_and_cloud_compute"},
    ]}

@app.get("/providers/higgsfield")
async def provider_status():
    return higgsfield.status()

@app.get("/guardian/scan")
async def scan():
    return await guardian.scan(settings.repositories, settings.health_urls)
