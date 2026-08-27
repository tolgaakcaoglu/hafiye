"""Gateway integration checks for the P6 task route boundary."""

from __future__ import annotations

from pathlib import Path

from gateway.run import GatewayRunner


def _config() -> dict:
    return {
        "model": {
            "default": "local-model",
            "provider": "custom",
            "base_url": "http://127.0.0.1:8080/v1",
        },
        "hafiye": {
            "privacy_mode": "NORMAL",
            "route_slots": {
                "default": {"provider": "custom", "model": "local-model"},
                "fast": {"provider": "custom", "model": "local-fast"},
            },
            "task_overrides": {
                "remote": {"provider": "openrouter", "model": "remote-task"},
                "gemini": {"provider": "gemini", "model": "gemini-task"},
            },
        },
    }


def _runtime(provider: str = "custom", base_url: str = "http://127.0.0.1:8080/v1") -> dict:
    return {
        "provider": provider,
        "requested_provider": provider,
        "base_url": base_url,
        "api_key": "test-key",
        "api_mode": "chat_completions",
        "command": None,
        "args": [],
        "credential_pool": None,
        "max_tokens": None,
    }


def test_gateway_reads_normal_hafiye_config_from_xdg_config_root(tmp_path, monkeypatch):
    """Native gateway route resolution shares the Hafiye CLI config root."""
    config_home = tmp_path / "config"
    config_home.mkdir()
    (config_home / "hafiye").mkdir()
    (config_home / "hafiye" / "config.yaml").write_text(
        """model:
  default: local-model
  provider: custom
hafiye:
  route_slots:
    default:
      provider: gemini
      model: gemini-flash-lite-latest
""",
        encoding="utf-8",
    )
    monkeypatch.delenv("HERMES_HOME", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

    import gateway.run as gateway_run
    from hermes_constants import get_hermes_home

    monkeypatch.setattr(gateway_run, "_hermes_home", get_hermes_home())

    loaded = gateway_run._load_gateway_config()

    assert loaded["hafiye"]["route_slots"]["default"]["provider"] == "gemini"
    assert gateway_run._gateway_config_home() == Path(config_home) / "hafiye"


def test_native_gateway_resolves_task_route_before_agent_creation(monkeypatch):
    monkeypatch.setattr("gateway.run._load_gateway_config", _config)

    def resolve_runtime_provider(*, requested=None, target_model=None, **_kwargs):
        if requested == "openrouter":
            return _runtime("openrouter", "https://openrouter.ai/api/v1")
        return _runtime(requested or "custom")

    monkeypatch.setattr(
        "hermes_cli.runtime_provider.resolve_runtime_provider",
        resolve_runtime_provider,
    )

    runner = object.__new__(GatewayRunner)
    runner._service_tier = None

    fast = runner._resolve_turn_agent_config(
        "hızlı cevap ver",
        "local-model",
        _runtime(),
    )
    assert fast["model"] == "local-fast"
    assert fast["hafiye_route_slot"] == "fast"
    assert fast["hafiye_privacy_mode"] == "NORMAL"

    remote = runner._resolve_turn_agent_config(
        "Bu görevde remote modeli kullan",
        "local-model",
        _runtime(),
    )
    assert remote["model"] == "remote-task"
    assert remote["runtime"]["provider"] == "openrouter"
    assert remote["hafiye_route"]["task_override"] == "remote"


def test_native_gateway_rejects_remote_task_under_local_only(monkeypatch):
    config = _config()
    config["hafiye"]["privacy_mode"] = "LOCAL_ONLY"
    monkeypatch.setattr("gateway.run._load_gateway_config", lambda: config)

    runner = object.__new__(GatewayRunner)
    runner._service_tier = None

    try:
        runner._resolve_turn_agent_config(
            "Gemini kullan",
            "local-model",
            _runtime(),
        )
    except RuntimeError as exc:
        assert "forbids remote/cloud" in str(exc)
    else:
        raise AssertionError("LOCAL_ONLY must reject a Gemini task before agent creation")


def test_native_gateway_passes_route_endpoint_when_global_url_is_stale(monkeypatch):
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
            "models": {"local-model": {}},
        }
    ]
    config["hafiye"]["route_slots"]["default"] = {
        "provider": "custom",
        "model": "local-model",
    }
    monkeypatch.setattr("gateway.run._load_gateway_config", lambda: config)

    calls = []

    def resolve_runtime_provider(*, requested=None, target_model=None, **kwargs):
        calls.append((requested, target_model, kwargs.get("explicit_base_url")))
        if requested == "custom":
            return _runtime("custom", "http://127.0.0.1:11435/v1")
        return _runtime(requested or "gemini", "https://generativelanguage.googleapis.com/v1beta")

    monkeypatch.setattr(
        "hermes_cli.runtime_provider.resolve_runtime_provider",
        resolve_runtime_provider,
    )

    runner = object.__new__(GatewayRunner)
    runner._service_tier = None
    result = runner._resolve_turn_agent_config(
        "yerel görev",
        "gemini-3.1-flash-lite",
        _runtime("gemini", "https://generativelanguage.googleapis.com/v1beta"),
    )

    assert result["model"] == "local-model"
    assert result["runtime"]["provider"] == "custom"
    assert calls[-1] == ("custom", "local-model", "http://127.0.0.1:11435/v1")
