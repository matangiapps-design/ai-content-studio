from dataclasses import dataclass

@dataclass
class HiggsfieldProvider:
    """Higgsfield adapter boundary; no undocumented endpoints are assumed."""
    api_key: str = ""
    base_url: str = ""

    def status(self) -> dict[str, object]:
        return {
            "provider": "higgsfield",
            "configured": bool(self.api_key and self.base_url),
            "generation_enabled": False,
            "note": "Verify the current account API schema and authentication before enabling generation.",
        }
