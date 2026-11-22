from datetime import datetime, timezone
from typing import Any
import httpx

class Guardian:
    """Read-only observer; never changes repositories or production services."""
    def __init__(self, token: str = "", timeout: float = 12.0):
        self.token = token
        self.timeout = timeout

    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def scan(self, repositories: list[str], service_urls: list[str]) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        repo_results: list[dict[str, str]] = []
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers()) as client:
            for name in repositories:
                try:
                    response = await client.get(f"https://api.github.com/repos/{name}")
                    if response.is_success:
                        repo = response.json()
                        repo_results.append({"repository": name, "status": "reachable", "default_branch": repo.get("default_branch", "")})
                    else:
                        repo_results.append({"repository": name, "status": "error"})
                        findings.append({"severity": "warning", "kind": "repository", "target": name, "detail": f"GitHub HTTP {response.status_code}"})
                except httpx.HTTPError as exc:
                    repo_results.append({"repository": name, "status": "error"})
                    findings.append({"severity": "warning", "kind": "repository", "target": name, "detail": type(exc).__name__})
            for url in service_urls:
                try:
                    response = await client.get(url)
                    if not response.is_success:
                        findings.append({"severity": "warning", "kind": "service", "target": url, "detail": f"HTTP {response.status_code}"})
                except httpx.HTTPError as exc:
                    findings.append({"severity": "critical", "kind": "service", "target": url, "detail": type(exc).__name__})
        return {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "repositories": repo_results,
            "findings": findings,
            "repair_mode": "proposal_only",
        }
