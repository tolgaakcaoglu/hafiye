"""P5 tests for Hafiye provider credentials in Linux Secret Service."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from hermes_cli import hafiye_keyring


class _MissingPasswordError(Exception):
    pass


class _FakeKeyringBackend:
    __module__ = "keyring.backends.SecretService"

    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str):
        return self.values.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self.values[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        if (service, username) not in self.values:
            raise _MissingPasswordError()
        del self.values[(service, username)]


class _FakeKeyringModule:
    __version__ = "test"

    class errors:
        PasswordDeleteError = _MissingPasswordError

    def __init__(self, backend: _FakeKeyringBackend) -> None:
        self.backend = backend

    def get_keyring(self):
        return self.backend

    def get_password(self, service: str, username: str):
        return self.backend.get_password(service, username)

    def set_password(self, service: str, username: str, password: str) -> None:
        self.backend.set_password(service, username, password)

    def delete_password(self, service: str, username: str) -> None:
        self.backend.delete_password(service, username)


def _install_fake_keyring(monkeypatch):
    backend = _FakeKeyringBackend()
    fake_module = _FakeKeyringModule(backend)
    monkeypatch.setattr(hafiye_keyring, "_keyring_module", lambda: fake_module)
    return backend


def test_keyring_reference_config_never_contains_secret(tmp_path: Path, monkeypatch) -> None:
    backend = _install_fake_keyring(monkeypatch)
    ref = hafiye_keyring.secret_ref_for_env("GEMINI_API_KEY", tmp_path)

    hafiye_keyring.put_secret(ref, "gemini-test-secret")
    assert hafiye_keyring.get_secret(ref) == "gemini-test-secret"
    assert hafiye_keyring.ensure_secret_reference("GEMINI_API_KEY", tmp_path) == ref

    config_text = (tmp_path / "config.yaml").read_text(encoding="utf-8")
    config = yaml.safe_load(config_text)
    assert "gemini-test-secret" not in config_text
    assert config["secrets"]["keyring"]["credentials"] == {
        "GEMINI_API_KEY": ref
    }
    assert backend.values

    assert hafiye_keyring.delete_secret(ref) is True
    assert hafiye_keyring.remove_secret_reference("GEMINI_API_KEY", tmp_path) is True
    assert "secrets" not in yaml.safe_load(
        (tmp_path / "config.yaml").read_text(encoding="utf-8")
    )


def test_provider_lifecycle_migrates_dotenv_to_keyring(tmp_path: Path, monkeypatch) -> None:
    backend = _install_fake_keyring(monkeypatch)
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    from hermes_cli.config import save_env_value
    from hermes_cli.credential_lifecycle import (
        remove_provider_env_credential,
        save_provider_env_credential,
    )

    save_env_value("GEMINI_API_KEY", "legacy-gemini-secret")
    (tmp_path / "config.yaml").write_text(
        "model:\n  provider: gemini\n  api_key: new-gemini-secret\n",
        encoding="utf-8",
    )
    result = save_provider_env_credential("GEMINI_API_KEY", "new-gemini-secret")

    assert result["secret_store"] == "linux-secret-service"
    assert "GEMINI_API_KEY" not in (tmp_path / ".env").read_text(encoding="utf-8")
    assert "new-gemini-secret" not in (tmp_path / "config.yaml").read_text(
        encoding="utf-8"
    )
    ref = hafiye_keyring.secret_ref_for_env("GEMINI_API_KEY", tmp_path)
    assert backend.values[(hafiye_keyring.KEYRING_SERVICE, ref)] == "new-gemini-secret"
    assert os.environ["GEMINI_API_KEY"] == "new-gemini-secret"

    removed = remove_provider_env_credential("GEMINI_API_KEY")
    assert removed["found"] is True
    assert "GEMINI_API_KEY" not in os.environ
    assert "secrets" not in yaml.safe_load(
        (tmp_path / "config.yaml").read_text(encoding="utf-8")
    )


def test_default_xdg_provider_lifecycle_uses_config_root(
    tmp_path: Path, monkeypatch
) -> None:
    """The default XDG config/data split must not hide saved credentials."""
    backend = _install_fake_keyring(monkeypatch)
    config_home = tmp_path / "config"
    data_home = tmp_path / "data"
    (config_home / "hafiye").mkdir(parents=True)
    (data_home / "hafiye").mkdir(parents=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    monkeypatch.delenv("HERMES_HOME", raising=False)

    from hermes_cli.credential_lifecycle import save_provider_env_credential

    result = save_provider_env_credential("GEMINI_API_KEY", "xdg-gemini-secret")

    assert result["secret_store"] == "linux-secret-service"
    config_path = config_home / "hafiye" / "config.yaml"
    data_path = data_home / "hafiye" / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    ref = hafiye_keyring.secret_ref_for_env(
        "GEMINI_API_KEY", config_home / "hafiye"
    )
    assert config["secrets"]["keyring"]["credentials"]["GEMINI_API_KEY"] == ref
    assert backend.values[(hafiye_keyring.KEYRING_SERVICE, ref)] == "xdg-gemini-secret"
    assert not data_path.exists()


def test_provider_removal_cleans_orphaned_keyring_item(tmp_path: Path, monkeypatch) -> None:
    _install_fake_keyring(monkeypatch)
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    from hermes_cli.credential_lifecycle import remove_provider_env_credential

    ref = hafiye_keyring.secret_ref_for_env("GEMINI_API_KEY", tmp_path)
    hafiye_keyring.put_secret(ref, "orphaned-gemini-secret")

    removed = remove_provider_env_credential("GEMINI_API_KEY")

    assert removed["found"] is True
    assert hafiye_keyring.get_secret(ref) is None


def test_keyring_source_hydrates_provider_env(tmp_path: Path, monkeypatch) -> None:
    _install_fake_keyring(monkeypatch)
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    ref = hafiye_keyring.secret_ref_for_env("OPENAI_API_KEY", tmp_path)
    hafiye_keyring.put_secret(ref, "openai-test-secret")
    hafiye_keyring.ensure_secret_reference("OPENAI_API_KEY", tmp_path)

    from hermes_cli.env_loader import load_hermes_dotenv, reset_secret_source_cache

    reset_secret_source_cache()
    os.environ.pop("OPENAI_API_KEY", None)
    load_hermes_dotenv(hermes_home=tmp_path)

    assert os.environ["OPENAI_API_KEY"] == "openai-test-secret"
