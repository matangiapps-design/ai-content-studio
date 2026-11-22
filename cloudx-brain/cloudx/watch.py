"""Scheduled Guardian runner; reports findings as one maintained GitHub issue."""
import asyncio
import json
import os
import sys
import httpx
from cloudx.guardian import Guardian
from cloudx.repair_agent import RepairAgent

ALERT_TITLE = "CloudX Guardian: repository health findings"

async def main() -> int:
    repos = [x.strip() for x in os.getenv("CLOUDX_GITHUB_REPOS", "").split(",") if x.strip()]
    services = [x.strip() for x in os.getenv("CLOUDX_SERVICE_URLS", "").split(",") if x.strip()]
    read_token = os.getenv("CLOUDX_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN", "")
    write_token = os.getenv("GITHUB_TOKEN", "")
    report = await Guardian(read_token).scan(repos, services)
    report["repair_plans"] = RepairAgent().plan(report["findings"])
    print(json.dumps(report, indent=2))
    host = os.getenv("GITHUB_REPOSITORY", "")
    if not host or not write_token:
        print("Issue reporting skipped: missing host repository or GITHUB_TOKEN.")
        return 1 if report["findings"] else 0

    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {write_token}",
               "X-GitHub-Api-Version": "2022-11-28"}
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        # Optional, bounded recovery: retry a failed workflow once, never loop.
        if os.getenv("CLOUDX_ENABLE_SAFE_RERUN", "false").lower() == "true":
            rerun_headers = Guardian(read_token).headers()
            async with httpx.AsyncClient(timeout=20, headers=rerun_headers) as repair_client:
                for finding in report["findings"]:
                    if finding.get("kind") != "ci_failure" or finding.get("run_attempt") != "1" or not finding.get("run_id"):
                        continue
                    target = finding.get("target", "")
                    rerun = await repair_client.post(f"https://api.github.com/repos/{target}/actions/runs/{finding['run_id']}/rerun-failed-jobs")
                    finding["safe_rerun"] = "requested" if rerun.status_code == 201 else f"not_requested_http_{rerun.status_code}"
        base = f"https://api.github.com/repos/{host}/issues"
        response = await client.get(base, params={"state": "open", "per_page": 100})
        if not response.is_success:
            print(f"Cannot inspect alert issues: HTTP {response.status_code}")
            return 1
        existing = next((i for i in response.json() if i.get("title") == ALERT_TITLE and "pull_request" not in i), None)
        if report["findings"]:
            lines = ["## Guardian findings", f"- Checked: {report['checked_at']}", f"- Findings: {len(report['findings'])}", ""]
            for plan in report["repair_plans"]:
                lines += [f"### {plan['severity']}: {plan['target']}", plan["finding"], f"Proposed action: {plan['recommended_action']}", ""]
            lines += ["No source changes were made. Repairs require an isolated branch, tests, and human approval.", "", "Full machine-readable report:", "", "<pre>", json.dumps(report, indent=2), "</pre>"]
            payload = {"body": "\n".join(lines)}
            if existing:
                result = await client.patch(f"{base}/{existing['number']}", json=payload)
            else:
                result = await client.post(base, json={"title": ALERT_TITLE, **payload})
            if not result.is_success:
                print(f"Cannot publish alert: HTTP {result.status_code} {result.text[:250]}")
                return 1
        elif existing:
            result = await client.patch(f"{base}/{existing['number']}", json={
                "state": "closed", "state_reason": "completed",
                "body": existing.get("body", "") + "\n\nGuardian recovery scan: no current findings."
            })
            if not result.is_success:
                print(f"Cannot close recovered alert: HTTP {result.status_code}")
                return 1
    return 1 if report["findings"] else 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
