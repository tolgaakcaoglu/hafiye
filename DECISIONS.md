# Implementation Decisions

These ADRs record implementation details only. They do not override `HAFIYE_MASTER_ROADMAP.md`.

## ADR-0001 — Preserve both initial Hafiye and Hermes histories

- Date: 2026-08-23
- Decision: Create the `hafiye/p0` branch from `upstream/main` and merge the existing Hafiye documentation history with `--allow-unrelated-histories`.
- Reason: The workspace initially contained Hafiye instructions without a usable Git checkout, while the product must preserve Hermes history. The resulting merge commit keeps both histories reachable and avoids rewriting upstream commits.
- Consequence: `AGENTS.md` carries the Hafiye binding instructions first and preserves the upstream Hermes development guide below them; the upstream source history remains the first-parent baseline.

## ADR-0002 — Use a user-space supported Python for baseline verification

- Date: 2026-08-23
- Decision: Use uv-managed CPython `3.13.15` in `.venv` rather than the system Python `3.14.4`.
- Reason: Hermes declares `>=3.11,<3.14`; installing system packages was not possible without interactive sudo.
- Consequence: This is a development-environment workaround, not a change to the product architecture or Python requirement.

## ADR-0003 — Use the pinned computer-use-linux source checkout for final P0 setup

- Date: 2026-08-23
- Decision: Use source commit `94736dc3e0dca56acfc89752c26869fb9ed01202` and its official `./install.sh`/setup flow for the final P0 readiness path.
- Reason: The source commit is the mandated upstream state, while the matching `0.4.10` release asset is unavailable. The released `0.4.9` package is retained only as historical diagnostic evidence.
- Consequence: No release-channel substitute is treated as the final setup. The source/release mismatch remains a warning in `KNOWN_ISSUES.md` and `UPSTREAM.md`.

## ADR-0004 — Keep Ubuntu's packaged ydotool user unit when the source installer duplicates it

- Date: 2026-08-23
- Decision: Use Ubuntu's active/enabled `ydotool.service` as the canonical per-user ydotoold service when present. Disable and remove the source installer-generated duplicate `ydotoold.service` if it targets the same socket.
- Evidence: The packaged unit runs `/usr/bin/ydotoold` successfully; the duplicate unit failed with `Another ydotoold is running with the same socket`. The root user-manager instance was also disabled. The final doctor and real window/input checks remain green through the non-root packaged unit.
- Consequence: This is an environment-specific service collision resolution; it does not change Hafiye's prescribed computer-use-linux architecture or the pinned source commit.

## ADR-0005 — Align normal storage with Hafiye XDG roots

- Date: 2026-08-23
- Decision: When no explicit HERMES_HOME or profile/context override is
  supplied, use ~/.config/hafiye, ~/.local/share/hafiye,
  ~/.local/state/hafiye, and ~/.cache/hafiye for configuration, data, state,
  and cache respectively. Keep explicit HERMES_HOME and upstream profile
  overrides on the existing single-root behavior.
- Reason: P1 requires Hafiye user-facing data roots while preserving upstream
  compatibility and existing profile semantics.
- Consequence: Python and Desktop use matching root resolution. The legacy
  migration command copies data conservatively and non-destructively; it does
  not delete or replace the legacy home.

## ADR-0006 — Rebrand the external boundary, retain upstream compatibility

- Date: 2026-08-23
- Decision: Rebrand normal user-facing CLI and Desktop identity to Hafiye,
  including package metadata, visible text, app identifiers, update/bootstrap
  messages, and neutral H monogram assets. Retain upstream Hermes module names,
  IPC keys, compatibility environment names, legacy protocol scheme, and
  upstream/legal attribution where they are part of the integration contract.
- Reason: P1 explicitly prohibits mass-renaming upstream internal source
  symbols while requiring that normal Hafiye use present no Hermes branding.
- Consequence: Hafiye has one user-facing identity without a parallel,
  incompatible internal protocol or a compatibility-breaking module rename.

## ADR-0007 — Separate the persistent Hafiye gateway lifecycle from Hermes

- Date: 2026-08-23
- Decision: Keep the upstream `hermes-gateway.service` lifecycle intact and add
  a separate user-scoped `hafiye-gateway.service` for Hafiye Desktop's
  persistent JSON-RPC/WebSocket backend. Bind it to loopback `127.0.0.1:9120`,
  authenticate with an owner-only token, and publish its descriptor under the
  Hafiye XDG state root.
- Reason: P2 requires Desktop to reconnect to a backend that survives Desktop
  shutdown, while upstream Hermes lifecycle behavior and history must remain
  preserved.
- Consequence: Desktop uses the persistent service first and retains the
  existing ephemeral backend path as an installation/development fallback;
  persistent restart control goes through the user systemd unit. This is an
  implementation detail and does not override the master roadmap.
