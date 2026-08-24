"""Shared cancellation and emergency-stop coordination for the TUI gateway.

The gateway owns the live work, while the durable ESTOP sentinel owns the
pause state.  Keeping the orchestration here gives the Desktop, voice, tray,
and RPC entry points one cancellation controller without making the controller
aware of session implementation details.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class EmergencyStopReport:
    """Observable result of one emergency-stop operation."""

    paused: bool
    reason: str
    sentinel: str
    stopped_desktop_sessions: int
    interrupted_sessions: int
    interrupted_delegations: int
    killed_processes: int
    session_errors: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "paused" if self.paused else "pause_failed",
            "paused": self.paused,
            "reason": self.reason,
            "sentinel": self.sentinel,
            "stopped_desktop_sessions": self.stopped_desktop_sessions,
            "interrupted_sessions": self.interrupted_sessions,
            "interrupted_delegations": self.interrupted_delegations,
            "killed_processes": self.killed_processes,
            "session_errors": list(self.session_errors),
        }


class CancellationController:
    """Coordinate all process-local cancellation effects.

    The callbacks are deliberately narrow: the controller decides ordering and
    aggregation, while the gateway supplies the session-specific interruption
    implementation.  This keeps it straightforward to exercise with fakes and
    prevents each UI surface from growing its own partial stop sequence.
    """

    def __init__(
        self,
        *,
        sessions: Mapping[str, dict[str, Any]],
        sessions_lock: Any,
        stop_tts: Callable[[], Any],
        stop_desktop_actions: Callable[[], int] | None = None,
        interrupt_session: Callable[[str, dict[str, Any], str], dict[str, Any]],
        interrupt_delegations: Callable[[str], int],
        kill_processes: Callable[[], int],
    ) -> None:
        self._sessions = sessions
        self._sessions_lock = sessions_lock
        self._stop_tts = stop_tts
        self._stop_desktop_actions = stop_desktop_actions
        self._interrupt_session = interrupt_session
        self._interrupt_delegations = interrupt_delegations
        self._kill_processes = kill_processes

    def emergency_stop(self, reason: str = "operator") -> EmergencyStopReport:
        """Pause new work and interrupt every cancellable live operation."""
        from agent import estop

        normalized_reason = str(reason or "operator").strip()[:240] or "operator"
        sentinel = estop.engage(reason=normalized_reason)

        # Audio is process-global and must be cut before session callbacks can
        # emit any more turn output.
        self._stop_tts()

        stopped_desktop_sessions = 0
        if self._stop_desktop_actions is not None:
            try:
                stopped_desktop_sessions = int(self._stop_desktop_actions())
            except Exception as exc:
                session_errors = [f"desktop: {exc}"]
            else:
                session_errors = []
        else:
            session_errors = []

        with self._sessions_lock:
            sessions = list(self._sessions.items())

        interrupted_sessions = 0
        for session_id, session in sessions:
            try:
                result = self._interrupt_session(session_id, session, normalized_reason)
            except Exception as exc:  # emergency stop must continue fan-out
                session_errors.append(f"{session_id}: {exc}")
                continue

            if result.get("status") == "interrupted":
                interrupted_sessions += 1
            if result.get("error"):
                session_errors.append(f"{session_id}: {result['error']}")

        try:
            interrupted_delegations = int(self._interrupt_delegations(normalized_reason))
        except Exception as exc:
            interrupted_delegations = 0
            session_errors.append(f"delegations: {exc}")

        try:
            killed_processes = int(self._kill_processes())
        except Exception as exc:
            killed_processes = 0
            session_errors.append(f"processes: {exc}")

        return EmergencyStopReport(
            paused=bool(estop.is_engaged()),
            reason=normalized_reason,
            sentinel=str(sentinel),
            stopped_desktop_sessions=stopped_desktop_sessions,
            interrupted_sessions=interrupted_sessions,
            interrupted_delegations=interrupted_delegations,
            killed_processes=killed_processes,
            session_errors=tuple(session_errors),
        )

    def resume(self) -> dict[str, Any]:
        """Lift only the durable emergency pause; explicit delegation pauses remain."""
        from agent import estop

        disengaged = estop.disengage()
        return {
            "status": "resumed" if not estop.is_engaged() else "resume_failed",
            "paused": bool(estop.is_engaged()),
            "disengaged": bool(disengaged),
        }
