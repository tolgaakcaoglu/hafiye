from __future__ import annotations

from pathlib import Path


def test_hafiye_onboarding_api_round_trip(monkeypatch, tmp_path: Path):
    from starlette.testclient import TestClient

    import hafiye_onboarding
    from hermes_cli import web_server

    state_root = tmp_path / "state"
    monkeypatch.setattr(hafiye_onboarding, "get_hafiye_state_home", lambda: state_root)
    monkeypatch.setenv("HAFIYE_ONBOARDING_FORCE", "1")

    client = TestClient(web_server.app)
    client.headers[web_server._SESSION_HEADER_NAME] = web_server._SESSION_TOKEN

    initial = client.get("/api/hafiye/onboarding")
    assert initial.status_code == 200
    assert initial.json()["required"] is True
    assert initial.json()["current_step"] == "welcome"

    updated = client.put(
        "/api/hafiye/onboarding",
        json={"current_step": "environment", "completed_steps": ["welcome"], "choices": {"compute_backend": "CUDA"}},
    )
    assert updated.status_code == 200
    assert updated.json()["current_step"] == "environment"
    assert updated.json()["choices"] == {"compute_backend": "CUDA"}

    completed = client.post("/api/hafiye/onboarding/complete")
    assert completed.status_code == 200
    assert completed.json()["completed"] is True
    assert len(completed.json()["completed_steps"]) == 20


def test_hafiye_onboarding_probe_endpoints_use_real_module_boundaries(monkeypatch):
    from starlette.testclient import TestClient

    import hafiye_onboarding
    from hermes_cli import web_server

    environment = {"platform": "Linux", "wayland": True, "compute": {"expected_auto_backend": "CUDA"}}
    autostart = {"available": True, "enabled": True, "active": True, "service": "hafiye-gateway.service"}
    monkeypatch.setattr(hafiye_onboarding, "environment_probe", lambda: environment)
    monkeypatch.setattr(hafiye_onboarding, "user_autostart_status", lambda: autostart)

    client = TestClient(web_server.app)
    client.headers[web_server._SESSION_HEADER_NAME] = web_server._SESSION_TOKEN

    assert client.get("/api/hafiye/onboarding/environment").json() == environment
    assert client.get("/api/hafiye/onboarding/autostart").json() == autostart
