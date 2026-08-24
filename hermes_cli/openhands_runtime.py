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
import shutil
import subprocess
import sys
from typing import Any, Mapping

from hermes_constants import get_hafiye_data_home, get_hafiye_state_home


OPENHANDS_REPOSITORY = "https://github.com/OpenHands/software-agent-sdk.git"
OPENHANDS_SOURCE_COMMIT = "6d38810359827823e62a5e1043d0d78d0bafb6de"
OPENHANDS_PACKAGE_NAMES = (
    "openhands-sdk",
    "openhands-tools",
    "openhands-workspace",
    "openhands-agent-server",
)
OPENHANDS_PACKAGE_VERSION = "1.41.0"
OPENHANDS_REQUESTED_VERSIONS = {
    name: OPENHANDS_PACKAGE_VERSION for name in OPENHANDS_PACKAGE_NAMES
}


class OpenHandsRuntimeError(RuntimeError):
    """An actionable failure while preparing the managed OpenHands runtime."""


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
    def source_root(self) -> Path:
        return self.runtime_root / "source"

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


def _run_capture(
    command: list[str], *, cwd: Path | None = None, timeout: float = 60
) -> subprocess.CompletedProcess[str]:
    """Run a managed setup command without invoking a shell."""

    try:
        return subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(command, 127, "", "command not found")
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(command, 124, "", f"timed out: {exc}")


def _command_detail(result: subprocess.CompletedProcess[str]) -> str:
    detail = (result.stderr or result.stdout or "").strip()
    return detail[-2500:] or "no output"


def _git_revision(source: Path) -> str:
    if not (source / ".git").exists():
        return ""
    result = _run_capture(["git", "-C", str(source), "rev-parse", "HEAD"], timeout=15)
    return result.stdout.strip() if result.returncode == 0 else ""


def _ensure_source_checkout(
    paths: OpenHandsRuntimePaths, source_ref: str
) -> str:
    """Clone/fetch the official SDK and check out the exact source pin."""

    source = paths.source_root
    if source.exists() and not (source / ".git").exists():
        raise OpenHandsRuntimeError(
            f"OpenHands source path is not a Git checkout: {source}"
        )

    paths.runtime_root.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        clone = _run_capture(
            [
                "git",
                "clone",
                "--filter=blob:none",
                OPENHANDS_REPOSITORY,
                str(source),
            ],
            timeout=300,
        )
        if clone.returncode != 0:
            raise OpenHandsRuntimeError(
                f"OpenHands source clone failed: {_command_detail(clone)}"
            )

    current = _git_revision(source)
    if current != source_ref:
        fetch = _run_capture(
            ["git", "-C", str(source), "fetch", "--depth", "1", "origin", source_ref],
            timeout=300,
        )
        if fetch.returncode != 0:
            raise OpenHandsRuntimeError(
                f"OpenHands source pin fetch failed: {_command_detail(fetch)}"
            )
        checkout = _run_capture(
            ["git", "-C", str(source), "checkout", "--detach", source_ref],
            timeout=60,
        )
        if checkout.returncode != 0:
            raise OpenHandsRuntimeError(
                f"OpenHands source pin checkout failed: {_command_detail(checkout)}"
            )

    actual = _git_revision(source)
    if actual != source_ref:
        raise OpenHandsRuntimeError(
            f"OpenHands source checkout resolved to {actual or 'unknown'}, expected {source_ref}"
        )
    return actual


def _ensure_virtualenv(
    paths: OpenHandsRuntimePaths, python_executable: str | Path | None = None
) -> None:
    if paths.python.is_file() and os.access(paths.python, os.X_OK):
        return

    paths.runtime_root.mkdir(parents=True, exist_ok=True)
    requested_python = str(python_executable or "3.13")
    uv = shutil.which("uv")
    if uv:
        command = [uv, "venv", "--python", requested_python, str(paths.venv_root)]
    else:
        base_python = str(python_executable or shutil.which("python3") or sys.executable)
        command = [base_python, "-m", "venv", str(paths.venv_root)]

    result = _run_capture(command, timeout=300)
    if result.returncode != 0 or not paths.python.is_file():
        raise OpenHandsRuntimeError(
            f"OpenHands virtualenv creation failed: {_command_detail(result)}"
        )


def _packages_match(package_versions: Mapping[str, Any]) -> bool:
    return all(
        str(package_versions.get(name) or "") == version
        for name, version in OPENHANDS_REQUESTED_VERSIONS.items()
    )


def _install_packages(paths: OpenHandsRuntimePaths) -> None:
    requirements = [
        f"{name}=={version}"
        for name, version in OPENHANDS_REQUESTED_VERSIONS.items()
    ]
    uv = shutil.which("uv")
    if uv:
        command = [uv, "pip", "install", "--python", str(paths.python), *requirements]
    else:
        command = [str(paths.python), "-m", "pip", "install", *requirements]

    result = _run_capture(command, timeout=1800)
    if result.returncode != 0:
        raise OpenHandsRuntimeError(
            f"OpenHands package installation failed: {_command_detail(result)}"
        )


def install_openhands_runtime(
    *,
    paths: OpenHandsRuntimePaths | None = None,
    source_ref: str = OPENHANDS_SOURCE_COMMIT,
    python_executable: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Install or reconcile the user-scoped, pinned OpenHands runtime.

    The source checkout is pinned independently from the package distribution
    versions.  This keeps the reproducible upstream source reference visible
    without replacing the tested Hafiye package pins with an arbitrary source
    build.
    """

    paths = paths or get_openhands_runtime_paths()
    if not source_ref or len(source_ref) != 40 or any(
        character not in "0123456789abcdefABCDEF" for character in source_ref
    ):
        raise OpenHandsRuntimeError("OpenHands source_ref must be a 40-character commit SHA")

    actual_source_commit = _ensure_source_checkout(paths, source_ref)
    _ensure_virtualenv(paths, python_executable)
    package_versions = _probe_packages(paths.python)
    packages_installed = False
    if force or not _packages_match(package_versions):
        _install_packages(paths)
        packages_installed = True

    manifest = write_openhands_runtime_manifest(
        paths=paths,
        source_commit=actual_source_commit,
        requested_versions=OPENHANDS_REQUESTED_VERSIONS,
    )
    doctor = openhands_runtime_doctor(paths)
    doctor["manifest_written"] = str(manifest)
    doctor["packages_installed"] = packages_installed
    if not doctor.get("ready"):
        raise OpenHandsRuntimeError(
            "OpenHands runtime setup completed but doctor is not ready: "
            + "; ".join(doctor.get("blockers", []))
        )
    return doctor


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
            mismatched = [
                f"{name}={package_versions.get(name)!r} (expected {version})"
                for name, version in OPENHANDS_REQUESTED_VERSIONS.items()
                if package_versions.get(name) != version
            ]
            if mismatched:
                blockers.append(
                    "OpenHands managed runtime has unexpected package versions: "
                    + ", ".join(mismatched)
                )

    if not paths.manifest.is_file():
        blockers.append(f"runtime manifest is missing: {paths.manifest}")

    expected_source_commit = str(
        manifest.get("source_commit") or OPENHANDS_SOURCE_COMMIT
    )
    source_checkout_commit = _git_revision(paths.source_root)
    if source_checkout_commit != expected_source_commit:
        blockers.append(
            "OpenHands source checkout is not pinned to the managed commit: "
            f"{source_checkout_commit or 'missing'} (expected {expected_source_commit})"
        )

    requested_versions = manifest.get("requested_versions")
    if not isinstance(requested_versions, dict) or not requested_versions:
        requested_versions = dict(OPENHANDS_REQUESTED_VERSIONS)

    return {
        "ready": not blockers,
        "python": str(paths.python),
        "runtime_root": str(paths.runtime_root),
        "manifest": str(paths.manifest),
        "manifest_present": paths.manifest.is_file(),
        "source_checkout": str(paths.source_root),
        "source_checkout_commit": source_checkout_commit,
        "source_checkout_ready": source_checkout_commit == expected_source_commit,
        "packages": package_versions,
        "source": manifest.get("source", OPENHANDS_REPOSITORY),
        "source_commit": expected_source_commit,
        "requested_versions": requested_versions,
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
    "OPENHANDS_PACKAGE_VERSION",
    "OPENHANDS_REQUESTED_VERSIONS",
    "OPENHANDS_REPOSITORY",
    "OPENHANDS_SOURCE_COMMIT",
    "OpenHandsRuntimeError",
    "OpenHandsRuntimePaths",
    "get_openhands_runtime_paths",
    "install_openhands_runtime",
    "openhands_runtime_doctor",
    "openhands_runtime_ready",
    "write_openhands_runtime_manifest",
]
