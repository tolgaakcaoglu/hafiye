"""Linux Secret Service secret source for Hafiye provider references."""

from __future__ import annotations

from pathlib import Path

from agent.secret_sources.base import ErrorKind, FetchResult, SecretSource, is_valid_env_name
from hermes_cli.hafiye_keyring import (
    SecretStoreError,
    get_secret,
    secret_ref_for_env,
)


class KeyringSource(SecretSource):
    """Resolve Hafiye's ``keyring://`` bindings into provider env vars."""

    name = "keyring"
    label = "Linux Secret Service"
    shape = "mapped"
    scheme = "keyring"

    def override_existing(self, cfg: dict) -> bool:
        # A configured Secret Service reference is explicit user intent and
        # must win over a stale shell export or legacy .env value.
        return bool(isinstance(cfg, dict) and cfg.get("override_existing", True))

    def config_schema(self) -> dict:
        return {
            "enabled": {"description": "Use Hafiye's Linux Secret Service", "default": True},
            "credentials": {
                "description": "Map ENV_VAR names to generated keyring:// references",
                "default": {},
            },
            "override_existing": {
                "description": "Resolved values overwrite shell/.env values",
                "default": True,
            },
        }

    def fetch(self, cfg: dict, home_path: Path) -> FetchResult:
        result = FetchResult()
        cfg = cfg if isinstance(cfg, dict) else {}
        credentials = cfg.get("credentials")
        if not isinstance(credentials, dict) or not credentials:
            result.error = (
                "secrets.keyring.enabled is true but no credentials are configured."
            )
            result.error_kind = ErrorKind.NOT_CONFIGURED
            return result

        for env_var, ref in credentials.items():
            if not isinstance(env_var, str) or not is_valid_env_name(env_var):
                result.warnings.append("Skipping an invalid keyring environment name.")
                continue
            if not isinstance(ref, str) or ref != secret_ref_for_env(env_var, home_path):
                result.warnings.append(f"Skipping invalid keyring reference for {env_var}.")
                continue
            try:
                value = get_secret(ref)
            except SecretStoreError as exc:
                result.error = str(exc)
                result.error_kind = ErrorKind.INTERNAL
                return result
            if value is None:
                result.warnings.append(f"No Secret Service value is available for {env_var}.")
                continue
            result.secrets[env_var] = value

        if not result.secrets and not result.error:
            result.error = "Configured Hafiye Secret Service references returned no values."
            result.error_kind = ErrorKind.EMPTY_VALUE
        return result

    def remediation(self, kind, cfg: dict) -> str:
        if kind == ErrorKind.INTERNAL:
            return (
                "Unlock the GNOME keyring and verify the Linux Secret Service backend "
                "with `hafiye doctor`, then retry the provider save."
            )
        return super().remediation(kind, cfg)


__all__ = ["KeyringSource"]
