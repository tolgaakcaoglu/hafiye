"""Managed Hafiye llama.cpp runtime and local GGUF model lifecycle.

This module is deliberately independent of the Hermes model-provider registry.
It owns the filesystem and process boundary for the local OpenAI-compatible
llama-server.  Provider wiring can therefore use the same loopback endpoint
from the CLI, Desktop, and the persistent gateway without making the agent
process responsible for downloading or supervising a model server.

The implementation follows the current llama.cpp server command line:
``llama-server --model ... --host ... --port ...``.  A runtime manifest records
the exact source commit and the backends that were actually compiled; a
requested backend is never reported as available merely because a GPU exists.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import psutil

from hermes_constants import get_hafiye_data_home, get_hafiye_state_home


LLAMA_REPOSITORY = "https://github.com/ggml-org/llama.cpp.git"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11435
DEFAULT_CONTEXT_SIZE = 4096
BACKENDS = ("AUTO", "CUDA", "VULKAN", "CPU")
GPU_BACKENDS = ("CUDA", "VULKAN")
MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
GGUF_SUFFIX = ".gguf"

# Hafiye's production model catalog is backend-owned so every Desktop surface
# sees the same pinned, integrity-checked choices. Catalog membership does not
# imply agent qualification or make a model the active/default route.
CURATED_LOCAL_MODEL_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "qwen3.8-27b-ud-iq1_s",
        "name": "Qwen3.8 27B UD-IQ1_S",
        "repo_id": "unsloth/Qwen3.8-27B-GGUF",
        "filename": "Qwen3.8-27B-UD-IQ1_S.gguf",
        "revision": "4ca720788d1e01f1bff70c033e0d0028fd02e502",
        "sha256": "3895b6eaa91e705c06ad1938d16c22e86f073c6a67df86260a1da79be3d1f887",
        "size": 6_192_222_208,
        "license": "Apache-2.0",
        "source_url": (
            "https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/blob/"
            "4ca720788d1e01f1bff70c033e0d0028fd02e502/"
            "Qwen3.8-27B-UD-IQ1_S.gguf"
        ),
        "featured": True,
        "qualification": "pending",
        "resource_warning": (
            "Agent qualification is pending; downloading this catalog model "
            "does not make it Hafiye's default route."
        ),
        "source_type": "huggingface",
        "requires_auth": False,
        "intended_use": "General local-agent qualification candidate",
        "download_files": (
            {
                "filename": "Qwen3.8-27B-UD-IQ1_S.gguf",
                "url": (
                    "https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/"
                    "4ca720788d1e01f1bff70c033e0d0028fd02e502/"
                    "Qwen3.8-27B-UD-IQ1_S.gguf"
                ),
                "sha256": "3895b6eaa91e705c06ad1938d16c22e86f073c6a67df86260a1da79be3d1f887",
                "size": 6_192_222_208,
            },
        ),
    },
    {
        "id": "qwen3.8-27b-uncensored-q4_k_m",
        "name": "Qwen3.8 27B Uncensored Q4_K_M",
        "repo_id": "orcarouter/Qwen3.8-27B-Uncensored",
        "filename": "Qwen3.8-27B-Uncensored-Q4_K_M.gguf",
        "revision": "q4_K_M@sha256:6fac2f98fdf7",
        "sha256": "3445102e9cde5d562508642c100a2f5ac3368a5a3f748442811d7a95daee3bec",
        "size": 16_810_714_496,
        "license": "Apache-2.0",
        "source_url": "https://ollama.com/orcarouter/Qwen3.8-27B-Uncensored%3Aq4_K_M",
        "featured": False,
        "qualification": "pending",
        "resource_warning": (
            "Uncensored model; Hafiye host, privilege, privacy, and emergency "
            "boundaries remain mandatory. The 15.7 GiB GGUF exceeds this "
            "host's 10 GiB VRAM and practical qualification envelope, so it "
            "is not a default route. Agent qualification is pending. The "
            "separate Ollama vision projector is not imported."
        ),
        "source_type": "ollama",
        "requires_auth": False,
        "intended_use": "Uncensored local model evaluation",
        "download_files": (
            {
                "filename": "Qwen3.8-27B-Uncensored-Q4_K_M.gguf",
                "url": (
                    "https://registry.ollama.ai/v2/orcarouter/"
                    "Qwen3.8-27B-Uncensored/blobs/sha256:"
                    "3445102e9cde5d562508642c100a2f5ac3368a5a3f748442811d7a95daee3bec"
                ),
                "sha256": "3445102e9cde5d562508642c100a2f5ac3368a5a3f748442811d7a95daee3bec",
                "size": 16_810_714_496,
            },
        ),
    },
    {
        "id": "qwen3.8-flash-next-uncensored-iq2_m",
        "name": "Qwen3.8 Flash Next Uncensored IQ2_M",
        "repo_id": "orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF",
        "filename": "Qwen3.8-Flash-Next-Uncensored-IQ2_M-00001-of-00002.gguf",
        "revision": "3da364f04d1e0161cae12db000399e0a91a9466f",
        "sha256": "4ba8d9bbe1e7439d6f1856998074df10fac97294320fa74b45c795d2fb6f4004",
        "size": 80_086_292_992,
        "license": "Apache-2.0",
        "source_url": "https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF",
        "featured": False,
        "qualification": "pending",
        "resource_warning": (
            "Security-research model for red teams and blue teams. Requires "
            "Hugging Face access approval and HF_TOKEN. The 74.6 GiB IQ2_M "
            "weights exceed this host's practical qualification envelope and "
            "are not a default route."
        ),
        "source_type": "huggingface",
        "requires_auth": True,
        "intended_use": "Security researchers, red teams, and blue teams",
        "download_files": (
            {
                "filename": "Qwen3.8-Flash-Next-Uncensored-IQ2_M-00001-of-00002.gguf",
                "url": (
                    "https://huggingface.co/orcarouter/"
                    "Qwen3.8-Flash-Next-Uncensored-GGUF/resolve/"
                    "3da364f04d1e0161cae12db000399e0a91a9466f/"
                    "Qwen3.8-Flash-Next-Uncensored-IQ2_M-00001-of-00002.gguf"
                ),
                "sha256": "4ba8d9bbe1e7439d6f1856998074df10fac97294320fa74b45c795d2fb6f4004",
                "size": 44_775_849_152,
            },
            {
                "filename": "Qwen3.8-Flash-Next-Uncensored-IQ2_M-00002-of-00002.gguf",
                "url": (
                    "https://huggingface.co/orcarouter/"
                    "Qwen3.8-Flash-Next-Uncensored-GGUF/resolve/"
                    "3da364f04d1e0161cae12db000399e0a91a9466f/"
                    "Qwen3.8-Flash-Next-Uncensored-IQ2_M-00002-of-00002.gguf"
                ),
                "sha256": "f4435dbacdca4d78b9aa50703bccd494386b27395bc82e4f7a3d15181d028fde",
                "size": 35_310_443_840,
            },
        ),
    },
)

# Qualification is model-registry state, not a UI/model-name special case.
# Keep this table limited to Hafiye's evidence-backed local qualification
# identities; unknown GGUFs remain unqualified until they have their own
# evidence.
_MODEL_CAPABILITY_PROFILES: tuple[tuple[re.Pattern[str], dict[str, Any]], ...] = (
    (
        re.compile(r"^qwen2\.5-0\.5b(?:[._-].*)?$", re.IGNORECASE),
        {
            "validation": True,
            "agent": False,
            "tool_calling": False,
            "resource_warning": None,
        },
    ),
    (
        re.compile(r"^qwen3-4b(?:[._-].*)?$", re.IGNORECASE),
        {
            "validation": False,
            "agent": True,
            "tool_calling": True,
            # This host already showed measurable swap pressure while the
            # model was loaded; keep the existing warning category visible.
            "resource_warning": "KI-046",
        },
    ),
    (
        re.compile(r"^qwen3-14b(?:[._-].*)?$", re.IGNORECASE),
        {
            "validation": False,
            "agent": True,
            "tool_calling": True,
            "resource_warning": "KI-046",
        },
    ),
)


class LocalRuntimeError(RuntimeError):
    """An actionable local-runtime failure."""


@dataclass(frozen=True)
class RuntimePaths:
    data_home: Path
    state_home: Path
    models: Path
    runtime: Path
    source: Path
    build: Path
    binary_dir: Path
    manifest: Path
    runtime_state: Path
    registry: Path
    server_state: Path
    server_log: Path

    @classmethod
    def from_roots(
        cls, data_home: Path | None = None, state_home: Path | None = None
    ) -> "RuntimePaths":
        data = Path(data_home or get_hafiye_data_home()).expanduser()
        state = Path(state_home or get_hafiye_state_home()).expanduser()
        runtime = data / "runtimes" / "llama.cpp"
        runtime_state = state / "local-runtime"
        return cls(
            data_home=data,
            state_home=state,
            models=data / "models",
            runtime=runtime,
            source=runtime / "source",
            build=runtime / "build",
            binary_dir=runtime / "bin",
            manifest=runtime / "manifest.json",
            runtime_state=runtime_state,
            registry=runtime_state / "models.json",
            server_state=runtime_state / "server.json",
            server_log=runtime_state / "llama-server.log",
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def model_capabilities(model_id: str | None) -> dict[str, Any]:
    """Return the evidence-backed capability state for a local model id."""
    identity = str(model_id or "").strip()
    for pattern, profile in _MODEL_CAPABILITY_PROFILES:
        if pattern.fullmatch(identity):
            return dict(profile)
    return {}


def _apply_model_capabilities(item: dict[str, Any]) -> bool:
    """Apply known qualification state and report whether the entry changed."""
    capabilities = model_capabilities(str(item.get("id") or ""))
    if not capabilities:
        return False
    if item.get("capabilities") == capabilities:
        return False
    item["capabilities"] = capabilities
    return True


def _ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def _context_compatibility_args(model_id: str, model_path: Path, context_size: int) -> list[str]:
    """Return llama.cpp context-extension flags for known GGUF families.

    Qwen2 GGUF files commonly advertise a 32K training context even when the
    model is intended to be served with YaRN extension.  Hermes requires a
    64K runtime window for tool-calling sessions, so an explicit larger Hafiye
    context must also update the Qwen2 metadata that llama-server uses for its
    safety cap.  Keep this narrowly scoped to Qwen2 identities; other models
    must continue to use their native metadata instead of being silently
    extrapolated.
    """
    requested = int(context_size)
    if requested <= 32768:
        return []
    identity = f"{model_id} {model_path.name}".lower()
    if re.search(r"qwen2(?:[._-]|$)", identity):
        return [
            "--rope-scaling",
            "yarn",
            "--yarn-orig-ctx",
            "32768",
            "--override-kv",
            f"qwen2.context_length=int:{requested}",
        ]
    # Qwen3.5/Qwen3.8 GGUFs advertise their much larger native context and
    # must not inherit the original Qwen3 40,960-token YaRN workaround.
    qwen35_family = bool(re.search(r"qwen3(?:[._-]?5|\.8)(?:[._-]|$)", identity))
    if (
        re.search(r"qwen3(?:[._-]|$)", identity)
        and not qwen35_family
        and requested > 40960
    ):
        # Official Qwen3 GGUFs advertise a 40,960-token training window.
        # Keep Hermes' 64K contract explicit while using the model's native
        # context as the YaRN origin and overriding llama.cpp's slot cap.
        scale = requested / 40960
        scale_text = f"{scale:.6g}"
        return [
            "--rope-scaling",
            "yarn",
            "--rope-scale",
            scale_text,
            "--yarn-orig-ctx",
            "40960",
            "--override-kv",
            f"qwen3.context_length=int:{requested}",
        ]
    return []


def _chat_template_args(model_id: str, model_path: Path) -> list[str]:
    """Return explicit chat-parser flags for model families needing them.

    Qwen3 GGUFs carry the authoritative Jinja template in their metadata.
    llama-server's Jinja path also exposes its reasoning/tool-call parser, so
    make that path explicit for managed Qwen3 servers and ask it to separate
    the model's ``<think>`` content from the assistant message.  Do not force
    a template name: the official Qwen3 GGUF metadata is the source of truth.
    """
    identity = f"{model_id} {model_path.name}".lower()
    if re.search(r"qwen3(?:[._-]|$)", identity):
        return ["--jinja", "--reasoning-format", "deepseek"]
    return []


def _memory_compatibility_args(
    model_id: str,
    model_path: Path,
    context_size: int,
    selected_backend: str,
) -> list[str]:
    """Keep large Qwen3 KV caches in host RAM when CUDA memory is tight."""
    identity = f"{model_id} {model_path.name}".lower()
    if (
        selected_backend == "CUDA"
        and int(context_size) > 40960
        and re.search(r"qwen3(?:[._-]|$)", identity)
    ):
        return ["--no-kv-offload"]
    return []


def _parallel_compatibility_args(
    model_id: str,
    model_path: Path,
    context_size: int,
) -> list[str]:
    """Keep large Qwen3 agent contexts to one llama-server slot.

    llama-server's automatic slot count created four 65K KV slots on the
    current host.  That multiplies the cache footprint for a model already
    carrying the Qwen3 resource warning and can starve a single Hafiye agent
    request.  The managed Qwen3 path is single-agent at a time on this
    resource envelope, so use one slot only for the large-context compatibility
    path.  Other models retain llama-server's upstream automatic behavior.
    """
    identity = f"{model_id} {model_path.name}".lower()
    if int(context_size) > 40960 and re.search(r"qwen3(?:[._-]|$)", identity):
        return ["--parallel", "1"]
    return []


def _default_gpu_layers(model_id: str, model_path: Path, selected_backend: str) -> int | str:
    """Use llama.cpp's fit-aware GPU selection for large Qwen3 GGUFs."""
    identity = f"{model_id} {model_path.name}".lower()
    if selected_backend == "CUDA" and re.search(r"qwen3(?:[._-]|$)", identity):
        return "auto"
    return 99 if selected_backend in GPU_BACKENDS else 0


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    _ensure_private_dir(path.parent)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            fd = -1
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            path.chmod(0o600)
        except OSError:
            pass
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            Path(temporary).unlink(missing_ok=True)
        except OSError:
            pass


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return dict(default)
    except (OSError, json.JSONDecodeError) as exc:
        raise LocalRuntimeError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise LocalRuntimeError(f"Expected a JSON object in {path}")
    return payload


def _run_capture(command: list[str], *, timeout: float = 10.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(command, 127, "", "command not found")
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(command, 124, "", f"timed out: {exc}")


def _command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def _pkg_config_has(package: str) -> bool:
    if not _command_exists("pkg-config"):
        return False
    return _run_capture(["pkg-config", "--exists", package], timeout=3).returncode == 0


def detect_compute_environment() -> dict[str, Any]:
    """Inspect the real host without treating diagnostic tools as blockers."""
    nvidia_smi = _command_exists("nvidia-smi")
    nvidia_present = False
    nvidia_name = ""
    if nvidia_smi:
        probe = _run_capture(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], timeout=5
        )
        names = [line.strip() for line in probe.stdout.splitlines() if line.strip()]
        nvidia_present = probe.returncode == 0 and bool(names)
        nvidia_name = names[0] if names else ""

    nvcc = shutil.which("nvcc")
    cuda_home = os.environ.get("CUDA_HOME", "").strip()
    cuda_toolkit = bool(nvcc) or bool(cuda_home and (Path(cuda_home) / "bin" / "nvcc").exists())
    vulkan_header = Path("/usr/include/vulkan/vulkan.h").exists()
    vulkan_build = _pkg_config_has("vulkan") or vulkan_header
    vulkan_runtime = _command_exists("vulkaninfo") or Path("/usr/lib/x86_64-linux-gnu/libvulkan.so.1").exists()
    return {
        "platform": platform.platform(),
        "nvidia_present": nvidia_present,
        "nvidia_name": nvidia_name,
        "nvidia_smi": nvidia_smi,
        "nvcc": str(nvcc) if nvcc else "",
        "cuda_toolkit_available": cuda_toolkit,
        "cuda_build_available": bool(nvidia_present and cuda_toolkit),
        "vulkan_build_available": vulkan_build,
        "vulkan_runtime_available": vulkan_runtime,
        "cpu_available": True,
        "expected_auto_backend": "CUDA" if nvidia_present and cuda_toolkit else ("VULKAN" if vulkan_build else "CPU"),
    }


def normalize_backend(value: str | None) -> str:
    normalized = (value or "AUTO").strip().upper()
    if normalized not in BACKENDS:
        raise LocalRuntimeError(
            f"Unknown compute backend {value!r}; choose one of {', '.join(BACKENDS)}"
        )
    return normalized


def choose_backend(
    requested: str | None = "AUTO",
    *,
    environment: dict[str, Any] | None = None,
    compiled: Iterable[str] | None = None,
) -> str:
    """Resolve AUTO using the fixed Hafiye CUDA → Vulkan → CPU policy."""
    requested_backend = normalize_backend(requested)
    env = environment or detect_compute_environment()
    compiled_set = {str(item).upper() for item in (compiled or ())}
    if compiled is None:
        compiled_set = {"CPU"}
        if env.get("cuda_build_available"):
            compiled_set.add("CUDA")
        if env.get("vulkan_build_available"):
            compiled_set.add("VULKAN")

    if requested_backend == "CPU":
        return "CPU"
    if requested_backend == "CUDA":
        if "CUDA" not in compiled_set or not env.get("cuda_build_available", False):
            raise LocalRuntimeError("CUDA was requested but the CUDA toolkit/runtime is not available")
        return "CUDA"
    if requested_backend == "VULKAN":
        if "VULKAN" not in compiled_set or not env.get("vulkan_runtime_available", True):
            raise LocalRuntimeError("Vulkan was requested but a Vulkan runtime/build is not available")
        return "VULKAN"

    if "CUDA" in compiled_set and env.get("cuda_build_available", False):
        return "CUDA"
    if "VULKAN" in compiled_set and env.get("vulkan_runtime_available", False):
        return "VULKAN"
    return "CPU"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_model_id(value: str) -> str:
    model_id = value.strip()
    if not MODEL_ID_RE.fullmatch(model_id):
        raise LocalRuntimeError(
            "Model id must contain 1-128 letters, numbers, dots, underscores, or hyphens"
        )
    return model_id


def _process_start_marker(pid: int) -> str | None:
    if os.name != "posix" or not Path("/proc").exists():
        return None
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].strip().split()
        return f"linux:{fields[19]}" if len(fields) > 19 else None
    except (FileNotFoundError, OSError, IndexError):
        return None


def _tail(path: Path, limit: int = 80) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
        return [_redact_runtime_diagnostic(line, limit=1200) for line in lines]
    except OSError:
        return []


def _redact_runtime_diagnostic(value: Any, *, limit: int = 800) -> str:
    """Return bounded recovery diagnostics without leaking credentials."""
    text = str(value or "").strip()
    try:
        from agent.redact import redact_sensitive_text

        text = redact_sensitive_text(text, force=True)
    except Exception:
        pass
    return text[-limit:] if text else "no diagnostic"


class LocalRuntimeManager:
    """Filesystem/process manager for one Hafiye installation."""

    def __init__(self, paths: RuntimePaths | None = None):
        self.paths = paths or RuntimePaths.from_roots()

    def _registry(self) -> dict[str, Any]:
        payload = _read_json(self.paths.registry, {"schema": 1, "models": []})
        models = payload.get("models")
        if not isinstance(models, list):
            raise LocalRuntimeError(f"Invalid model registry: {self.paths.registry}")
        payload["schema"] = 1
        return payload

    def _save_registry(self, payload: dict[str, Any]) -> None:
        _atomic_write_json(self.paths.registry, payload)

    def _manifest(self) -> dict[str, Any]:
        return _read_json(self.paths.manifest, {})

    def _binary(self) -> Path:
        candidates = (
            self.paths.binary_dir / "llama-server",
            self.paths.build / "bin" / "llama-server",
            self.paths.build / "bin" / "Release" / "llama-server",
        )
        for candidate in candidates:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        raise LocalRuntimeError(
            "llama-server is not installed; run `hafiye runtime install` first"
        )

    def models(self) -> list[dict[str, Any]]:
        payload = self._registry()
        result: list[dict[str, Any]] = []
        changed = False
        for item in payload["models"]:
            if not isinstance(item, dict):
                changed = True
                continue
            path = Path(str(item.get("path", "")))
            item = dict(item)
            item["available"] = path.is_file()
            if _apply_model_capabilities(item):
                changed = True
            result.append(item)
        if changed:
            payload["models"] = result
            self._save_registry(payload)
        return result

    def model_catalog(self) -> list[dict[str, Any]]:
        """Return curated downloads enriched with their local install state."""
        installed = {str(item.get("id")): item for item in self.models()}
        result: list[dict[str, Any]] = []
        for catalog_item in CURATED_LOCAL_MODEL_CATALOG:
            item = json.loads(json.dumps(catalog_item))
            local = installed.get(str(item["id"]))
            expected_files = [
                {
                    "filename": entry["filename"],
                    "sha256": entry["sha256"],
                    "size": entry["size"],
                }
                for entry in item["download_files"]
            ]
            exact_catalog_registration = bool(
                local
                and local.get("catalog_revision") == item["revision"]
                and local.get("catalog_files") == expected_files
            )
            local_path = Path(str(local.get("path", ""))) if local else None
            all_catalog_files_available = bool(
                local_path
                and all(
                    (local_path.parent / Path(str(entry["filename"])).name).is_file()
                    for entry in expected_files
                )
            )
            if not local:
                item["install_status"] = "downloadable"
            elif exact_catalog_registration and all_catalog_files_available:
                item["install_status"] = "installed"
            elif exact_catalog_registration:
                # An interrupted or partially removed split download is safe
                # to resume because its immutable file list is still exact.
                item["install_status"] = "downloadable"
            elif (
                local.get("available") is True
                and len(expected_files) == 1
                and str(local.get("sha256", "")).lower()
                == str(item["sha256"]).lower()
            ):
                item["install_status"] = "installed"
            else:
                # Never overwrite a user model which happens to share the id.
                item["install_status"] = "conflict"
            result.append(item)
        return result

    def _download_catalog_file(
        self,
        file_entry: dict[str, Any],
        destination: Path,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Download one immutable catalog file with resume and SHA-256 verification."""
        expected_sha = str(file_entry["sha256"]).lower()
        if destination.is_file() and _sha256(destination).lower() == expected_sha:
            return

        partial = destination.with_name(destination.name + ".part")
        offset = partial.stat().st_size if partial.exists() else 0
        request_headers = dict(headers or {})
        if offset:
            request_headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(str(file_entry["url"]), headers=request_headers)
        try:
            response = urllib.request.urlopen(request, timeout=60)
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403}:
                raise LocalRuntimeError(
                    "Catalog download is not authorized; accept the model's access terms "
                    "and configure HF_TOKEN in Hafiye Providers"
                ) from exc
            raise LocalRuntimeError(f"Catalog model download failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise LocalRuntimeError(f"Catalog model download failed: {exc}") from exc
        try:
            status = getattr(response, "status", 200)
            if offset and status != 206:
                offset = 0
            mode = "ab" if offset else "wb"
            with partial.open(mode) as output:
                try:
                    partial.chmod(0o600)
                except OSError:
                    pass
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
        except (OSError, http.client.HTTPException) as exc:
            raise LocalRuntimeError(
                f"Catalog model download was interrupted for {file_entry['filename']}: {exc}"
            ) from exc
        finally:
            response.close()

        actual_sha = _sha256(partial).lower()
        if actual_sha != expected_sha:
            partial.unlink(missing_ok=True)
            raise LocalRuntimeError(
                f"Downloaded checksum mismatch for {file_entry['filename']}: "
                f"expected {expected_sha}, got {actual_sha}"
            )
        os.replace(partial, destination)

    def download_catalog_model(self, model_id: str) -> dict[str, Any]:
        """Download a backend-owned catalog entry, including split GGUF shards."""
        selected_id = _safe_model_id(model_id)
        catalog = next(
            (item for item in self.model_catalog() if item.get("id") == selected_id),
            None,
        )
        if not catalog:
            raise LocalRuntimeError(f"Unknown catalog model {selected_id!r}")
        if catalog["install_status"] == "installed":
            return self.model(selected_id)
        if catalog["install_status"] == "conflict":
            raise LocalRuntimeError(
                f"Model id {selected_id!r} already exists; delete it before downloading"
            )

        headers: dict[str, str] = {}
        if catalog.get("requires_auth"):
            token = os.environ.get("HF_TOKEN", "").strip()
            if not token or token.startswith("keyring://"):
                raise LocalRuntimeError(
                    "This gated Hugging Face model requires approved access and HF_TOKEN; "
                    "configure the Hugging Face credential in Hafiye Providers"
                )
            headers["Authorization"] = f"Bearer {token}"

        model_dir = self.paths.models / selected_id
        _ensure_private_dir(model_dir)
        files = list(catalog["download_files"])
        for file_entry in files:
            filename = Path(str(file_entry["filename"])).name
            if not filename.lower().endswith(GGUF_SUFFIX):
                raise LocalRuntimeError("Catalog entries may contain only .gguf files")
            self._download_catalog_file(file_entry, model_dir / filename, headers=headers)

        primary = model_dir / Path(str(files[0]["filename"])).name
        registered_files = [
            {
                "filename": Path(str(entry["filename"])).name,
                "sha256": str(entry["sha256"]).lower(),
                "size": int(entry["size"]),
            }
            for entry in files
        ]
        item = {
            "id": selected_id,
            "name": catalog["name"],
            "path": str(primary),
            "size": int(catalog["size"]),
            "sha256": registered_files[0]["sha256"],
            "source": f"catalog:{catalog['source_type']}",
            "source_url": catalog["source_url"],
            "catalog_revision": catalog["revision"],
            "catalog_files": registered_files,
            "updated_at": _now(),
        }
        _apply_model_capabilities(item)
        payload = self._registry()
        payload["models"] = [
            entry for entry in payload["models"] if entry.get("id") != selected_id
        ]
        payload["models"].append(item)
        self._save_registry(payload)
        return item

    def model(self, model_id: str) -> dict[str, Any]:
        model_id = _safe_model_id(model_id)
        for item in self.models():
            if item.get("id") == model_id:
                path = Path(str(item.get("path", "")))
                if not path.is_file():
                    raise LocalRuntimeError(f"Model {model_id!r} is missing: {path}")
                return item
        raise LocalRuntimeError(f"Model {model_id!r} is not registered")

    def import_model(self, source: str | Path, model_id: str | None = None) -> dict[str, Any]:
        source_path = Path(source).expanduser().resolve()
        if not source_path.is_file():
            raise LocalRuntimeError(f"GGUF source does not exist: {source_path}")
        if source_path.suffix.lower() != GGUF_SUFFIX:
            raise LocalRuntimeError("Only .gguf model files can be imported")
        selected_id = _safe_model_id(model_id or source_path.stem)
        _ensure_private_dir(self.paths.models)
        destination = self.paths.models / f"{selected_id}.gguf"
        existing = next((item for item in self.models() if item.get("id") == selected_id), None)
        digest = _sha256(source_path)
        if destination.exists() and destination.resolve() != source_path:
            if _sha256(destination) != digest:
                raise LocalRuntimeError(
                    f"Model id {selected_id!r} already exists with different contents; choose another id"
                )
        elif destination.resolve() != source_path:
            fd, temporary = tempfile.mkstemp(prefix=f".{selected_id}.", dir=self.paths.models)
            try:
                os.fchmod(fd, 0o600)
                with os.fdopen(fd, "wb") as output, source_path.open("rb") as input_stream:
                    fd = -1
                    shutil.copyfileobj(input_stream, output, length=1024 * 1024)
                    output.flush()
                    os.fsync(output.fileno())
                os.replace(temporary, destination)
            finally:
                if fd >= 0:
                    os.close(fd)
                Path(temporary).unlink(missing_ok=True)
        item = {
            "id": selected_id,
            "name": source_path.name,
            "path": str(destination if destination.exists() else source_path),
            "size": source_path.stat().st_size,
            "sha256": digest,
            "source": "import",
            "updated_at": _now(),
        }
        _apply_model_capabilities(item)
        payload = self._registry()
        payload["models"] = [entry for entry in payload["models"] if entry.get("id") != selected_id]
        payload["models"].append(item)
        self._save_registry(payload)
        return item

    def download_model(
        self,
        repo_id: str,
        filename: str,
        *,
        revision: str = "main",
        model_id: str | None = None,
        sha256: str | None = None,
    ) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_id.strip()):
            raise LocalRuntimeError("repo_id must look like an owner/repository")
        filename = Path(filename).name
        if not filename.lower().endswith(GGUF_SUFFIX):
            raise LocalRuntimeError("Only .gguf model files can be downloaded")
        selected_id = _safe_model_id(model_id or Path(filename).stem)
        _ensure_private_dir(self.paths.models)
        destination = self.paths.models / f"{selected_id}.gguf"
        existing = next((item for item in self.models() if item.get("id") == selected_id), None)
        if existing and destination.is_file():
            if (
                sha256
                and str(existing.get("sha256", "")).lower() == sha256.strip().lower()
            ):
                return existing
            raise LocalRuntimeError(
                f"Model id {selected_id!r} already exists; delete it or choose another id"
            )
        partial = destination.with_name(destination.name + ".part")
        url = f"https://huggingface.co/{repo_id}/resolve/{revision}/{filename}"
        offset = partial.stat().st_size if partial.exists() else 0
        request_headers = {"Range": f"bytes={offset}-"} if offset else {}
        hf_token = os.environ.get("HF_TOKEN", "").strip()
        if hf_token and not hf_token.startswith("keyring://"):
            request_headers["Authorization"] = f"Bearer {hf_token}"
        request = urllib.request.Request(url, headers=request_headers)
        try:
            response = urllib.request.urlopen(request, timeout=60)
        except urllib.error.URLError as exc:
            raise LocalRuntimeError(f"Model download failed: {exc}") from exc
        try:
            status = getattr(response, "status", 200)
            if offset and status != 206:
                offset = 0
            mode = "ab" if offset else "wb"
            with partial.open(mode) as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
        finally:
            response.close()
        actual_sha = _sha256(partial)
        if sha256 and actual_sha.lower() != sha256.strip().lower():
            raise LocalRuntimeError(
                f"Downloaded checksum mismatch: expected {sha256}, got {actual_sha}"
            )
        os.replace(partial, destination)
        item = self.import_model(destination, selected_id)
        item.update({
            "source": "huggingface",
            "source_url": url,
            "revision": revision,
        })
        payload = self._registry()
        payload["models"] = [item if entry.get("id") == selected_id else entry for entry in payload["models"]]
        self._save_registry(payload)
        return item

    def delete_model(self, model_id: str) -> dict[str, Any]:
        model_id = _safe_model_id(model_id)
        item = self.model(model_id)
        state = self._read_server_state()
        if state.get("model_id") == model_id and self._server_is_alive(state):
            raise LocalRuntimeError("Stop/unload the active model before deleting it")
        path = Path(str(item["path"]))
        catalog_files = item.get("catalog_files")
        if isinstance(catalog_files, list) and path.parent == self.paths.models / model_id:
            for entry in catalog_files:
                if isinstance(entry, dict):
                    (path.parent / Path(str(entry.get("filename", ""))).name).unlink(
                        missing_ok=True
                    )
            try:
                path.parent.rmdir()
            except OSError:
                pass
        else:
            path.unlink(missing_ok=True)
        payload = self._registry()
        payload["models"] = [entry for entry in payload["models"] if entry.get("id") != model_id]
        self._save_registry(payload)
        return {"ok": True, "id": model_id}

    def install_runtime(self, *, backend: str = "AUTO", source_ref: str = "master") -> dict[str, Any]:
        requested = normalize_backend(backend)
        environment = detect_compute_environment()
        if requested == "CUDA" and not environment["cuda_build_available"]:
            raise LocalRuntimeError(
                "CUDA build requested but nvcc/CUDA toolkit is unavailable; install the toolkit and retry"
            )
        if requested == "VULKAN" and not environment["vulkan_build_available"]:
            raise LocalRuntimeError(
                "Vulkan build requested but Vulkan development headers/pkg-config metadata are unavailable"
            )
        _ensure_private_dir(self.paths.runtime)
        if not (self.paths.source / ".git").is_dir():
            if self.paths.source.exists():
                raise LocalRuntimeError(f"Runtime source path is not a Git checkout: {self.paths.source}")
            self.paths.source.parent.mkdir(parents=True, exist_ok=True)
            clone = _run_capture(["git", "clone", "--depth", "1", "--recurse-submodules", LLAMA_REPOSITORY, str(self.paths.source)], timeout=300)
            if clone.returncode != 0:
                raise LocalRuntimeError(f"llama.cpp clone failed: {(clone.stderr or clone.stdout).strip()}")
        if source_ref and source_ref not in {"master", "main"}:
            fetch = _run_capture(["git", "-C", str(self.paths.source), "fetch", "--depth", "1", "origin", source_ref], timeout=300)
            if fetch.returncode != 0:
                raise LocalRuntimeError(f"llama.cpp source ref fetch failed: {(fetch.stderr or fetch.stdout).strip()}")
            checkout = _run_capture(["git", "-C", str(self.paths.source), "checkout", "--detach", source_ref], timeout=60)
            if checkout.returncode != 0:
                raise LocalRuntimeError(f"llama.cpp source ref checkout failed: {(checkout.stderr or checkout.stdout).strip()}")
        compiled: list[str] = ["CPU"]
        cmake_args = ["cmake", "-S", str(self.paths.source), "-B", str(self.paths.build), "-DCMAKE_BUILD_TYPE=Release", "-DLLAMA_BUILD_TESTS=OFF"]
        if requested == "CUDA" or (requested == "AUTO" and environment["cuda_build_available"]):
            cmake_args.append("-DGGML_CUDA=ON")
            compiled.append("CUDA")
        elif requested == "VULKAN" or (requested == "AUTO" and environment["vulkan_build_available"]):
            cmake_args.append("-DGGML_VULKAN=ON")
            compiled.append("VULKAN")
        selected = choose_backend(requested, environment=environment, compiled=compiled)
        configure = _run_capture(cmake_args, timeout=300)
        if configure.returncode != 0:
            raise LocalRuntimeError(f"llama.cpp CMake configure failed: {(configure.stderr or configure.stdout).strip()}")
        jobs = max(1, min(os.cpu_count() or 1, 8))
        build = _run_capture(["cmake", "--build", str(self.paths.build), "--config", "Release", "--target", "llama-server", "-j", str(jobs)], timeout=1800)
        if build.returncode != 0:
            raise LocalRuntimeError(f"llama.cpp build failed: {(build.stderr or build.stdout).strip()[-4000:]}")
        binary = next((candidate for candidate in (self.paths.build / "bin" / "llama-server", self.paths.build / "bin" / "Release" / "llama-server") if candidate.is_file()), None)
        if binary is None:
            raise LocalRuntimeError("llama.cpp build completed without build/bin/llama-server")
        # Linux refuses to replace an executable while it is mapped by a live
        # process (ETXTBSY).  A runtime rebuild is an explicit lifecycle
        # operation, so stop the managed server gracefully before publishing
        # the new binary.  The active model is not restarted implicitly; the
        # caller can load it again after the build has completed.
        server_was_running = self._server_is_alive()
        if server_was_running:
            self.stop_server()
        _ensure_private_dir(self.paths.binary_dir)
        installed_binary = self.paths.binary_dir / "llama-server"
        shutil.copy2(binary, installed_binary)
        installed_binary.chmod(installed_binary.stat().st_mode | stat.S_IXUSR)
        revision = _run_capture(["git", "-C", str(self.paths.source), "rev-parse", "HEAD"], timeout=10)
        source_commit = revision.stdout.strip() if revision.returncode == 0 else ""
        manifest = {
            "schema": 1,
            "repository": LLAMA_REPOSITORY,
            "source_ref": source_ref,
            "source_commit": source_commit,
            "binary": str(installed_binary),
            "requested_backend": requested,
            "selected_backend": selected,
            "compiled_backends": sorted(set(compiled)),
            "environment": environment,
            "server_was_stopped_for_install": server_was_running,
            "installed_at": _now(),
        }
        if selected == "CPU" and requested == "AUTO" and environment["nvidia_present"] and not environment["cuda_toolkit_available"]:
            manifest["warning"] = "NVIDIA is present, but CUDA toolkit/nvcc is unavailable; AUTO selected CPU."
        _atomic_write_json(self.paths.manifest, manifest)
        return manifest

    def version(self) -> dict[str, Any]:
        manifest = self._manifest()
        if not manifest:
            return {"installed": False, "version": "", "manifest": {}}
        try:
            binary = self._binary()
        except LocalRuntimeError:
            return {"installed": False, "version": "", "manifest": manifest}
        result = _run_capture([str(binary), "--version"], timeout=10)
        return {
            "installed": result.returncode == 0,
            "version": (result.stdout or result.stderr).strip(),
            "manifest": manifest,
        }

    def _read_server_state(self) -> dict[str, Any]:
        return _read_json(self.paths.server_state, {})

    def _write_server_state(self, state: dict[str, Any]) -> None:
        _atomic_write_json(self.paths.server_state, state)

    def _server_is_alive(self, state: dict[str, Any] | None = None) -> bool:
        state = state or self._read_server_state()
        try:
            pid = int(state.get("pid", 0))
        except (TypeError, ValueError):
            return False
        if pid <= 0:
            return False
        if not psutil.pid_exists(pid):
            return False
        marker = state.get("start_marker")
        return not marker or marker == _process_start_marker(pid)

    def _http_json(self, path: str, *, method: str = "GET", body: dict[str, Any] | None = None, port: int = DEFAULT_PORT) -> tuple[int, dict[str, Any] | str]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(f"http://{DEFAULT_HOST}:{port}{path}", data=data, method=method, headers={"Content-Type": "application/json"} if data else {})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                raw = response.read().decode("utf-8", errors="replace")
                try:
                    payload: dict[str, Any] | str = json.loads(raw)
                except json.JSONDecodeError:
                    payload = raw
                return response.status, payload
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = raw
            return exc.code, payload
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return 0, str(exc)

    def health(self) -> dict[str, Any]:
        state = self._read_server_state()
        alive = self._server_is_alive(state)
        port = int(state.get("port", DEFAULT_PORT) or DEFAULT_PORT)
        http_status, http_payload = self._http_json("/health", port=port) if alive else (0, "not running")
        models_status, models_payload = self._http_json("/v1/models", port=port) if alive else (0, "not running")
        memory: dict[str, str] = {}
        if alive and os.name == "posix":
            try:
                for line in Path(f"/proc/{int(state['pid'])}/status").read_text(encoding="utf-8").splitlines():
                    if line.startswith(("VmRSS:", "VmSize:")):
                        key, value = line.split(":", 1)
                        memory[key] = value.strip()
            except (KeyError, FileNotFoundError, OSError):
                pass
        return {
            "running": alive,
            "ready": alive and http_status == 200,
            "host": DEFAULT_HOST,
            "port": port,
            "endpoint": f"http://{DEFAULT_HOST}:{port}/v1",
            "pid": int(state.get("pid", 0) or 0),
            "model_id": state.get("model_id", ""),
            "requested_backend": state.get("requested_backend", ""),
            "selected_backend": state.get("selected_backend", ""),
            "health_status": http_status,
            "health_response": http_payload,
            "models_status": models_status,
            "models_response": models_payload,
            "memory": memory,
            "log_tail": _tail(self.paths.server_log),
        }

    def start_server(
        self,
        model_id: str,
        *,
        backend: str = "AUTO",
        context_size: int = DEFAULT_CONTEXT_SIZE,
        gpu_layers: int | None = None,
        port: int = DEFAULT_PORT,
    ) -> dict[str, Any]:
        if not 1024 <= int(port) <= 65535:
            raise LocalRuntimeError("Server port must be between 1024 and 65535")
        if int(context_size) <= 0:
            raise LocalRuntimeError("Context size must be positive")
        item = self.model(model_id)
        binary = self._binary()
        manifest = self._manifest()
        compiled = manifest.get("compiled_backends", ["CPU"])
        selected = choose_backend(backend, environment=detect_compute_environment(), compiled=compiled)
        current = self._read_server_state()
        if self._server_is_alive(current):
            same = current.get("model_id") == model_id and current.get("selected_backend") == selected
            if same:
                return self.health()
            self.stop_server()
        _ensure_private_dir(self.paths.runtime_state)
        log_stream = self.paths.server_log.open("ab")
        actual_gpu_layers: int | str = (
            int(gpu_layers)
            if gpu_layers is not None
            else _default_gpu_layers(model_id, Path(str(item["path"])), selected)
        )
        device = "CUDA0" if selected == "CUDA" else ("Vulkan0" if selected == "VULKAN" else "none")
        command = [
            str(binary),
            "--model",
            str(item["path"]),
            "--host",
            DEFAULT_HOST,
            "--port",
            str(port),
            "--ctx-size",
            str(int(context_size)),
            "--device",
            device,
            "-ngl",
            str(actual_gpu_layers),
            *_chat_template_args(model_id, Path(str(item["path"]))),
            *_context_compatibility_args(model_id, Path(str(item["path"])), int(context_size)),
            *_parallel_compatibility_args(model_id, Path(str(item["path"])), int(context_size)),
            *_memory_compatibility_args(
                model_id,
                Path(str(item["path"])),
                int(context_size),
                selected,
            ),
        ]
        try:
            process = subprocess.Popen(command, stdout=log_stream, stderr=subprocess.STDOUT, start_new_session=True)
        except OSError as exc:
            log_stream.close()
            raise LocalRuntimeError(f"Could not start llama-server: {exc}") from exc
        finally:
            log_stream.close()
        state = {
            "schema": 1,
            "pid": process.pid,
            "start_marker": _process_start_marker(process.pid),
            "host": DEFAULT_HOST,
            "port": int(port),
            "model_id": model_id,
            "requested_backend": normalize_backend(backend),
            "selected_backend": selected,
            "context_size": int(context_size),
            "gpu_layers": actual_gpu_layers,
            "command": command,
            "started_at": _now(),
        }
        self._write_server_state(state)
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if not self._server_is_alive(state):
                detail = "\n".join(_tail(self.paths.server_log, 30))
                self._write_server_state({})
                raise LocalRuntimeError(f"llama-server exited during startup:\n{detail}")
            status, _ = self._http_json("/health", port=int(port))
            if status == 200:
                return self.health()
            time.sleep(0.5)
        self.stop_server()
        raise LocalRuntimeError("llama-server did not become healthy within 90 seconds")

    def stop_server(self) -> dict[str, Any]:
        state = self._read_server_state()
        if self._server_is_alive(state):
            pid = int(state["pid"])
            try:
                psutil.Process(pid).terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline and self._server_is_alive(state):
                time.sleep(0.25)
            if self._server_is_alive(state):
                try:
                    psutil.Process(pid).kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        self._write_server_state({})
        return {"ok": True, "stopped": True}

    def recover_server(self, *, max_attempts: int = 1) -> dict[str, Any]:
        """Recover a crashed/unhealthy server from its last safe state.

        Recovery is deliberately explicit and bounded.  It never guesses a
        model, backend, or port when the persisted state is absent, and it
        never recursively retries through ``start_server``.  A failed startup
        already clears the live server state, so a later invocation must be a
        new, observable recovery request rather than an unbounded supervisor.
        """
        try:
            attempts_limit = int(max_attempts)
        except (TypeError, ValueError) as exc:
            raise LocalRuntimeError("max_attempts must be an integer") from exc
        if not 1 <= attempts_limit <= 3:
            raise LocalRuntimeError("max_attempts must be between 1 and 3")

        try:
            state = self._read_server_state()
        except LocalRuntimeError as exc:
            return {
                "ok": False,
                "recovered": False,
                "code": "runtime_state_invalid",
                "blockers": [_redact_runtime_diagnostic(exc)],
                "attempts": [],
            }

        model_id = str(state.get("model_id", "") or "").strip()
        if not model_id:
            return {
                "ok": False,
                "recovered": False,
                "code": "runtime_recovery_state_missing",
                "blockers": [
                    "No crashed llama-server state is available; choose a model and start the server first."
                ],
                "attempts": [],
            }

        if self._server_is_alive(state):
            current = self.health()
            if current.get("ready"):
                return {
                    "ok": True,
                    "recovered": False,
                    "code": "runtime_already_ready",
                    "health": current,
                    "attempts": [],
                }
            # A live but unhealthy process must be stopped before start_server;
            # otherwise its same-model fast path would return the unhealthy
            # status without replacing the process.
            self.stop_server()

        requested_backend = str(state.get("requested_backend", "AUTO") or "AUTO")
        try:
            requested_backend = normalize_backend(requested_backend)
        except LocalRuntimeError:
            requested_backend = "AUTO"

        def _state_int(name: str, fallback: int) -> int:
            try:
                value = int(state.get(name, fallback))
            except (TypeError, ValueError):
                return fallback
            return value

        context_size = max(1, _state_int("context_size", DEFAULT_CONTEXT_SIZE))
        port = _state_int("port", DEFAULT_PORT)
        if not 1024 <= port <= 65535:
            port = DEFAULT_PORT
        raw_gpu_layers = state.get("gpu_layers")
        try:
            gpu_layers = int(raw_gpu_layers) if raw_gpu_layers is not None else None
        except (TypeError, ValueError):
            gpu_layers = None

        attempts: list[dict[str, Any]] = []
        for attempt in range(1, attempts_limit + 1):
            try:
                health = self.start_server(
                    model_id,
                    backend=requested_backend,
                    context_size=context_size,
                    gpu_layers=gpu_layers,
                    port=port,
                )
            except LocalRuntimeError as exc:
                attempts.append(
                    {
                        "attempt": attempt,
                        "ok": False,
                        "error": _redact_runtime_diagnostic(exc),
                    }
                )
                continue
            if health.get("ready"):
                return {
                    "ok": True,
                    "recovered": True,
                    "code": "runtime_recovered",
                    "health": health,
                    "attempts": [*attempts, {"attempt": attempt, "ok": True}],
                }
            attempts.append(
                {
                    "attempt": attempt,
                    "ok": False,
                    "error": "llama-server started without becoming ready",
                }
            )

        return {
            "ok": False,
            "recovered": False,
            "code": "runtime_recovery_failed",
            "model_id": model_id,
            "attempts": attempts,
            "blockers": [
                "llama-server recovery exhausted its bounded attempts; inspect the local runtime log and choose a new recovery action."
            ],
        }

    def doctor(self) -> dict[str, Any]:
        environment = detect_compute_environment()
        version = self.version()
        health = self.health()
        blockers: list[str] = []
        warnings: list[str] = []
        if not version["installed"]:
            blockers.append("llama-server is not installed")
        if environment["nvidia_present"] and not environment["cuda_toolkit_available"]:
            warnings.append("NVIDIA is present but CUDA toolkit/nvcc is not installed; AUTO will use the compiled fallback")
        if health["running"] and not health["ready"]:
            blockers.append("llama-server is running but its /health endpoint is not ready")
        return {
            "ok": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "environment": environment,
            "runtime": version,
            "server": health,
            "paths": {key: str(value) for key, value in self.paths.__dict__.items()},
        }


def runtime_manager() -> LocalRuntimeManager:
    return LocalRuntimeManager()


__all__ = [
    "BACKENDS",
    "DEFAULT_CONTEXT_SIZE",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "LocalRuntimeError",
    "LocalRuntimeManager",
    "RuntimePaths",
    "choose_backend",
    "detect_compute_environment",
    "normalize_backend",
    "_redact_runtime_diagnostic",
    "runtime_manager",
]
