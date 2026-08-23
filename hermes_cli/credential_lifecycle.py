"""Unified provider-credential lifecycle across every store Hermes reads.

A Hafiye provider API key can live in up to THREE related stores at once:

    1. Linux Secret Service                    — the canonical secret store
    2. ``~/.hermes/config.yaml``               — a non-secret ``keyring://`` ref
    3. ``~/.hermes/.env`` / ``auth.json``       — legacy migration and runtime

The auth store may also contain:

    ``~/.hermes/auth.json`` →
       ``credential_pool.<provider>[*]``      — env-seeded pool entries
       (``source == "env:<VAR>"``) persisted by the pool loader
    ``~/.hermes/config.yaml``                  — inline mirrors written by the
       custom-endpoint flows (``model.api_key``, ``auxiliary.<task>.api_key``,
       ``custom_providers[*].api_key``)

Historically the desktop/dashboard endpoints (PUT/DELETE ``/api/env``) and the
TUI-gateway RPCs only mutated store 1. That divergence is the root cause of a
whole bug family:

    * #51071 / #59761 — deleting a key removes it from ``.env`` but the stale
      ``credential_pool`` entry (and ``provider_models_cache.json`` row)
      survives, so the provider keeps appearing in the model picker, even
      across restarts (the pool loader is additive-only).
    * #62269 — updating a key rewrites ``.env`` but leaves the OLD key in a
      higher-precedence ``config.yaml`` mirror (``model.api_key`` wins over
      env at client construction), producing persistent 401s with a key the
      UI no longer shows.

This module is the single choke point: every surface that saves or removes a
provider credential should route through :func:`save_provider_env_credential`
/ :func:`remove_provider_env_credential` so Secret Service, references,
legacy files, and runtime caches stay consistent.

OAuth preservation contract: removal only prunes credential-pool entries whose
``source`` is exactly ``env:<VAR>``. OAuth/device-code/manual/borrowed entries
(``device_code``, ``manual*``, ``gh_cli``, ``claude_code``, ``oauth``, …) and
the ``providers.<id>`` OAuth token blocks in auth.json are never touched —
deleting an API key must not revoke an OAuth grant for the same provider.

Secrecy contract: no function in this module logs, prints, or returns a
credential value. Results carry key NAMES and config PATHS only.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

__all__ = [
    "save_provider_env_credential",
    "remove_provider_env_credential",
    "purge_env_credential_references",
]


def _providers_for_env_var(env_var: str) -> List[str]:
    """Provider ids whose registered api_key_env_vars include ``env_var``."""
    try:
        from hermes_cli.auth import PROVIDER_REGISTRY
    except Exception:
        return []
    hits: List[str] = []
    for pid, cfg in PROVIDER_REGISTRY.items():
        try:
            if env_var in (cfg.api_key_env_vars or ()):
                hits.append(pid)
        except Exception:
            continue
    return hits


def _is_hafiye_provider_secret(env_var: str) -> bool:
    """Return True for provider credentials owned by Hafiye's keyring path."""
    # Some Hermes provider registries list shared aliases that are owned by a
    # different product surface.  ``GITHUB_TOKEN`` is the canonical example:
    # it is a Skills Hub/tool credential even though Copilot accepts it as a
    # fallback alias.  Respect the authoritative env metadata before looking
    # at the provider registry so the shared tool value remains on the
    # upstream .env path.
    try:
        from hermes_cli.config_defaults import OPTIONAL_ENV_VARS

        info = OPTIONAL_ENV_VARS.get(env_var)
        if info and info.get("category") and info.get("category") != "provider":
            return False
    except Exception:
        pass
    if env_var == "AWS_BEARER_TOKEN_BEDROCK":
        return True
    if env_var.startswith("HERMES_CUSTOM_") and env_var.endswith("_API_KEY"):
        return True
    return bool(_providers_for_env_var(env_var))


def _prune_env_pool_entries(env_var: str) -> List[str]:
    """Drop ``credential_pool`` entries seeded from ``env:<env_var>``.

    Operates across ALL providers in the pool (the source string names the
    env var unambiguously, and shared vars like GITHUB_TOKEN may seed more
    than one provider). Entries with any other source — OAuth, device-code,
    manual, borrowed-CLI — are preserved verbatim, as are the
    ``providers.<id>`` OAuth blocks.

    Returns the list of provider ids that had entries pruned.
    """
    from hermes_cli.auth import _auth_store_lock, _load_auth_store, _save_auth_store

    source = f"env:{env_var}"
    pruned: List[str] = []
    with _auth_store_lock():
        auth_store = _load_auth_store()
        pool = auth_store.get("credential_pool")
        if not isinstance(pool, dict):
            return pruned
        changed = False
        for provider in list(pool.keys()):
            entries = pool[provider]
            if not isinstance(entries, list):
                continue
            kept = [
                entry
                for entry in entries
                if not (isinstance(entry, dict) and entry.get("source") == source)
            ]
            if len(kept) == len(entries):
                continue
            changed = True
            pruned.append(provider)
            if kept:
                pool[provider] = kept
            else:
                del pool[provider]
        if changed:
            _save_auth_store(auth_store)
    return pruned


def _scrub_config_yaml_mirrors(old_value: str, new_value: str | None) -> List[str]:
    """Reconcile config.yaml api_key mirrors that hold ``old_value``.

    Value-matched on purpose: we only touch a config entry when it provably
    holds the SAME credential that just changed in ``.env`` — an independent
    key the user configured for a different endpoint is left alone.

    ``new_value=None`` removes the mirror field; a string replaces it.
    Operates on the RAW user config (never the defaults-merged view) so the
    write doesn't bake defaults into the user's file. Returns the dotted
    paths that were updated (names only — never values).
    """
    if not old_value:
        return []
    from utils import atomic_yaml_write, fast_safe_load

    from hermes_cli.config import (
        get_config_path,
        require_readable_config_before_write,
    )

    config_path = get_config_path()
    if not config_path.exists():
        return []
    try:
        with open(config_path, encoding="utf-8") as f:
            user_config = fast_safe_load(f) or {}
    except Exception:
        return []
    if not isinstance(user_config, dict):
        return []

    touched: List[str] = []

    def _fix(section: Any, key_path: str) -> None:
        if not isinstance(section, dict):
            return
        # "api" is the legacy alias for model.api_key kept by older configs.
        for field in ("api_key", "api"):
            current = section.get(field)
            if isinstance(current, str) and current == old_value:
                if new_value:
                    section[field] = new_value
                else:
                    section.pop(field, None)
                touched.append(f"{key_path}.{field}")

    _fix(user_config.get("model"), "model")

    aux = user_config.get("auxiliary")
    if isinstance(aux, dict):
        for task, slot_cfg in aux.items():
            _fix(slot_cfg, f"auxiliary.{task}")

    custom = user_config.get("custom_providers")
    if isinstance(custom, list):
        for idx, entry in enumerate(custom):
            _fix(entry, f"custom_providers.{idx}")
    elif isinstance(custom, dict):
        for name, entry in custom.items():
            _fix(entry, f"custom_providers.{name}")

    if touched:
        require_readable_config_before_write(config_path)
        atomic_yaml_write(config_path, user_config, sort_keys=False)
    return touched


def _provider_config_sections(user_config: Dict[str, Any]):
    """Yield config mappings that may contain provider credential mirrors."""
    model = user_config.get("model")
    if isinstance(model, dict):
        yield model, "model"

    auxiliary = user_config.get("auxiliary")
    if isinstance(auxiliary, dict):
        for task, section in auxiliary.items():
            if isinstance(section, dict):
                yield section, f"auxiliary.{task}"

    for key in ("custom_providers", "providers"):
        collection = user_config.get(key)
        if isinstance(collection, list):
            for index, section in enumerate(collection):
                if isinstance(section, dict):
                    yield section, f"{key}.{index}"
        elif isinstance(collection, dict):
            for name, section in collection.items():
                if isinstance(section, dict):
                    yield section, f"{key}.{name}"


def _scrub_provider_config_mirrors(
    old_value: str | None, env_var: str, new_value: str | None = None
) -> List[str]:
    """Replace an inline provider secret with its env/keyring indirection."""
    from utils import atomic_yaml_write, fast_safe_load

    from hermes_cli.config import (
        get_config_path,
        require_readable_config_before_write,
    )

    config_path = get_config_path()
    if not config_path.exists():
        return []
    try:
        with open(config_path, encoding="utf-8") as f:
            user_config = fast_safe_load(f) or {}
    except Exception:
        return []
    if not isinstance(user_config, dict):
        return []

    touched: List[str] = []
    for section, key_path in _provider_config_sections(user_config):
        matched = False
        for field in ("api_key", "api"):
            current = section.get(field)
            if (
                isinstance(current, str)
                and current
                and current in {old_value, new_value}
            ):
                section.pop(field, None)
                touched.append(f"{key_path}.{field}")
                matched = True
        if matched or section.get("key_env") == env_var:
            if section.get("key_env") != env_var:
                section["key_env"] = env_var
                touched.append(f"{key_path}.key_env")

    if touched:
        require_readable_config_before_write(config_path)
        atomic_yaml_write(config_path, user_config, sort_keys=False)
    return touched


def _remove_provider_config_refs(
    env_var: str, old_value: str | None
) -> List[str]:
    """Remove provider config pointers/raw mirrors for a deleted credential."""
    from utils import atomic_yaml_write, fast_safe_load

    from hermes_cli.config import (
        get_config_path,
        require_readable_config_before_write,
    )

    config_path = get_config_path()
    if not config_path.exists():
        return []
    try:
        with open(config_path, encoding="utf-8") as f:
            user_config = fast_safe_load(f) or {}
    except Exception:
        return []
    if not isinstance(user_config, dict):
        return []

    touched: List[str] = []
    for section, key_path in _provider_config_sections(user_config):
        for field in ("key_env", "api_key_env"):
            if section.get(field) == env_var:
                section.pop(field, None)
                touched.append(f"{key_path}.{field}")
        for field in ("api_key", "api"):
            current = section.get(field)
            if old_value and isinstance(current, str) and current == old_value:
                section.pop(field, None)
                touched.append(f"{key_path}.{field}")

    if touched:
        require_readable_config_before_write(config_path)
        atomic_yaml_write(config_path, user_config, sort_keys=False)
    return touched


def _refresh_runtime_provider_secret(env_var: str, value: str | None) -> None:
    """Refresh the current process without leaking a profile into a sibling."""
    try:
        from agent.secret_scope import is_multiplex_active

        if is_multiplex_active():
            from hermes_cli.env_loader import (
                hydrate_profile_secret_sources,
                reset_secret_source_cache,
            )
            from hermes_constants import get_hermes_home

            reset_secret_source_cache()
            hydrate_profile_secret_sources(get_hermes_home())
            return
    except Exception:
        # The next process/startup hydration remains authoritative. The
        # existing Hermes lifecycle also treats in-process env refresh as
        # best-effort around profile switching.
        return

    if value is None:
        os.environ.pop(env_var, None)
    else:
        os.environ[env_var] = value


def _save_hafiye_provider_secret(env_var: str, value: str) -> Dict[str, Any]:
    """Store a provider credential in Secret Service and remove legacy .env."""
    from hermes_cli.config import load_env, remove_env_value
    from hermes_cli.hafiye_keyring import (
        SecretStoreError,
        ensure_secret_reference,
        get_secret,
        keyring_references,
        put_secret,
        secret_ref_for_env,
    )
    from hermes_constants import get_hermes_home

    home = get_hermes_home()
    value = value.strip()
    if not value:
        raise ValueError("Credential value must not be empty")

    old_dotenv = load_env().get(env_var)
    ref = secret_ref_for_env(env_var, home)
    old_keyring: str | None = None
    if env_var in keyring_references(home):
        old_keyring = get_secret(ref)
    old_value = old_keyring or old_dotenv

    put_secret(ref, value)
    try:
        ensure_secret_reference(env_var, home)
        if old_dotenv is not None:
            removed = remove_env_value(env_var)
            if not removed and load_env().get(env_var) == old_dotenv:
                raise SecretStoreError("Could not remove the legacy .env credential.")
    except Exception:
        # Keep a previously working keyring value if the config migration
        # cannot be completed. Never leave a new value half-configured.
        try:
            if old_keyring:
                put_secret(ref, old_keyring)
            else:
                from hermes_cli.hafiye_keyring import delete_secret

                delete_secret(ref)
        except Exception:
            pass
        raise

    config_updates = _scrub_provider_config_mirrors(old_value, env_var, value)
    _refresh_runtime_provider_secret(env_var, value)

    try:
        from hermes_cli.auth import unsuppress_credential_source

        for provider in _providers_for_env_var(env_var):
            unsuppress_credential_source(provider, f"env:{env_var}")
    except Exception:
        pass

    return {
        "ok": True,
        "key": env_var,
        "config_updates": config_updates,
        "secret_store": "linux-secret-service",
    }


def _remove_hafiye_provider_secret(env_var: str) -> Dict[str, Any]:
    """Remove a provider credential from Secret Service, config and legacy .env."""
    from hermes_cli.config import load_env, remove_env_value
    from hermes_cli.hafiye_keyring import (
        delete_secret,
        get_secret,
        remove_secret_reference,
        secret_ref_for_env,
    )
    from hermes_constants import get_hermes_home

    home = get_hermes_home()
    old_dotenv = load_env().get(env_var)
    ref = secret_ref_for_env(env_var, home)
    old_keyring = get_secret(ref)
    removed_from_keyring = delete_secret(ref)
    removed_reference = remove_secret_reference(env_var, home)
    removed_from_env = remove_env_value(env_var)
    old_value = old_keyring or old_dotenv
    config_scrubbed = _remove_provider_config_refs(env_var, old_value)
    try:
        refs = purge_env_credential_references(env_var)
    except Exception:
        # Secret storage removal is already complete. A read-only auth-pool
        # cleanup failure must not make the Desktop report that the provider
        # credential could not be deleted.
        refs = {"pool_pruned": [], "providers": []}
    _refresh_runtime_provider_secret(env_var, None)

    return {
        "ok": True,
        "key": env_var,
        "removed": bool(removed_from_env or removed_from_keyring),
        "secret_reference_removed": removed_reference,
        "pool_pruned": refs["pool_pruned"],
        "providers": refs["providers"],
        "config_scrubbed": config_scrubbed,
        "secret_store": "linux-secret-service",
        "found": bool(
            removed_from_env
            or removed_from_keyring
            or removed_reference
            or refs["pool_pruned"]
            or config_scrubbed
        ),
    }


def purge_env_credential_references(
    env_var: str, *, clear_models_cache: bool = True
) -> Dict[str, Any]:
    """Remove non-.env references to an env-var credential.

    Prunes ``credential_pool`` env-seeded entries and (optionally) the
    affected providers' rows in ``provider_models_cache.json`` so the model
    picker stops advertising a provider whose key is gone (#59761).
    """
    pruned = _prune_env_pool_entries(env_var)
    providers = sorted(set(pruned) | set(_providers_for_env_var(env_var)))
    # Make the removal sticky the same way `hermes auth remove` does: a
    # lingering shell export (or another live process's os.environ) would
    # otherwise re-seed the pool entry on the next load_pool(). The matching
    # save path lifts the suppression on an explicit re-add.
    try:
        from hermes_cli.auth import suppress_credential_source

        for provider in providers:
            suppress_credential_source(provider, f"env:{env_var}")
    except Exception:
        pass
    if clear_models_cache and providers:
        try:
            from hermes_cli.models import clear_provider_models_cache

            for provider in providers:
                clear_provider_models_cache(provider)
        except Exception:
            # Cache cleanup is best-effort — a failure here must not block
            # the credential removal itself.
            pass
    return {"pool_pruned": pruned, "providers": providers}


def save_provider_env_credential(env_var: str, value: str) -> Dict[str, Any]:
    """Save/update a provider credential or legacy env value.

    Hafiye provider credentials use Linux Secret Service and leave only a
    ``keyring://`` reference in config.yaml. Non-provider Hermes environment
    values retain the upstream .env lifecycle for compatibility with channel
    and tool setup flows.
    """
    if _is_hafiye_provider_secret(env_var):
        return _save_hafiye_provider_secret(env_var, value)

    from hermes_cli.config import load_env, save_env_value

    old_value = load_env().get(env_var)
    save_env_value(env_var, value)

    config_updates: List[str] = []
    if value and old_value and old_value != value:
        config_updates = _scrub_config_yaml_mirrors(old_value, value)

    # A prior UI/CLI removal may have suppressed this env source; a fresh
    # save is an explicit re-add, so lift the suppression for every provider
    # that reads this var.
    try:
        from hermes_cli.auth import unsuppress_credential_source

        for provider in _providers_for_env_var(env_var):
            unsuppress_credential_source(provider, f"env:{env_var}")
    except Exception:
        pass

    return {"ok": True, "key": env_var, "config_updates": config_updates}


def remove_provider_env_credential(env_var: str) -> Dict[str, Any]:
    """Remove a credential from EVERY store it lives in.

    Hafiye provider credentials are removed from Secret Service and their
    config references; legacy/non-provider values use the upstream .env path.
    Every path also prunes env-seeded
    ``credential_pool`` entries, drops the affected providers' model-cache
    rows, and removes any config.yaml mirror holding the same value.
    OAuth/device-code/manual credentials are preserved (see module docstring).

    ``found`` is True when ANY store held the credential — callers that
    previously 404'd on ".env miss" should key off this instead so a stale
    pool-only entry can still be cleaned up through the same button.
    """
    if _is_hafiye_provider_secret(env_var):
        return _remove_hafiye_provider_secret(env_var)

    from hermes_cli.config import load_env, remove_env_value

    old_value = load_env().get(env_var)
    removed_from_env = remove_env_value(env_var)
    refs = purge_env_credential_references(env_var)
    config_scrubbed = _scrub_config_yaml_mirrors(old_value, None) if old_value else []

    return {
        "ok": True,
        "key": env_var,
        "removed": removed_from_env,
        "pool_pruned": refs["pool_pruned"],
        "providers": refs["providers"],
        "config_scrubbed": config_scrubbed,
        "found": bool(removed_from_env or refs["pool_pruned"] or config_scrubbed),
    }
