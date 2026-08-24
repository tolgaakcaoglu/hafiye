"""Hafiye's explicit native desktop-browser route.

Hermes' ``browser_*`` tools remain the structured automation lane.  This
small Hafiye tool is the explicit escape hatch for the other roadmap path:
the user's already-authenticated normal Linux browser window, driven through
the managed ``computer-use-linux`` MCP provider.  It deliberately does not
launch a second browser profile or inspect browser cookies.

The MCP server remains the implementation of desktop control.  This module
only supplies the browser-specific routing contract and a bounded sequence for
common browser actions (focus, state, navigation, page action, typing, key
press, scroll, screenshot).  It calls the already-registered MCP tools rather
than copying their AT-SPI/Wayland implementation into Hermes.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict, Iterable, Optional

from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

_MCP_SERVER = "hafiye-computer-use-linux"
_MCP_PREFIX = f"mcp__{_MCP_SERVER.replace('-', '_')}__"
_TARGET_KEYS = (
    "window_id",
    "pid",
    "app_id",
    "title",
    "wm_class",
    "terminal_command",
    "terminal_cwd",
    "terminal_pid",
    "tty",
)
_SELECTOR_KEYS = (
    "element_index",
    "element_identifier",
    "name",
    "role",
    "states",
    "text",
    "action_name",
)

_NATIVE_BROWSER_SCHEMA: Dict[str, Any] = {
    "name": "browser_native",
    "description": (
        "Explicit native desktop browser route through Hafiye's managed "
        "computer-use-linux MCP provider. Use browser_* structured tools by "
        "default. Use this only when the task explicitly requires the user's "
        "already-authenticated normal Linux browser session and structured "
        "automation cannot safely reuse it. Start with action='windows' or "
        "action='focused', bind an exact window_id, then use action='state' "
        "before page actions. This route never launches a new browser profile "
        "and never reads cookies."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "windows",
                    "focused",
                    "focus",
                    "state",
                    "navigate",
                    "click",
                    "type",
                    "press",
                    "scroll",
                    "screenshot",
                ],
                "description": "Native browser operation to perform.",
            },
            "window_id": {
                "type": "integer",
                "description": "Exact compositor window id. Required for mutations when possible.",
            },
            "pid": {"type": "integer"},
            "app_id": {"type": "string"},
            "title": {"type": "string"},
            "wm_class": {"type": "string"},
            "url": {
                "type": "string",
                "description": "URL for action='navigate'. Secret-bearing and cloud-metadata URLs are rejected.",
            },
            "element_index": {
                "type": "integer",
                "description": "AT-SPI element index from the latest action='state' result.",
            },
            "element_identifier": {"type": "string"},
            "name": {"type": "string"},
            "role": {"type": "string"},
            "states": {"type": "array", "items": {"type": "string"}},
            "text": {"type": "string"},
            "value": {"type": "string"},
            "key": {
                "type": "string",
                "description": "Key or key combination for action='press'.",
            },
            "direction": {
                "type": "string",
                "enum": ["up", "down", "left", "right"],
            },
            "pages": {"type": "number"},
            "include_screenshot": {"type": "boolean"},
            "max_nodes": {"type": "integer"},
            "max_depth": {"type": "integer"},
            "action_name": {
                "type": "string",
                "description": "Optional accessibility action for action='click'.",
            },
        },
        "required": ["action"],
    },
}


def check_browser_native_requirements() -> bool:
    """Expose the native lane only when the managed Linux doctor is ready."""
    if not sys.platform.startswith("linux"):
        return False
    try:
        from hafiye_computer_use import resolve_computer_use_linux_binary, run_doctor

        binary = resolve_computer_use_linux_binary()
        return bool(binary and run_doctor(binary, timeout=5.0).get("ok"))
    except Exception:
        logger.debug("Native Hafiye browser readiness probe failed", exc_info=True)
        return False


def _target_args(args: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: args[key]
        for key in _TARGET_KEYS
        if args.get(key) is not None
    }


def _selector_args(args: Dict[str, Any]) -> Dict[str, Any]:
    selector: Dict[str, Any] = {}
    for key in _SELECTOR_KEYS:
        value = args.get(key)
        if value is None:
            continue
        if key == "action_name":
            selector["action"] = value
        else:
            selector[key] = value
    return selector


def _decode_result(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def _result_failed(value: Any) -> bool:
    payload = _decode_result(value)
    if not isinstance(payload, dict):
        return False
    if payload.get("isError") is True:
        return True
    if payload.get("success") is False or payload.get("ok") is False:
        return True
    return bool(payload.get("error"))


def _call_managed_tool(
    tool: str,
    args: Dict[str, Any],
    *,
    task_id: Optional[str],
    session_id: Optional[str],
    user_task: Optional[str],
) -> Any:
    """Dispatch one registered managed-MCP tool, discovering lazily if needed."""
    name = f"{_MCP_PREFIX}{tool}"
    if registry.get_entry(name) is None:
        try:
            from tools.mcp_tool import discover_mcp_tools

            discover_mcp_tools()
        except Exception as exc:
            return tool_error(f"Managed computer-use-linux discovery failed: {exc}")
    if registry.get_entry(name) is None:
        return tool_error(
            "The managed computer-use-linux MCP tools are not registered. "
            "Run the Computer readiness check and retry."
        )
    return registry.dispatch(
        name,
        dict(args),
        task_id=task_id,
        session_id=session_id,
        user_task=user_task,
    )


def _require_target(action: str, target: Dict[str, Any]) -> Optional[str]:
    if target:
        return None
    return (
        f"Native browser action '{action}' requires a target window. "
        "Use action='windows' first and pass window_id (or another exact "
        "window selector)."
    )


def _safe_navigation_url(url: Any) -> Optional[str]:
    value = str(url or "").strip()
    if not value:
        return "A URL is required for native browser navigation."
    try:
        from agent.redact import _PREFIX_RE
        from tools.url_safety import is_always_blocked_url, sensitive_query_param_name

        if _PREFIX_RE.search(value):
            return "Navigation URL appears to contain a secret or API token."
        sensitive_key = sensitive_query_param_name(value)
        if sensitive_key:
            return (
                "Navigation URL contains a credential-bearing query parameter "
                f"({sensitive_key})."
            )
        if is_always_blocked_url(value):
            return "Navigation to cloud metadata endpoints is blocked."
    except Exception:
        logger.debug("Native browser URL safety check failed", exc_info=True)
    return None


def _run_steps(
    action: str,
    steps: Iterable[tuple[str, Dict[str, Any]]],
    *,
    task_id: Optional[str],
    session_id: Optional[str],
    user_task: Optional[str],
) -> str:
    results = []
    for tool, tool_args in steps:
        result = _call_managed_tool(
            tool,
            tool_args,
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
        results.append({"tool": tool, "result": _decode_result(result)})
        if _result_failed(result):
            return json.dumps(
                {
                    "success": False,
                    "route": "native",
                    "action": action,
                    "steps": results,
                },
                ensure_ascii=False,
            )
    return json.dumps(
        {
            "success": True,
            "route": "native",
            "action": action,
            "steps": results,
        },
        ensure_ascii=False,
    )


def browser_native(
    action: str,
    *,
    window_id: Optional[int] = None,
    pid: Optional[int] = None,
    app_id: Optional[str] = None,
    title: Optional[str] = None,
    wm_class: Optional[str] = None,
    url: Optional[str] = None,
    element_index: Optional[int] = None,
    element_identifier: Optional[str] = None,
    name: Optional[str] = None,
    role: Optional[str] = None,
    states: Optional[list[str]] = None,
    text: Optional[str] = None,
    value: Optional[str] = None,
    key: Optional[str] = None,
    direction: Optional[str] = None,
    pages: Optional[float] = None,
    include_screenshot: Optional[bool] = None,
    max_nodes: Optional[int] = None,
    max_depth: Optional[int] = None,
    action_name: Optional[str] = None,
    task_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_task: Optional[str] = None,
) -> str:
    """Run one explicit native-browser operation through computer-use-linux."""
    action = str(action or "").strip().lower()
    target = {
        key: val
        for key, val in {
            "window_id": window_id,
            "pid": pid,
            "app_id": app_id,
            "title": title,
            "wm_class": wm_class,
        }.items()
        if val is not None
    }
    args = {
        "element_index": element_index,
        "element_identifier": element_identifier,
        "name": name,
        "role": role,
        "states": states,
        "text": text,
        "value": value,
        "key": key,
        "direction": direction,
        "pages": pages,
        "include_screenshot": include_screenshot,
        "max_nodes": max_nodes,
        "max_depth": max_depth,
        "action_name": action_name,
    }
    args = {key: val for key, val in args.items() if val is not None}

    if action == "windows":
        return _run_steps(
            action,
            [("list_windows", {})],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "focused":
        return _run_steps(
            action,
            [("focused_window", {})],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )

    target_error = _require_target(action, target)
    if target_error:
        return json.dumps(
            {"success": False, "route": "native", "action": action, "error": target_error},
            ensure_ascii=False,
        )

    if action == "focus":
        return _run_steps(
            action,
            [("activate_window", target)],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "state":
        state_args = dict(target)
        for key_name in ("include_screenshot", "max_nodes", "max_depth"):
            if key_name in args:
                state_args[key_name] = args[key_name]
        return _run_steps(
            action,
            [("get_app_state", state_args)],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "navigate":
        url_error = _safe_navigation_url(url)
        if url_error:
            return json.dumps(
                {"success": False, "route": "native", "action": action, "error": url_error},
                ensure_ascii=False,
            )
        return _run_steps(
            action,
            [
                ("activate_window", target),
                ("press_key", {**target, "key": "Ctrl+L"}),
                ("type_text", {**target, "text": str(url).strip()}),
                ("press_key", {**target, "key": "Enter"}),
            ],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "click":
        selector = _selector_args(args)
        if not selector:
            return json.dumps(
                {"success": False, "route": "native", "action": action, "error": "A native accessibility selector is required."},
                ensure_ascii=False,
            )
        return _run_steps(
            action,
            [("activate_window", target), ("perform_action", selector)],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "type":
        typed = text if text is not None else value
        if typed is None:
            return json.dumps(
                {"success": False, "route": "native", "action": action, "error": "Text is required for native typing."},
                ensure_ascii=False,
            )
        selector = _selector_args({key: val for key, val in args.items() if key != "text"})
        if selector:
            selector["value"] = str(typed)
            return _run_steps(
                action,
                [("activate_window", target), ("set_value", selector)],
                task_id=task_id,
                session_id=session_id,
                user_task=user_task,
            )
        return _run_steps(
            action,
            [("activate_window", target), ("type_text", {**target, "text": str(typed)})],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "press":
        if not key:
            return json.dumps(
                {"success": False, "route": "native", "action": action, "error": "A key is required for native key input."},
                ensure_ascii=False,
            )
        return _run_steps(
            action,
            [("press_key", {**target, "key": key})],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "scroll":
        if not direction:
            return json.dumps(
                {"success": False, "route": "native", "action": action, "error": "A direction is required for native scrolling."},
                ensure_ascii=False,
            )
        scroll_args = {**target, "direction": direction}
        if pages is not None:
            scroll_args["pages"] = pages
        return _run_steps(
            action,
            [("scroll", scroll_args)],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    if action == "screenshot":
        return _run_steps(
            action,
            [("screenshot", target)],
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )

    return json.dumps(
        {
            "success": False,
            "route": "native",
            "action": action,
            "error": "Unknown native browser action.",
        },
        ensure_ascii=False,
    )


registry.register(
    name="browser_native",
    toolset="browser",
    schema=_NATIVE_BROWSER_SCHEMA,
    handler=lambda args, **kw: browser_native(
        action=args.get("action", ""),
        window_id=args.get("window_id"),
        pid=args.get("pid"),
        app_id=args.get("app_id"),
        title=args.get("title"),
        wm_class=args.get("wm_class"),
        url=args.get("url"),
        element_index=args.get("element_index"),
        element_identifier=args.get("element_identifier"),
        name=args.get("name"),
        role=args.get("role"),
        states=args.get("states"),
        text=args.get("text"),
        value=args.get("value"),
        key=args.get("key"),
        direction=args.get("direction"),
        pages=args.get("pages"),
        include_screenshot=args.get("include_screenshot"),
        max_nodes=args.get("max_nodes"),
        max_depth=args.get("max_depth"),
        action_name=args.get("action_name"),
        task_id=kw.get("task_id"),
        session_id=kw.get("session_id"),
        user_task=kw.get("user_task"),
    ),
    check_fn=check_browser_native_requirements,
    emoji="🧭",
)
