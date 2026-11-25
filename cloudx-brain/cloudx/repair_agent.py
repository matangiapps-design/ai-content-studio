from typing import Any

class RepairAgent:
    """Create evidence-based repair plans; all source changes require human approval."""
    def plan(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        actions = {
            "ci_failure": "Inspect the failed workflow and first failing job; reproduce on an isolated branch, add a regression test, then open a pull request.",
            "service": "Inspect service logs, deployment health, configuration and dependencies; restore only through the approved deployment process.",
            "repository": "Verify repository name, access permissions, token scope and GitHub availability.",
        }
        return [{
            "target": f.get("target", "unknown"), "severity": f.get("severity", "info"),
            "finding": f.get("detail", ""),
            "recommended_action": actions.get(f.get("kind"), "Collect logs and classify the failure before proposing a change."),
            "requires_human_approval": True, "auto_fix_applied": False,
        } for f in findings]
