"""``hermes pause`` / ``hermes resume`` — the global emergency stop.

``hermes pause`` writes the ESTOP sentinel at ``$HERMES_HOME/ESTOP``, which
halts cron dispatch, kanban dispatch, and new gateway turns on their next
check. In-flight work is never killed. ``hermes resume`` removes the
sentinel and normal operation resumes on the next tick — no restart needed.

Ported from: gastownhall/gastown estop.go (MIT); related prior art:
#26778 (/panic — kill/exit semantics, different), #44617.
"""

from __future__ import annotations

import argparse
import json
import time
import uuid


def _request_persistent_gateway(method: str, params: dict | None = None) -> dict | None:
    """Best-effort RPC to the local persistent Hafiye gateway.

    The CLI still works when the Desktop backend is not installed or is down:
    the durable ESTOP sentinel is the fallback.  When the backend is alive,
    this sends the same emergency RPC used by Desktop, voice, and tray.
    """
    try:
        from websockets.sync.client import connect

        from hermes_cli.persistent_gateway import (
            _read_private_token,
            connection_descriptor,
            paths,
        )

        targets = paths()
        token = _read_private_token(targets.token_file)
        if not token:
            return None
        descriptor = connection_descriptor(targets)
        port = int(descriptor["port"])
        request_id = f"cli-{uuid.uuid4().hex}"
        url = f"ws://127.0.0.1:{port}/api/ws?token={token}"
        with connect(url, open_timeout=1.5, close_timeout=1.5, max_size=None) as websocket:
            websocket.send(
                json.dumps(
                    {
                        "id": request_id,
                        "method": method,
                        "params": params or {},
                    },
                    separators=(",", ":"),
                )
            )
            deadline = time.monotonic() + 3.0
            while time.monotonic() < deadline:
                response = json.loads(websocket.recv(timeout=max(0.1, deadline - time.monotonic())))
                if response.get("id") != request_id:
                    continue
                if response.get("error"):
                    return None
                result = response.get("result")
                return result if isinstance(result, dict) else None
    except Exception:
        return None
    return None


def cmd_pause(args: argparse.Namespace) -> int:
    """Engage the global emergency stop."""
    from agent.estop import engage, get_state, is_engaged

    reason = getattr(args, "reason", None)
    already = is_engaged()
    path = engage(reason=reason)
    state = get_state() or {}
    verb = "Still paused" if already else "Hermes paused"
    detail = f" — reason: {state['reason']}" if state.get("reason") else ""
    print(f"⏸️  {verb}{detail}")
    print(f"    sentinel: {path}")
    print(
        "    Cron dispatch, kanban dispatch, and new gateway turns are on hold.\n"
        "    In-flight work keeps running. Run `hermes resume` to lift the pause."
    )
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    """Disengage the global emergency stop."""
    from agent.estop import disengage, sentinel_path

    if disengage():
        print("▶️  Hermes resumed — dispatch picks up on the next tick.")
    else:
        print(f"Hermes is not paused (no sentinel at {sentinel_path()}).")
    return 0


def cmd_emergency_stop(args: argparse.Namespace) -> int:
    """Run the full process-wide emergency stop through the live gateway."""
    from agent.estop import engage, get_state

    reason = getattr(args, "reason", None) or "cli"
    report = _request_persistent_gateway("emergency.stop", {"reason": reason})
    if report is None:
        path = engage(reason=reason)
        state = get_state() or {}
        print(f"⏹️  Hafiye emergency stop engaged — reason: {state.get('reason') or reason}")
        print(f"    sentinel: {path}")
        print("    Persistent gateway was unavailable; new work is blocked until `hermes resume`.")
        return 0

    print(f"⏹️  Hafiye emergency stop engaged — reason: {report.get('reason') or reason}")
    print(
        "    TTS, active sessions, desktop backends, delegations, and processes "
        f"were signaled (sessions={report.get('interrupted_sessions', 0)}, "
        f"desktop={report.get('stopped_desktop_sessions', 0)}, "
        f"delegations={report.get('interrupted_delegations', 0)}, "
        f"processes={report.get('killed_processes', 0)})."
    )
    return 0


def build_pause_parser(subparsers) -> None:
    """Attach the ``pause`` and ``resume`` subcommands to ``subparsers``."""
    pause_parser = subparsers.add_parser(
        "pause",
        help="Emergency stop: pause cron/kanban dispatch and new gateway turns",
        description=(
            "Engage the global emergency stop. Halts NEW work only — cron "
            "dispatch, kanban dispatch, and new gateway turns — until "
            "`hermes resume`. In-flight work is never killed."
        ),
    )
    pause_parser.add_argument(
        "--reason",
        default=None,
        help="Optional reason stored in the sentinel and shown to users",
    )
    pause_parser.set_defaults(func=cmd_pause)

    resume_parser = subparsers.add_parser(
        "resume",
        help="Lift the emergency stop set by `hermes pause`",
        description="Remove the ESTOP sentinel; dispatch resumes on the next tick.",
    )
    resume_parser.set_defaults(func=cmd_resume)

    emergency_parser = subparsers.add_parser(
        "emergency-stop",
        help="Stop active Hafiye work and pause new work through the live gateway",
        description=(
            "Run the process-wide Hafiye emergency stop. The command uses the "
            "persistent gateway when available and falls back to the durable "
            "pause sentinel when it is not."
        ),
    )
    emergency_parser.add_argument(
        "--reason",
        default=None,
        help="Optional reason stored in the emergency-stop state",
    )
    emergency_parser.set_defaults(func=cmd_emergency_stop)
