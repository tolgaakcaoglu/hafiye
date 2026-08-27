"""P6 Hafiye routing and privacy policy behavior tests."""

from __future__ import annotations

import pytest

from hafiye_policy import (
    HafiyePolicyError,
    extract_task_override,
    filter_tool_definitions,
    enforce_runtime_policy,
    filter_fallback_chain,
    is_local_runtime,
    offline_tool_block_message,
    resolve_hafiye_route,
)


def _config(**overrides):
    config = {
        "model": {
            "default": "local-model",
            "provider": "custom",
            "base_url": "http://127.0.0.1:8080/v1",
        },
        "fallback_providers": [
            {"provider": "custom", "model": "local-fallback", "base_url": "http://127.0.0.1:8081/v1"},
            {"provider": "gemini", "model": "gemini-3.1-pro-preview"},
        ],
        "hafiye": {
            "privacy_mode": "NORMAL",
            "route_slots": {
                "default": {"provider": "custom", "model": "local-model"},
                "fast": {"provider": "custom", "model": "local-fast"},
                "reasoning": {"provider": "openrouter", "model": "remote-reasoner"},
                "coding": {"provider": "custom", "model": "local-coder"},
                "vision": {"provider": "custom", "model": "local-vision"},
                "long_context": {"provider": "custom", "model": "local-long"},
                "memory_aux": {"provider": "custom", "model": "local-memory"},
                "compression_aux": {"provider": "custom", "model": "local-compression"},
            },
            "task_overrides": {
                "remote": {"provider": "openrouter", "model": "remote-task"},
                "gemini": {"provider": "gemini", "model": "gemini-task"},
            },
        },
    }
    config.update(overrides)
    return config


def test_normal_local_task_uses_default_route():
    route = resolve_hafiye_route(_config(), task_text="Dosyayı yerel olarak incele")

    # "yerel" is a task-scoped LOCAL_ONLY request, while the selected runtime
    # remains the configured local route.
    assert route.provider == "custom"
    assert route.model == "local-model"
    assert route.privacy_mode == "LOCAL_ONLY"
    assert route.task_override == "mode:LOCAL_ONLY"


def test_local_only_route_resolves_named_custom_endpoint_over_remote_global_model():
    config = _config()
    config["model"] = {
        "default": "gemini-3.1-flash-lite",
        "provider": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
    }
    config["custom_providers"] = [
        {
            "name": "Local llama.cpp",
            "base_url": "http://127.0.0.1:11435/v1",
            "models": {
                "/home/tolga/.local/share/hafiye/models/qwen3-4b-q4_k_m.gguf": {}
            },
        }
    ]
    config["hafiye"]["privacy_mode"] = "LOCAL_ONLY"
    config["hafiye"]["route_slots"]["default"] = {
        "provider": "custom",
        "model": "qwen3-4b-q4_k_m",
    }

    route = resolve_hafiye_route(config)

    assert route.provider == "custom"
    assert route.model == "qwen3-4b-q4_k_m"
    assert route.privacy_mode == "LOCAL_ONLY"
    assert route.base_url == "http://127.0.0.1:11435/v1"
    assert route.as_dict()["base_url"] == "http://127.0.0.1:11435/v1"


def test_route_level_endpoint_is_used_for_selected_provider():
    config = _config()
    config["model"] = {
        "default": "gemini-3.1-flash-lite",
        "provider": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
    }
    config["hafiye"]["route_slots"]["default"] = {
        "provider": "custom",
        "model": "local-model",
        "base_url": "http://127.0.0.1:19001/v1",
    }

    route = resolve_hafiye_route(config)

    assert route.base_url == "http://127.0.0.1:19001/v1"


def test_explicit_remote_task_uses_configured_remote_override():
    route = resolve_hafiye_route(_config(), task_text="Bu görev için remote modeli kullan")

    assert route.provider == "openrouter"
    assert route.model == "remote-task"
    assert route.privacy_mode == "NORMAL"
    assert route.task_override == "remote"


def test_explicit_gemini_task_uses_gemini_override():
    route = resolve_hafiye_route(_config(), task_text="Gemini kullanarak yanıtla")

    assert route.provider == "gemini"
    assert route.model == "gemini-task"
    assert route.task_override == "gemini"


def test_task_slot_override_is_scoped_to_the_task():
    route = resolve_hafiye_route(_config(), task_text="hızlı cevap ver")

    assert route.slot == "fast"
    assert route.model == "local-fast"
    assert route.source == "config"


def test_explicit_provider_and_model_override_onboarding_default_slot():
    config = _config()

    route = resolve_hafiye_route(
        config,
        provider="gemini",
        model="gemini-explicit",
        explicit_overrides=True,
    )

    assert route.provider == "gemini"
    assert route.model == "gemini-explicit"
    assert route.source == "explicit"


def test_local_only_blocks_remote_route_even_when_requested_in_prompt():
    config = _config()
    config["hafiye"]["privacy_mode"] = "LOCAL_ONLY"

    with pytest.raises(HafiyePolicyError, match="forbids remote/cloud"):
        resolve_hafiye_route(config, task_text="Gemini kullan")


def test_offline_blocks_network_tools_but_keeps_local_tools():
    definitions = [
        {"type": "function", "function": {"name": "web_search"}},
        {"type": "function", "function": {"name": "browser_snapshot"}},
        {"type": "function", "function": {"name": "read_file"}},
        {"type": "function", "function": {"name": "terminal"}},
    ]

    filtered = filter_tool_definitions(definitions, "OFFLINE")
    names = {entry["function"]["name"] for entry in filtered}

    assert names == {"read_file", "terminal"}
    assert offline_tool_block_message("web_search")
    assert offline_tool_block_message("read_file") is None


def test_offline_blocks_unknown_mcp_network_surface():
    assert offline_tool_block_message("mcp_remote_fetch")
    assert offline_tool_block_message("tool_call")


def test_local_only_rejects_remote_runtime_and_accepts_loopback():
    with pytest.raises(HafiyePolicyError, match="blocked provider"):
        enforce_runtime_policy(
            "LOCAL_ONLY",
            provider="gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        )

    enforce_runtime_policy(
        "LOCAL_ONLY",
        provider="custom",
        base_url="http://127.0.0.1:8080/v1",
        model="local-model",
    )
    assert is_local_runtime("custom", "http://localhost:8080/v1")


def test_local_provider_alias_does_not_make_remote_url_local():
    assert not is_local_runtime("ollama", "https://ollama.com/v1")
    assert not is_local_runtime("llama.cpp", "https://remote.example/v1")
    assert is_local_runtime("ollama", "")


def test_local_privacy_keeps_only_legal_fallbacks():
    entries = [
        {"provider": "custom", "model": "local-fallback", "base_url": "http://127.0.0.1:8081/v1"},
        {"provider": "openrouter", "model": "remote-fallback"},
    ]

    legal = filter_fallback_chain(entries, "LOCAL_ONLY")
    assert [entry["provider"] for entry in legal] == ["custom"]


def test_slot_locality_policy_cannot_be_relaxed_by_task_normal_mode():
    config = _config()
    config["hafiye"]["route_slots"]["coding"]["locality_policy"] = "LOCAL_ONLY"

    route = resolve_hafiye_route(
        config,
        slot="coding",
        task_text="normal modda kod yaz",
    )

    assert route.privacy_mode == "LOCAL_ONLY"
    assert route.locality_policy == "LOCAL_ONLY"
