from fastapi import FastAPI, Query
from cloudx.config import settings
from cloudx.guardian import Guardian
from cloudx.memory import EventMemory
from cloudx.providers import HiggsfieldProvider
from cloudx.repair_agent import RepairAgent

app = FastAPI(title="CloudX Brain", version="0.2.0")
guardian = Guardian(settings.github_token)
memory = EventMemory()
higgsfield = HiggsfieldProvider(settings.higgsfield_api_key, settings.higgsfield_base_url)
repair_agent = RepairAgent()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "cloudx-brain", "version": "0.2.0"}

@app.get("/agents")
async def agents():
    return {"agents": [
        {"id": "guardian", "status": "ready", "role": "monitor_repositories_ci_and_services"},
        {"id": "repair-agent", "status": "ready", "role": "diagnose_and_propose_approval_gated_repairs"},
        {"id": "memory", "status": "ready", "role": "persist_operational_events"},
        {"id": "model-router", "status": "planned", "role": "select_best_model"},
        {"id": "gpu-manager", "status": "planned", "role": "manage_local_and_cloud_compute"},
    ]}

@app.get("/providers/higgsfield")
async def provider_status():
    return higgsfield.status()

@app.get("/guardian/scan")
async def scan():
    report = await guardian.scan(settings.repositories, settings.health_urls)
    memory.record(report["checked_at"], "guardian_scan", report)
    report["repair_plans"] = repair_agent.plan(report["findings"])
    return report

@app.get("/memory/recent")
async def recent_memory(limit: int = Query(default=30, ge=1, le=200)):
    return {"events": memory.recent(limit)}
