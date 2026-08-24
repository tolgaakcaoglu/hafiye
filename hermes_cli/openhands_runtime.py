"""Hafiye-managed OpenHands V1 runtime discovery.

OpenHands is an implementation dependency of Hafiye, not a second Hafiye
agent runtime.  Keep its Python environment isolated from Hermes' venv because
the SDK brings a large LiteLLM/tooling dependency graph with its own version
constraints.  The coding delegate uses the runtime resolved here and records
the installed package versions in the Hafiye data root.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Mapping

from hermes_constants import get_hafiye_data_home, get_hafiye_state_home


OPENHANDS_REPOSITORY = "https://github.com/OpenHands/software-agent-sdk.git"
OPENHANDS_PACKAGE_NAMES = (
    "openhands-sdk",
    "openhands-tools",
    "openhands-workspace",
    "openhands-agent-server",
)


@dataclass(frozen=True)
class OpenHandsRuntimePaths:
    """Filesystem locations for the Hafiye-managed OpenHands environment."""

    data_root: Path
    state_root: Path

    @classmethod
    def from_roots(
        cls,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ) -> "OpenHandsRuntimePaths":
        return cls(
            Path(data_root) if data_root is not None else get_hafiye_data_home(),
            Path(state_root) if state_root is not None else get_hafiye_state_home(),
        )

    @property
    def runtime_root(self) -> Path:
        return self.data_root / "runtimes" / "openhands"

    @property
    def venv_root(self) -> Path:
        return self.runtime_root / "venv"

    @property
    def python(self) -> Path:
        if os.name == "nt":
            return self.venv_root / "Scripts" / "python.exe"
        return self.venv_root / "bin" / "python"

    @property
    def manifest(self) -> Path:
        return self.runtime_root / "manifest.json"

    @property
    def request_root(self) -> Path:
        return self.state_root / "openhands" / "requests"


def get_openhands_runtime_paths() -> OpenHandsRuntimePaths:
    return OpenHandsRuntimePaths.from_roots()


def _read_manifest(paths: OpenHandsRuntimePaths) -> dict[str, Any]:
    try:
        raw = json.loads(paths.manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _probe_packages(python: Path) -> dict[str, Any]:
    code = (
        "import importlib.metadata as m, json; names = "
        + repr(OPENHANDS_PACKAGE_NAMES)
        + "; out = {}; "
        "\nfor name in names:\n"
        "    try: out[name] = m.version(name)\n"
        "    except m.PackageNotFoundError: out[name] = None\n"
        "print(json.dumps(out, sort_keys=True))"
    )
    try:
        completed = subprocess.run(
            [str(python), "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env={
                **os.environ,
                "OPENHANDS_SUPPRESS_BANNER": "1",
            },
        )
        if completed.returncode != 0:
            return {"error": (completed.stderr or "").strip()[-500:]}
        raw = json.loads(completed.stdout.strip() or "{}")
        return raw if isinstance(raw, dict) else {"error": "invalid probe output"}
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def openhands_runtime_doctor(
    paths: OpenHandsRuntimePaths | None = None,
) -> dict[str, Any]:
    """Return actionable readiness information without importing OpenHands."""

    paths = paths or get_openhands_runtime_paths()
    manifest = _read_manifest(paths)
    blockers: list[str] = []
    warnings: list[str] = []

    if not paths.python.is_file() or not os.access(paths.python, os.X_OK):
        blockers.append(f"managed OpenHands Python is missing: {paths.python}")

    package_versions: dict[str, Any] = {}
    if not blockers:
        package_versions = _probe_packages(paths.python)
        if package_versions.get("error"):
            blockers.append(f"OpenHands runtime probe failed: {package_versions['error']}")
        else:
            missing = [
                name for name in OPENHANDS_PACKAGE_NAMES
                if not package_versions.get(name)
            ]
            if missing:
                blockers.append(
                    "OpenHands managed runtime is missing packages: "
                    + ", ".join(missing)
                )

    if not paths.manifest.is_file():
        warnings.append(f"runtime manifest is missing: {paths.manifest}")

    return {
        "ready": not blockers,
        "python": str(paths.python),
        "runtime_root": str(paths.runtime_root),
        "manifest": str(paths.manifest),
        "manifest_present": paths.manifest.is_file(),
        "packages": package_versions,
        "source": manifest.get("source", OPENHANDS_REPOSITORY),
        "source_commit": manifest.get("source_commit", ""),
        "requested_versions": manifest.get("requested_versions", {}),
        "blockers": blockers,
        "warnings": warnings,
    }


def openhands_runtime_ready(
    paths: OpenHandsRuntimePaths | None = None,
) -> bool:
    return bool(openhands_runtime_doctor(paths).get("ready"))


def write_openhands_runtime_manifest(
    *,
    paths: OpenHandsRuntimePaths | None = None,
    source_commit: str = "",
    requested_versions: Mapping[str, str] | None = None,
) -> Path:
    """Record the package pin after an official runtime installation."""

    paths = paths or get_openhands_runtime_paths()
    paths.runtime_root.mkdir(parents=True, exist_ok=True)
    package_versions = _probe_packages(paths.python)
    payload = {
        "schema": 1,
        "source": OPENHANDS_REPOSITORY,
        "source_commit": source_commit,
        "requested_versions": dict(requested_versions or {}),
        "installed_versions": package_versions,
    }
    paths.manifest.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    try:
        paths.manifest.chmod(0o644)
    except OSError:
        pass
    return paths.manifest


__all__ = [
    "OPENHANDS_PACKAGE_NAMES",
    "OPENHANDS_REPOSITORY",
    "OpenHandsRuntimePaths",
    "get_openhands_runtime_paths",
    "openhands_runtime_doctor",
    "openhands_runtime_ready",
    "write_openhands_runtime_manifest",
]
