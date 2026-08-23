"""Tests for Hafiye's public identity and XDG root compatibility layer."""

from pathlib import Path
from types import SimpleNamespace

from hermes_cli.migrate import cmd_migrate_legacy_home
from hermes_constants import (
    get_config_path,
    get_env_path,
    get_hafiye_cache_home,
    get_hafiye_config_home,
    get_hafiye_data_home,
    get_hafiye_state_home,
    get_hermes_home,
)


def test_default_xdg_roots_are_separate(monkeypatch, tmp_path):
    monkeypatch.delenv("HERMES_HOME", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    assert get_hafiye_config_home() == tmp_path / "config" / "hafiye"
    assert get_hafiye_data_home() == tmp_path / "data" / "hafiye"
    assert get_hafiye_state_home() == tmp_path / "state" / "hafiye"
    assert get_hafiye_cache_home() == tmp_path / "cache" / "hafiye"
    assert get_hermes_home() == get_hafiye_data_home()
    assert get_config_path() == tmp_path / "config" / "hafiye" / "config.yaml"
    assert get_env_path() == tmp_path / "config" / "hafiye" / ".env"


def test_explicit_hermes_home_keeps_profile_single_root(monkeypatch, tmp_path):
    home = tmp_path / "profile"
    monkeypatch.setenv("HERMES_HOME", str(home))

    assert get_hafiye_config_home() == home
    assert get_hafiye_data_home() == home
    assert get_hafiye_state_home() == home
    assert get_hafiye_cache_home() == home
    assert get_config_path() == home / "config.yaml"
    assert get_env_path() == home / ".env"


def test_legacy_home_import_is_preview_then_non_destructive_apply(monkeypatch, tmp_path, capsys):
    legacy = tmp_path / ".hermes"
    legacy.mkdir()
    (legacy / "config.yaml").write_text("model:\n  provider: local\n", encoding="utf-8")
    (legacy / ".env").write_text("OPENAI_API_KEY=secret\n", encoding="utf-8")
    (legacy / "state.db").write_bytes(b"sqlite-placeholder")
    (legacy / "cache").mkdir()
    (legacy / "cache" / "model.json").write_text("{}", encoding="utf-8")
    (legacy / "MEMORY.md").write_text("keep me\n", encoding="utf-8")

    monkeypatch.delenv("HERMES_HOME", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg-config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg-data"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg-state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg-cache"))

    args = SimpleNamespace(source=str(legacy), apply=False, dry_run=True, overwrite=False)
    assert cmd_migrate_legacy_home(args) == 0
    assert not (tmp_path / "xdg-config" / "hafiye" / "config.yaml").exists()
    assert "Dry-run mode" in capsys.readouterr().out

    args.apply = True
    args.dry_run = False
    assert cmd_migrate_legacy_home(args) == 0

    config_root = tmp_path / "xdg-config" / "hafiye"
    data_root = tmp_path / "xdg-data" / "hafiye"
    state_root = tmp_path / "xdg-state" / "hafiye"
    cache_root = tmp_path / "xdg-cache" / "hafiye"
    assert (config_root / "config.yaml").read_text(encoding="utf-8").startswith("model:")
    assert (config_root / ".env").read_text(encoding="utf-8") == "OPENAI_API_KEY=secret\n"
    assert (state_root / "state.db").read_bytes() == b"sqlite-placeholder"
    assert (cache_root / "model.json").read_text(encoding="utf-8") == "{}"
    assert (data_root / "MEMORY.md").read_text(encoding="utf-8") == "keep me\n"
    assert (config_root / ".legacy-hermes-import.json").exists()
    assert (config_root / ".env").stat().st_mode & 0o077 == 0
