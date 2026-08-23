"""Hafiye's Linux Secret Service storage boundary.

Hafiye provider credentials are stored in the user's Secret Service through
the Python ``keyring`` package.  ``config.yaml`` contains only stable
``keyring://`` references; the credential value is never serialized there.

The module is deliberately lazy about importing :mod:`keyring`.  Hermes has
many non-provider startup paths, and a missing Secret Service backend must not
make unrelated CLI commands fail.  Provider save/read paths receive a clear
``SecretStoreError`` instead.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, Optional

from hermes_constants import get_hermes_home
from utils import atomic_yaml_write, fast_safe_load

KEYRING_SERVICE = "hafiye"
KEYRING_REF_PREFIX = "keyring://hafiye/"

_ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_REF_RE = re.compile(
    r"^keyring://hafiye/env/(?P<home>[0-9a-f]{16})/(?P<env>[A-Za-z_][A-Za-z0-9_]*)$"
)


class SecretStoreError(RuntimeError):
    """The configured Linux Secret Service cannot be used safely."""


def _keyring_module():
    """Import keyring only when a Hafiye provider path actually needs it."""
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - exercised on lean installs
        raise SecretStoreError(
            "Python keyring is not installed; install Hafiye's locked dependencies."
        ) from exc
    return keyring


def _backend():
    keyring = _keyring_module()
    try:
        backend = keyring.get_keyring()
    except Exception as exc:  # noqa: BLE001 - backend errors are user diagnostics
        raise SecretStoreError(
            f"Linux Secret Service backend could not be initialized ({type(exc).__name__})."
        ) from exc
    module_name = type(backend).__module__
    class_name = type(backend).__name__
    if "SecretService" not in module_name:
        raise SecretStoreError(
            "Hafiye requires the Linux Secret Service keyring backend; "
            f"the active backend is {module_name}.{class_name}."
        )
    return keyring, backend


def backend_info() -> Dict[str, Any]:
    """Return non-secret diagnostics about the active keyring backend."""
    try:
        keyring, backend = _backend()
    except SecretStoreError as exc:
        return {
            "available": False,
            "secret_service": False,
            "backend": None,
            "error": str(exc),
        }
    backend_type = f"{type(backend).__module__}.{type(backend).__name__}"
    return {
        "available": True,
        "secret_service": True,
        "backend": backend_type,
        "priority": getattr(backend, "priority", None),
        "keyring_version": getattr(keyring, "__version__", None),
    }


def _home_fingerprint(home_path: Optional[str | Path] = None) -> str:
    home = Path(home_path) if home_path is not None else get_hermes_home()
    try:
        identity = str(home.expanduser().resolve())
    except OSError:
        identity = str(home.expanduser())
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def _validate_env_name(env_var: str) -> str:
    if not isinstance(env_var, str) or not _ENV_NAME_RE.fullmatch(env_var):
        raise ValueError(f"Invalid environment variable name: {env_var!r}")
    return env_var


def secret_ref_for_env(
    env_var: str, home_path: Optional[str | Path] = None
) -> str:
    """Return the stable, non-secret reference for one profile credential."""
    return (
        f"{KEYRING_REF_PREFIX}env/{_home_fingerprint(home_path)}/"
        f"{_validate_env_name(env_var)}"
    )


def _username_for_ref(ref: str) -> str:
    match = _REF_RE.fullmatch(ref.strip()) if isinstance(ref, str) else None
    if match is None:
        raise ValueError("Invalid Hafiye keyring reference")
    return ref.strip()


def _validate_ref_for_env(
    ref: str, env_var: str, home_path: Optional[str | Path] = None
) -> str:
    expected = secret_ref_for_env(env_var, home_path)
    if not isinstance(ref, str) or ref.strip() != expected:
        raise ValueError(f"Invalid Hafiye keyring reference for {env_var}")
    return expected


def get_secret(ref: str) -> Optional[str]:
    """Resolve one reference without logging or returning diagnostics on value."""
    username = _username_for_ref(ref)
    keyring, _backend_obj = _backend()
    try:
        value = keyring.get_password(KEYRING_SERVICE, username)
    except Exception as exc:  # noqa: BLE001 - normalize backend-specific errors
        raise SecretStoreError(
            f"Linux Secret Service read failed ({type(exc).__name__})."
        ) from exc
    if value is None or not str(value).strip():
        return None
    return str(value)


def put_secret(ref: str, value: str) -> None:
    """Store one provider credential in Secret Service."""
    username = _username_for_ref(ref)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Secret value must not be empty")
    keyring, _backend_obj = _backend()
    try:
        keyring.set_password(KEYRING_SERVICE, username, value)
    except Exception as exc:  # noqa: BLE001 - normalize backend-specific errors
        raise SecretStoreError(
            f"Linux Secret Service write failed ({type(exc).__name__})."
        ) from exc


def delete_secret(ref: str) -> bool:
    """Delete one credential; return False when it was not present."""
    username = _username_for_ref(ref)
    keyring, _backend_obj = _backend()
    try:
        keyring.delete_password(KEYRING_SERVICE, username)
    except Exception as exc:  # noqa: BLE001 - backend-specific missing errors vary
        errors = getattr(keyring, "errors", None)
        delete_error = getattr(errors, "PasswordDeleteError", None)
        if delete_error is not None and isinstance(exc, delete_error):
            return False
        if type(exc).__name__ in {"PasswordDeleteError", "ItemNotFound"}:
            return False
        raise SecretStoreError(
            f"Linux Secret Service delete failed ({type(exc).__name__})."
        ) from exc
    return True


def _config_path(home_path: Optional[str | Path] = None) -> Path:
    if home_path is not None:
        return Path(home_path) / "config.yaml"
    from hermes_cli.config import get_config_path

    return get_config_path()


def _read_raw_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        return {}
    try:
        with config_path.open(encoding="utf-8") as handle:
            data = fast_safe_load(handle) or {}
    except Exception as exc:  # noqa: BLE001 - preserve config write guard behavior
        raise SecretStoreError(
            f"Cannot read {config_path}: config parsing failed ({type(exc).__name__})."
        ) from exc
    if not isinstance(data, dict):
        raise SecretStoreError("config.yaml must contain a mapping at its root.")
    return data


def _write_raw_config(config_path: Path, data: Dict[str, Any]) -> None:
    from hermes_cli.config import require_readable_config_before_write

    require_readable_config_before_write(config_path)
    atomic_yaml_write(config_path, data, sort_keys=False, create_mode=0o600)


def keyring_references(
    home_path: Optional[str | Path] = None,
) -> Dict[str, str]:
    """Read valid env-var → reference bindings without touching secret values."""
    config = _read_raw_config(_config_path(home_path))
    secrets_cfg = config.get("secrets")
    keyring_cfg = secrets_cfg.get("keyring") if isinstance(secrets_cfg, dict) else None
    credentials = keyring_cfg.get("credentials") if isinstance(keyring_cfg, dict) else None
    if not isinstance(credentials, dict):
        return {}

    home = home_path if home_path is not None else get_hermes_home()
    result: Dict[str, str] = {}
    for env_var, ref in credentials.items():
        if not isinstance(env_var, str) or not _ENV_NAME_RE.fullmatch(env_var):
            continue
        if not isinstance(ref, str):
            continue
        try:
            result[env_var] = _validate_ref_for_env(ref, env_var, home)
        except ValueError:
            continue
    return result


def ensure_secret_reference(
    env_var: str, home_path: Optional[str | Path] = None
) -> str:
    """Add one keyring reference to raw config, preserving unrelated settings."""
    _validate_env_name(env_var)
    config_path = _config_path(home_path)
    config = _read_raw_config(config_path)
    secrets_cfg = config.setdefault("secrets", {})
    if not isinstance(secrets_cfg, dict):
        raise SecretStoreError("config.yaml secrets section must be a mapping.")
    keyring_cfg = secrets_cfg.setdefault("keyring", {})
    if not isinstance(keyring_cfg, dict):
        raise SecretStoreError("config.yaml secrets.keyring section must be a mapping.")
    credentials = keyring_cfg.setdefault("credentials", {})
    if not isinstance(credentials, dict):
        raise SecretStoreError(
            "config.yaml secrets.keyring.credentials must be a mapping."
        )
    ref = secret_ref_for_env(env_var, home_path)
    changed = credentials.get(env_var) != ref or keyring_cfg.get("enabled") is not True
    credentials[env_var] = ref
    keyring_cfg["enabled"] = True
    if changed:
        _write_raw_config(config_path, config)
    return ref


def remove_secret_reference(
    env_var: str, home_path: Optional[str | Path] = None
) -> bool:
    """Remove one keyring reference from raw config; return whether it existed."""
    _validate_env_name(env_var)
    config_path = _config_path(home_path)
    config = _read_raw_config(config_path)
    secrets_cfg = config.get("secrets")
    keyring_cfg = secrets_cfg.get("keyring") if isinstance(secrets_cfg, dict) else None
    credentials = keyring_cfg.get("credentials") if isinstance(keyring_cfg, dict) else None
    if not isinstance(credentials, dict) or env_var not in credentials:
        return False

    credentials.pop(env_var, None)
    if not credentials:
        # Avoid an enabled-but-empty source producing a startup warning after
        # the last Hafiye provider credential is removed.
        if isinstance(secrets_cfg, dict):
            secrets_cfg.pop("keyring", None)
            if not secrets_cfg:
                config.pop("secrets", None)
    _write_raw_config(config_path, config)
    return True


def get_secret_for_env(
    env_var: str, home_path: Optional[str | Path] = None
) -> Optional[str]:
    """Resolve a configured provider env var, or return ``None`` if unbound."""
    refs = keyring_references(home_path)
    ref = refs.get(env_var)
    if ref is None:
        return None
    return get_secret(ref)


__all__ = [
    "KEYRING_SERVICE",
    "KEYRING_REF_PREFIX",
    "SecretStoreError",
    "backend_info",
    "secret_ref_for_env",
    "get_secret",
    "put_secret",
    "delete_secret",
    "keyring_references",
    "ensure_secret_reference",
    "remove_secret_reference",
    "get_secret_for_env",
]
