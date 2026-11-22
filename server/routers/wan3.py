"""Authenticated WaveSpeed Wan 3.0 scene rendering endpoints."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from config import load_config
from server.core.queue import create_job, get_job, submit_to_queue, update_job, current_job_id
from server.core.security import media_path
from services.wan3_client import Wan3Client

router = APIRouter()

class Wan3RenderRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=8000)
    duration: int = Field(default=5, ge=2, le=30)
    aspect_ratio: str = "16:9"
    resolution: str = "720p"
    enable_audio: bool = True
    enable_prompt_expansion: bool = True
    seed: Optional[int] = None

def run_wan3_task(job_id: str, req: Wan3RenderRequest):
    current_job_id.set(job_id)
    try:
        cfg = load_config()
        api_key = cfg.get("WAVESPEED_API_KEY") or cfg.get("WAVESPEED_AI_KEY") or os.getenv("WAVESPEED_API_KEY")
        client = Wan3Client(api_key=api_key)
        update_job(job_id, status="running", step="Submitting scene to WaveSpeed Wan 3.0", progress=0.05)
        task_id = client.submit(prompt=req.prompt, duration=req.duration, aspect_ratio=req.aspect_ratio,
            resolution=req.resolution, enable_audio=req.enable_audio,
            enable_prompt_expansion=req.enable_prompt_expansion, seed=req.seed)
        update_job(job_id, step=f"Rendering with Wan 3.0 • task {task_id}", progress=0.15)
        video_url = client.wait(task_id)
        output = str(Path("workspace") / f"wan3_{job_id}.mp4")
        client.download(video_url, output)
        if not Path(output).is_file() or Path(output).stat().st_size == 0:
            raise RuntimeError("Provider completed but the downloaded video is empty.")
        update_job(job_id, status="completed", step="Scene render complete", progress=1.0, result=output)
    except Exception as exc:
        update_job(job_id, status="failed", step="Scene render failed", error=str(exc), progress=1.0)
    finally:
        current_job_id.set(None)

@router.get("/status")
def wan3_status():
    cfg = load_config()
    configured = bool(cfg.get("WAVESPEED_API_KEY") or cfg.get("WAVESPEED_AI_KEY") or os.getenv("WAVESPEED_API_KEY"))
    return {"engine": "WaveSpeed Wan 3.0", "configured": configured, "max_duration_seconds": 30,
            "resolutions": ["480p", "720p", "1080p"],
            "note": "Each generation is billed by WaveSpeed. Configure the key on the server only."}

@router.post("/generate")
def start_wan3_render(req: Wan3RenderRequest):
    if req.aspect_ratio not in {"16:9", "9:16", "1:1", "4:3", "3:4"}:
        raise HTTPException(422, "Unsupported aspect ratio.")
    if req.resolution not in {"480p", "720p", "1080p"}:
        raise HTTPException(422, "Resolution must be 480p, 720p or 1080p.")
    cfg = load_config()
    if not (cfg.get("WAVESPEED_API_KEY") or cfg.get("WAVESPEED_AI_KEY") or os.getenv("WAVESPEED_API_KEY")):
        raise HTTPException(503, "WaveSpeed is not configured. Add WAVESPEED_API_KEY to the server environment/config.")
    job_id = create_job("Wan 3.0: " + req.prompt[:90], job_type="wan3")
    submit_to_queue(run_wan3_task, job_id, req)
    return {"job_id": job_id, "status": "queued"}

@router.get("/jobs/{job_id}")
def wan3_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Render job not found.")
    return {key: job.get(key) for key in ("id", "status", "progress", "step", "result", "error")}

@router.get("/jobs/{job_id}/video")
def download_wan3_video(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Render job not found.")
    if job.get("status") != "completed" or not job.get("result"):
        raise HTTPException(409, "Video is not ready yet.")
    path = media_path(job["result"], roots=("workspace",))
    return FileResponse(path, media_type="video/mp4", filename=f"MATANGI-{job_id}.mp4")
