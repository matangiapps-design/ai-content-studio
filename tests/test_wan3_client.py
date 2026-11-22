import pytest

from services.wan3_client import Wan3Client


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_submit_uses_documented_wavespeed_wan3_route(monkeypatch):
    client = Wan3Client(api_key="test-key")
    captured = {}

    def fake_post(url, json, timeout):
        captured.update(url=url, payload=json, timeout=timeout)
        return FakeResponse({"data": {"id": "prediction-123"}})

    monkeypatch.setattr(client.session, "post", fake_post)
    task_id = client.submit(
        "A cinematic test scene",
        duration=8,
        aspect_ratio="9:16",
        resolution="720p",
    )

    assert task_id == "prediction-123"
    assert captured["url"] == "https://api.wavespeed.ai/api/v3/alibaba/wan-3.0/text-to-video"
    assert captured["payload"]["duration"] == 8
    assert captured["payload"]["aspect_ratio"] == "9:16"
    assert captured["payload"]["resolution"] == "720p"


@pytest.mark.parametrize("duration", [1, 31])
def test_submit_rejects_duration_outside_provider_limits(duration):
    client = Wan3Client(api_key="test-key")
    with pytest.raises(ValueError, match="between 2 and 30"):
        client.submit("test", duration=duration)


def test_submit_rejects_unsupported_resolution():
    client = Wan3Client(api_key="test-key")
    with pytest.raises(ValueError, match="resolution"):
        client.submit("test", resolution="4k")


def test_list_models_uses_authenticated_server_side_catalogue(monkeypatch):
    client = Wan3Client(api_key="test-key")
    captured = {}

    def fake_get(url, timeout):
        captured.update(url=url, timeout=timeout)
        return FakeResponse({"data": [
            {"id": "alibaba/wan-3.0/text-to-video", "name": "Wan 3.0", "task": "text-to-video"},
            {"model_id": "vendor/wan-3.6/text-to-video", "name": "Wan 3.6"},
            {"name": "invalid-without-id"},
            "vendor/another-model",
        ]})

    monkeypatch.setattr(client.session, "get", fake_get)
    models = client.list_models()

    assert captured["url"] == "https://api.wavespeed.ai/api/v3/models"
    assert [model["id"] for model in models] == [
        "alibaba/wan-3.0/text-to-video",
        "vendor/wan-3.6/text-to-video",
        "vendor/another-model",
    ]
    assert models[1]["name"] == "Wan 3.6"


def test_list_models_rejects_unexpected_response_shape(monkeypatch):
    client = Wan3Client(api_key="test-key")
    monkeypatch.setattr(client.session, "get", lambda url, timeout: FakeResponse({"data": "unexpected"}))
    with pytest.raises(RuntimeError, match="unexpected response shape"):
        client.list_models()
