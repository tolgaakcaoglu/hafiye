"""P7 execution-policy classification and dispatch-boundary tests."""

from __future__ import annotations

import json
from unittest.mock import patch

from hafiye_execution_policy import (
    DEFAULT_EXECUTION_POLICY,
    evaluate_tool_call,
    normalize_execution_policy,
    resolve_execution_policy,
)
from model_tools import handle_function_call


def _config(policy: str) -> dict:
    return {"hafiye": {"execution_policy": policy}}


def test_policy_normalization_and_default():
    assert normalize_execution_policy("write-confirm") == "WRITE_CONFIRM"
    assert normalize_execution_policy("not-a-policy") == DEFAULT_EXECUTION_POLICY
    assert resolve_execution_policy({}) == DEFAULT_EXECUTION_POLICY


def test_read_only_allows_read_tools_and_known_read_only_terminal_commands():
    config = _config("READ_ONLY")

    assert evaluate_tool_call("read_file", {"path": "README.md"}, config=config).allowed
    assert evaluate_tool_call("process", {"action": "list"}, config=config).allowed
    assert evaluate_tool_call("terminal", {"command": "pwd"}, config=config).allowed
    assert evaluate_tool_call(
        "terminal", {"command": "git status --short"}, config=config
    ).allowed


def test_read_only_blocks_mutating_host_operations():
    config = _config("READ_ONLY")

    for tool_name, args in (
        ("write_file", {"path": "out.txt", "content": "x"}),
        ("patch", {"path": "out.txt", "old_string": "x", "new_string": "y"}),
        ("process", {"action": "kill", "session_id": "proc_test"}),
        ("execute_code", {"code": "open('out.txt', 'w').close()"}),
        ("terminal", {"command": "touch out.txt"}),
    ):
        decision = evaluate_tool_call(tool_name, args, config=config)
        assert decision is not None
        assert decision.allowed is False
        assert decision.requires_confirmation is False


def test_privileged_confirm_only_requires_confirmation_for_privileged_calls():
    config = _config("PRIVILEGED_CONFIRM")

    assert evaluate_tool_call(
        "write_file", {"path": "out.txt", "content": "x"}, config=config
    ).allowed
    assert evaluate_tool_call(
        "terminal", {"command": "touch out.txt"}, config=config
    ).allowed
    privileged = evaluate_tool_call(
        "terminal", {"command": "sudo id"}, config=config
    )
    assert privileged is not None
    assert privileged.requires_confirmation


def test_write_confirm_leaves_reads_unprompted_and_confirms_writes():
    config = _config("WRITE_CONFIRM")

    assert evaluate_tool_call("terminal", {"command": "pwd"}, config=config).allowed
    write = evaluate_tool_call("terminal", {"command": "touch out.txt"}, config=config)
    assert write is not None
    assert write.requires_confirmation
    assert write.warning is not None


def test_read_only_dispatch_blocks_before_registry_dispatch():
    with (
        patch("hafiye_execution_policy.resolve_execution_policy", return_value="READ_ONLY"),
        patch("model_tools.registry.dispatch") as dispatch,
    ):
        result = json.loads(
            handle_function_call(
                "write_file",
                {"path": "out.txt", "content": "x"},
                task_id="p7-test",
            )
        )

    assert "error" in result
    assert "READ_ONLY" in result["error"]
    dispatch.assert_not_called()


def test_write_confirm_uses_existing_approval_surface_before_dispatch():
    with (
        patch("hafiye_execution_policy.resolve_execution_policy", return_value="WRITE_CONFIRM"),
        patch(
            "tools.approval.check_all_command_guards",
            return_value={"approved": True, "user_approved": True},
        ) as check_guards,
        patch("model_tools.registry.dispatch", return_value='{"ok":true}') as dispatch,
    ):
        result = handle_function_call(
            "process",
            {"action": "kill", "session_id": "proc_test"},
            task_id="p7-test",
        )

    assert result == '{"ok":true}'
    check_guards.assert_called_once()
    assert check_guards.call_args.kwargs["enforce_policy"] is True
    dispatch.assert_called_once()
