"""Unit tests for Hafiye's managed computer-use-linux boundary."""

import json
import subprocess
from unittest.mock import patch

import hafiye_computer_use as computer_use


def _doctor_payload(**overrides):
    readiness = {
        "can_register_mcp_tools": True,
        "can_build_accessibility_tree": True,
        "can_send_development_input": True,
        "can_query_windows": True,
        **overrides,
    }
    return {"readiness": readiness, "checks": []}


def test_run_doctor_exposes_stable_readiness_contract(monkeypatch):
    payload = _doctor_payload()
    monkeypatch.setattr(
        computer_use,
        "_run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args, 0, json.dumps(payload), ""
        ),
    )

    result = computer_use.run_doctor("/tmp/computer-use-linux")

    assert result["ok"] is True
    assert result["binary"] == "/tmp/computer-use-linux"
    assert result["blockers"] == []
    assert result["readiness"] == {
        "can_register_mcp_tools": True,
        "can_build_accessibility_tree": True,
        "can_send_development_input": True,
        "can_query_windows": True,
    }


def test_run_doctor_fails_when_required_readiness_is_false(monkeypatch):
    payload = _doctor_payload(can_query_windows=False)
    monkeypatch.setattr(
        computer_use,
        "_run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args, 0, json.dumps(payload), ""
        ),
    )

    result = computer_use.run_doctor("/tmp/computer-use-linux")

    assert result["ok"] is False
    assert result["readiness"]["can_query_windows"] is False


def test_managed_mcp_config_is_pinned_and_does_not_require_user_config(monkeypatch):
    monkeypatch.setattr(computer_use, "resolve_computer_use_linux_binary", lambda: "/opt/computer-use-linux")
    monkeypatch.setattr(computer_use.sys, "platform", "linux")
    monkeypatch.setattr(computer_use, "_desktop_env", lambda: {"WAYLAND_DISPLAY": "wayland-0"})

    config = computer_use.managed_mcp_server_config()

    assert config == {
        "command": "/opt/computer-use-linux",
        "args": ["mcp"],
        "env": {"WAYLAND_DISPLAY": "wayland-0"},
        "timeout": 120,
        "connect_timeout": 30,
        "enabled": True,
        "managed": True,
        "built_in": True,
        "source_commit": computer_use.COMPUTER_USE_LINUX_SOURCE_COMMIT,
    }


def test_missing_binary_is_a_blocker(monkeypatch):
    monkeypatch.setattr(computer_use, "resolve_computer_use_linux_binary", lambda: None)

    result = computer_use.run_doctor()

    assert result["ok"] is False
    assert result["readiness"] == {key: False for key in computer_use._REQUIRED_READINESS}
    assert result["blockers"] == ["computer-use-linux binary is not installed"]


def test_mcp_config_injects_managed_server_without_editing_user_config(monkeypatch):
    managed = {"command": "/opt/computer-use-linux", "args": ["mcp"]}
    monkeypatch.setattr(computer_use, "managed_mcp_server_config", lambda: managed)
    monkeypatch.setattr(computer_use, "COMPUTER_USE_LINUX_MCP_SERVER", "hafiye-computer-use-linux")

    with patch("hermes_cli.config.load_config", return_value={"mcp_servers": {}}):
        from tools.mcp_tool import _load_mcp_config

        result = _load_mcp_config()

    assert result["hafiye-computer-use-linux"] == managed


def test_computer_use_failure_contract_classifies_readiness_and_redacts():
    result = computer_use.classify_computer_use_failure(
        json.dumps({"error": "AT-SPI readiness failed for sk-hafiye-secret-012345678901234567890"})
    )

    assert result["ok"] is False
    assert result["code"] == "accessibility_unavailable"
    assert result["retryable"] is False
    assert result["blocker"] is True
    assert "sk-hafiye-secret" not in result["detail"]
