"""WaveSpeedAI Wan 3.0 client for ODIA HERO.

Requires WAVESPEED_API_KEY in the server environment. Never expose it to the browser.
"""
from __future__ import annotations
import os, time, requests

BASE = "https://api.wavespeed.ai/api/v3"
MODEL = "alibaba/wan-3.0/text-to-video"
TERMINAL_FAILURES = {"failed", "cancelled", "timeout", "deleted"}

class Wan3Client:
    def __init__(self, api_key: str | None = None, timeout_seconds: int = 1800):
        self.api_key = api_key or os.getenv("WAVESPEED_API_KEY")
        if not self.api_key:
            raise RuntimeError("WAVESPEED_API_KEY is missing. Add it to the server .env; never paste it into chat or commit it.")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})

    def submit(self, prompt: str, duration: int = 20, aspect_ratio: str = "16:9",
               resolution: str = "720p", enable_audio: bool = False,
               enable_prompt_expansion: bool = False, seed: int | None = None) -> str:
        if not 2 <= int(duration) <= 30:
            raise ValueError("Wan 3.0 duration must be between 2 and 30 seconds per generation.")
        if aspect_ratio not in {"16:9", "9:16", "1:1", "4:3", "3:4"}:
            raise ValueError("Unsupported aspect ratio.")
        if resolution not in {"480p", "720p", "1080p"}:
            raise ValueError("Wan 3.0 resolution must be 480p, 720p or 1080p.")
        payload = {
            "prompt": prompt, "duration": int(duration), "aspect_ratio": aspect_ratio,
            "resolution": resolution, "enable_audio": bool(enable_audio),
            "enable_prompt_expansion": bool(enable_prompt_expansion)
        }
        if seed is not None:
            payload["seed"] = int(seed)
        response = self.session.post(f"{BASE}/{MODEL}", json=payload, timeout=120)
        response.raise_for_status()
        body = response.json()
        task = body.get("data", body)
        task_id = task.get("id")
        if not task_id:
            raise RuntimeError(f"Wan submission did not return a prediction id: {body}")
        return str(task_id)

    def wait(self, task_id: str, poll_seconds: int = 3) -> str:
        deadline = time.monotonic() + self.timeout_seconds
        url = f"{BASE}/predictions/{task_id}/result"
        while time.monotonic() < deadline:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            body = response.json()
            result = body.get("data", body)
            status = result.get("status")
            if status == "completed":
                outputs = result.get("outputs") or []
                if not outputs:
                    raise RuntimeError(f"Wan task {task_id} completed without outputs.")
                return outputs[0] if isinstance(outputs[0], str) else outputs[0]["url"]
            if status in TERMINAL_FAILURES:
                raise RuntimeError(f"Wan task {task_id} ended with status={status}: {result}")
            time.sleep(poll_seconds)
        raise TimeoutError(f"Wan task {task_id} did not finish within {self.timeout_seconds}s.")

    def download(self, url: str, destination: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        with requests.get(url, stream=True, timeout=180) as response:
            response.raise_for_status()
            with open(destination, "wb") as handle:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        return destination
