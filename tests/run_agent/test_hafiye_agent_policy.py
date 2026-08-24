"""Agent-boundary tests for the P6 privacy policy."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hafiye_policy import HafiyePolicyError
from run_agent import AIAgent


@pytest.fixture(autouse=True)
def _isolate_hermes_home(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    (tmp_path / ".env").write_text("", encoding="utf-8")


def _route(mode: str) -> dict:
    return {
        "slot": "default",
        "provider": "custom",
        "model": "local-model",
        "privacy_mode": mode,
        "source": "test",
        "fallback_providers": [
            {"provider": "custom", "model": "local-fallback", "base_url": "http://127.0.0.1:8081/v1"},
            {"provider": "gemini", "model": "gemini-3.1-pro-preview"},
        ],
    }


@patch("run_agent.OpenAI")
def test_offline_agent_removes_network_tools_and_keeps_local_tools(mock_openai):
    mock_openai.return_value = MagicMock()
    agent = AIAgent(
        api_key="no-key-required",
        base_url="http://127.0.0.1:8080/v1",
        provider="custom",
        model="local-model",
        enabled_toolsets=["web", "file", "terminal"],
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
        hafiye_privacy_mode="OFFLINE",
        hafiye_route=_route("OFFLINE"),
    )

    names = set(agent.valid_tool_names)
    assert "web_search" not in names
    assert "read_file" in names
    assert "terminal" in names
    assert agent.hafiye_privacy_mode == "OFFLINE"

    agent.close()


@patch("run_agent.OpenAI")
def test_local_only_agent_rejects_remote_provider_before_client_use(mock_openai):
    with pytest.raises(HafiyePolicyError, match="blocked provider"):
        AIAgent(
            api_key="test-key",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            provider="gemini",
            model="gemini-3.1-pro-preview",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            hafiye_privacy_mode="LOCAL_ONLY",
            hafiye_route={
                "slot": "default",
                "privacy_mode": "LOCAL_ONLY",
                "provider": "gemini",
                "model": "gemini-3.1-pro-preview",
            },
        )

    mock_openai.assert_not_called()


@patch("run_agent.OpenAI")
def test_normal_agent_allows_explicit_remote_provider(mock_openai):
    mock_openai.return_value = MagicMock()
    agent = AIAgent(
        api_key="test-key",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        provider="gemini",
        model="gemini-3.1-pro-preview",
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
        hafiye_privacy_mode="NORMAL",
        hafiye_route={
            "slot": "default",
            "privacy_mode": "NORMAL",
            "provider": "gemini",
            "model": "gemini-3.1-pro-preview",
        },
    )

    assert agent.hafiye_privacy_mode == "NORMAL"
    agent.close()


@patch("run_agent.OpenAI")
def test_local_only_fallback_chain_excludes_remote_before_activation(mock_openai):
    mock_openai.return_value = MagicMock()
    agent = AIAgent(
        api_key="no-key-required",
        base_url="http://127.0.0.1:8080/v1",
        provider="custom",
        model="local-model",
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
        fallback_model=[
            {"provider": "custom", "model": "local-fallback", "base_url": "http://127.0.0.1:8081/v1"},
            {"provider": "gemini", "model": "gemini-3.1-pro-preview"},
        ],
        hafiye_privacy_mode="LOCAL_ONLY",
        hafiye_route=_route("LOCAL_ONLY"),
    )

    assert [entry["provider"] for entry in agent._fallback_chain] == ["custom"]
    with patch(
        "agent.auxiliary_client.resolve_provider_client",
        return_value=(MagicMock(), "local-fallback"),
    ) as resolve_client:
        assert agent._try_activate_fallback() is True

    assert resolve_client.call_args.args[0] == "custom"
    assert agent.provider == "custom"
    agent.close()
