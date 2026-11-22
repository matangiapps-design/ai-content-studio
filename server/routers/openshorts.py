"""Free-first adapter for a self-hosted OpenShorts instance.

Hosted OpenShorts endpoints are blocked by default to prevent surprise metered
usage. Set OPENSHORTS_ALLOW_HOSTED=true only when paid cloud usage is intended.
"""
from __future__ import annotations

import ipaddress
import os
import re
from typing import Any, Optional
from urllib.parse import urljoin, urlsplit

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, HttpUrl, model_validator

router = APIRouter()
_JOB_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "host.docker.internal", "openshorts", "openshorts-backend"}


def _service_config() -> tuple[str, bool, Optional[str]]:
    """Return (base_url, self_hosted, config_error); never accept user-supplied hosts."""
    raw = os.getenv("OPENSHORTS_API_URL", "").strip()
    if not raw:
        return "", True, "OPENSHORTS_API_URL is not configured."
    try:
        parsed = urlsplit(raw)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Use an http:// or https:// OpenShorts API URL.")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("OpenShorts API URL must not contain credentials, query parameters or fragments.")
        host = parsed.hostname.lower().rstrip(".")
        local = host in _LOCAL_HOSTS or host.endswith((".local", ".internal", ".localhost"))
        try:
            ip = ipaddress.ip_address(host)
            local = local or ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            # Docker Compose service names without a public DNS suffix are local.
            local = local or "." not in host
        allow_hosted = os.getenv("OPENSHORTS_ALLOW_HOSTED", "false").lower() == "true"
        if not local and not allow_hosted:
            return "", False, "Remote/hosted OpenShorts is disabled to prevent unexpected usage charges. Use a self-hosted private URL."
        if parsed.scheme == "http" and not local:
            return "", False, "Remote OpenShorts connections must use HTTPS."
        return raw.rstrip("/"), local, None
    except ValueError as exc:
        return "", True, str(exc)


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    key = os.getenv("OPENSHORTS_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    gemini_key = os.getenv("OPENSHORTS_GEMINI_API_KEY", "").strip()
    if gemini_key:
        headers["X-Gemini-Key"] = gemini_key
    return headers


async def _request(method: str, path: str, payload: Optional[dict[str, Any]] = None) -> tuple[int, Any]:
    base, _, error = _service_config()
    if error or not base:
        raise HTTPException(status_code=503, detail=error or "OpenShorts is not configured.")
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=8.0), follow_redirects=False) as client:
            response = await client.request(
                method,
                base + path,
                headers=_headers(),
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"OpenShorts connection failed: {type(exc).__name__}") from exc
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text[:1000]}
    return response.status_code, data


def _raise_upstream(status_code: int, data: Any) -> None:
    if status_code >= 400:
        detail = data.get("detail", data) if isinstance(data, dict) else data
        # Preserve quota and concurrency signals so the UI can explain them.
        mapped = status_code if status_code in {400, 401, 402, 403, 404, 409, 422, 429} else 502
        raise HTTPException(status_code=mapped, detail=detail)


class OpenShortsGenerateRequest(BaseModel):
    url: HttpUrl
    acknowledged: bool = False
    target_clips: Optional[int] = Field(default=None, ge=1, le=15)
    clip_min_seconds: int = Field(default=15, ge=5, le=175)
    clip_max_seconds: int = Field(default=60, ge=10, le=180)
    output_format: str = "vertical"

    @model_validator(mode="after")
    def validate_request(self) -> "OpenShortsGenerateRequest":
        if self.url.scheme != "https":
            raise ValueError("OpenShorts accepts public HTTPS source URLs only.")
        if not self.acknowledged:
            raise ValueError("Confirm that you own or have permission to process this video.")
        if self.clip_max_seconds < self.clip_min_seconds + 5:
            raise ValueError("Maximum clip length must be at least 5 seconds longer than minimum.")
        if self.output_format not in {"auto", "vertical", "horizontal", "square"}:
            raise ValueError("Output format must be auto, vertical, horizontal or square.")
        return self


@router.get("/status")
async def openshorts_status():
    base, self_hosted, config_error = _service_config()
    if config_error:
        return {
            "engine": "OpenShorts",
            "configured": False,
            "reachable": False,
            "mode": "self-hosted",
            "message": config_error,
        }
    try:
        status_code, data = await _request("GET", "/openapi.json")
        _raise_upstream(status_code, data)
        info = data.get("info", {}) if isinstance(data, dict) else {}
        return {
            "engine": "OpenShorts",
            "configured": True,
            "reachable": True,
            "mode": "self-hosted" if self_hosted else "hosted",
            "service": info.get("title", "OpenShorts API"),
            "version": info.get("version"),
            "message": "Ready for video clipping. No social publishing is triggered by this integration.",
        }
    except HTTPException as exc:
        return {
            "engine": "OpenShorts",
            "configured": True,
            "reachable": False,
            "mode": "self-hosted" if self_hosted else "hosted",
            "message": str(exc.detail),
        }


@router.post("/generate")
async def generate_openshorts(req: OpenShortsGenerateRequest):
    base, _, config_error = _service_config()
    if config_error or not base:
        raise HTTPException(status_code=503, detail=config_error or "OpenShorts is not configured.")
    payload: dict[str, Any] = {
        "url": str(req.url),
        "acknowledged": True,
        "output_format": req.output_format,
        "clip_min_seconds": req.clip_min_seconds,
        "clip_max_seconds": req.clip_max_seconds,
        "layouts": ["auto"],
    }
    if req.target_clips is not None:
        payload["target_clips"] = req.target_clips
    status_code, data = await _request("POST", "/api/process", payload)
    _raise_upstream(status_code, data)
    if isinstance(data, dict) and data.get("needs_confirmation"):
        raise HTTPException(status_code=409, detail={
            "needs_confirmation": True,
            "quality_check": data.get("quality_check", {}),
            "message": "The source is below OpenShorts' quality threshold. No low-quality job was submitted.",
        })
    if not isinstance(data, dict) or not data.get("job_id"):
        raise HTTPException(status_code=502, detail="OpenShorts returned no job_id.")
    return {"engine": "OpenShorts", "job_id": str(data["job_id"]), "status": data.get("status", "queued")}


async def _get_job(job_id: str) -> dict[str, Any]:
    if not _JOB_ID_RE.fullmatch(job_id or ""):
        raise HTTPException(status_code=400, detail="Invalid job_id.")
    status_code, data = await _request("GET", f"/api/status/{job_id}")
    _raise_upstream(status_code, data)
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="OpenShorts returned an invalid job response.")
    return data


@router.get("/jobs/{job_id}")
async def openshorts_job(job_id: str):
    data = await _get_job(job_id)
    result = data.get("result")
    clips = result.get("clips", []) if isinstance(result, dict) else []
    safe_clips = []
    for index, clip in enumerate(clips if isinstance(clips, list) else []):
        if not isinstance(clip, dict):
            continue
        item = dict(clip)
        item["matangi_download_path"] = f"/api/openshorts/jobs/{job_id}/clips/{index}/download"
        safe_clips.append(item)
    return {
        "engine": "OpenShorts",
        "job_id": job_id,
        "status": data.get("status", "unknown"),
        "logs": data.get("logs", []),
        "clips": safe_clips,
        "error": data.get("error") or data.get("failure"),
    }


@router.get("/jobs/{job_id}/clips/{clip_index}/download")
async def openshorts_clip_download(job_id: str, clip_index: int):
    data = await _get_job(job_id)
    result = data.get("result")
    clips = result.get("clips", []) if isinstance(result, dict) else []
    if not isinstance(clips, list) or clip_index < 0 or clip_index >= len(clips):
        raise HTTPException(status_code=404, detail="Clip not found.")
    clip = clips[clip_index]
    if not isinstance(clip, dict):
        raise HTTPException(status_code=404, detail="Clip not found.")

    base, _, config_error = _service_config()
    if config_error or not base:
        raise HTTPException(status_code=503, detail=config_error or "OpenShorts is not configured.")
    raw_url = clip.get("video_url") or clip.get("download_url")
    if not isinstance(raw_url, str) or not raw_url:
        raise HTTPException(status_code=404, detail="OpenShorts did not provide a clip download URL.")
    target = urljoin(base + "/", raw_url)
    base_parts, target_parts = urlsplit(base), urlsplit(target)
    if (target_parts.scheme, target_parts.netloc) != (base_parts.scheme, base_parts.netloc):
        raise HTTPException(status_code=502, detail="OpenShorts returned a clip URL outside its configured service origin.")

    client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=8.0), follow_redirects=False)
    try:
        request = client.build_request("GET", target, headers=_headers())
        upstream = await client.send(request, stream=True)
    except httpx.HTTPError as exc:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"Clip download failed: {type(exc).__name__}") from exc
    if not upstream.is_success:
        status = upstream.status_code
        await upstream.aclose()
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"OpenShorts clip download returned HTTP {status}.")

    async def stream():
        try:
            async for chunk in upstream.aiter_bytes(256 * 1024):
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    filename = f"MATANGI-OpenShorts-{job_id}-{clip_index + 1}.mp4"
    return StreamingResponse(
        stream(),
        media_type=upstream.headers.get("content-type", "video/mp4"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
