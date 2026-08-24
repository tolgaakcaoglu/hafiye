from __future__ import annotations

import json
import os
from pathlib import Path

from hermes_cli import voice_runtime


def test_voice_runtime_paths_use_hafiye_runtime_roots(tmp_path: Path):
    paths = voice_runtime.VoiceRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")

    assert paths.whisper_root == tmp_path / "data" / "runtimes" / "whisper.cpp"
    assert paths.whisper_source == paths.whisper_root / "source"
    assert paths.piper_root == tmp_path / "data" / "runtimes" / "piper"
    assert paths.piper_python == paths.piper_root / "venv" / "bin" / "python"


def test_managed_whisper_readiness_requires_binary_model_and_manifest(tmp_path: Path):
    paths = voice_runtime.VoiceRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")
    model = paths.whisper_models / "ggml-base.bin"
    binary = paths.whisper_root / "build-cpu" / "bin" / "whisper-cli"
    model.parent.mkdir(parents=True)
    binary.parent.mkdir(parents=True)
    model.write_bytes(b"model")
    binary.write_bytes(b"#!/bin/sh\n")
    os.chmod(binary, 0o700)
    paths.whisper_manifest.parent.mkdir(parents=True, exist_ok=True)
    paths.whisper_manifest.write_text(
        json.dumps(
            {
                "source_commit": "abc123",
                "compiled_backends": ["CPU"],
                "binaries": {"CPU": str(binary)},
                "models": {"base": str(model)},
            }
        )
    )

    assert voice_runtime.whisper_runtime_ready(paths=paths)


def test_piper_voice_listing_and_readiness_are_external_runtime_only(tmp_path: Path):
    paths = voice_runtime.VoiceRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")
    paths.piper_voices.mkdir(parents=True)
    (paths.piper_voices / "tr_TR-dfki-medium.onnx").write_bytes(b"onnx")
    (paths.piper_voices / "tr_TR-dfki-medium.onnx.json").write_text(
        json.dumps({"language": {"code": "tr_TR"}, "dataset": "dfki"})
    )
    paths.piper_python.parent.mkdir(parents=True)
    paths.piper_python.write_bytes(b"#!/bin/sh\n")
    os.chmod(paths.piper_python, 0o700)
    paths.piper_manifest.write_text(json.dumps({"package": "piper-tts", "voices": ["tr_TR-dfki-medium"]}))

    voices = voice_runtime.list_piper_voices(paths)

    assert voices == [
        {
            "dataset": "dfki",
            "language": "tr_TR",
            "name": "tr_TR-dfki-medium",
            "path": str(paths.piper_voices / "tr_TR-dfki-medium.onnx"),
        }
    ]
    assert voice_runtime.piper_runtime_ready(voice="tr_TR-dfki-medium", paths=paths)


def test_whisper_backend_fallback_order_uses_cuda_vulkan_cpu(monkeypatch):
    monkeypatch.setattr(
        voice_runtime,
        "choose_backend",
        lambda requested, *, environment, compiled: "CUDA",
    )

    assert voice_runtime._whisper_candidates(
        "AUTO",
        environment={"cuda_build_available": True},
        compiled=["CPU", "CUDA", "VULKAN"],
    ) == ["CUDA", "VULKAN", "CPU"]


def test_whisper_retries_final_backend_after_process_crash(tmp_path: Path, monkeypatch):
    paths = voice_runtime.VoiceRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")
    source = tmp_path / "input.wav"
    source.write_bytes(b"wav")
    model = paths.whisper_models / "ggml-base.bin"
    binary = paths.whisper_root / "build-cpu" / "bin" / "whisper-cli"
    model.parent.mkdir(parents=True)
    binary.parent.mkdir(parents=True)
    model.write_bytes(b"model")
    binary.write_bytes(b"#!/bin/sh\n")
    binary.chmod(0o700)
    paths.whisper_manifest.parent.mkdir(parents=True, exist_ok=True)
    paths.whisper_manifest.write_text(
        json.dumps(
            {
                "source_commit": "abc123",
                "compiled_backends": ["CPU"],
                "binaries": {"CPU": str(binary)},
                "models": {"base": str(model)},
            }
        )
    )
    attempts = []

    def fake_run(command, **kwargs):
        attempts.append(command)
        if len(attempts) == 2:
            output_base = Path(command[command.index("-of") + 1])
            output_base.with_suffix(".txt").write_text("merhaba dünya\n")
            return voice_runtime.subprocess.CompletedProcess(command, 0, "", "")
        return voice_runtime.subprocess.CompletedProcess(command, 139, "", "segmentation fault")

    monkeypatch.setattr(voice_runtime, "_run", fake_run)
    monkeypatch.setattr(
        voice_runtime,
        "detect_compute_environment",
        lambda: {"cuda_build_available": False, "vulkan_runtime_available": False},
    )

    result = voice_runtime.run_whisper_stt(
        source,
        tmp_path / "transcripts",
        paths=paths,
    )

    assert result["success"] is True
    assert result["backend"] == "CPU"
    assert len(attempts) == 2


def test_whisper_retries_last_available_backend_when_later_binary_is_missing(
    tmp_path: Path, monkeypatch
):
    paths = voice_runtime.VoiceRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")
    source = tmp_path / "input.wav"
    source.write_bytes(b"wav")
    model = paths.whisper_models / "ggml-base.bin"
    binary = paths.whisper_root / "build-vulkan" / "bin" / "whisper-cli"
    model.parent.mkdir(parents=True)
    binary.parent.mkdir(parents=True)
    model.write_bytes(b"model")
    binary.write_bytes(b"#!/bin/sh\n")
    binary.chmod(0o700)
    paths.whisper_manifest.parent.mkdir(parents=True, exist_ok=True)
    paths.whisper_manifest.write_text(
        json.dumps(
            {
                "source_commit": "abc123",
                "compiled_backends": ["VULKAN", "CPU"],
                "binaries": {"VULKAN": str(binary)},
                "models": {"base": str(model)},
            }
        )
    )
    attempts = []

    def fake_run(command, **kwargs):
        attempts.append(command)
        if len(attempts) == 2:
            output_base = Path(command[command.index("-of") + 1])
            output_base.with_suffix(".txt").write_text("merhaba dünya\n")
            return voice_runtime.subprocess.CompletedProcess(command, 0, "", "")
        return voice_runtime.subprocess.CompletedProcess(command, 139, "", "segmentation fault")

    monkeypatch.setattr(voice_runtime, "_run", fake_run)
    monkeypatch.setattr(
        voice_runtime,
        "detect_compute_environment",
        lambda: {"cuda_build_available": False, "vulkan_runtime_available": True},
    )

    result = voice_runtime.run_whisper_stt(
        source,
        tmp_path / "transcripts",
        backend="AUTO",
        paths=paths,
    )

    assert result["success"] is True
    assert result["backend"] == "VULKAN"
    assert len(attempts) == 2


def test_piper_retries_a_crashed_process_once(tmp_path: Path, monkeypatch):
    paths = voice_runtime.VoiceRuntimePaths.from_roots(tmp_path / "data", tmp_path / "state")
    paths.piper_python.parent.mkdir(parents=True)
    paths.piper_python.write_bytes(b"#!/bin/sh\n")
    paths.piper_python.chmod(0o700)
    monkeypatch.setattr(voice_runtime, "piper_runtime_ready", lambda **kwargs: True)
    attempts = []

    def fake_run(command, **kwargs):
        attempts.append(command)
        if len(attempts) == 2:
            output = Path(command[command.index("-f") + 1])
            output.write_bytes(b"RIFF-valid-enough")
            return voice_runtime.subprocess.CompletedProcess(command, 0, "", "")
        return voice_runtime.subprocess.CompletedProcess(command, 139, "", "piper crashed")

    monkeypatch.setattr(voice_runtime, "_run", fake_run)
    output = tmp_path / "speech.wav"

    result = voice_runtime.synthesize_piper(
        "Merhaba",
        output,
        {"piper": {"voice": "tr_TR-dfki-medium"}},
        paths=paths,
    )

    assert result == str(output)
    assert output.read_bytes() == b"RIFF-valid-enough"
    assert len(attempts) == 2
