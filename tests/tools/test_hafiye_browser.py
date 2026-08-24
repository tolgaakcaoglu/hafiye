import json

import pytest

from tools import hafiye_browser as native_browser


def _success(tool, args):
    return {"tool": tool, "args": args, "ok": True}


def test_native_windows_route_uses_managed_mcp_tool(monkeypatch):
    calls = []

    def fake_call(tool, args, **kwargs):
        calls.append((tool, args, kwargs))
        return json.dumps(_success(tool, args))

    monkeypatch.setattr(native_browser, "_call_managed_tool", fake_call)

    result = json.loads(native_browser.browser_native("windows", task_id="task-1"))

    assert result["success"] is True
    assert result["route"] == "native"
    assert calls[0][0] == "list_windows"
    assert calls[0][1] == {}


def test_native_navigation_is_an_explicit_targeted_sequence(monkeypatch):
    calls = []

    def fake_call(tool, args, **kwargs):
        calls.append((tool, args))
        return json.dumps({"ok": True})

    monkeypatch.setattr(native_browser, "_call_managed_tool", fake_call)

    result = json.loads(
        native_browser.browser_native(
            "navigate",
            window_id=42,
            url="https://example.test/account",
            task_id="task-2",
        )
    )

    assert result["success"] is True
    assert [tool for tool, _ in calls] == [
        "activate_window",
        "press_key",
        "type_text",
        "press_key",
    ]
    assert calls[0][1] == {"window_id": 42}
    assert calls[1][1] == {"window_id": 42, "key": "Ctrl+L"}
    assert calls[2][1] == {"window_id": 42, "text": "https://example.test/account"}
    assert calls[3][1] == {"window_id": 42, "key": "Enter"}


def test_native_state_and_click_preserve_exact_window_binding(monkeypatch):
    calls = []

    def fake_call(tool, args, **kwargs):
        calls.append((tool, args))
        return json.dumps({"ok": True})

    monkeypatch.setattr(native_browser, "_call_managed_tool", fake_call)

    state = json.loads(
        native_browser.browser_native(
            "state",
            window_id=99,
            include_screenshot=False,
            max_nodes=200,
        )
    )
    click = json.loads(
        native_browser.browser_native(
            "click",
            window_id=99,
            element_index=7,
            action_name="click",
        )
    )

    assert state["success"] is True
    assert click["success"] is True
    assert calls[0] == (
        "get_app_state",
        {"window_id": 99, "include_screenshot": False, "max_nodes": 200},
    )
    assert calls[1] == ("activate_window", {"window_id": 99})
    assert calls[2] == (
        "perform_action",
        {"element_index": 7, "action": "click"},
    )


def test_native_type_uses_accessibility_value_when_selector_is_given(monkeypatch):
    calls = []

    def fake_call(tool, args, **kwargs):
        calls.append((tool, args))
        return json.dumps({"ok": True})

    monkeypatch.setattr(native_browser, "_call_managed_tool", fake_call)

    result = json.loads(
        native_browser.browser_native(
            "type",
            window_id=7,
            element_index=3,
            text="search phrase",
        )
    )

    assert result["success"] is True
    assert calls == [
        ("activate_window", {"window_id": 7}),
        ("set_value", {"element_index": 3, "value": "search phrase"}),
    ]


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"action": "navigate", "url": "https://example.test"}, "requires a target window"),
        ({"action": "navigate", "window_id": 4, "url": "https://evil.test/?token=opaque-secret"}, "credential"),
        ({"action": "click", "window_id": 4}, "selector"),
    ],
)
def test_native_route_fails_closed_without_target_or_safe_input(kwargs, message):
    result = json.loads(native_browser.browser_native(**kwargs))

    assert result["success"] is False
    assert message.lower() in result["error"].lower()


def test_native_readiness_uses_pinned_doctor(monkeypatch):
    monkeypatch.setattr(native_browser.sys, "platform", "linux")
    monkeypatch.setattr(
        "hafiye_computer_use.resolve_computer_use_linux_binary",
        lambda: "/opt/computer-use-linux",
    )
    calls = []

    def fake_doctor(binary, *, timeout):
        calls.append((binary, timeout))
        return {"ok": True}

    monkeypatch.setattr("hafiye_computer_use.run_doctor", fake_doctor)

    assert native_browser.check_browser_native_requirements() is True
    assert calls == [("/opt/computer-use-linux", 5.0)]


def test_native_failure_returns_structured_recovery_code_and_redacts(monkeypatch):
    def fake_call(tool, args, **kwargs):
        return json.dumps({"error": "AT-SPI unavailable sk-hafiye-secret-012345678901234567890"})

    monkeypatch.setattr(native_browser, "_call_managed_tool", fake_call)

    result = json.loads(native_browser.browser_native("state", window_id=7))

    assert result["success"] is False
    assert result["failure"]["code"] == "accessibility_unavailable"
    assert result["failure"]["blocker"] is True
    assert "sk-hafiye-secret" not in json.dumps(result)


def test_structured_browser_download_calls_agent_browser_download(monkeypatch, tmp_path):
    from tools import browser_tool

    calls = []
    monkeypatch.setattr(browser_tool, "_is_camofox_mode", lambda: False)
    monkeypatch.setattr(browser_tool, "_last_session_key", lambda task_id: task_id)
    monkeypatch.setattr(browser_tool, "_blocked_private_page_action", lambda *args: None)

    def fake_run(task_id, command, args):
        calls.append((task_id, command, args))
        return {"success": True, "data": {"path": args[-1]}}

    monkeypatch.setattr(browser_tool, "_run_browser_command", fake_run)
    destination = tmp_path / "nested" / "fixture.txt"

    result = json.loads(
        browser_tool.browser_download("e4", str(destination), task_id="structured-task")
    )

    assert result["success"] is True
    assert result["downloaded"] == str(destination)
    assert calls == [
        ("structured-task", "download", ["@e4", str(destination)])
    ]
    assert destination.parent.is_dir()


def test_structured_browser_download_requires_absolute_path(monkeypatch):
    from tools import browser_tool

    monkeypatch.setattr(browser_tool, "_is_camofox_mode", lambda: False)
    monkeypatch.setattr(browser_tool, "_last_session_key", lambda task_id: task_id)
    monkeypatch.setattr(browser_tool, "_blocked_private_page_action", lambda *args: None)

    result = json.loads(browser_tool.browser_download("@e1", "relative.txt"))

    assert result["success"] is False
    assert "absolute" in result["error"]
