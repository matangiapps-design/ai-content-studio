import re
import uuid
import httpx

class HiggsfieldProvider:
    """Server-side Higgsfield REST client following the official API request lifecycle."""
    BASE_URL = "https://api.higgsfield.ai"

    def __init__(self, key_id: str = "", key_secret: str = "", timeout: float = 45.0):
        self.key_id, self.key_secret, self.timeout = key_id, key_secret, timeout

    @property
    def configured(self) -> bool:
        return bool(self.key_id and self.key_secret)

    def headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        if not self.configured:
            raise RuntimeError("Higgsfield API credentials are not configured.")
        headers = {"Authorization": f"Key {self.key_id}:{self.key_secret}", "Content-Type": "application/json"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    @staticmethod
    def validate_model_path(model_path: str) -> str:
        path = model_path.strip().strip("/")
        if not path or len(path) > 180 or not re.fullmatch(r"[A-Za-z0-9._/-]+", path) or ".." in path.split("/"):
            raise ValueError("Provide a valid documented Higgsfield model endpoint path.")
        return path

    async def submit(self, model_path: str, payload: dict, idempotency_key: str | None = None) -> dict:
        path = self.validate_model_path(model_path)
        key = idempotency_key or str(uuid.uuid4())
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.BASE_URL}/{path}", headers=self.headers(key), json=payload)
            response.raise_for_status()
            return response.json()

    async def status(self, request_id: str) -> dict:
        if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", request_id):
            raise ValueError("Invalid Higgsfield request ID.")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.BASE_URL}/requests/{request_id}/status", headers=self.headers())
            response.raise_for_status()
            return response.json()

    def info(self) -> dict[str, object]:
        return {
            "provider": "higgsfield",
            "configured": self.configured,
            "generation_enabled": self.configured,
            "api_base": self.BASE_URL,
            "model_catalog": "Use model-specific documentation; CloudX does not guess model endpoints or schemas.",
        }
