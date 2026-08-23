"""CLI handlers for ``hermes migrate ...``.

Currently exposes only ``hermes migrate xai`` — diagnoses and (with --apply)
rewrites references to xAI models retired on May 15, 2026.
"""
from __future__ import annotations

import sys
import json
import shutil
import stat
import time
from pathlib import Path
from typing import Any

from hermes_cli.colors import Colors, color
from hermes_cli.config import load_config
from hermes_constants import (
    get_hafiye_cache_home,
    get_hafiye_config_home,
    get_hafiye_data_home,
    get_hafiye_state_home,
)


def cmd_migrate(args: Any) -> int:
    """Dispatcher for ``hermes migrate <subtype>``."""
    sub = getattr(args, "migrate_type", None)
    if sub == "xai":
        return cmd_migrate_xai(args)
    if sub == "legacy-home":
        return cmd_migrate_legacy_home(args)

    print(
        "usage: hafiye migrate {legacy-home,xai} [options]",
        file=sys.stderr,
    )
    return 2


_LEGACY_HERMES_HOME = Path.home() / ".hermes"
_LEGACY_IMPORT_MARKER = ".legacy-hermes-import.json"


def _copy_plan_entry(source: Path, destination: Path, *, overwrite: bool) -> tuple[str, Path, Path]:
    """Return a planned action without following a source symlink."""
    if source.is_symlink():
        return ("skip-symlink", source, destination)
    if destination.exists() and not overwrite:
        return ("skip-existing", source, destination)
    return ("copy", source, destination)


def _legacy_home_plan(
    source: Path,
    *,
    config_home: Path,
    data_home: Path,
    state_home: Path,
    cache_home: Path,
    overwrite: bool,
) -> list[tuple[str, Path, Path]]:
    """Build a conservative, class-aware legacy ``~/.hermes`` import plan."""
    if not source.exists():
        return []

    plan: list[tuple[str, Path, Path]] = []

    # Configuration and credentials belong in the XDG config root.
    for name in ("config.yaml", ".env"):
        path = source / name
        if path.exists():
            plan.append(_copy_plan_entry(path, config_home / name, overwrite=overwrite))

    # SQLite state is copied as a family so a cleanly stopped WAL database can
    # be imported without silently dropping its journal sidecars.
    for path in sorted(source.glob("state.db*")):
        plan.append(_copy_plan_entry(path, state_home / path.name, overwrite=overwrite))

    # Legacy cache layouts map into the disposable cache root.  Preserve the
    # directory names for future cleanup and avoid nesting ``cache/cache``.
    for name in ("cache", "image_cache", "audio_cache"):
        path = source / name
        if path.exists():
            destination = cache_home if name == "cache" else cache_home / name
            plan.append(_copy_plan_entry(path, destination, overwrite=overwrite))

    excluded = {"config.yaml", ".env", "cache", "image_cache", "audio_cache"}
    for path in sorted(source.iterdir()):
        if path.name in excluded or path.name.startswith("state.db"):
            continue
        plan.append(_copy_plan_entry(path, data_home / path.name, overwrite=overwrite))
    return plan


def _apply_legacy_home_plan(plan: list[tuple[str, Path, Path]]) -> tuple[int, int]:
    """Apply a previously reviewed plan and return ``(copied, skipped)``."""
    copied = 0
    skipped = 0
    for action, source, destination in plan:
        if action != "copy":
            skipped += 1
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)
        if destination.name == ".env":
            destination.chmod(stat.S_IRUSR | stat.S_IWUSR)
        copied += 1
    return copied, skipped


def cmd_migrate_legacy_home(args: Any) -> int:
    """Preview or import a legacy ``~/.hermes`` profile into Hafiye roots."""
    source = Path(getattr(args, "source", "") or _LEGACY_HERMES_HOME).expanduser()
    config_home = get_hafiye_config_home()
    data_home = get_hafiye_data_home()
    state_home = get_hafiye_state_home()
    cache_home = get_hafiye_cache_home()
    overwrite = bool(getattr(args, "overwrite", False))
    dry_run = bool(getattr(args, "dry_run", False)) or not bool(getattr(args, "apply", False))
    marker = config_home / _LEGACY_IMPORT_MARKER

    print()
    print(color("◆ Hermes → Hafiye data import", Colors.CYAN, Colors.BOLD))
    print(f"  Source: {source}")
    print(f"  Config: {config_home}")
    print(f"  Data:   {data_home}")
    print(f"  State:  {state_home}")
    print(f"  Cache:  {cache_home}")
    print()

    if source.resolve() == data_home.resolve():
        print(color("  Source and destination are the same; nothing to import.", Colors.YELLOW))
        return 0
    if marker.exists() and not overwrite:
        print(color(f"  Import already recorded in {marker}; use --overwrite to review again.", Colors.YELLOW))
        return 0
    if not source.is_dir():
        print(color("  Legacy Hermes home was not found; no import is needed.", Colors.DIM))
        return 0

    plan = _legacy_home_plan(
        source,
        config_home=config_home,
        data_home=data_home,
        state_home=state_home,
        cache_home=cache_home,
        overwrite=overwrite,
    )
    if not plan:
        print(color("  No importable files were found.", Colors.DIM))
        return 0

    for action, src, dst in plan:
        label = "copy" if action == "copy" else action.replace("-", " ")
        print(f"  {label:14} {src} → {dst}")

    if dry_run:
        print()
        print(color("Dry-run mode — no files were written.", Colors.DIM))
        print(color("Re-run with `hafiye migrate legacy-home --apply` to import the plan.", Colors.DIM))
        return 0

    copied, skipped = _apply_legacy_home_plan(plan)
    config_home.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps(
            {
                "source": str(source),
                "data_home": str(data_home),
                "config_home": str(config_home),
                "state_home": str(state_home),
                "cache_home": str(cache_home),
                "copied": copied,
                "skipped": skipped,
                "completed_at": int(time.time()),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    marker.chmod(stat.S_IRUSR | stat.S_IWUSR)
    print()
    print(color(f"✓ Imported {copied} item(s); skipped {skipped} existing/symlink item(s).", Colors.GREEN))
    print(color(f"  Import record: {marker}", Colors.DIM))
    return 0


def cmd_migrate_xai(args: Any) -> int:
    """Run xAI May-15 model migration in dry-run or apply mode."""
    from hermes_cli.xai_retirement import (
        MIGRATION_GUIDE_URL,
        RETIREMENT_DATE,
        apply_migration,
        find_retired_xai_refs,
        format_issue,
    )

    apply = bool(getattr(args, "apply", False))
    no_backup = bool(getattr(args, "no_backup", False))

    config = load_config()
    issues = find_retired_xai_refs(config)

    print()
    print(color(
        f"◆ xAI Model Retirement Migration ({RETIREMENT_DATE})",
        Colors.CYAN, Colors.BOLD,
    ))
    print()

    if not issues:
        print(f"  {color('✓', Colors.GREEN)} No retired xAI models in config — nothing to migrate.")
        return 0

    print(f"  Found {len(issues)} retired xAI model reference(s):")
    print()
    for issue in issues:
        print(f"    {color('⚠', Colors.YELLOW)} {format_issue(issue)}")
    print()
    print(f"    {color('→', Colors.CYAN)} Migration guide: {MIGRATION_GUIDE_URL}")
    print()

    config_path = _resolve_config_path()

    if not apply:
        print(color("Dry-run mode — no changes written.", Colors.DIM))
        print(color(
            "Re-run with `hermes migrate xai --apply` to rewrite "
            f"{config_path} in-place (backup created automatically).",
            Colors.DIM,
        ))
        return 0

    if not config_path or not config_path.exists():
        print(
            f"  {color('✗', Colors.RED)} Could not locate config.yaml "
            f"(looked at: {config_path})",
            file=sys.stderr,
        )
        return 1

    try:
        result = apply_migration(
            config_path=config_path,
            issues=issues,
            backup=not no_backup,
        )
    except Exception as exc:
        print(
            f"  {color('✗', Colors.RED)} Migration failed: {exc}",
            file=sys.stderr,
        )
        return 1

    if not result.config_changed:
        print(f"  {color('⚠', Colors.YELLOW)} No changes written.")
        return 0

    if result.backup_path is not None:
        print(f"  {color('✓', Colors.GREEN)} Backup: {result.backup_path}")
    print(
        f"  {color('✓', Colors.GREEN)} Updated {len(result.issues_resolved)} "
        f"slot(s) in {result.file_path}"
    )
    print()
    print(color(
        "Run `hermes doctor` to confirm no retired xAI models remain.",
        Colors.DIM,
    ))
    return 0


def _resolve_config_path() -> Path:
    """Best-effort: locate the active config.yaml on disk."""
    from hermes_cli.config import get_hermes_home

    return get_hermes_home() / "config.yaml"
