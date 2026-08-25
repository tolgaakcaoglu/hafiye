from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import pytest

import hafiye_execution_policy
import hafiye_rootd
import tools.terminal_tool as terminal_module
from hafiye_rootd import RootBrokerServer


def _config(tmp_path: Path) -> dict:
    return {
        "env_type": "local",
        "cwd": str(tmp_path),
        "timeout": 5,
        "lifetime_seconds": 60,
        "local_persistent": False,
    }


class _FakeBroker:
    calls: list[tuple[str, dict]] = []

    def __init__(self, *args, **kwargs):
        return None

    def exec(self, command: str, **kwargs):
        self.calls.append((command, kwargs))
        return {
            "returncode": 0,
            "stdout": "HAFIYE_ROOTD_OK",
            "stderr": "",
            "timed_out": False,
            "stdout_truncated": False,
            "stderr_truncated": False,
        }


def _fake_environment(tmp_path: Path):
    class FakeEnvironment:
        cwd = str(tmp_path)
        env = {}

        def __init__(self):
            self.commands: list[str] = []

        def execute(self, command: str, **kwargs):
            self.commands.append(command)
            return {
                "output": "HAFIYE_NORMAL_OK",
                "returncode": 0,
                "cwd_observed": False,
            }

    return FakeEnvironment()


def test_privileged_terminal_forms_route_to_rootd_without_normal_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    config = _config(tmp_path)
    _FakeBroker.calls = []
    normal_environment_created = False

    def fail_if_normal_environment_is_created(**kwargs):
        nonlocal normal_environment_created
        normal_environment_created = True
        raise AssertionError("privileged terminal command reached normal environment")

    monkeypatch.setattr(terminal_module, "_get_env_config", lambda: config)
    monkeypatch.setattr(
        hafiye_execution_policy,
        "resolve_execution_policy",
        lambda config=None: "FULL_AUTONOMOUS",
    )
    monkeypatch.setattr(hafiye_rootd, "RootBrokerClient", _FakeBroker)
    monkeypatch.setattr(terminal_module, "_create_environment", fail_if_normal_environment_is_created)

    commands = (
        "sudo id",
        "/usr/bin/sudo id",
        "env HAFIYE_TEST=1 sudo id",
        "command sudo id",
        "echo safe; sudo id",
        "'sudo' id",
        "sh -c 'sudo id'",
        "bash -lc \"env X=Y /bin/pkexec id\"",
        "su -c 'id'",
        "doas id",
    )
    for command in commands:
        result = json.loads(terminal_module.terminal_tool(command, task_id="ki043-test"))
        assert result["exit_code"] == 0
        assert result["privileged_via"] == "hafiye-rootd"

    assert not normal_environment_created
    assert [command for command, _ in _FakeBroker.calls] == list(commands)


def test_gemini_ki043_chown_scenario_is_rootd_routed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    config = _config(tmp_path)
    _FakeBroker.calls = []
    monkeypatch.setattr(terminal_module, "_get_env_config", lambda: config)
    monkeypatch.setattr(
        hafiye_execution_policy,
        "resolve_execution_policy",
        lambda config=None: "FULL_AUTONOMOUS",
    )
    monkeypatch.setattr(hafiye_rootd, "RootBrokerClient", _FakeBroker)
    monkeypatch.setattr(
        terminal_module,
        "_create_environment",
        lambda **kwargs: pytest.fail("Gemini KI-043 command used normal terminal"),
    )

    command = "sudo chown root:root /usr/libexec/snapd/snap-confine"
    result = json.loads(terminal_module.terminal_tool(command, task_id="gemini-ki043"))

    assert result["privileged_via"] == "hafiye-rootd"
    assert _FakeBroker.calls[0][0] == command


def test_rerouted_sudo_creates_root_broker_audit_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    socket_path = tmp_path / "run" / "root.sock"
    audit_log = tmp_path / "log" / "rootd.jsonl"
    server = RootBrokerServer(
        socket_path=socket_path,
        allowed_uid=os.getuid(),
        audit_log=audit_log,
        estop_path=tmp_path / "ESTOP",
        io_timeout=2,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.monotonic() + 2
    while not socket_path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert socket_path.exists()
    try:
        monkeypatch.setenv("HAFIYE_ROOTD_SOCKET", str(socket_path))
        monkeypatch.setattr(terminal_module, "_get_env_config", lambda: _config(tmp_path))
        monkeypatch.setattr(
            hafiye_execution_policy,
            "resolve_execution_policy",
            lambda config=None: "FULL_AUTONOMOUS",
        )

        command = "sudo -n /bin/true || /bin/true"
        result = json.loads(
            terminal_module.terminal_tool(command, task_id="ki043-audit")
        )
        lines = audit_log.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines]

        assert result["privileged_via"] == "hafiye-rootd"
        assert any(
            record.get("operation") == "root.exec" and record.get("status") == "accepted"
            for record in records
        )
        assert any(
            record.get("operation") == "root.exec"
            and record.get("status") in {"success", "command_failed"}
            for record in records
        )
        assert all(command not in line for line in lines)
    finally:
        server.close()
        thread.join(timeout=2)


def test_normal_terminal_command_remains_in_normal_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    config = _config(tmp_path)
    environment = _fake_environment(tmp_path)
    monkeypatch.setattr(terminal_module, "_get_env_config", lambda: config)
    monkeypatch.setattr(
        hafiye_execution_policy,
        "resolve_execution_policy",
        lambda config=None: "FULL_AUTONOMOUS",
    )
    monkeypatch.setattr(terminal_module, "_create_environment", lambda **kwargs: environment)
    monkeypatch.setattr(
        terminal_module,
        "_check_all_guards",
        lambda *args, **kwargs: {"approved": True},
    )
    monkeypatch.setattr(terminal_module, "_active_environments", {})
    monkeypatch.setattr(terminal_module, "_last_activity", {})

    result = json.loads(terminal_module.terminal_tool("printf normal", task_id="normal-test"))

    assert result["exit_code"] == 0
    assert "HAFIYE_NORMAL_OK" in result["output"]
    assert environment.commands == ["printf normal"]


def test_read_only_blocks_privileged_terminal_before_rootd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    config = _config(tmp_path)
    _FakeBroker.calls = []
    monkeypatch.setattr(terminal_module, "_get_env_config", lambda: config)
    monkeypatch.setattr(
        hafiye_execution_policy,
        "resolve_execution_policy",
        lambda config=None: "READ_ONLY",
    )
    monkeypatch.setattr(hafiye_rootd, "RootBrokerClient", _FakeBroker)

    result = json.loads(terminal_module.terminal_tool("sudo id", task_id="readonly-test"))

    assert result["status"] == "blocked"
    assert "READ_ONLY" in result["error"]
    assert _FakeBroker.calls == []


def test_confirmation_policy_requires_approval_before_rootd_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    config = _config(tmp_path)
    environment = _fake_environment(tmp_path)
    _FakeBroker.calls = []
    monkeypatch.setattr(terminal_module, "_get_env_config", lambda: config)
    monkeypatch.setattr(
        hafiye_execution_policy,
        "resolve_execution_policy",
        lambda config=None: "PRIVILEGED_CONFIRM",
    )
    monkeypatch.setattr(hafiye_rootd, "RootBrokerClient", _FakeBroker)
    monkeypatch.setattr(terminal_module, "_create_environment", lambda **kwargs: environment)
    monkeypatch.setattr(terminal_module, "_active_environments", {})
    monkeypatch.setattr(terminal_module, "_last_activity", {})
    monkeypatch.setattr(
        terminal_module,
        "_check_all_guards",
        lambda *args, **kwargs: {
            "approved": False,
            "status": "pending_approval",
            "command": "sudo id",
            "description": "Hafiye policy confirmation",
        },
    )

    pending = json.loads(terminal_module.terminal_tool("sudo id", task_id="confirm-pending"))
    assert pending["status"] == "pending_approval"
    assert _FakeBroker.calls == []
    assert environment.commands == []

    monkeypatch.setattr(
        terminal_module,
        "_check_all_guards",
        lambda *args, **kwargs: {"approved": True, "user_approved": True},
    )
    approved = json.loads(terminal_module.terminal_tool("sudo id", task_id="confirm-approved"))
    assert approved["privileged_via"] == "hafiye-rootd"
    assert approved["approval"]
    assert environment.commands == []
    assert _FakeBroker.calls[-1][0] == "sudo id"
