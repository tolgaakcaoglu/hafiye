"""Turn-local postcondition gate for failed native browser actions.

``browser_native`` already returns explicit structured failures.  This module
keeps the agent loop from accepting a text-only success claim immediately
after one of those failures: the model gets a bounded chance to obtain fresh
browser state, and an unresolved failure becomes a truthful blocker.
"""

from __future__ import annotations

from typing import Any

from utils import safe_json_loads


_STATE_ATTR = "_native_browser_verification"
_MAX_NUDGES = 2


def _state(agent: Any) -> dict[str, Any]:
    state = getattr(agent, _STATE_ATTR, None)
    if not isinstance(state, dict):
        state = {
            "required": False,
            "verified": False,
            "nudges": 0,
            "last_failed_action": "browser action",
        }
        setattr(agent, _STATE_ATTR, state)
    return state


def reset_for_turn(agent: Any) -> None:
    """Clear native-browser verification state at the start of a user turn."""
    setattr(
        agent,
        _STATE_ATTR,
        {
            "required": False,
            "verified": False,
            "nudges": 0,
            "last_failed_action": "browser action",
        },
    )


def _payload(result: Any) -> dict[str, Any] | None:
    if isinstance(result, str):
        result = safe_json_loads(result)
    return result if isinstance(result, dict) else None


def record_tool_result(agent: Any, tool_name: str, result: Any, *, failed: bool) -> None:
    """Record native-browser failures and a later fresh successful state read.

    A successful state read is the smallest provider-independent evidence that
    lets the model reassess the visible browser after a failed action.  Other
    successful browser actions do not satisfy this gate because they do not
    establish the resulting page or playback state.
    """
    if tool_name != "browser_native":
        return
    payload = _payload(result)
    action = str(payload.get("action") or "browser action") if payload else "browser action"
    state = _state(agent)
    if failed:
        state["required"] = True
        state["verified"] = False
        state["last_failed_action"] = action
        return
    if state.get("required") and action == "state":
        state["required"] = False
        state["verified"] = True


def build_verification_nudge(agent: Any) -> str | None:
    """Return a bounded internal prompt requiring fresh native browser state."""
    state = _state(agent)
    if not state.get("required") or state.get("verified"):
        return None
    nudges = int(state.get("nudges") or 0)
    if nudges >= _MAX_NUDGES:
        return None
    state["nudges"] = nudges + 1
    action = state.get("last_failed_action") or "browser action"
    return (
        f"The previous browser_native action='{action}' returned an explicit "
        "failure. Do not claim the browser task is complete. Use "
        "browser_native with action='state' to obtain fresh state, then either "
        "recover the task and verify the requested result or report the exact "
        "blocker truthfully."
    )


def verification_blocker(agent: Any) -> str | None:
    """Return a truthful terminal response after bounded recovery is exhausted."""
    state = _state(agent)
    if not state.get("required") or state.get("verified"):
        return None
    if int(state.get("nudges") or 0) < _MAX_NUDGES:
        return None
    action = state.get("last_failed_action") or "browser action"
    return (
        f"Browser işlemi ({action}) başarısız oldu ve taze durumla doğrulanamadı; "
        "tamamlandı diyemiyorum."
    )

