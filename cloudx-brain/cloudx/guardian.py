from datetime import datetime, timezone
from typing import Any
import httpx

class Guardian:
    """Read-only observer for repositories, CI and configured service endpoints."""
    def __init__(self, token: str = "", timeout: float = 12.0):
        self.token, self.timeout = token, timeout

    def headers(self) -> dict[str, str]:
        h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def scan(self, repositories: list[str], service_urls: list[str]) -> dict[str, Any]:
        findings, repo_results = [], []
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers()) as client:
            for name in repositories:
                item = {"repository": name, "status": "unknown"}
                try:
                    response = await client.get(f"https://api.github.com/repos/{name}")
                    if not response.is_success:
                        item["status"] = "error"
                        findings.append({"severity": "warning", "kind": "repository", "target": name, "detail": f"GitHub HTTP {response.status_code}"})
                    else:
                        data = response.json()
                        item.update(status="reachable", default_branch=data.get("default_branch", ""), archived=data.get("archived", False))
                        runs_response = await client.get(f"https://api.github.com/repos/{name}/actions/runs?per_page=10")
                        if runs_response.is_success:
                            runs = runs_response.json().get("workflow_runs", [])
                            latest = next((r for r in runs if r.get("status") == "completed"), None)
                            if latest:
                                item["latest_workflow"] = {"name": latest.get("name"), "conclusion": latest.get("conclusion"), "url": latest.get("html_url"), "run_id": latest.get("id"), "run_attempt": latest.get("run_attempt", 1)}
                                if latest.get("conclusion") not in ("success", "neutral", "skipped"):
                                    findings.append({"severity": "warning", "kind": "ci_failure", "target": name, "detail": f"Latest completed workflow: {latest.get('conclusion')}", "url": latest.get("html_url", ""), "run_id": str(latest.get("id", "")), "run_attempt": str(latest.get("run_attempt", 1))})
                        elif runs_response.status_code not in (403, 404):
                            findings.append({"severity": "info", "kind": "ci_visibility", "target": name, "detail": f"Workflow status unavailable: HTTP {runs_response.status_code}"})
                except httpx.HTTPError as exc:
                    item["status"] = "error"
                    findings.append({"severity": "warning", "kind": "repository", "target": name, "detail": type(exc).__name__})
                repo_results.append(item)
            for url in service_urls:
                try:
                    response = await client.get(url)
                    if not response.is_success:
                        findings.append({"severity": "warning", "kind": "service", "target": url, "detail": f"HTTP {response.status_code}"})
                except httpx.HTTPError as exc:
                    findings.append({"severity": "critical", "kind": "service", "target": url, "detail": type(exc).__name__})
        return {"checked_at": datetime.now(timezone.utc).isoformat(), "repositories": repo_results,
                "findings": findings, "repair_mode": "diagnose_and_propose_only", "automatic_source_changes": False}
