from __future__ import annotations

import json
from pathlib import Path

import hafiye_onboarding


def _use_state_root(monkeypatch, tmp_path: Path) -> Path:
    state_root = tmp_path / "state" / "hafiye"
    monkeypatch.setattr(hafiye_onboarding, "get_hafiye_state_home", lambda: state_root)
    monkeypatch.delenv("HAFIYE_PACKAGE_ROOT", raising=False)
    monkeypatch.delenv("HAFIYE_ONBOARDING_FORCE", raising=False)
    return state_root


def test_default_state_is_complete_shape_and_private(tmp_path, monkeypatch):
    state_root = _use_state_root(monkeypatch, tmp_path)

    state = hafiye_onboarding.onboarding_state()

    assert state["required"] is False
    assert state["completed"] is False
    assert state["current_step"] == "welcome"
    assert len(state["steps"]) == 20
    assert state["completed_steps"] == []
    assert state["state_path"] == str(state_root / "onboarding.json")
    assert not (state_root / "onboarding.json").exists()


def test_state_updates_filter_choices_and_completion_is_atomic(tmp_path, monkeypatch):
    state_root = _use_state_root(monkeypatch, tmp_path)

    updated = hafiye_onboarding.update_onboarding_state(
        current_step="environment",
        completed_steps=["welcome", "welcome", "not-a-step"],
        choices={"compute_backend": "CUDA", "unknown_secret": "discard", "wake_word_enabled": True},
    )

    assert updated["current_step"] == "environment"
    assert updated["completed_steps"] == ["welcome"]
    assert updated["choices"] == {"compute_backend": "CUDA", "wake_word_enabled": True}

    path = state_root / "onboarding.json"
    assert json.loads(path.read_text(encoding="utf-8"))["current_step"] == "environment"
    assert path.stat().st_mode & 0o777 == 0o600

    completed = hafiye_onboarding.complete_onboarding()

    assert completed["completed"] is True
    assert completed["completed_steps"] == list(hafiye_onboarding.ONBOARDING_STEPS)
    assert completed["current_step"] == "doctor"


def test_unknown_step_is_rejected(tmp_path, monkeypatch):
    _use_state_root(monkeypatch, tmp_path)

    try:
        hafiye_onboarding.update_onboarding_state(current_step="nope")
    except ValueError as exc:
        assert "Unknown onboarding step" in str(exc)
    else:
        raise AssertionError("unknown onboarding steps must be rejected")


def test_packaged_detection_supports_launcher_root_and_force(tmp_path, monkeypatch):
    _use_state_root(monkeypatch, tmp_path)
    package_root = tmp_path / "package"
    (package_root / "backend").mkdir(parents=True)

    monkeypatch.setenv("HAFIYE_PACKAGE_ROOT", str(package_root))
    assert hafiye_onboarding.is_packaged_install() is True
    assert hafiye_onboarding.onboarding_state()["required"] is True

    (package_root / "backend").rmdir()
    monkeypatch.delenv("HAFIYE_PACKAGE_ROOT")
    monkeypatch.setenv("HAFIYE_ONBOARDING_FORCE", "1")
    assert hafiye_onboarding.is_packaged_install() is False
    assert hafiye_onboarding.onboarding_state()["required"] is True


def test_autostart_status_uses_user_systemd(monkeypatch):
    calls: list[list[str]] = []

    monkeypatch.setattr(hafiye_onboarding.shutil, "which", lambda name: "/usr/bin/systemctl")

    def capture(command, timeout=4.0):
        del timeout
        calls.append(command)
        if command[-2:] == ["is-enabled", "hafiye-gateway.service"]:
            return 0, "enabled"
        if command[-2:] == ["is-active", "hafiye-gateway.service"]:
            return 0, "active"
        return 0, ""

    monkeypatch.setattr(hafiye_onboarding, "_capture", capture)

    status = hafiye_onboarding.user_autostart_status()

    assert status["enabled"] is True
    assert status["active"] is True
    assert calls == [
        ["/usr/bin/systemctl", "--user", "is-enabled", "hafiye-gateway.service"],
        ["/usr/bin/systemctl", "--user", "is-active", "hafiye-gateway.service"],
    ]


def test_environment_probe_exposes_compute_and_host_fields(monkeypatch):
    monkeypatch.setattr(
        hafiye_onboarding,
        "_version",
        lambda command: {"gnome-shell": "GNOME Shell 46", "node": "v22", "cmake": "cmake 3", "cargo": "cargo 1"}[command[0]],
    )
    monkeypatch.setattr(hafiye_onboarding.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setattr(
        "hermes_cli.local_runtime.detect_compute_environment",
        lambda: {"nvidia_present": True, "cuda_available": True, "selected_backend": "CUDA"},
    )

    probe = hafiye_onboarding.environment_probe()

    assert probe["platform"]
    assert probe["session_type"] == "wayland"
    assert probe["wayland"] is True
    assert probe["compute"]["selected_backend"] == "CUDA"
    assert probe["audio"]["wpctl"] == "/usr/bin/wpctl"
