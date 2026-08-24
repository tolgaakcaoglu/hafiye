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

## ADR-0008 — Keep Composer lifecycle and tray state in the Desktop main process

- Date: 2026-08-23
- Decision: Keep Composer launch modes, the global accelerator, XDG autostart,
  systemd user-service login enablement, tray actions, and close-to-tray
  behavior under Electron's main-process authority. The renderer receives
  operational state through the existing Quick Entry bridge and uses the
  existing voice/submit/cancel business paths.
- Reason: Global shortcuts, tray ownership, window lifetime, and login
  integration are OS/Desktop concerns. Keeping them beside the existing Hermes
  Quick Entry owner avoids a second configuration system and preserves the
  roadmap requirement that closing Desktop must not terminate the persistent
  Hafiye core.
- Consequence: Composer settings are persisted in the Desktop user-data root,
  not gateway config. Later-phase controls that are not implemented are
  visibly disabled and labeled rather than exposing fake state. The generated
  autostart entry is conservative and only removes an existing file when it is
  recognizably Hafiye-owned.

## ADR-0009 — Manage llama.cpp as a private Hafiye runtime boundary

- Date: 2026-08-23
- Decision: Keep the managed llama.cpp source/build and GGUF model registry under
  Hafiye's XDG data/state roots. Run `llama-server` as the non-root Hafiye user
  on loopback `127.0.0.1:11435`; expose lifecycle operations to CLI and Desktop
  through the shared runtime manager and authenticated gateway API.
- Reason: P4 requires install/version/model import/download/list/load/unload and
  server lifecycle behavior without hard-coded models or a second business-logic
  implementation. The runtime manifest records the exact managed source commit,
  compiled backends, and selected AUTO backend.
- Consequence: AUTO follows the binding CUDA → Vulkan → CPU policy, with CUDA
  primary on the current RTX 3080. A runtime rebuild stops the managed server
  before replacing its executable, then leaves model restart explicit so Linux
  does not hit `ETXTBSY` and no hidden model reload occurs. The managed source
  pin `c060ca974c773c7c3d17fd1b66dc9d312bc292c0` is separate from the pinned
  Hermes commit.

## ADR-0010 — Store provider credentials in Linux Secret Service

- Date: 2026-08-24
- Decision: Provider-owned credentials are canonical in the Linux Secret
  Service. Hafiye config may store only profile-scoped `keyring://` references;
  the raw value is hydrated into the process only when provider resolution or a
  connection test needs it. Generic channel/tool credentials retain Hermes'
  existing `.env` compatibility path.
- Reason: P5 requires Secret Service storage and forbids normal plaintext API
  keys in YAML/JSON while preserving the existing Hermes provider and secret
  source contracts. Shared aliases such as `GITHUB_TOKEN` must remain owned by
  their non-provider tool surface rather than being reclassified by a provider
  fallback alias.
- Consequence: Legacy raw provider config and `.env` values are migrated or
  removed through the credential lifecycle, stale keyring references are
  cleaned on deletion, and no second provider-resolution system is introduced.
  This is an implementation detail and does not override the master roadmap.

## ADR-0011 — Centralize P6 routing and privacy enforcement at shared boundaries

- Date: 2026-08-24
- Decision: Store Hafiye route slots, task-scoped overrides, locality policy,
  and privacy normalization in `hafiye_policy.py`. Resolve a task route before
  native gateway/API agent construction, pass the resolved route into
  `AIAgent`, and enforce `LOCAL_ONLY`/`OFFLINE` again at runtime, fallback,
  tool-schema, and tool-dispatch boundaries.
- Reason: P6 requires identical behavior across CLI, gateway, API, and Desktop
  while preserving Hermes prompt-cache stability. A task override must be
  selected before agent construction and must not be injected into persisted
  conversation history. Defense-in-depth at the agent/tool boundary prevents
  stale or direct calls from bypassing the policy.
- Consequence: The existing Hermes provider/fallback infrastructure remains the
  execution engine; Hafiye adds one shared policy layer and one `hafiye` config
  namespace. OFFLINE removes network-capable tool surfaces while retaining
  local terminal/filesystem/desktop capabilities. This ADR does not override
  the master roadmap.

## ADR-0012 — Preserve gateway cache and fallback-refresh contracts

- Date: 2026-08-24
- Decision: Normalize the gateway cache-busting result to a mapping before
  adding Hafiye route keys, and select a per-turn Hafiye fallback chain through
  a helper that still performs the upstream disk-refresh call at each agent
  construction site.
- Reason: Lightweight gateway runners and existing upstream source-level
  tests exercise the pre-Hafiye contracts directly. Hafiye route metadata must
  extend the cache signature without assuming every embedding returns a dict,
  and per-turn fallback routing must not freeze or bypass Hermes' refresh
  behavior.
- Consequence: Hafiye route state remains part of the agent cache key, while
  upstream fallback reload behavior and compatibility test contracts remain
  intact. This is an implementation detail and does not override the master
  roadmap.

## ADR-0013 — Bind provider Secret Service references to the active config root

- Date: 2026-08-24
- Decision: When the normal XDG split is active, Hafiye provider credential
  save, refresh, and removal operations use `get_config_path().parent` as the
  secret-reference root. Explicit `HERMES_HOME` continues to use its existing
  single-root behavior.
- Reason: Runtime secret-source hydration reads the active config root. Using
  the data root for lifecycle writes made a newly saved provider credential
  appear successful in the current process but disappear from the next
  process.
- Consequence: Linux Secret Service remains the canonical provider store,
  config contains only keyring references, and the default-XDG regression is
  covered by `test_default_xdg_provider_lifecycle_uses_config_root`. This ADR
  records an implementation correction and does not override the master
  roadmap.

## ADR-0014 — Enforce Hafiye host policies at existing Hermes boundaries

- Date: 2026-08-24
- Decision: Add one shared Hafiye host-tool classifier/resolver. Terminal
  combines policy findings with Hermes' existing command-guard approval flow;
  the other host tools are gated at the shared `model_tools` dispatch boundary;
  `execute_code` receives one short-lived approval scope for the same call.
  The default remains real local-host execution under `FULL_AUTONOMOUS`.
- Reason: Every CLI, gateway, Desktop, and direct dispatch path must observe
  the same `FULL_AUTONOMOUS`, `PRIVILEGED_CONFIRM`, `WRITE_CONFIRM`, and
  `READ_ONLY` behavior without creating a second approval surface or changing
  Hermes' prompt-cache-sensitive conversation machinery.
- Consequence: `READ_ONLY` is conservative and blocks unknown/compound host
  mutations; confirmation policies fail closed without an interactive user
  approval surface. P8's `hafiye-rootd` remains the later privileged-operation
  broker and is not folded into P7.

## ADR-0015 — Keep privileged operations behind a local root broker

- Date: 2026-08-24
- Decision: Implement the roadmap-prescribed `hafiye-rootd` as a dedicated
  root systemd service on `/run/hafiye/root.sock`. Authenticate Linux peers
  with `SO_PEERCRED`, allow only the configured local UID, use strict
  length-prefixed JSON framing, and audit every accepted/rejected request with
  redacted arguments. Keep the main Hafiye gateway and Desktop processes
  non-root.
- Reason: P8 requires narrowly brokered privileged operations without running
  the agent stack as root. A local Unix socket preserves the required host
  capability while avoiding a network-exposed root API and keeping the
  privileged boundary explicit for CLI, gateway, and future Desktop callers.
- Consequence: Package/service/power/file/root-exec operations have one shared
  protocol and audit boundary. The service installation uses normal
  interactive sudo once; no passwordless sudo or `NOPASSWD` sudoers rule is
  introduced. The rootd implementation and its CLI remain separate from
  Hermes' upstream agent loop and prompt-cache-sensitive tool schema.

## ADR-0016 — Manage computer-use-linux through the existing Hermes MCP client

- Date: 2026-08-24
- Decision: Resolve the pinned `agent-sh/computer-use-linux` binary through
  Hafiye's managed boundary and inject a reserved, in-memory MCP server entry
  into Hermes' existing MCP loader and platform toolset resolver. Pass only the
  current desktop session's display/DBus/XDG routing variables to the stdio
  child. Do not require a user `mcp_servers` edit.
- Reason: P9 requires computer-use-linux to be a built-in MCP provider with
  real Wayland/GNOME readiness and Desktop diagnostics, while preserving
  Hermes' MCP connection, registration, schema, and discovery behavior.
- Consequence: The provider is automatically available when the pinned binary
  is installed, exposes its real 18-tool registration to the model, and
  surfaces doctor readiness in `Settings → Computer`. The existing Hermes
  cua-driver integration remains intact for its other supported platforms;
  this ADR does not override the master roadmap or change the Hermes upstream
  pin.

## ADR-0017 — Keep structured and native browser control as explicit lanes

- Date: 2026-08-24
- Decision: Reuse Hermes' existing structured `browser_*` automation as
  Hafiye's structured browser lane while preserving current Hermes backend
  selection. Add `browser_download` for the official `agent-browser`
  download operation, and add one explicit `browser_native`
  adapter that delegates to the already-managed computer-use-linux MCP tools
  for an existing normal desktop browser window.
- Reason: P10 requires both structured automation and native control of a
  user's already-authenticated browser session. A dedicated adapter keeps the
  distinction visible to the model and preserves the existing Hermes browser
  extension router, while avoiding a second desktop-control implementation,
  browser profile, or cookie store.
- Consequence: Native actions must bind an exact window and fail closed when a
  target or accessibility selector is missing. Navigation retains Hafiye URL
  secret/metadata safety checks. Structured downloads require an absolute
  destination path. This is an implementation detail and does not override
  the master roadmap.
