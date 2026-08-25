from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from hermes_cli import local_runtime
from hermes_cli.local_runtime import LocalRuntimeError, LocalRuntimeManager, RuntimePaths, choose_backend


def test_runtime_paths_use_separate_xdg_data_and_state_roots(tmp_path: Path):
    paths = RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")

    assert paths.models == tmp_path / "data" / "models"
    assert paths.runtime == tmp_path / "data" / "runtimes" / "llama.cpp"
    assert paths.registry == tmp_path / "state" / "local-runtime" / "models.json"
    assert paths.server_log == tmp_path / "state" / "local-runtime" / "llama-server.log"


def test_auto_backend_uses_cuda_then_vulkan_then_cpu():
    cuda_host = {"cuda_build_available": True, "vulkan_runtime_available": True}
    assert choose_backend("AUTO", environment=cuda_host, compiled=["CPU", "CUDA", "VULKAN"]) == "CUDA"

    vulkan_host = {"cuda_build_available": False, "vulkan_runtime_available": True}
    assert choose_backend("AUTO", environment=vulkan_host, compiled=["CPU", "VULKAN"]) == "VULKAN"

    cpu_host = {"cuda_build_available": False, "vulkan_runtime_available": False}
    assert choose_backend("AUTO", environment=cpu_host, compiled=["CPU"]) == "CPU"

    with pytest.raises(LocalRuntimeError, match="CUDA"):
        choose_backend("CUDA", environment=cpu_host, compiled=["CPU"])


def test_qwen2_context_extension_is_explicit_and_narrow():
    qwen_args = local_runtime._context_compatibility_args(
        "qwen2.5-0.5b-instruct-q4",
        Path("qwen2.5-0.5b-instruct-q4.gguf"),
        65536,
    )
    assert qwen_args == [
        "--rope-scaling",
        "yarn",
        "--yarn-orig-ctx",
        "32768",
        "--override-kv",
        "qwen2.context_length=int:65536",
    ]
    assert local_runtime._context_compatibility_args(
        "qwen2.5-0.5b-instruct-q4",
        Path("qwen2.5-0.5b-instruct-q4.gguf"),
        32768,
    ) == []
    assert local_runtime._context_compatibility_args(
        "llama-3.2-1b-instruct-q4",
        Path("llama-3.2-1b-instruct-q4.gguf"),
        65536,
    ) == []


def test_qwen3_uses_embedded_jinja_and_reasoning_parser():
    assert local_runtime._chat_template_args(
        "qwen3-14b-q4_k_m",
        Path("Qwen3-14B-Q4_K_M.gguf"),
    ) == ["--jinja", "--reasoning-format", "deepseek"]
    assert local_runtime._chat_template_args(
        "qwen2.5-0.5b-instruct-q4",
        Path("qwen2.5-0.5b-instruct-q4.gguf"),
    ) == []


def test_qwen3_large_context_uses_yarn_override_and_cpu_kv():
    model_path = Path("Qwen3-14B-Q4_K_M.gguf")
    assert local_runtime._context_compatibility_args(
        "qwen3-14b-q4_k_m", model_path, 65536
    ) == [
        "--rope-scaling",
        "yarn",
        "--rope-scale",
        "1.6",
        "--yarn-orig-ctx",
        "40960",
        "--override-kv",
        "qwen3.context_length=int:65536",
    ]
    assert local_runtime._context_compatibility_args(
        "qwen3-14b-q4_k_m", model_path, 40960
    ) == []
    assert local_runtime._memory_compatibility_args(
        "qwen3-14b-q4_k_m", model_path, 65536, "CUDA"
    ) == ["--no-kv-offload"]
    assert local_runtime._memory_compatibility_args(
        "qwen3-14b-q4_k_m", model_path, 65536, "CPU"
    ) == []
    assert local_runtime._default_gpu_layers(
        "qwen3-14b-q4_k_m", model_path, "CUDA"
    ) == "auto"


def test_local_model_registry_exposes_evidence_backed_capability_state(tmp_path: Path):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    qwen2_source = tmp_path / "qwen2.5-0.5b-instruct-q4.gguf"
    qwen3_source = tmp_path / "qwen3-14b-q4_k_m.gguf"
    qwen2_source.write_bytes(b"qwen2-validation-fixture")
    qwen3_source.write_bytes(b"qwen3-agent-fixture")

    qwen2 = manager.import_model(qwen2_source, "qwen2.5-0.5b-instruct-q4")
    qwen3 = manager.import_model(qwen3_source, "qwen3-14b-q4_k_m")

    assert qwen2["capabilities"] == {
        "validation": True,
        "agent": False,
        "tool_calling": False,
        "resource_warning": None,
    }
    assert qwen3["capabilities"] == {
        "validation": False,
        "agent": True,
        "tool_calling": True,
        "resource_warning": "KI-046",
    }
    persisted = json.loads(manager.paths.registry.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in persisted["models"]}
    assert by_id["qwen2.5-0.5b-instruct-q4"]["capabilities"]["agent"] is False
    assert by_id["qwen3-14b-q4_k_m"]["capabilities"]["agent"] is True


def test_unknown_local_model_stays_unqualified(tmp_path: Path):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    source = tmp_path / "unknown.gguf"
    source.write_bytes(b"unknown-fixture")

    item = manager.import_model(source, "unknown")

    assert "capabilities" not in item
    assert local_runtime.model_capabilities("unknown") == {}


def test_import_model_is_checksum_registered_and_private(tmp_path: Path):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    source = tmp_path / "tiny.gguf"
    source.write_bytes(b"GGUF-test-payload")

    item = manager.import_model(source, "tiny")

    assert item["id"] == "tiny"
    assert item["size"] == source.stat().st_size
    assert item["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert Path(item["path"]).read_bytes() == source.read_bytes()
    assert (manager.paths.models / "tiny.gguf").stat().st_mode & 0o077 == 0
    assert manager.models()[0]["available"] is True
    assert json.loads(manager.paths.registry.read_text()) ["models"][0]["id"] == "tiny"


def test_import_rejects_conflicting_model_id(tmp_path: Path):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    first = tmp_path / "first.gguf"
    second = tmp_path / "second.gguf"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    manager.import_model(first, "same")

    with pytest.raises(LocalRuntimeError, match="already exists"):
        manager.import_model(second, "same")


def test_download_uses_partial_file_and_registers_checksum(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    destination = manager.paths.models / "downloaded.gguf"
    destination.parent.mkdir(parents=True)
    partial = destination.with_name(destination.name + ".part")
    partial.write_bytes(b"prefix-")

    class Response:
        status = 206

        def read(self, _size: int) -> bytes:
            if not hasattr(self, "done"):
                self.done = True
                return b"suffix"
            return b""

        def close(self) -> None:
            return None

    captured = {}

    def fake_urlopen(request, timeout=0):
        captured["range"] = request.headers.get("Range")
        return Response()

    monkeypatch.setattr(local_runtime.urllib.request, "urlopen", fake_urlopen)
    item = manager.download_model("owner/repo", "downloaded.gguf", model_id="downloaded")

    assert captured["range"] == "bytes=7-"
    assert Path(item["path"]).read_bytes() == b"prefix-suffix"
    assert item["source"] == "huggingface"
    assert item["source_url"].endswith("/owner/repo/resolve/main/downloaded.gguf")
    assert item["revision"] == "main"
    assert not partial.exists()


def test_server_health_is_safe_when_not_running(tmp_path: Path):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    health = manager.health()

    assert health["running"] is False
    assert health["ready"] is False
    assert health["endpoint"] == "http://127.0.0.1:11435/v1"


def test_server_recovery_reuses_saved_state_and_is_bounded(tmp_path: Path, monkeypatch):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))
    manager._write_server_state(
        {
            "pid": 999999,
            "model_id": "saved-model",
            "requested_backend": "CUDA",
            "context_size": 8192,
            "gpu_layers": 99,
            "port": 12345,
        }
    )
    calls = []

    def fake_start(model_id, **kwargs):
        calls.append((model_id, kwargs))
        return {"running": True, "ready": True, "model_id": model_id}

    monkeypatch.setattr(manager, "start_server", fake_start)

    result = manager.recover_server(max_attempts=2)

    assert result["ok"] is True
    assert result["recovered"] is True
    assert calls == [
        (
            "saved-model",
            {
                "backend": "CUDA",
                "context_size": 8192,
                "gpu_layers": 99,
                "port": 12345,
            },
        )
    ]


def test_server_recovery_does_not_guess_when_state_is_missing(tmp_path: Path):
    manager = LocalRuntimeManager(RuntimePaths.from_roots(tmp_path / "data", tmp_path / "state"))

    result = manager.recover_server()

    assert result["ok"] is False
    assert result["code"] == "runtime_recovery_state_missing"
    assert result["attempts"] == []
