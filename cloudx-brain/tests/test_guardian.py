from cloudx.guardian import Guardian
from cloudx.repair_agent import RepairAgent
from cloudx.memory import EventMemory

def test_guardian_is_read_only():
    guardian = Guardian()
    assert "Authorization" not in guardian.headers()
    assert "Accept" in guardian.headers()

def test_higgsfield_not_enabled_without_verified_config():
    from cloudx.providers import HiggsfieldProvider
    assert HiggsfieldProvider().status()["generation_enabled"] is False

def test_repair_agent_proposes_but_never_applies():
    plan = RepairAgent().plan([{"kind": "ci_failure", "target": "org/repo", "detail": "failed"}])[0]
    assert plan["requires_human_approval"] is True
    assert plan["auto_fix_applied"] is False
    assert "pull request" in plan["recommended_action"]

def test_event_memory_persists(tmp_path):
    store = EventMemory(str(tmp_path / "events.db"))
    store.record("2026-11-23T00:00:00Z", "test", {"ok": True})
    assert store.recent()[0]["payload"] == {"ok": True}
