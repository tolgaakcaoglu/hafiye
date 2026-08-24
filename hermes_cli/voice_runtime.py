"""Managed local whisper.cpp and Piper runtimes for Hafiye voice.

The voice engines deliberately live outside the Hafiye application
environment.  whisper.cpp is built as separate CPU/CUDA/Vulkan variants so
the fixed Hafiye backend policy can fall back deterministically.  Piper is
installed in its own virtual environment and is invoked as a subprocess; its
GPL package is therefore not imported into the Hermes process.

The public functions in this module are intentionally small integration
seams for the STT/TTS tools and the Desktop settings API.  The module is also
executable for setup and diagnostics::

    python -m hermes_cli.voice_runtime doctor
    python -m hermes_cli.voice_runtime install-whisper --backend AUTO
    python -m hermes_cli.voice_runtime install-piper --voice tr_TR-dfki-medium
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from hermes_constants import get_hafiye_data_home, get_hafiye_state_home
from hermes_cli.local_runtime import (
    BACKENDS,
    choose_backend,
    detect_compute_environment,
    normalize_backend,
)

logger = logging.getLogger(__name__)


WHISPER_REPOSITORY = "https://github.com/ggml-org/whisper.cpp.git"
PIPER_PACKAGE = "piper-tts"
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_WHISPER_LANGUAGE = "tr"
DEFAULT_PIPER_VOICE = "tr_TR-dfki-medium"
_MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class VoiceRuntimeError(RuntimeError):
    """An actionable managed voice-runtime failure."""


@dataclass(frozen=True)
class VoiceRuntimePaths:
    """XDG-compatible paths for the managed voice engines."""

    data_home: Path
    state_home: Path
    whisper_root: Path
    whisper_source: Path
    whisper_models: Path
    whisper_manifest: Path
    piper_root: Path
    piper_venv: Path
    piper_python: Path
    piper_voices: Path
    piper_manifest: Path

    @classmethod
    def from_roots(
        cls,
        data_home: Path | None = None,
        state_home: Path | None = None,
    ) -> "VoiceRuntimePaths":
        data = Path(data_home or get_hafiye_data_home()).expanduser()
        state = Path(state_home or get_hafiye_state_home()).expanduser()
        whisper_root = data / "runtimes" / "whisper.cpp"
        piper_root = data / "runtimes" / "piper"
        piper_venv = piper_root / "venv"
        piper_python = piper_venv / "bin" / "python"
        if os.name == "nt":
            piper_python = piper_venv / "Scripts" / "python.exe"
        return cls(
            data_home=data,
            state_home=state,
            whisper_root=whisper_root,
            whisper_source=whisper_root / "source",
            whisper_models=whisper_root / "models",
            whisper_manifest=whisper_root / "manifest.json",
            piper_root=piper_root,
            piper_venv=piper_venv,
            piper_python=piper_python,
            piper_voices=piper_root / "voices",
            piper_manifest=piper_root / "manifest.json",
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _ensure_private_dir(path.parent)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    os.replace(temporary, path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def _child_env() -> dict[str, str]:
    """Return a child environment without Hermes credentials."""
    try:
        from tools.environments.local import hermes_subprocess_env

        return hermes_subprocess_env(inherit_credentials=False)
    except Exception:  # pragma: no cover - only a defensive import fallback
        child = dict(os.environ)
        for name in list(child):
            if "KEY" in name or "TOKEN" in name or "PASSWORD" in name or "SECRET" in name:
                child.pop(name, None)
        return child


def _run(
    command: list[str],
    *,
    timeout: float,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    logger.info("voice runtime command: %s", " ".join(shlex.quote(item) for item in command))
    try:
        return subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            env=env or _child_env(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(command, 127, "", f"command not found: {command[0]}")
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(command, 124, "", f"timed out after {timeout}s: {exc}")


def _failure(label: str, result: subprocess.CompletedProcess[str]) -> VoiceRuntimeError:
    details = (result.stderr or result.stdout or "").strip()
    if len(details) > 4000:
        details = details[-4000:]
    try:
        from agent.redact import redact_sensitive_text

        details = redact_sensitive_text(details, force=True)
    except Exception:
        pass
    return VoiceRuntimeError(f"{label} failed (exit {result.returncode}): {details or 'no output'}")


def _safe_model(model: str | None) -> str:
    value = str(model or DEFAULT_WHISPER_MODEL).strip()
    if not _MODEL_RE.fullmatch(value):
        raise VoiceRuntimeError(f"Invalid whisper model name: {value!r}")
    return value


def _git_output(source: Path, *args: str) -> str:
    result = _run(["git", "-C", str(source), *args], timeout=60)
    if result.returncode != 0:
        raise _failure("git", result)
    return (result.stdout or "").strip()


def _ensure_whisper_checkout(paths: VoiceRuntimePaths, source_ref: str) -> str:
    source = paths.whisper_source
    _ensure_private_dir(paths.whisper_root)
    if not (source / ".git").is_dir():
        if source.exists():
            raise VoiceRuntimeError(f"Whisper source path is not a Git checkout: {source}")
        clone = _run(
            ["git", "clone", "--depth", "1", "--recurse-submodules", WHISPER_REPOSITORY, str(source)],
            timeout=900,
        )
        if clone.returncode != 0:
            raise _failure("whisper.cpp clone", clone)

    if source_ref and source_ref not in {"main", "master"}:
        fetch = _run(
            ["git", "-C", str(source), "fetch", "--depth", "1", "origin", source_ref],
            timeout=900,
        )
        if fetch.returncode != 0:
            raise _failure("whisper.cpp source fetch", fetch)
        checkout = _run(
            ["git", "-C", str(source), "checkout", "--detach", source_ref],
            timeout=120,
        )
        if checkout.returncode != 0:
            raise _failure("whisper.cpp source checkout", checkout)

    return _git_output(source, "rev-parse", "HEAD")


def _whisper_binary(build_dir: Path) -> Path | None:
    for candidate in (
        build_dir / "bin" / "whisper-cli",
        build_dir / "bin" / "Release" / "whisper-cli",
        build_dir / "whisper-cli",
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def _toolchain_has_vulkan_build_tools() -> bool:
    return all(shutil.which(tool) for tool in ("glslc", "spirv-opt"))


def _build_whisper_variant(paths: VoiceRuntimePaths, backend: str) -> Path:
    build_dir = paths.whisper_root / f"build-{backend.lower()}"
    cmake = [
        "cmake",
        "-S",
        str(paths.whisper_source),
        "-B",
        str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DWHISPER_BUILD_TESTS=OFF",
        "-DWHISPER_BUILD_EXAMPLES=ON",
        "-DWHISPER_BUILD_SERVER=OFF",
        "-DGGML_CUDA=ON" if backend == "CUDA" else "-DGGML_CUDA=OFF",
        "-DGGML_VULKAN=ON" if backend == "VULKAN" else "-DGGML_VULKAN=OFF",
    ]
    configured = _run(cmake, timeout=900)
    if configured.returncode != 0:
        raise _failure(f"whisper.cpp {backend} CMake configure", configured)

    jobs = str(max(1, min(os.cpu_count() or 1, 8)))
    built = _run(
        ["cmake", "--build", str(build_dir), "--config", "Release", "--target", "whisper-cli", "-j", jobs],
        timeout=1800,
    )
    if built.returncode != 0:
        raise _failure(f"whisper.cpp {backend} build", built)
    binary = _whisper_binary(build_dir)
    if binary is None:
        raise VoiceRuntimeError(f"whisper.cpp {backend} build completed without whisper-cli: {build_dir}")
    return binary


def _download_whisper_model(paths: VoiceRuntimePaths, model: str) -> Path:
    model = _safe_model(model)
    _ensure_private_dir(paths.whisper_models)
    model_path = paths.whisper_models / f"ggml-{model}.bin"
    if model_path.is_file() and model_path.stat().st_size > 0:
        return model_path
    script = paths.whisper_source / "models" / "download-ggml-model.sh"
    if not script.is_file():
        raise VoiceRuntimeError(f"whisper.cpp model download script is missing: {script}")
    result = _run(["sh", str(script), model, str(paths.whisper_models)], timeout=1800)
    if result.returncode != 0:
        raise _failure("whisper.cpp model download", result)
    if not model_path.is_file() or model_path.stat().st_size == 0:
        raise VoiceRuntimeError(f"whisper.cpp model download did not create {model_path}")
    return model_path


def install_whisper(
    *,
    backend: str = "AUTO",
    source_ref: str = "master",
    model: str = DEFAULT_WHISPER_MODEL,
    paths: VoiceRuntimePaths | None = None,
) -> dict[str, Any]:
    """Build whisper.cpp variants and install a multilingual GGML model."""
    paths = paths or VoiceRuntimePaths.from_roots()
    requested = normalize_backend(backend)
    environment = detect_compute_environment()
    if requested == "CUDA" and not environment.get("cuda_build_available"):
        raise VoiceRuntimeError("CUDA whisper.cpp build requested but CUDA toolkit/GPU is unavailable")
    if requested == "VULKAN" and (
        not environment.get("vulkan_build_available") or not _toolchain_has_vulkan_build_tools()
    ):
        raise VoiceRuntimeError("Vulkan whisper.cpp build requested but Vulkan development tools are unavailable")

    source_commit = _ensure_whisper_checkout(paths, source_ref)
    compile_backends: list[str] = ["CPU"]
    if requested == "CUDA" or (requested == "AUTO" and environment.get("cuda_build_available")):
        compile_backends.append("CUDA")
    if requested == "VULKAN" or (
        requested == "AUTO"
        and environment.get("vulkan_build_available")
        and _toolchain_has_vulkan_build_tools()
    ):
        compile_backends.append("VULKAN")

    binaries: dict[str, str] = {}
    for compiled_backend in compile_backends:
        binaries[compiled_backend] = str(_build_whisper_variant(paths, compiled_backend))

    model_path = _download_whisper_model(paths, model)
    selected = choose_backend(
        requested,
        environment=environment,
        compiled=compile_backends,
    )
    manifest = {
        "schema": 1,
        "engine": "whisper.cpp",
        "repository": WHISPER_REPOSITORY,
        "source_ref": source_ref,
        "source_commit": source_commit,
        "compiled_backends": compile_backends,
        "binaries": binaries,
        "models": {_safe_model(model): str(model_path)},
        "selected_backend": selected,
        "environment": environment,
        "updated_at": _now(),
    }
    _write_json(paths.whisper_manifest, manifest)
    return manifest


def _whisper_manifest(paths: VoiceRuntimePaths | None = None) -> dict[str, Any]:
    return _read_json((paths or VoiceRuntimePaths.from_roots()).whisper_manifest)


def whisper_runtime_ready(
    *,
    model: str = DEFAULT_WHISPER_MODEL,
    paths: VoiceRuntimePaths | None = None,
) -> bool:
    paths = paths or VoiceRuntimePaths.from_roots()
    manifest = _whisper_manifest(paths)
    models = manifest.get("models") if isinstance(manifest.get("models"), dict) else {}
    model_path = Path(str(models.get(_safe_model(model), "")))
    binaries = manifest.get("binaries") if isinstance(manifest.get("binaries"), dict) else {}
    return (
        bool(manifest.get("source_commit"))
        and model_path.is_file()
        and any(Path(str(path)).is_file() and os.access(str(path), os.X_OK) for path in binaries.values())
    )


def default_local_stt_command() -> str:
    """Return the Hermes command-hook template for managed whisper.cpp."""
    python = shlex.quote(sys.executable)
    return (
        f"{python} -m hermes_cli.voice_runtime stt"
        " --input {input_path} --output-dir {output_dir}"
        " --model {model} --language {language}"
    )


def _whisper_candidates(
    requested: str,
    *,
    environment: dict[str, Any],
    compiled: Iterable[str],
) -> list[str]:
    selected = choose_backend(requested, environment=environment, compiled=compiled)
    fallback_order = {
        "CUDA": ("VULKAN", "CPU"),
        "VULKAN": ("CPU",),
        "CPU": (),
    }
    available = {str(item).upper() for item in compiled}
    return [item for item in (selected, *fallback_order[selected]) if item in available]


def run_whisper_stt(
    input_path: str | Path,
    output_dir: str | Path,
    *,
    model: str = DEFAULT_WHISPER_MODEL,
    language: str = DEFAULT_WHISPER_LANGUAGE,
    backend: str = "AUTO",
    paths: VoiceRuntimePaths | None = None,
) -> dict[str, Any]:
    """Run whisper.cpp with CUDA → Vulkan → CPU fallback."""
    paths = paths or VoiceRuntimePaths.from_roots()
    model = _safe_model(model)
    manifest = _whisper_manifest(paths)
    compiled = [str(item).upper() for item in manifest.get("compiled_backends", [])]
    binaries = manifest.get("binaries") if isinstance(manifest.get("binaries"), dict) else {}
    models = manifest.get("models") if isinstance(manifest.get("models"), dict) else {}
    model_path = Path(str(models.get(model, "")))
    source = Path(input_path).expanduser()
    destination = Path(output_dir).expanduser()
    if not source.is_file():
        raise VoiceRuntimeError(f"STT input does not exist: {source}")
    if not model_path.is_file():
        raise VoiceRuntimeError(f"Whisper model is not installed: {model}")
    if not compiled:
        raise VoiceRuntimeError("whisper.cpp has no compiled backend manifest; run install-whisper")
    _ensure_private_dir(destination)

    environment = detect_compute_environment()
    candidates = _whisper_candidates(backend, environment=environment, compiled=compiled)
    available_indices = [
        index
        for index, candidate in enumerate(candidates)
        if Path(str(binaries.get(candidate, ""))).is_file()
        and os.access(str(binaries.get(candidate, "")), os.X_OK)
    ]
    failures: list[str] = []
    for candidate_index, candidate in enumerate(candidates):
        binary = Path(str(binaries.get(candidate, "")))
        if not binary.is_file() or not os.access(str(binary), os.X_OK):
            failures.append(f"{candidate}: binary missing")
            continue
        # Backend fallback is the first recovery path.  If CPU is the final
        # available backend, retry it once for a transient process crash; no
        # more than two subprocess attempts are ever made for one backend.
        attempts = 2 if available_indices and candidate_index == available_indices[-1] else 1
        for attempt in range(1, attempts + 1):
            target = destination / "transcript"
            target.with_suffix(".txt").unlink(missing_ok=True)
            command = [
                str(binary),
                "-m",
                str(model_path),
                "-f",
                str(source),
                "-otxt",
                "-of",
                str(target),
                "-l",
                str(language or DEFAULT_WHISPER_LANGUAGE),
                "-np",
            ]
            if candidate == "CPU":
                command.append("-ng")
            result = _run(command, timeout=600)
            transcript_path = target.with_suffix(".txt")
            if result.returncode == 0 and transcript_path.is_file():
                transcript = transcript_path.read_text(encoding="utf-8", errors="replace").strip()
                return {
                    "success": True,
                    "provider": "local_command",
                    "backend": candidate,
                    "model": model,
                    "language": language or DEFAULT_WHISPER_LANGUAGE,
                    "transcript": transcript,
                    "output_path": str(transcript_path),
                }
            detail = (result.stderr or result.stdout or "no transcript output").strip()
            try:
                from agent.redact import redact_sensitive_text

                detail = redact_sensitive_text(detail, force=True)
            except Exception:
                pass
            failures.append(f"{candidate} attempt {attempt}: {detail[-800:]}")

    raise VoiceRuntimeError("whisper.cpp STT failed across backends: " + " | ".join(failures))


def _piper_python(paths: VoiceRuntimePaths) -> Path:
    if not paths.piper_python.is_file() or not os.access(str(paths.piper_python), os.X_OK):
        raise VoiceRuntimeError(f"Managed Piper Python is missing: {paths.piper_python}")
    return paths.piper_python


def install_piper(
    *,
    voice: str = DEFAULT_PIPER_VOICE,
    python_executable: str | None = None,
    paths: VoiceRuntimePaths | None = None,
) -> dict[str, Any]:
    """Install Piper in its own venv and download one voice model."""
    paths = paths or VoiceRuntimePaths.from_roots()
    voice = str(voice or DEFAULT_PIPER_VOICE).strip()
    if not voice:
        raise VoiceRuntimeError("Piper voice cannot be empty")
    _ensure_private_dir(paths.piper_root)
    _ensure_private_dir(paths.piper_voices)

    if not paths.piper_python.is_file():
        creator = _run(
            [python_executable or sys.executable, "-m", "venv", str(paths.piper_venv)],
            timeout=300,
        )
        if creator.returncode != 0:
            raise _failure("Piper virtual environment creation", creator)

    python = _piper_python(paths)
    install = _run(
        [str(python), "-m", "pip", "install", "--upgrade", PIPER_PACKAGE],
        timeout=1800,
    )
    if install.returncode != 0:
        raise _failure("Piper package installation", install)

    download = _run(
        [str(python), "-m", "piper.download_voices", voice, "--data-dir", str(paths.piper_voices)],
        timeout=1800,
    )
    if download.returncode != 0:
        raise _failure("Piper voice download", download)
    model_path = paths.piper_voices / f"{voice}.onnx"
    metadata_path = paths.piper_voices / f"{voice}.onnx.json"
    if not model_path.is_file() or not metadata_path.is_file():
        raise VoiceRuntimeError(f"Piper voice download did not create {model_path}")

    version = _run([str(python), "-m", "pip", "show", PIPER_PACKAGE], timeout=30)
    package_version = ""
    for line in (version.stdout or "").splitlines():
        if line.lower().startswith("version:"):
            package_version = line.split(":", 1)[1].strip()
            break
    manifest = {
        "schema": 1,
        "engine": "piper",
        "package": PIPER_PACKAGE,
        "package_version": package_version,
        "python": str(python),
        "voices_dir": str(paths.piper_voices),
        "voices": [voice],
        "updated_at": _now(),
    }
    _write_json(paths.piper_manifest, manifest)
    return manifest


def _piper_manifest(paths: VoiceRuntimePaths | None = None) -> dict[str, Any]:
    return _read_json((paths or VoiceRuntimePaths.from_roots()).piper_manifest)


def piper_runtime_ready(
    *,
    voice: str = DEFAULT_PIPER_VOICE,
    paths: VoiceRuntimePaths | None = None,
) -> bool:
    paths = paths or VoiceRuntimePaths.from_roots()
    voice = str(voice or DEFAULT_PIPER_VOICE).strip()
    return (
        bool(_piper_manifest(paths).get("package"))
        and paths.piper_python.is_file()
        and (paths.piper_voices / f"{voice}.onnx").is_file()
        and (paths.piper_voices / f"{voice}.onnx.json").is_file()
    )


def _voice_metadata(path: Path) -> dict[str, Any]:
    metadata_path = path.with_name(path.name + ".json")
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    language = payload.get("language") if isinstance(payload, dict) else {}
    language = language if isinstance(language, dict) else {}
    return {
        "name": path.name.removesuffix(".onnx"),
        "path": str(path),
        "language": str(language.get("code") or language.get("family") or ""),
        "dataset": str(payload.get("dataset") or "") if isinstance(payload, dict) else "",
    }


def list_piper_voices(paths: VoiceRuntimePaths | None = None) -> list[dict[str, Any]]:
    paths = paths or VoiceRuntimePaths.from_roots()
    if not paths.piper_voices.is_dir():
        return []
    voices = []
    for model_path in sorted(paths.piper_voices.glob("*.onnx")):
        if (model_path.with_name(model_path.name + ".json")).is_file():
            voices.append(_voice_metadata(model_path))
    return voices


def synthesize_piper(
    text: str,
    output_path: str | Path,
    config: dict[str, Any] | None = None,
    *,
    paths: VoiceRuntimePaths | None = None,
) -> str:
    """Synthesize text by invoking the managed Piper process."""
    paths = paths or VoiceRuntimePaths.from_roots()
    piper_config = config.get("piper") if isinstance(config, dict) else {}
    piper_config = piper_config if isinstance(piper_config, dict) else {}
    voice = str(piper_config.get("voice") or DEFAULT_PIPER_VOICE).strip()
    if not piper_runtime_ready(voice=voice, paths=paths):
        raise VoiceRuntimeError(f"Managed Piper voice is not ready: {voice}")
    if not str(text or "").strip():
        raise VoiceRuntimeError("Piper text cannot be empty")

    python = _piper_python(paths)
    destination = Path(output_path).expanduser()
    _ensure_private_dir(destination.parent)
    wav_path = destination if destination.suffix.lower() == ".wav" else destination.with_suffix(".wav")
    command = [
        str(python),
        "-m",
        "piper",
        "--data-dir",
        str(paths.piper_voices),
        "-m",
        voice,
        "-f",
        str(wav_path),
    ]
    if piper_config.get("use_cuda"):
        command.append("--cuda")
    for option, key in (
        ("--length-scale", "length_scale"),
        ("--noise-scale", "noise_scale"),
        ("--noise-w-scale", "noise_w_scale"),
        ("--volume", "volume"),
    ):
        if key in piper_config:
            command.extend([option, str(piper_config[key])])
    if piper_config.get("normalize_audio") is False:
        command.append("--no-normalize")
    command.extend(["--", str(text)])
    failures: list[str] = []
    for attempt in range(1, 3):
        # A crashed Piper process can leave a zero-byte or partial WAV behind;
        # remove it before each bounded retry so stale output is never reported
        # as a successful synthesis.
        wav_path.unlink(missing_ok=True)
        if wav_path != destination:
            destination.unlink(missing_ok=True)
        result = _run(command, timeout=600)
        if result.returncode != 0:
            failures.append(str(_failure("Piper synthesis", result)))
            continue
        if not wav_path.is_file() or wav_path.stat().st_size == 0:
            failures.append(f"Piper attempt {attempt} completed without audio output")
            continue

        if wav_path != destination:
            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                raise VoiceRuntimeError("ffmpeg is required to convert Piper WAV output")
            converted = _run(
                [ffmpeg, "-y", "-loglevel", "error", "-i", str(wav_path), str(destination)],
                timeout=120,
            )
            if converted.returncode != 0:
                failures.append(str(_failure("Piper audio conversion", converted)))
                continue
            wav_path.unlink(missing_ok=True)
        return str(destination)

    raise VoiceRuntimeError(
        "Piper synthesis recovery exhausted after 2 bounded attempts: "
        + " | ".join(failures)
    )


def voice_runtime_doctor(paths: VoiceRuntimePaths | None = None) -> dict[str, Any]:
    """Return non-secret readiness details for both local voice engines."""
    paths = paths or VoiceRuntimePaths.from_roots()
    whisper = _whisper_manifest(paths)
    piper = _piper_manifest(paths)
    whisper_models = whisper.get("models") if isinstance(whisper.get("models"), dict) else {}
    whisper_binaries = whisper.get("binaries") if isinstance(whisper.get("binaries"), dict) else {}
    whisper_ready = whisper_runtime_ready(paths=paths)
    default_voice = str((piper.get("voices") or [DEFAULT_PIPER_VOICE])[0])
    piper_ready = piper_runtime_ready(voice=default_voice, paths=paths)
    environment = detect_compute_environment()
    compiled = [str(item).upper() for item in whisper.get("compiled_backends", [])]
    selected = None
    if compiled:
        try:
            selected = choose_backend("AUTO", environment=environment, compiled=compiled)
        except Exception:
            selected = None
    blockers: list[str] = []
    if not whisper_ready:
        blockers.append("managed whisper.cpp runtime/model is not ready")
    if not piper_ready:
        blockers.append("managed Piper runtime/Turkish voice is not ready")
    return {
        "ok": not blockers,
        "platform": platform.platform(),
        "whisper": {
            "ready": whisper_ready,
            "source_commit": whisper.get("source_commit", ""),
            "compiled_backends": compiled,
            "selected_auto_backend": selected,
            "binaries": whisper_binaries,
            "models": whisper_models,
        },
        "piper": {
            "ready": piper_ready,
            "package_version": piper.get("package_version", ""),
            "python": str(paths.piper_python),
            "voices": list_piper_voices(paths),
        },
        "environment": environment,
        "blockers": blockers,
        "warnings": [],
    }


def _json_print(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Hafiye local voice runtimes")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="Inspect managed voice runtime readiness")
    doctor.set_defaults(handler=lambda args: voice_runtime_doctor())

    install_whisper_parser = commands.add_parser("install-whisper", help="Build whisper.cpp and install a model")
    install_whisper_parser.add_argument("--backend", choices=BACKENDS, default="AUTO")
    install_whisper_parser.add_argument("--source-ref", default="master")
    install_whisper_parser.add_argument("--model", default=DEFAULT_WHISPER_MODEL)
    install_whisper_parser.set_defaults(
        handler=lambda args: install_whisper(backend=args.backend, source_ref=args.source_ref, model=args.model)
    )

    install_piper_parser = commands.add_parser("install-piper", help="Install Piper and download a voice")
    install_piper_parser.add_argument("--voice", default=DEFAULT_PIPER_VOICE)
    install_piper_parser.set_defaults(handler=lambda args: install_piper(voice=args.voice))

    voices = commands.add_parser("voices", help="List installed Piper voices")
    voices.set_defaults(handler=lambda args: {"voices": list_piper_voices()})

    stt = commands.add_parser("stt", help="Run the managed whisper.cpp STT hook")
    stt.add_argument("--input", required=True)
    stt.add_argument("--output-dir", required=True)
    stt.add_argument("--model", default=DEFAULT_WHISPER_MODEL)
    stt.add_argument("--language", default=DEFAULT_WHISPER_LANGUAGE)
    stt.add_argument("--backend", choices=BACKENDS, default="AUTO")
    stt.set_defaults(
        handler=lambda args: run_whisper_stt(
            args.input,
            args.output_dir,
            model=args.model,
            language=args.language,
            backend=args.backend,
        )
    )

    speak = commands.add_parser("piper-speak", help="Run managed Piper synthesis")
    speak.add_argument("--text", required=True)
    speak.add_argument("--output", required=True)
    speak.add_argument("--voice", default=DEFAULT_PIPER_VOICE)
    speak.set_defaults(
        handler=lambda args: synthesize_piper(
            args.text,
            args.output,
            {"piper": {"voice": args.voice, "runtime": "managed"}},
        )
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result = args.handler(args)
    except VoiceRuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _json_print(result)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by setup commands
    raise SystemExit(main())


__all__ = [
    "DEFAULT_PIPER_VOICE",
    "DEFAULT_WHISPER_LANGUAGE",
    "DEFAULT_WHISPER_MODEL",
    "VoiceRuntimeError",
    "VoiceRuntimePaths",
    "default_local_stt_command",
    "install_piper",
    "install_whisper",
    "list_piper_voices",
    "piper_runtime_ready",
    "run_whisper_stt",
    "synthesize_piper",
    "voice_runtime_doctor",
    "whisper_runtime_ready",
]
