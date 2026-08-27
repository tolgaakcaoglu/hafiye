from agent.local_model_compat import apply_local_qwen3_no_think, is_local_qwen3_route


def test_local_qwen3_route_is_narrow_and_endpoint_aware():
    assert is_local_qwen3_route(
        provider="custom",
        base_url="http://127.0.0.1:11435/v1",
        model="qwen3-4b-q4_k_m",
    )
    assert not is_local_qwen3_route(
        provider="gemini",
        base_url="http://127.0.0.1:11435/v1",
        model="qwen3-4b-q4_k_m",
    )
    assert not is_local_qwen3_route(
        provider="custom",
        base_url="https://llm.example.com/v1",
        model="qwen3-4b-q4_k_m",
    )
    assert not is_local_qwen3_route(
        provider="custom",
        base_url="http://127.0.0.1:11435/v1",
        model="gemma-3-270m-it-q8",
    )


def test_local_qwen3_no_think_prefix_is_idempotent_and_preserves_controls():
    assert apply_local_qwen3_no_think("Terminali aç") == "/no_think\nTerminali aç"
    assert apply_local_qwen3_no_think("/no_think\nTerminali aç") == "/no_think\nTerminali aç"
    assert apply_local_qwen3_no_think("/think\nDerin düşün") == "/think\nDerin düşün"
    assert apply_local_qwen3_no_think([{"type": "text", "text": "Terminali aç"}]) == [
        {"type": "text", "text": "Terminali aç"}
    ]


def test_route_resolution_recovers_named_provider_from_gguf_catalog(monkeypatch):
    from hermes_cli import runtime_provider as runtime

    monkeypatch.setattr(
        runtime,
        "load_config",
        lambda: {
            "custom_providers": [
                {
                    "name": "Local llama.cpp",
                    "base_url": "http://127.0.0.1:11435/v1",
                    "model": "gemma-3-270m-it-q8",
                    "models": {"/home/tolga/.local/share/hafiye/models/qwen3-4b-q4_k_m.gguf": {}},
                }
            ]
        },
    )
    monkeypatch.setattr(runtime, "_try_resolve_from_custom_pool", lambda *args, **kwargs: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    resolved = runtime.resolve_runtime_provider(
        requested="custom", target_model="qwen3-4b-q4_k_m"
    )

    assert resolved["provider"] == "custom"
    assert resolved["base_url"] == "http://127.0.0.1:11435/v1"
    assert resolved["api_key"] == "no-key-required"
    assert resolved["source"] == "custom_provider:Local llama.cpp"
