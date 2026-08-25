import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import hafiye_rootd

from scripts.build_deb import build_package


REPO_ROOT = Path(__file__).resolve().parents[2]


def _fixture_desktop(tmp_path: Path) -> Path:
    desktop = tmp_path / "linux-unpacked"
    (desktop / "resources").mkdir(parents=True)
    binary = desktop / "hafiye-desktop"
    binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
    sandbox = desktop / "chrome-sandbox"
    sandbox.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    sandbox.chmod(sandbox.stat().st_mode | stat.S_IXUSR)
    (desktop / "resources" / "app.asar").write_bytes(b"fixture")
    return desktop


def _build_fixture_package(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    output = tmp_path / "hafiye.deb"
    manifest = build_package(
        output=output,
        desktop_dir=_fixture_desktop(tmp_path),
        version="0.20.5",
        architecture="amd64",
    )
    assert output.is_file()
    return output, manifest


def test_deb_contains_the_roadmap_packaging_contract(tmp_path):
    package, manifest = _build_fixture_package(tmp_path)
    contents = subprocess.run(
        ["dpkg-deb", "--contents", str(package)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout

    required_paths = (
        "./usr/lib/hafiye/desktop/hafiye-desktop",
        "./usr/lib/hafiye/desktop/chrome-sandbox",
        "./usr/lib/hafiye/backend/hermes_cli/main.py",
        "./usr/lib/hafiye/backend/hafiye_rootd.py",
        "./usr/lib/hafiye/bin/hafiye",
        "./usr/lib/hafiye/bin/hafiye-dependency-doctor",
        "./usr/lib/systemd/user/hafiye-gateway.service",
        "./usr/lib/hafiye/systemd/hafiye-rootd.service.in",
        "./usr/share/applications/hafiye.desktop",
        "./etc/xdg/autostart/hafiye.desktop",
        "./usr/share/icons/hicolor/1024x1024/apps/hafiye.png",
        "./usr/share/doc/hafiye/copyright",
        "./usr/share/doc/hafiye/LICENSE",
        "./usr/lib/hafiye/package-manifest.json",
    )
    for path in required_paths:
        assert path in contents

    assert manifest["pinned_upstream_commit"] == "f293e7206b4ddd66042329442c6afebc19a8808d"
    assert manifest["baseline_merge_commit"] == "2ac06b131a237916432503ac67bbcada6dbea39e"
    assert manifest["desktop_runtime_policy"] == "download-on-first-run"

    control = subprocess.run(
        ["dpkg-deb", "--field", str(package)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    assert "Package: hafiye\n" in control
    assert "Version: 0.20.5-1\n" in control
    assert "Architecture: amd64\n" in control
    assert "Depends: python3 (>= 3.11), python3 (<< 3.14), python3-venv, systemd\n" in control


def test_deb_preserves_electron_sandbox_setuid_mode(tmp_path):
    package, _ = _build_fixture_package(tmp_path)
    extracted = tmp_path / "sandbox-root"
    extracted.mkdir()
    subprocess.run(["dpkg-deb", "--extract", str(package), str(extracted)], check=True)

    sandbox = extracted / "usr/lib/hafiye/desktop/chrome-sandbox"
    assert stat.S_IMODE(sandbox.stat().st_mode) == 0o4755


def test_extracted_deb_launcher_and_doctor_use_the_same_backend(tmp_path):
    package, _ = _build_fixture_package(tmp_path)
    extracted = tmp_path / "root"
    extracted.mkdir()
    subprocess.run(["dpkg-deb", "--extract", str(package), str(extracted)], check=True)

    env = os.environ.copy()
    env.update(
        {
            "HAFIYE_PACKAGE_ROOT": str(extracted / "usr/lib/hafiye"),
            "HAFIYE_PACKAGE_PYTHON": sys.executable,
            "HAFIYE_PYTHON_VENV": str(Path(sys.executable).resolve().parents[1]),
        }
    )
    result = subprocess.run(
        [str(extracted / "usr/bin/hafiye"), "package", "doctor", "--json"],
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blockers"] == []
    assert payload["backend_root"] == str(extracted / "usr/lib/hafiye/backend")

    if shutil.which("fakeroot") and shutil.which("dpkg"):
        install_root = tmp_path / "dpkg-root"
        (install_root / "var/lib/dpkg").mkdir(parents=True)
        (install_root / "var/lib/dpkg/status").write_text("", encoding="utf-8")
        unpack = subprocess.run(
            [
                "fakeroot",
                "dpkg",
                f"--root={install_root}",
                "--force-not-root",
                "--force-script-chrootless",
                "--force-depends",
                "--unpack",
                str(package),
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        assert unpack.returncode == 0, unpack.stderr + unpack.stdout
        configure = subprocess.run(
            [
                "fakeroot",
                "dpkg",
                f"--root={install_root}",
                "--force-not-root",
                "--force-script-chrootless",
                "--force-depends",
                "--configure",
                "hafiye",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        assert configure.returncode == 0, configure.stderr + configure.stdout
        assert (install_root / "usr/lib/hafiye/package-manifest.json").is_file()

    manifest = json.loads(
        (extracted / "usr/lib/hafiye/package-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["package"] == "hafiye"


def test_rootd_sudo_handoff_is_import_path_independent(monkeypatch):
    calls = []
    monkeypatch.setattr(hafiye_rootd.shutil, "which", lambda name: "/usr/bin/sudo" if name == "sudo" else None)

    def fake_run(command, *, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(hafiye_rootd.subprocess, "run", fake_run)
    assert hafiye_rootd._run_sudo_install(["--install-system", "--allowed-uid", "1000"]) == 0
    assert calls == [
        [
            "/usr/bin/sudo",
            sys.executable,
            str(Path(hafiye_rootd.__file__).resolve()),
            "--install-system",
            "--allowed-uid",
            "1000",
        ]
    ]
