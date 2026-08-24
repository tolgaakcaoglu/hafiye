"""Dependency and package-layout doctor used by the Debian installation.

This module intentionally uses only the Python standard library. It must be
usable before the optional Hafiye environment exists, so the package wrapper
can diagnose a fresh install and can create the user-scoped dependency venv
without importing the full Hermes application.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_EXTRAS = (
    "cron",
    "pty",
    "mcp",
    "acp",
    "web",
    "computer-use",
)
REQUIRED_IMPORTS = ("httpx", "pydantic", "rich", "yaml")
OPTIONAL_COMMANDS = (
    "curl",
    "git",
    "rg",
    "ffmpeg",
    "wpctl",
    "ydotool",
    "nvidia-smi",
    "cargo",
)


def package_root() -> Path:
    override = os.environ.get("HAFIYE_PACKAGE_ROOT", "").strip()
    return Path(override).expanduser() if override else Path("/usr/lib/hafiye")


def backend_root() -> Path:
    return package_root() / "backend"


def _check(name: str, *, required: bool, ok: bool, detail: str, path: str = "") -> dict[str, Any]:
    return {
        "name": name,
        "required": required,
        "ok": ok,
        "detail": detail,
        **({"path": path} if path else {}),
    }


def _command_check(command: str, *, required: bool = False) -> dict[str, Any]:
    resolved = shutil.which(command)
    if resolved:
        return _check(command, required=required, ok=True, detail="available", path=resolved)
    return _check(command, required=required, ok=False, detail="not found")


def _python_check() -> dict[str, Any]:
    version = platform.python_version()
    supported = (3, 11) <= sys.version_info[:2] < (3, 14)
    return _check(
        "python",
        required=True,
        ok=supported,
        detail=(
            f"{version} ({sys.executable})"
            if supported
            else f"{version} is outside the supported 3.11–3.13 range"
        ),
        path=sys.executable,
    )


def _source_check() -> list[dict[str, Any]]:
    root = backend_root()
    expected = (
        "pyproject.toml",
        "uv.lock",
        "hermes_cli/main.py",
        "hermes_cli/persistent_gateway.py",
        "hafiye_rootd.py",
    )
    missing = [relative for relative in expected if not (root / relative).is_file()]
    return [
        _check(
            "backend_source",
            required=True,
            ok=not missing,
            detail="source and lock metadata present" if not missing else f"missing: {', '.join(missing)}",
            path=str(root),
        ),
        _check(
            "desktop_binary",
            required=True,
            ok=(root.parent / "desktop" / "hafiye-desktop").is_file()
            and os.access(root.parent / "desktop" / "hafiye-desktop", os.X_OK)
            and (root.parent / "desktop" / "resources" / "app.asar").is_file(),
            detail=(
                "Electron Desktop resources present"
                if (root.parent / "desktop" / "resources" / "app.asar").is_file()
                else "Electron Desktop resources are missing"
            ),
            path=str(root.parent / "desktop"),
        ),
    ]


def _layout_checks() -> list[dict[str, Any]]:
    root = package_root()
    paths = (
        ("hafiye_launcher", root / "bin" / "hafiye"),
        ("desktop_launcher", root / "bin" / "hafiye-desktop"),
        ("dependency_installer", root / "bin" / "hafiye-dependency-doctor"),
        ("gateway_user_unit", Path("/usr/lib/systemd/user/hafiye-gateway.service") if root == Path("/usr/lib/hafiye") else root / "systemd-user" / "hafiye-gateway.service"),
        ("root_broker_template", root / "systemd" / "hafiye-rootd.service.in"),
        ("desktop_entry", root / "desktop-entry" / "hafiye.desktop"),
        ("autostart_entry", root / "desktop-entry" / "hafiye-autostart.desktop"),
        ("package_manifest", root / "package-manifest.json"),
    )
    checks = []
    for name, path in paths:
        checks.append(
            _check(
                name,
                required=True,
                ok=path.exists(),
                detail="installed" if path.exists() else "missing from package",
                path=str(path),
            )
        )
    return checks


def _dependency_check() -> dict[str, Any]:
    missing = []
    for module in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(module)
    candidate = os.environ.get("HAFIYE_PYTHON_VENV", "") or ""
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv and candidate:
        in_venv = Path(sys.executable).resolve().as_posix().startswith(Path(candidate).expanduser().resolve().as_posix())
    if missing:
        detail = f"missing imports: {', '.join(missing)}; run hafiye package install"
    elif not in_venv:
        detail = "imports available from the selected interpreter"
    else:
        detail = "core imports available in the user dependency environment"
    return _check(
        "python_dependencies",
        required=True,
        ok=not missing,
        detail=detail,
        path=sys.executable,
    )


def diagnose() -> dict[str, Any]:
    checks = [_python_check(), *_source_check(), *_layout_checks(), _dependency_check()]
    checks.append(_command_check("systemctl", required=True))
    checks.append(_command_check("systemd-run", required=False))
    checks.extend(_command_check(command) for command in OPTIONAL_COMMANDS)
    blockers = [
        f"{check['name']}: {check['detail']}"
        for check in checks
        if check["required"] and not check["ok"]
    ]
    return {
        "ok": not blockers,
        "package_root": str(package_root()),
        "backend_root": str(backend_root()),
        "python": sys.executable,
        "checks": checks,
        "blockers": blockers,
        "warnings": [
            f"{check['name']}: {check['detail']}"
            for check in checks
            if not check["required"] and not check["ok"]
        ],
    }


def _run(command: list[str], *, cwd: Path | None = None) -> None:
    print("→", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def install_dependencies(extras: list[str]) -> int:
    uv = shutil.which("uv")
    if not uv:
        print("Hafiye dependency install requires uv; install uv and rerun `hafiye package install`.", file=sys.stderr)
        return 2
    python = Path(sys.executable)
    target = Path(
        os.environ.get("HAFIYE_PYTHON_VENV", "")
        or (Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "hafiye" / "python-venv")
    ).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target_python = target / "bin" / "python"
    if not target_python.exists():
        _run([uv, "venv", "--python", str(python), str(target)])

    with tempfile.TemporaryDirectory(prefix="hafiye-deps-") as temporary:
        requirements = Path(temporary) / "requirements.txt"
        export = [
            uv,
            "export",
            "--project",
            str(backend_root()),
            "--frozen",
            "--no-dev",
            "--no-emit-project",
            "--format",
            "requirements.txt",
            "--output-file",
            str(requirements),
        ]
        for extra in extras:
            export.extend(("--extra", extra))
        _run(export)
        _run([uv, "pip", "install", "--python", str(target_python), "--requirement", str(requirements)])
    marker = target / "hafiye-dependencies.json"
    marker.write_text(
        json.dumps({"extras": extras, "python": str(target_python)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Installed Hafiye Python dependencies into {target}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hafiye Debian package dependency doctor")
    subparsers = parser.add_subparsers(dest="command")
    doctor = subparsers.add_parser("doctor", help="inspect package, Python, and host dependencies")
    doctor.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    install = subparsers.add_parser("install", help="install locked Python dependencies into the user venv")
    install.add_argument(
        "--extra",
        action="append",
        dest="extras",
        choices=sorted({"cron", "pty", "mcp", "acp", "web", "computer-use"}),
        help="optional dependency extra; may be repeated",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    command = args.command or "doctor"
    if command == "install":
        return install_dependencies(args.extras or list(DEFAULT_EXTRAS))
    result = diagnose()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Hafiye package doctor: {'OK' if result['ok'] else 'BLOCKED'}")
        for check in result["checks"]:
            state = "ok" if check["ok"] else ("required" if check["required"] else "warning")
            print(f"  [{state}] {check['name']}: {check['detail']}")
        if result["blockers"]:
            print("Blockers:")
            for blocker in result["blockers"]:
                print(f"  - {blocker}")
        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
