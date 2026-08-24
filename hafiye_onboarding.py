"""First-run Hafiye Desktop onboarding state and host probes.

The GUI wizard is deliberately a thin client of this module and of the
existing runtime managers.  This file owns only non-secret setup state and
read-only/explicit user-session probes; it does not become a second config
store for routing, providers, or runtime lifecycle.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hermes_constants import get_hafiye_state_home


ONBOARDING_SCHEMA = 1
ONBOARDING_STATE_FILENAME = "onboarding.json"
ONBOARDING_STEPS = (
    "welcome",
    "environment",
    "computer",
    "compute",
    "llama-runtime",
    "local-model",
    "local-server",
    "remote-provider",
    "gemini",
    "routing",
    "microphone",
    "whisper",
    "stt",
    "piper",
    "tts",
    "wake-word",
    "test-hafiye",
    "execution-policy",
    "autostart",
    "doctor",
)
_CHOICE_KEYS = {
    "compute_backend",
    "model_id",
    "piper_voice",
    "execution_policy",
    "wake_word_enabled",
    "remote_provider_skipped",
    "gemini_skipped",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def state_path() -> Path:
    return get_hafiye_state_home() / ONBOARDING_STATE_FILENAME


def _default_state() -> dict[str, Any]:
    return {
        "schema": ONBOARDING_SCHEMA,
        "completed": False,
        "current_step": ONBOARDING_STEPS[0],
        "completed_steps": [],
        "choices": {},
        "updated_at": _now(),
    }


def _read_state() -> dict[str, Any]:
    path = state_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _default_state()
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read Hafiye onboarding state: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Hafiye onboarding state must be a JSON object")
    return _normalise_state(payload)


def _normalise_state(payload: dict[str, Any]) -> dict[str, Any]:
    result = _default_state()
    result["schema"] = payload.get("schema", ONBOARDING_SCHEMA)
    result["completed"] = payload.get("completed") is True
    current = str(payload.get("current_step") or ONBOARDING_STEPS[0])
    result["current_step"] = current if current in ONBOARDING_STEPS else ONBOARDING_STEPS[0]
    completed_steps = payload.get("completed_steps")
    if isinstance(completed_steps, list):
        result["completed_steps"] = [
            step for step in dict.fromkeys(str(item) for item in completed_steps) if step in ONBOARDING_STEPS
        ]
    choices = payload.get("choices")
    if isinstance(choices, dict):
        result["choices"] = {
            key: value
            for key, value in choices.items()
            if key in _CHOICE_KEYS and isinstance(value, (bool, int, float, str))
        }
    result["updated_at"] = str(payload.get("updated_at") or _now())
    return result


def _write_state(payload: dict[str, Any]) -> dict[str, Any]:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            fd = -1
            json.dump(_normalise_state(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            Path(temporary).unlink(missing_ok=True)
        except OSError:
            pass
    return _normalise_state(payload)


def is_packaged_install() -> bool:
    """Return whether the active backend belongs to the Debian package.

    The launcher exports ``HAFIYE_PACKAGE_ROOT``.  The conventional path is a
    fallback for the packaged systemd unit, whose environment is intentionally
    small and does not inherit a shell environment.
    """

    explicit_root = os.environ.get("HAFIYE_PACKAGE_ROOT", "").strip()
    if explicit_root:
        return (Path(explicit_root) / "backend").is_dir() or (Path(explicit_root) / "desktop").is_dir()
    return Path("/usr/lib/hafiye/backend").is_dir() and Path("/usr/lib/hafiye/desktop").is_dir()


def onboarding_state() -> dict[str, Any]:
    state = _read_state()
    forced = os.environ.get("HAFIYE_ONBOARDING_FORCE", "").strip().lower() in {"1", "true", "yes", "on"}
    state.update(
        {
            "required": bool(forced or is_packaged_install()),
            "state_path": str(state_path()),
            "package_root": os.environ.get("HAFIYE_PACKAGE_ROOT", "") or "/usr/lib/hafiye",
            "steps": list(ONBOARDING_STEPS),
        }
    )
    return state


def update_onboarding_state(
    *,
    current_step: str | None = None,
    completed_steps: list[str] | None = None,
    choices: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = _read_state()
    if current_step is not None:
        current_step = str(current_step).strip()
        if current_step not in ONBOARDING_STEPS:
            raise ValueError(f"Unknown onboarding step: {current_step}")
        current["current_step"] = current_step
    if completed_steps is not None:
        current["completed_steps"] = completed_steps
    if choices is not None:
        current["choices"] = choices
    current["updated_at"] = _now()
    _write_state(current)
    return onboarding_state()


def complete_onboarding() -> dict[str, Any]:
    current = _read_state()
    current["completed"] = True
    current["completed_steps"] = list(ONBOARDING_STEPS)
    current["current_step"] = ONBOARDING_STEPS[-1]
    current["updated_at"] = _now()
    _write_state(current)
    return onboarding_state()


def _capture(command: list[str], timeout: float = 4.0) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return 127, ""
    return result.returncode, (result.stdout or result.stderr or "").strip()


def _version(command: list[str]) -> str:
    _, output = _capture(command)
    return output.splitlines()[0][:200] if output else ""


def _cpu_model() -> str:
    _, output = _capture(["lscpu"])
    for line in output.splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip().lower() in {"model name", "model"} and value.strip():
            return value.strip()[:200]
    return platform.processor()[:200]


def environment_probe() -> dict[str, Any]:
    """Collect the non-secret Linux facts the first-run wizard must show."""

    from hermes_cli.local_runtime import detect_compute_environment

    session_type = os.environ.get("XDG_SESSION_TYPE", "")
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
    gnome_version = _version(["gnome-shell", "--version"])
    memory: dict[str, Any] = {}
    try:
        import psutil

        vm = psutil.virtual_memory()
        memory = {"total": vm.total, "available": vm.available, "percent": vm.percent}
    except Exception:
        pass
    audio = {
        "wpctl": shutil.which("wpctl") or "",
        "pactl": shutil.which("pactl") or "",
        "pipewire": shutil.which("pipewire") or "",
        "wireplumber": shutil.which("wireplumber") or "",
    }
    return {
        "platform": platform.system(),
        "os_release": platform.release(),
        "kernel": platform.uname().release,
        "architecture": platform.machine(),
        "desktop": current_desktop,
        "gnome_version": gnome_version,
        "session_type": session_type,
        "wayland": session_type.lower() == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY")),
        "x11": bool(os.environ.get("DISPLAY")),
        "cpu": _cpu_model(),
        "cpu_count": os.cpu_count(),
        "memory": memory,
        "python": platform.python_version(),
        "node": _version(["node", "--version"]),
        "cmake": _version(["cmake", "--version"]),
        "cargo": _version(["cargo", "--version"]),
        "audio": audio,
        "compute": detect_compute_environment(),
    }


def user_autostart_status(service: str = "hafiye-gateway.service") -> dict[str, Any]:
    systemctl = shutil.which("systemctl")
    if not systemctl:
        return {"available": False, "enabled": False, "active": False, "service": service, "message": "systemctl not found"}
    enabled_code, enabled_text = _capture([systemctl, "--user", "is-enabled", service])
    active_code, active_text = _capture([systemctl, "--user", "is-active", service])
    return {
        "available": True,
        "enabled": enabled_code == 0,
        "active": active_code == 0,
        "service": service,
        "enabled_state": enabled_text[:200],
        "active_state": active_text[:200],
        "message": "" if enabled_code == 0 else (enabled_text or active_text or "user service is not enabled"),
    }


def enable_user_autostart(service: str = "hafiye-gateway.service") -> dict[str, Any]:
    systemctl = shutil.which("systemctl")
    if not systemctl:
        raise RuntimeError("systemctl is not installed")
    reload_code, reload_text = _capture([systemctl, "--user", "daemon-reload"], timeout=15)
    if reload_code != 0:
        raise RuntimeError(reload_text or "systemd user daemon-reload failed")
    enable_code, enable_text = _capture([systemctl, "--user", "enable", "--now", service], timeout=30)
    if enable_code != 0:
        raise RuntimeError(enable_text or "could not enable the Hafiye user service")
    return user_autostart_status(service)


__all__ = [
    "ONBOARDING_STEPS",
    "complete_onboarding",
    "enable_user_autostart",
    "environment_probe",
    "is_packaged_install",
    "onboarding_state",
    "state_path",
    "update_onboarding_state",
    "user_autostart_status",
]
