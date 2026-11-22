from cloudx.guardian import Guardian

def test_guardian_is_read_only():
    guardian = Guardian()
    assert "Authorization" not in guardian.headers()
    assert "Accept" in guardian.headers()

def test_higgsfield_not_enabled_without_verified_config():
    from cloudx.providers import HiggsfieldProvider
    assert HiggsfieldProvider().status()["generation_enabled"] is False
