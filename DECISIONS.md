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

## ADR-0018 — Keep voice runtimes external and device selection renderer-local

- Date: 2026-08-24
- Decision: Manage whisper.cpp and Piper beneath the Hafiye runtime data root.
  Invoke Piper through its separate process/CLI boundary, route local STT
  through Hermes' custom command hook, and persist the selected microphone
  `deviceId` in the Desktop renderer's Hafiye voice settings store. The
  backend's public Piper voice-list response omits filesystem paths.
- Reason: P11 requires whisper.cpp/Piper as the fixed local voice machinery and
  explicitly keeps Piper outside Hafiye application libraries. Physical input
  device IDs belong to the host renderer that owns `getUserMedia`; stripping
  runtime paths prevents local filesystem details from becoming a public API
  contract.
- Consequence: Push-to-talk, continuous capture, and wake capture share one
  selected-device stream helper with OS-default fallback and hotplug handling.
  The managed runtime doctor and real speech acceptance remain independent: a
  green runtime doctor does not count as successful microphone transcription.
  This ADR records implementation details and does not override the master
  roadmap.

## ADR-0019 — Train and ship the prescribed Hafiye openWakeWord model

- Date: 2026-08-24
- Decision: Use the official openWakeWord `train.Model` pipeline from the pinned
  source checkout, generate Turkish positive samples with the managed Piper
  `tr_TR-dfki-medium` voice, and ship the resulting standalone
  `tools/wakewords/hafiye.onnx` as Hafiye's Linux default. Keep the default
  sensitivity at `0.6` and confirmation frames at `3`, with legacy Hermes model
  aliases resolving to the Hafiye asset.
- Reason: P12 requires a bundled custom Hafiye wake word with a reproducible
  local training path and real false-positive/activation validation. This
  keeps wake detection on-device and uses the already-fixed openWakeWord and
  Piper machinery without adding a cloud dependency or a second wake engine.
- Consequence: The source checkout, training venv, seed, sample count, model
  hash, and validation metrics are recorded in ENVIRONMENT.md and UPSTREAM.md.
  The openWakeWord CPython 3.13 packaging limitation is a documented warning;
  the official source checkout and ONNX runtime are the accepted host path.
  This ADR does not override the master roadmap.

## ADR-0020 — Keep client wake capture alive while Desktop is minimized

- Date: 2026-08-24
- Decision: While the Desktop renderer owns an active client-side wake audio
  graph, notify Electron through a dedicated IPC signal and include that
  renderer in the existing stream-throttle activity calculation. On capture
  stop or renderer destruction, remove the signal and restore normal idle
  throttling.
- Reason: Chromium can pause an idle hidden renderer's `ScriptProcessorNode`
  callbacks when a window is minimized. That would leave the backend lease
  apparently armed while no PCM reaches the detector. The existing stream
  throttle is the smallest boundary that directly controls this behavior and
  does not change the persistent gateway or wake detector architecture.
- Consequence: A minimized Hafiye Desktop window continues local wake capture,
  while ordinary idle windows retain Chromium's normal throttling. The real
  minimized-window acceptance is recorded in TEST_MATRIX.md; no permanent
  global disable-throttling setting is introduced. This ADR records an
  implementation detail and does not override the master roadmap.

## ADR-0021 — Centralize process-wide cancellation at the gateway

- Date: 2026-08-24
- Decision: Route Desktop Stop, Composer Stop, tray Stop, the Turkish voice
  stop phrase, CLI `emergency-stop`, and the global accelerator to one
  gateway-owned `CancellationController`. The controller engages the durable
  ESTOP sentinel, cuts TTS, stops managed desktop actions, interrupts active
  sessions and delegations, kills registered cancellable processes, and makes
  the root broker reject new privileged calls. `emergency.resume` is an
  intentional explicit transition out of the paused state.
- Reason: P13 requires one cancellation mechanism across all user surfaces and
  requires cancellation to cross the TTS, desktop, long-task, subagent, and
  privileged-operation boundaries. Keeping the orchestration in the gateway
  avoids independent partial-stop implementations.
- Consequence: Normal `session.interrupt` shares the same session-level cleanup
  seam, while process-wide emergency stop uses the durable sentinel and global
  fan-out. The generic upstream CUA path is left untouched; Hafiye's managed
  Linux MCP provider is gated at its own boundary.

## ADR-0022 — Use a GNOME custom-keybinding fallback on Wayland

- Date: 2026-08-24
- Decision: Electron `globalShortcut` remains the first registration path for
  the mandated `Ctrl+Super+Escape`. If the real GNOME Wayland session rejects
  it, install one reserved GNOME user custom keybinding that invokes the local
  Hafiye CLI, which then uses the authenticated persistent-gateway stop RPC.
  Preserve unrelated custom bindings and remove only the Hafiye-owned entry on
  clean shutdown.
- Reason: Electron global accelerators are unavailable in this host's native
  Wayland session, but P13 requires a real global keyboard stop. GNOME's
  existing user-level keybinding service supplies that compositor-level path
  without a second cancellation protocol or privileged system change.
- Consequence: The fallback is session/user scoped and requires no sudo,
  passwordless sudo, or systemd modification. The gateway broadcasts the stop
  event so renderer-owned TTS playback also stops when the GNOME command was
  triggered outside Electron.

## ADR-0023 — Run OpenHands V1 through a managed one-shot worker

- Date: 2026-08-24
- Decision: Integrate the official OpenHands V1 SDK/runtime behind Hafiye's
  `coding_delegate` tool, using a Hafiye-managed user runtime and a one-shot
  worker subprocess for each local repository task. Resolve the model through
  Hafiye's `coding` route, keep the repository path local, and register the
  worker in Hermes' existing process registry so the shared cancellation
  controller can stop it.
- Reason: The master roadmap fixes OpenHands as Hafiye's coding specialist and
  P13 requires a real delegation that the emergency-stop path can cancel. A
  subprocess gives OpenHands its official dependency environment while keeping
  Hafiye responsible for routing, privacy policy, secret handling, progress
  records, and process cancellation.
- Consequence: The worker consumes the credential at its private boundary and
  emits only redacted progress/result metadata. The managed runtime doctor
  hides `coding_delegate` when the official packages are absent. The later P15
  Task Center bridge extends this boundary without changing the decision to
  keep OpenHands behind Hafiye delegation. This records implementation detail
  only and does not override the master roadmap.

## ADR-0024 — Reuse Hermes project registry and session search

- Date: 2026-08-24
- Decision: Use the pinned Hermes per-profile `projects.db`, deterministic
  project slug/name tools, gateway `projects.*` RPCs, authoritative project
  tree, and FTS5 `session_search` as Hafiye's P14 implementation boundary. Add
  Hafiye acceptance coverage around those existing surfaces instead of
  introducing a second project or conversation store.
- Reason: The master roadmap explicitly selects Hermes memory/session search
  as the conversational base and requires deterministic project path
  resolution across restart. The existing Hermes surfaces provide that
  persistence and the Desktop already consumes the same gateway state.
- Consequence: Project metadata and session recall remain shared by CLI/TUI/
  Desktop-compatible backend paths, upstream history stays intact, and P14
  acceptance is verified with a fresh-process path/recall test plus real
  Electron browse/search/edit/delete coverage. This ADR records an
  implementation detail and does not override the master roadmap.

## ADR-0025 — Bridge delegated coding progress through the shared Task Center

- Date: 2026-08-24
- Decision: Keep P15 coding-task records in a shared process-local
  `TaskCenterRegistry`. The coding delegate emits only safe lifecycle,
  current-step, progress, tool, command, changed-file, result, and error
  summaries. The gateway exposes `tasks.list`/`tasks.cancel` and broadcasts
  `task.update`; Desktop renders the same records in the Task Center panel.
- Reason: P15 requires real OpenHands progress and result visibility while the
  Hafiye gateway remains the single backend/business-logic boundary. Reusing
  Hermes process registration preserves cancellation and emergency-stop
  ownership, and redacted summaries prevent private chain-of-thought from
  entering the user-facing task surface.
- Consequence: P15 provides the real coding-delegate bridge but does not claim
  durable generic task history. Persistence, complete task categories, and the
  full Task Center product surface remain P16 work; this ADR does not override
  the master roadmap.

## ADR-0026 — Persist Task Center records in the Hafiye state root

- Date: 2026-08-24
- Decision: Store the shared Task Center registry in
  `task_center.db` under Hafiye's XDG state root, using SQLite WAL and a
  thread-safe process-local cache. Persist only the master task fields and
  redacted operator metadata. On a new gateway process, keep `QUEUED` work
  queued and convert in-flight worker states to explicit
  `FAILED / INTERRUPTED_BY_GATEWAY_RESTART` records.
- Reason: P16 requires completed/failed history and restart/reconnect behavior
  while CLI, gateway, and Desktop continue to use one business-logic boundary.
  A small local state database provides that persistence without making
  OpenHands a second runtime or exposing its transcript.
- Consequence: Task Center history is user-scoped and survives Desktop or
  gateway reconnects. Actual worker resumption is not inferred after process
  loss; future scheduling/resume semantics remain subject to the roadmap's
  later phases. This ADR does not override the master roadmap.

## ADR-0027 — Compose the P17 Control Center from existing real surfaces

- Date: 2026-08-24
- Decision: Add a Hafiye-specific `/control-center` Electron overlay with the
  19 roadmap pages, while keeping the existing Hermes Settings route and
  deep-link behavior intact. Config pages use `ConfigSettings`; providers,
  Skills/MCP, scheduler, logs, computer-use, Task Center, and About reuse their
  existing backend/API surfaces.
- Reason: The master roadmap requires one functional Hafiye Control Center,
  not a second configuration system. Composing the already-tested surfaces
  keeps Desktop and CLI/gateway state on one business-logic boundary and
  avoids decorative switches or duplicated persistence.
- Consequence: Page navigation is Hafiye-specific, but mutations remain real
  gateway/config/tool/scheduler operations. The shared privacy selector exposes
  the fixed `NORMAL`, `LOCAL_ONLY`, and `OFFLINE` modes. This ADR records the
  implementation boundary and does not override the master roadmap.

## ADR-0028 — Carry Hafiye policy through Hermes scheduled jobs

- Date: 2026-08-24
- Decision: Reuse Hermes cron persistence, scheduler claims/execution,
  recurring state updates, skills/toolset catalog, and MCP safety merge. Store
  optional per-job `route` and `privacy_mode` fields in the existing job
  record, expose them with the existing profile-aware gateway REST API, and
  resolve them immediately before the real scheduled `AIAgent` is built.
  `enabled_toolsets` remains Hermes' explicit allowlist, with its existing
  managed-MCP and safety denylist merge preserved.
- Reason: P18 requires scheduled jobs to choose route, privacy mode, and
  enabled tools through Hafiye Desktop while CLI, gateway, and Desktop keep
  one scheduler/business-logic boundary. Scheduled jobs are detached from an
  interactive conversation, so their route slot is stable and natural-language
  route overrides are not applied. A per-job privacy selection may strengthen
  the configured route/installation policy but may not weaken it.
- Consequence: Existing Hermes jobs remain compatible because absent route and
  privacy fields inherit the normal Hafiye policy. The real cron editor uses
  the gateway toolset catalog and clearly marks custom allowlists; the
  scheduler's safety filtering still applies. This ADR records implementation
  detail only and does not override the master roadmap.

## ADR-0029 — Compose P19 hardening around Hermes safety primitives

- Date: 2026-08-24
- Decision: Keep Hermes' existing prompt-injection boundaries, forced secret
  redaction, provider error classification/backoff, exact-call loop detector,
  checkpoint manager, and corrupt-config recovery as the implementation
  authorities. Add only Hafiye-specific bounded runtime recovery, task action
  admission, computer-use failure classification, and one hardening doctor/
  retention command that reads the existing config and state roots.
- Reason: P19 requires crash/outage recovery, loop/action limits, rollback,
  config recovery, audit retention, and disk limits. Reusing the upstream
  controls preserves Hermes behavior and prompt-cache/tool-surface invariants;
  bounded Hafiye adapters provide the missing managed llama/voice/CUA and
  operator-maintenance contracts without a parallel supervisor or config store.
- Consequence: Recovery attempts are explicit and capped, diagnostics are
  redacted/bounded, retention mutation is isolated to known audit/checkpoint
  stores, and `hafiye hardening doctor` can validate the complete boundary
  without starting a runtime. This ADR does not override the master roadmap.

## ADR-0030 — Assemble one Ubuntu/Debian package around the existing runtimes

- Date: 2026-08-24
- Decision: Build the P20 `.deb` as an outer package around the existing real
  Electron `linux-unpacked` output and the Hafiye backend source/lock metadata.
  Install package-owned launchers and assets under `/usr/lib/hafiye`, expose
  the user gateway vendor unit, and activate the root broker explicitly for the
  target user rather than shipping an implicitly runnable root service. Keep
  managed model, voice, and computer-use runtimes as first-run/setup downloads.
- Reason: The master roadmap fixes Ubuntu/Debian and `.deb` as the primary
  packaging target while allowing managed external runtimes to download during
  setup. One package boundary keeps Desktop, CLI/backend, gateway, root-broker
  activation, XDG entries, and notices together without creating a second
  runtime or configuration store.
- Consequence: Package doctor/install can validate and prepare the user-scoped
  runtime after installation; a privileged live install remains a release
  operator action and was not performed during rootless acceptance. This ADR
  records implementation detail only and does not override the master roadmap.

## ADR-0031 — Keep P21 onboarding state at the Hafiye XDG state boundary

- Date: 2026-08-25
- Decision: Persist only onboarding progress and choices in an atomic,
  owner-readable `onboarding.json` under the Hafiye XDG state root. Each wizard
  action calls the existing authenticated gateway/config/runtime/voice/autostart
  boundary; onboarding does not create a parallel config file, model registry,
  service manager, or provider credential store. The wizard is enabled for the
  packaged installation through the package-root marker and remains inert in a
  normal development checkout unless explicitly forced for acceptance tests.
- Reason: P21 is a GUI first-run sequence, but the CLI, Desktop, and persistent
  gateway must continue to share one backend/business-logic boundary. A small
  resumable progress record is necessary for first-run UX while the actual
  mutations must remain in the already-tested Hafiye authorities.
- Consequence: A fresh packaged launch can resume the exact roadmap step and
  the final doctor is the only completion transition. This records
  implementation detail only and does not override the master roadmap.

## ADR-0032 — Do not force HERMES_HOME into normal-XDG user service units

- Date: 2026-08-25
- Decision: When Hafiye resolves its normal XDG roots, generated
  `hafiye-gateway.service` units omit `Environment=HERMES_HOME=...`. If a caller
  explicitly supplies `HERMES_HOME` or a context/profile override, that value is
  preserved in the unit. Packaged launchers separately export
  `HAFIYE_PACKAGE_ROOT` for packaged-install detection.
- Reason: Forcing the legacy single-root compatibility variable into a normal
  XDG unit made the persistent gateway read a different onboarding/runtime
  state from the CLI. Omitting it restores one state boundary without changing
  upstream compatibility for explicit profiles.
- Consequence: Reinstalling/regenerating the user unit is required after the
  fix; the live service was reinstalled/restarted and its authenticated doctor
  now returns `ok=true` with `blockers=[]`. No root service or passwordless sudo
  rule is involved. This records implementation detail only and does not
  override the master roadmap.

## ADR-0033 — Keep the product CLI as adapters over existing Hafiye boundaries

- Date: 2026-08-25
- Decision: Implement the P22 `hafiye` command vocabulary as thin adapters over
  the existing one-shot agent, persistent gateway service, local GGUF runtime,
  provider catalog, Hafiye route/privacy policy, durable Task Center, and
  computer-use-linux doctor. Preserve Hermes' existing CLI commands and use
  `projects` and `automation` as aliases for the existing project and cron
  implementations.
- Reason: The master roadmap requires CLI and Desktop to share backend/business
  logic. A second command-specific config, model registry, task store, or
  scheduler would split state and violate that boundary.
- Consequence: Normal gateway turns continue to treat configured route slots as
  authoritative. Explicit one-shot CLI provider/model arguments use a narrowly
  scoped policy override so a populated onboarding default cannot swallow an
  explicit command-line selection. This records implementation detail only and
  does not override `HAFIYE_MASTER_ROADMAP.md`.
