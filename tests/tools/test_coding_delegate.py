from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import model_tools
from hermes_cli.openhands_runtime import OpenHandsRuntimePaths
from tools import coding_delegate_tool
from tools.openhands_worker import _model_name


def test_openhands_runtime_doctor_and_tool_are_discoverable():
    assert "coding_delegate" in model_tools.get_all_tool_names()
    entry = model_tools.registry.get_entry("coding_delegate")
    assert entry is not None
    original_check = entry.check_fn
    entry.check_fn = lambda: True
    definitions = model_tools.get_tool_definitions(
        enabled_toolsets=["delegation"],
        quiet_mode=True,
    )
    entry.check_fn = original_check
    names = {item["function"]["name"] for item in definitions}
    assert "coding_delegate" in names


def test_worker_model_name_uses_hafiye_provider_route():
    assert _model_name("gemini", "gemini-flash-lite-latest") == (
        "gemini/gemini-flash-lite-latest"
    )
    assert _model_name("local", "qwen-test") == "openai/qwen-test"
    assert _model_name("openrouter", "anthropic/claude") == (
        "openrouter/anthropic/claude"
    )


def test_handle_function_call_forwards_parent_agent_only_to_coding_delegate(monkeypatch):
    captured = {}

    def fake_dispatch(name, args, **kwargs):
        captured.update({"name": name, "args": args, "kwargs": kwargs})
        return json.dumps({"ok": True})

    monkeypatch.setattr(model_tools.registry, "dispatch", fake_dispatch)
    parent = SimpleNamespace(session_id="session-1")
    result = model_tools.handle_function_call(
        "coding_delegate",
        {"goal": "inspect", "repository_path": "/tmp"},
        task_id="task-1",
        parent_agent=parent,
        skip_pre_tool_call_hook=True,
        skip_tool_request_middleware=True,
        skip_tool_execution_middleware=True,
    )

    assert json.loads(result) == {"ok": True}
    assert captured["kwargs"]["parent_agent"] is parent


def test_coding_delegate_uses_managed_process_and_redacts_secret_from_command(
    tmp_path: Path, monkeypatch
):
    repository = tmp_path / "repo"
    repository.mkdir()
    paths = OpenHandsRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")
    fake_session = SimpleNamespace(id="proc_coding_test")
    captured = {}

    monkeypatch.setattr(coding_delegate_tool, "openhands_runtime_ready", lambda: True)
    monkeypatch.setattr(
        coding_delegate_tool,
        "get_openhands_runtime_paths",
        lambda: paths,
    )
    monkeypatch.setattr(
        coding_delegate_tool,
        "load_config",
        lambda: {"hafiye": {"route_slots": {"coding": {}}}},
    )
    monkeypatch.setattr(
        coding_delegate_tool.process_registry,
        "spawn_local",
        lambda command, **kwargs: (
            captured.update({"command": command, "kwargs": kwargs}) or fake_session
        ),
    )
    monkeypatch.setattr(
        coding_delegate_tool,
        "_wait_for_process",
        lambda _session_id, **_kwargs: {"status": "exited", "exit_code": 0},
    )
    monkeypatch.setattr(
        coding_delegate_tool.process_registry,
        "read_log",
        lambda *_args, **_kwargs: {
            "output": json.dumps(
                {
                    "type": "result",
                    "status": "completed",
                    "execution_status": "finished",
                    "summary": "done",
                }
            )
        },
    )
    monkeypatch.setattr(
        coding_delegate_tool,
        "get_openhands_runtime_paths",
        lambda: paths,
    )

    parent = SimpleNamespace(
        provider="gemini",
        model="gemini-flash-lite-latest",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key="secret-not-in-command",
        session_id="session-1",
    )
    result = json.loads(
        coding_delegate_tool._handle_coding_delegate(
            {
                "goal": "fix the failing test",
                "repository_path": str(repository),
                "expected_verification": "pytest -q",
            },
            parent_agent=parent,
            task_id="task-1",
            session_id="session-1",
        )
    )

    assert result["status"] == "completed"
    assert result["process_id"] == fake_session.id
    assert parent.api_key not in captured["command"]
    assert captured["kwargs"]["env_vars"]["_HERMES_FORCE_HAFIYE_OPENHANDS_CREDENTIAL"] == parent.api_key
    assert not list(paths.request_root.glob("*.json"))
