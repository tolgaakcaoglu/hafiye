from __future__ import annotations

import os
from pathlib import Path
import subprocess

from hermes_cli import openhands_runtime


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_openhands_runtime_doctor_reports_missing_user_scoped_setup(tmp_path: Path):
    paths = openhands_runtime.OpenHandsRuntimePaths.from_roots(
        tmp_path / "data", tmp_path / "state"
    )

    result = openhands_runtime.openhands_runtime_doctor(paths)

    assert result["ready"] is False
    assert result["manifest_present"] is False
    assert result["source_checkout_ready"] is False
    assert any("managed OpenHands Python" in blocker for blocker in result["blockers"])
    assert any("source checkout" in blocker for blocker in result["blockers"])


def test_openhands_runtime_install_pins_source_and_preserves_package_versions(
    tmp_path: Path, monkeypatch
):
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git("init", cwd=upstream)
    _git("config", "user.email", "test@example.invalid", cwd=upstream)
    _git("config", "user.name", "Hafiye test", cwd=upstream)
    (upstream / "README.md").write_text("OpenHands fixture\n", encoding="utf-8")
    _git("add", "README.md", cwd=upstream)
    _git("commit", "-m", "fixture", cwd=upstream)
    source_ref = _git("rev-parse", "HEAD", cwd=upstream)

    paths = openhands_runtime.OpenHandsRuntimePaths.from_roots(
        tmp_path / "data", tmp_path / "state"
    )
    fake_python = paths.venv_root / "bin" / "python"

    monkeypatch.setattr(openhands_runtime, "OPENHANDS_REPOSITORY", str(upstream))
    monkeypatch.setattr(
        openhands_runtime,
        "_ensure_virtualenv",
        lambda _paths, _python=None: (
            fake_python.parent.mkdir(parents=True, exist_ok=True),
            fake_python.touch(),
            os.chmod(fake_python, 0o700),
        ),
    )
    monkeypatch.setattr(
        openhands_runtime,
        "_probe_packages",
        lambda _python: dict(openhands_runtime.OPENHANDS_REQUESTED_VERSIONS),
    )

    result = openhands_runtime.install_openhands_runtime(
        paths=paths,
        source_ref=source_ref,
    )

    assert result["ready"] is True
    assert result["source_checkout_commit"] == source_ref
    assert result["packages_installed"] is False
    assert result["requested_versions"] == openhands_runtime.OPENHANDS_REQUESTED_VERSIONS
    assert paths.manifest.is_file()
