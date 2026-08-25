#!/usr/bin/env python3
"""Build the Hafiye Ubuntu/Debian package described by the master roadmap.

The Electron builder's Linux artifact contains only the Desktop shell. This
outer package adds the Hafiye backend, user-service and root-broker launch
paths, XDG entries, icons, and notices while leaving managed model/voice/CUA
runtimes to the first-run dependency/runtime installers.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "packaging" / "debian"
RUNTIME_DIRS = (
    "agent",
    "acp_adapter",
    "cron",
    "gateway",
    "hermes_cli",
    "plugins",
    "providers",
    "skills",
    "optional-skills",
    "optional-mcps",
    "tools",
    "tui_gateway",
)
EXCLUDED_DIRS = {
    "tests",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
TOP_LEVEL_SUFFIXES = {".py", ".toml", ".lock", ".txt", ".yaml", ".yml"}
TOP_LEVEL_FILES = {
    "hermes",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "pyproject.toml",
    "setup.py",
    "uv.lock",
    ".python-version",
}


def _debian_architecture(value: str | None) -> str:
    if value:
        return value
    mapping = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "armv7l": "armhf",
        "armv6l": "armel",
    }
    machine = platform.machine().lower()
    if machine not in mapping:
        raise SystemExit(f"Unsupported Debian architecture for {machine!r}; pass --arch explicitly")
    return mapping[machine]


def _project_version() -> str:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"(?m)^version\s*=\s*[\"']([^\"']+)[\"']\s*$", text)
    if not match:
        raise SystemExit("Could not read project version from pyproject.toml")
    return match.group(1)


def _git_value(command: list[str], fallback: str = "unknown") -> str:
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return fallback
    return result.stdout.strip() or fallback


def _upstream_value(label: str) -> str:
    text = (REPO_ROOT / "UPSTREAM.md").read_text(encoding="utf-8")
    pattern = rf"(?m)^- {re.escape(label)}:\s*\n\s*([0-9a-f]{{7,40}})\s*$"
    match = re.search(pattern, text)
    return match.group(1) if match else "unknown"


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.unlink(missing_ok=True)
        destination.symlink_to(os.readlink(source))
    else:
        shutil.copy2(source, destination)


def _iter_files(directory: Path) -> Iterable[Path]:
    for path in sorted(directory.rglob("*")):
        relative_parts = set(path.relative_to(directory).parts)
        if relative_parts & EXCLUDED_DIRS:
            continue
        if path.is_file() or path.is_symlink():
            yield path


def _copy_backend(stage: Path) -> None:
    backend = stage / "usr" / "lib" / "hafiye" / "backend"
    backend.mkdir(parents=True, exist_ok=True)

    for entry in REPO_ROOT.iterdir():
        if entry.name.startswith(".") and entry.name not in {".python-version"}:
            continue
        if entry.is_file() and (entry.name in TOP_LEVEL_FILES or entry.suffix in TOP_LEVEL_SUFFIXES):
            _copy_file(entry, backend / entry.name)

    for relative in RUNTIME_DIRS:
        source = REPO_ROOT / relative
        if not source.is_dir():
            continue
        for file_path in _iter_files(source):
            _copy_file(file_path, backend / file_path.relative_to(REPO_ROOT))

    # The installer itself is part of the backend/dependency boundary. Keep
    # runtime scripts but omit CI/test harnesses and their fixture payloads.
    scripts = REPO_ROOT / "scripts"
    for file_path in _iter_files(scripts):
        relative = file_path.relative_to(scripts)
        if relative.parts[:1] in {("tests",), ("ci",)}:
            continue
        _copy_file(file_path, backend / "scripts" / relative)

    # The package doctor is invoked before third-party dependencies exist and
    # is intentionally shipped even when packaging/debian is not tracked in a
    # source archive yet.
    doctor = TEMPLATE_ROOT / "dependency_doctor.py"
    _copy_file(doctor, backend / "packaging" / "debian" / doctor.name)


def _copy_desktop(stage: Path, desktop_dir: Path) -> None:
    binary = desktop_dir / "hafiye-desktop"
    asar = desktop_dir / "resources" / "app.asar"
    if not binary.is_file() or not asar.is_file():
        raise SystemExit(
            f"Desktop pack is incomplete at {desktop_dir}; run `cd apps/desktop && npm run pack` first"
        )
    destination = stage / "usr" / "lib" / "hafiye" / "desktop"
    shutil.copytree(desktop_dir, destination, symlinks=True)

    # Electron's Linux renderer sandbox refuses to start unless this helper is
    # installed root-owned with the setuid bit.  The source unpacked tree is
    # normally owned by the unprivileged build user, but dpkg preserves the
    # mode from the staging tree and --root-owner-group supplies root:root in
    # the resulting package.  Set the mode after copying so Debian packages
    # built without a root build environment remain launchable after install.
    sandbox = destination / "chrome-sandbox"
    if sandbox.exists() or sandbox.is_symlink():
        if sandbox.is_symlink() or not stat.S_ISREG(sandbox.stat(follow_symlinks=False).st_mode):
            raise SystemExit(f"Electron sandbox helper must be a regular file: {sandbox}")
        sandbox.chmod(0o4755)


def _write_text(stage: Path, relative: str, text: str, *, mode: int = 0o644) -> Path:
    path = stage / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)
    return path


def _install_templates(stage: Path, version: str, architecture: str, manifest: dict[str, str]) -> None:
    control = (TEMPLATE_ROOT / "control.in").read_text(encoding="utf-8")
    control = control.replace("@VERSION@", f"{version}-1").replace("@ARCH@", architecture)
    _write_text(stage, "DEBIAN/control", control)
    for name in ("postinst", "prerm", "postrm"):
        source = TEMPLATE_ROOT / name
        _write_text(stage, f"DEBIAN/{name}", source.read_text(encoding="utf-8"), mode=0o755)

    package_root = "usr/lib/hafiye"
    bin_root = f"{package_root}/bin"
    for name in (
        "hafiye",
        "hafiye-python",
        "hafiye-dependency-doctor",
        "hafiye-gateway-run",
        "hafiye-rootd",
        "hafiye-rootd-activate",
        "hafiye-desktop",
        "hafiye-desktop-launcher",
    ):
        source = TEMPLATE_ROOT / name
        _write_text(stage, f"{bin_root}/{name}", source.read_text(encoding="utf-8"), mode=0o755)

    # Stable system-facing command names. The implementation stays under the
    # package root so the user can run the same package from a test root.
    for name in ("hafiye", "hafiye-desktop", "hafiye-rootd", "hafiye-rootd-activate"):
        target = f"../lib/hafiye/bin/{name}"
        link = stage / "usr" / "bin" / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.unlink(missing_ok=True)
        link.symlink_to(target)

    unit = (TEMPLATE_ROOT / "hafiye-gateway.service").read_text(encoding="utf-8")
    _write_text(stage, "usr/lib/systemd/user/hafiye-gateway.service", unit)
    _write_text(stage, f"{package_root}/systemd-user/hafiye-gateway.service", unit)
    rootd_template = (TEMPLATE_ROOT / "hafiye-rootd.service.in").read_text(encoding="utf-8")
    _write_text(stage, f"{package_root}/systemd/hafiye-rootd.service.in", rootd_template)

    for name in ("hafiye.desktop", "hafiye-autostart.desktop"):
        entry = (TEMPLATE_ROOT / name).read_text(encoding="utf-8")
        _write_text(stage, f"{package_root}/desktop-entry/{name}", entry)
        if name == "hafiye.desktop":
            _write_text(stage, f"usr/share/applications/{name}", entry)
        else:
            # Keep the conventional XDG autostart filename even though the
            # source template is named separately to distinguish it from the
            # launcher's application entry.
            _write_text(stage, "etc/xdg/autostart/hafiye.desktop", entry)

    _copy_file(REPO_ROOT / "apps" / "desktop" / "assets" / "hafiye-icon.png", stage / "usr/share/icons/hicolor/1024x1024/apps/hafiye.png")
    _copy_file(REPO_ROOT / "apps" / "desktop" / "assets" / "hafiye-icon.svg", stage / "usr/share/icons/hicolor/scalable/apps/hafiye.svg")

    docs = stage / "usr" / "share" / "doc" / "hafiye"
    docs.mkdir(parents=True, exist_ok=True)
    _copy_file(TEMPLATE_ROOT / "copyright", docs / "copyright")
    for name in ("LICENSE", "README.md", "UPSTREAM.md"):
        source = REPO_ROOT / name
        if source.is_file():
            _copy_file(source, docs / name)
    chromium_notice = stage / "usr" / "lib" / "hafiye" / "desktop" / "LICENSES.chromium.html"
    if chromium_notice.is_file():
        _copy_file(chromium_notice, docs / "LICENSES.chromium.html")

    _write_text(
        stage,
        f"{package_root}/package-manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )


def build_package(*, output: Path, desktop_dir: Path, version: str, architecture: str) -> dict[str, str]:
    source_commit = _git_value(["git", "rev-parse", "HEAD"])
    manifest = {
        "package": "hafiye",
        "version": version,
        "architecture": architecture,
        "source_commit": source_commit,
        "pinned_upstream_commit": _upstream_value("Pinned upstream commit"),
        "baseline_merge_commit": _upstream_value("Baseline merge commit"),
        "desktop_product": "Hafiye",
        "desktop_runtime_policy": "download-on-first-run",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hafiye-deb-") as temporary:
        stage = Path(temporary) / "root"
        stage.mkdir()
        _copy_backend(stage)
        _copy_desktop(stage, desktop_dir)
        _install_templates(stage, version, architecture, manifest)
        subprocess.run(
            ["dpkg-deb", "--build", "--root-owner-group", str(stage), str(output)],
            cwd=REPO_ROOT,
            check=True,
        )
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the Hafiye Ubuntu/Debian package")
    parser.add_argument("--output", type=Path, help="output .deb path (default: dist/hafiye_<version>_<arch>.deb)")
    parser.add_argument(
        "--desktop-dir",
        type=Path,
        default=REPO_ROOT / "apps" / "desktop" / "release" / "linux-unpacked",
        help="existing Electron linux-unpacked directory",
    )
    parser.add_argument("--version", default=None, help="override Debian package version")
    parser.add_argument("--arch", default=None, help="Debian architecture, e.g. amd64")
    parser.add_argument("--json", action="store_true", help="print build metadata as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    version = args.version or _project_version()
    architecture = _debian_architecture(args.arch)
    output = args.output or (REPO_ROOT / "dist" / f"hafiye_{version}_{architecture}.deb")
    manifest = build_package(
        output=output.expanduser().resolve(),
        desktop_dir=args.desktop_dir.expanduser().resolve(),
        version=version,
        architecture=architecture,
    )
    if args.json:
        print(json.dumps({"output": str(output.resolve()), **manifest}, indent=2, sort_keys=True))
    else:
        print(f"Built {output.resolve()}")
        print(f"Source commit: {manifest['source_commit']}")
        print(f"Pinned upstream: {manifest['pinned_upstream_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
