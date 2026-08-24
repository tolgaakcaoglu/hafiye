"""Managed computer-use-linux integration for Hafiye.

The Linux desktop controller is an upstream MCP server, not a second
computer-control implementation inside Hermes.  This module owns the small
amount of Hafiye policy around it: the pinned source identity, binary
resolution, the real-session environment passed to the stdio child, doctor
normalisation, and the built-in MCP entry that is merged at runtime.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from hermes_constants import get_hafiye_cache_home


COMPUTER_USE_LINUX_SOURCE_COMMIT = "94736dc3e0dca56acfc89752c26869fb9ed01202"
COMPUTER_USE_LINUX_MCP_SERVER = "hafiye-computer-use-linux"
COMPUTER_USE_LINUX_MCP_ARGS = ("mcp",)
_REQUIRED_READINESS = (
    "can_register_mcp_tools",
    "can_build_accessibility_tree",
    "can_send_development_input",
    "can_query_windows",
)
_DESKTOP_ENV_KEYS = (
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "XAUTHORITY",
    "DBUS_SESSION_BUS_ADDRESS",
    "XDG_CURRENT_DESKTOP",
    "XDG_SESSION_TYPE",
    "XDG_RUNTIME_DIR",
)


def source_checkout() -> Path:
    """Return the managed pinned source checkout location."""
    return get_hafiye_cache_home() / "computer-use-linux"


def _binary_candidates() -> Iterable[Path]:
    checkout = source_checkout()
    yield Path.home() / ".local" / "bin" / "computer-use-linux"
    yield checkout / "target" / "release" / "computer-use-linux"
    yield checkout / "target" / "debug" / "computer-use-linux"


def resolve_computer_use_linux_binary() -> Optional[str]:
    """Resolve the exact computer-use-linux executable, if installed."""
    for candidate in _binary_candidates():
        try:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate.resolve())
        except OSError:
            continue

    path_hit = shutil.which("computer-use-linux")
    return str(Path(path_hit).resolve()) if path_hit else None


def _desktop_env() -> Dict[str, str]:
    """Pass only non-secret session routing variables to the MCP child."""
    return {
        key: value
        for key in _DESKTOP_ENV_KEYS
        if (value := os.environ.get(key))
    }


def _run(binary: str, *args: str, timeout: float) -> subprocess.CompletedProcess[str]:
    try:
        from tools.environments.local import _sanitize_subprocess_env

        env = _sanitize_subprocess_env(os.environ)
    except Exception:
        env = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "HOME", "USER", "LANG", "LC_ALL", "TERM", "SHELL"}
            or key.startswith("XDG_")
        }
    env.update(_desktop_env())
    return subprocess.run(
        [binary, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        stdin=subprocess.DEVNULL,
        timeout=timeout,
    )


def _error_text(result: subprocess.CompletedProcess[str]) -> str:
    text = (result.stderr or result.stdout or "").strip()
    return text.splitlines()[-1][:400] if text else "computer-use-linux returned no diagnostic"


def classify_computer_use_failure(value: Any) -> Dict[str, Any]:
    """Turn a managed desktop-action failure into a stable recovery contract.

    The upstream MCP server owns the actual AT-SPI/Wayland implementation.  A
    Hafiye caller still needs to distinguish a missing readiness prerequisite
    from a stale window target or a transient action timeout, without exposing
    raw child-process diagnostics or credentials to the model/logs.
    """
    payload = value
    if isinstance(value, str):
        try:
            payload = json.loads(value)
        except (TypeError, ValueError):
            payload = value
    if isinstance(payload, dict):
        parts = [payload.get("error"), payload.get("message"), payload.get("detail")]
        text = " ".join(str(part) for part in parts if part).strip()
    else:
        text = str(payload or "").strip()
    try:
        from agent.redact import redact_sensitive_text

        text = redact_sensitive_text(text, force=True)
    except Exception:
        pass
    lowered = text.lower()

    if any(
        token in lowered
        for token in (
            "at-spi",
            "accessibility tree",
            "accessibility",
            "can_build_accessibility_tree",
        )
    ):
        code, retryable, blocker = "accessibility_unavailable", False, True
    elif any(
        token in lowered
        for token in ("uinput", "ydotool", "development input", "can_send_development_input")
    ):
        code, retryable, blocker = "input_backend_unavailable", False, True
    elif any(token in lowered for token in ("readiness", "doctor", "not registered", "blocker")):
        code, retryable, blocker = "computer_use_not_ready", False, True
    elif any(token in lowered for token in ("window", "focused", "target")):
        code, retryable, blocker = "window_target_unavailable", True, False
    elif any(token in lowered for token in ("timeout", "timed out", "deadline")):
        code, retryable, blocker = "desktop_action_timeout", True, False
    else:
        code, retryable, blocker = "desktop_action_failed", True, False

    return {
        "ok": False,
        "code": code,
        "retryable": retryable,
        "blocker": blocker,
        "detail": text[-400:] if text else "computer-use-linux action failed",
    }


def _normalise_doctor_report(report: Any) -> Dict[str, Any]:
    """Keep the upstream report intact while exposing stable Hafiye fields."""
    report = report if isinstance(report, dict) else {}
    raw_readiness = report.get("readiness")
    raw_readiness = raw_readiness if isinstance(raw_readiness, dict) else {}
    readiness = {
        key: raw_readiness.get(key) is True
        for key in _REQUIRED_READINESS
    }
    blockers = raw_readiness.get("blockers")
    if not isinstance(blockers, list):
        blockers = []
    blockers = [str(item) for item in blockers]
    ready = all(readiness.values()) and not blockers
    return {
        "ok": ready,
        "readiness": readiness,
        "blockers": blockers,
        "report": report,
    }


def run_doctor(
    binary: Optional[str] = None,
    *,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Run the pinned binary's real ``doctor`` command and normalise it."""
    resolved = binary or resolve_computer_use_linux_binary()
    if not resolved:
        return {
            "ok": False,
            "binary": None,
            "readiness": {key: False for key in _REQUIRED_READINESS},
            "blockers": ["computer-use-linux binary is not installed"],
            "report": {},
            "error": "computer-use-linux binary is not installed",
        }

    try:
        result = _run(resolved, "doctor", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "ok": False,
            "binary": resolved,
            "readiness": {key: False for key in _REQUIRED_READINESS},
            "blockers": [f"doctor failed: {type(exc).__name__}"],
            "report": {},
            "error": f"computer-use-linux doctor failed: {type(exc).__name__}",
        }

    try:
        report = json.loads(result.stdout or "")
    except (TypeError, ValueError):
        report = {}

    normalized = _normalise_doctor_report(report)
    normalized["binary"] = resolved
    if result.returncode != 0:
        normalized["ok"] = False
        normalized["blockers"] = normalized["blockers"] or [_error_text(result)]
        normalized["error"] = _error_text(result)
    else:
        normalized["error"] = None
    return normalized


def computer_use_linux_status() -> Dict[str, Any]:
    """Return the Desktop/CLI status contract for the managed Linux backend."""
    supported = sys.platform.startswith("linux")
    binary = resolve_computer_use_linux_binary() if supported else None
    if supported:
        doctor = run_doctor(binary)
        readiness = doctor["readiness"]
        blockers = doctor["blockers"]
        ready = doctor["ok"]
        checks = [
            {
                "label": key,
                "status": "ok" if value else "error",
                "message": "ready" if value else "required readiness check is false",
            }
            for key, value in readiness.items()
        ]
        return {
            "platform": sys.platform,
            "platform_supported": True,
            "backend": "computer-use-linux",
            "installed": bool(binary),
            "binary": binary,
            "version": f"source {COMPUTER_USE_LINUX_SOURCE_COMMIT[:12]}",
            "source_commit": COMPUTER_USE_LINUX_SOURCE_COMMIT,
            "ready": ready,
            "can_grant": False,
            "checks": checks,
            "readiness": readiness,
            "blockers": blockers,
            "mcp_server": COMPUTER_USE_LINUX_MCP_SERVER,
            "mcp_configured": bool(binary),
            "mcp_registered": None,
            "accessibility": readiness["can_build_accessibility_tree"],
            "screen_recording": None,
            "screen_recording_capturable": None,
            "source": {"executable": binary} if binary else None,
            "doctor": doctor["report"],
            "error": doctor.get("error"),
        }

    return {
        "platform": sys.platform,
        "platform_supported": False,
        "backend": "computer-use-linux",
        "installed": False,
        "binary": None,
        "version": None,
        "source_commit": COMPUTER_USE_LINUX_SOURCE_COMMIT,
        "ready": None,
        "can_grant": False,
        "checks": [],
        "readiness": {key: False for key in _REQUIRED_READINESS},
        "blockers": ["computer-use-linux is Linux-only"],
        "mcp_server": COMPUTER_USE_LINUX_MCP_SERVER,
        "mcp_configured": False,
        "mcp_registered": None,
        "accessibility": None,
        "screen_recording": None,
        "screen_recording_capturable": None,
        "source": None,
        "doctor": {},
        "error": "computer-use-linux is Linux-only",
    }


def managed_mcp_server_config() -> Optional[Dict[str, Any]]:
    """Build the in-memory MCP entry; no user config edit is required."""
    if not sys.platform.startswith("linux"):
        return None
    binary = resolve_computer_use_linux_binary()
    if not binary:
        return None
    return {
        "command": binary,
        "args": list(COMPUTER_USE_LINUX_MCP_ARGS),
        "env": _desktop_env(),
        "timeout": 120,
        "connect_timeout": 30,
        "enabled": True,
        "managed": True,
        "built_in": True,
        "source_commit": COMPUTER_USE_LINUX_SOURCE_COMMIT,
    }
