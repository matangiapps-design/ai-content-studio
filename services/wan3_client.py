"""WaveSpeedAI Wan 3.0 client for ODIA HERO.

Requires WAVESPEED_API_KEY in the server environment. Never expose it to the browser.
"""
from __future__ import annotations
import os, time, requests

BASE = "https://api.wavespeed.ai/api/v3"
MODEL = "alibaba/wan-3.0/text-to-video"
IMAGE_MODEL = "alibaba/wan-3.0/image-to-video"
TERMINAL_FAILURES = {"failed", "cancelled", "timeout", "deleted"}


class Wan3Client:
    def __init__(self, api_key: str | None = None, timeout_seconds: int = 1800):
        self.api_key = api_key or os.getenv("WAVESPEED_API_KEY")
        if not self.api_key:
            raise RuntimeError("WAVESPEED_API_KEY is missing. Add it to the server .env; never paste it into chat or commit it.")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})

    def list_models(self) -> list[dict]:
        """Return the models visible to this API key; never guess model IDs.

        WaveSpeed's account-scoped catalogue is queried server-side. The raw
        response is normalized to model IDs and safe display metadata only.
        """
        response = self.session.get(f"{BASE}/models", timeout=30)
        response.raise_for_status()
        body = response.json()
        data = body.get("data", body) if isinstance(body, dict) else body
        if isinstance(data, dict):
            data = data.get("models", data.get("items", []))
        if not isinstance(data, list):
            raise RuntimeError("WaveSpeed model catalogue returned an unexpected response shape.")
        models = []
        for item in data:
            if isinstance(item, str):
                model_id, name, task = item, item, None
            elif isinstance(item, dict):
                model_id = item.get("model_id") or item.get("id") or item.get("name")
                name = item.get("name") or model_id
                task = item.get("task") or item.get("type")
            else:
                continue
            if isinstance(model_id, str) and model_id.strip():
                models.append({"id": model_id.strip(), "name": str(name or model_id), "task": task})
        return models

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

    def submit_image_to_video(self, image_path: str, prompt: str, duration: int = 5,
                             aspect_ratio: str = "9:16", resolution: str = "720p",
                             generate_audio: bool = False, seed: int | None = None) -> str:
        """Submit a local image as a base64 first frame to Wan 3.0 Image-to-Video."""
        import base64
        from pathlib import Path
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Reference image not found: {path}")
        suffix = path.suffix.lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(suffix)
        if not mime:
            raise ValueError("Reference image must be JPG or PNG.")
        if not 2 <= int(duration) <= 30:
            raise ValueError("Wan 3.0 image-to-video duration must be between 2 and 30 seconds.")
        if aspect_ratio not in {"16:9", "9:16", "1:1", "4:3", "3:4"}:
            raise ValueError("Unsupported aspect ratio.")
        if resolution not in {"480p", "720p", "1080p"}:
            raise ValueError("Resolution must be 480p, 720p or 1080p.")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        payload = {
            "image": f"data:{mime};base64,{encoded}", "prompt": prompt,
            "duration": int(duration), "aspect_ratio": aspect_ratio,
            "resolution": resolution, "generate_audio": bool(generate_audio),
            "enable_prompt_expansion": False,
        }
        if seed is not None:
            payload["seed"] = int(seed)
        response = self.session.post(f"{BASE}/{IMAGE_MODEL}", json=payload, timeout=120)
        response.raise_for_status()
        body = response.json()
        task = body.get("data", body)
        task_id = task.get("id")
        if not task_id:
            raise RuntimeError(f"Wan image-to-video submission did not return a prediction id: {body}")
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
