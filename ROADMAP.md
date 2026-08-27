# Roadmap

The authoritative phase definitions are in HAFIYE_MASTER_ROADMAP.md. This file
records execution status only.

- [x] P0 Fork + environment
- [x] P1 Hafiye external identity and data root
- [x] P2 Persistent gateway + Desktop connection
- [x] P3 Hafiye Composer + tray + autostart
- [x] P4 llama.cpp managed local runtime
- [x] P5 Providers + Gemini + remote OpenAI-compatible
- [x] P6 Model router + privacy modes
- [x] P7 Full host tools + execution policy
- [x] P8 Hafiye root broker
- [x] P9 Linux computer use
- [x] P10 Browser
- [x] P11 Local Turkish voice stack
- [x] P12 Custom Hafiye wake word
- [x] P13 Barge-in + emergency stop
- [x] P14 Memory + project registry
- [x] P15 OpenHands coding delegate
- [x] P16 Task Center
- [x] P17 Control Center
- [x] P18 Scheduler / skills / MCP
- [x] P19 Hardening
- [x] P20 Packaging
- [x] P21 First-run onboarding
- [x] P22 CLI
- [ ] P23 Final E2E suite
- [ ] P24 Hafiye Jarvis experience convergence

## P11 execution status

- [x] Build/install managed whisper.cpp with CUDA primary and Vulkan/CPU
      fallback; configure the Turkish local-STT command hook.
- [x] Install managed external Piper with `tr_TR-dfki-medium` and expose the
      real voice-list/preview API and Desktop controls.
- [x] Remove the Desktop microphone path's hard-coded OpenAI transcription
      behavior; route recording through the configured Hafiye backend.
- [x] Add persistent microphone selection, OS-default fallback, and hotplug
      handling for push-to-talk, continuous capture, and wake capture paths.
- [x] Run the managed doctor, targeted backend tests, Desktop UI/typecheck/build,
      and real Electron voice settings smoke tests.
- [x] Speak Turkish into the real microphone and obtain the correct text.
- [x] Verify a Turkish Hafiye response is synthesized through the real managed
      Piper process.

P11 is complete. The synchronized real microphone capture produced the correct
Turkish sentence through both the managed whisper.cpp command and Hafiye's
`transcribe_audio()` hook. Direct Piper, Hafiye TTS, Desktop settings, and the
real Electron voice smoke also passed. KI-025 is resolved; P12 followed and is
now complete.

## P12 execution status

- [x] Train and bundle the Turkish `hafiye.onnx` openWakeWord model.
- [x] Configure Hafiye as the default local wake model while preserving legacy
      Hermes aliases for compatibility.
- [x] Expose the real wake-word toggle and tuning fields in Desktop Voice
      settings; persist the default sensitivity and confirmation frames.
- [x] Keep client-side wake capture alive while Desktop is minimized by
      disabling renderer background throttling only for the active wake graph.
- [x] Run synthetic validation, real normal-room false-positive testing, real
      Turkish activation testing, and the minimized Desktop acceptance flow.
- [x] Run the targeted wake-word tests, Desktop tests/typecheck, production
      build, lint, compilation, and whitespace checks.

P12 is complete. The source implementation is recorded in commit
`d1c5f4c9c5254ba34844e583e5486972e33bdd6b`. The bundled model is the standalone
ONNX asset `tools/wakewords/hafiye.onnx` with SHA-256
`9eb0e8c9fd509900ba5d33b4c43906817265605846564af76232daeea194ba50`.
Synthetic validation at threshold `0.6` reached accuracy `1.0`; a normal-room
music recording produced zero detector fires, while a real Turkish “Hafiye”
recording produced detector fires and a fresh Desktop session. The real
Electron acceptance also detected the phrase after the Hafiye window was
minimized. P13 — Barge-in + emergency stop followed and is now complete; P14
is the next incomplete phase.

## P0 execution status

- [x] Preserve upstream Git history and establish the Hafiye development branch.
- [x] Configure origin and upstream.
- [x] Record the pinned Hermes commit in UPSTREAM.md.
- [x] Inspect and record the real Ubuntu/Linux environment.
- [x] Install the user-space Python toolchain needed by the upstream constraints.
- [x] Run the unmodified upstream backend test suite and the optional-SDK run.
- [x] Build and test the unmodified Hermes Desktop baseline.
- [x] Run the historical and pinned-source computer-use-linux diagnostics.
- [x] Complete the pinned-source official setup and pass final doctor readiness.
- [x] Classify the exact upstream baseline failures under
      ACCEPTED_UPSTREAM_BASELINE.

P0 is complete. The original five-failure set remains the historical
`ACCEPTED_UPSTREAM_BASELINE`; the current exact-node comparison reproduces
only historical IDs 2 and 3 (`2 failed, 3 passed`). Fewer failures update the
current observed subset without changing the historical whitelist. The accepted
failures, missing pactl, and missing vulkaninfo are documented
warnings/diagnostics and are not P0 blockers.

## P1 execution status

- [x] Rebrand normal user-facing CLI and Desktop surfaces to Hafiye.
- [x] Add the Hafiye CLI alias while retaining Hermes launcher compatibility.
- [x] Rebrand Desktop title, menus, Quick Entry, onboarding, notifications,
      update/bootstrap text, app identifiers, and default assets.
- [x] Keep upstream internal module names, IPC keys, compatibility environment
      names, legacy protocol scheme, and legal/upstream attribution intact.
- [x] Implement the four Hafiye XDG roots:
      config, data, state, and cache.
- [x] Keep explicit HERMES_HOME and profile/context overrides compatible with
      the upstream single-root behavior.
- [x] Add and test a conservative, non-destructive legacy Hermes-home
      migration command.
- [x] Add neutral H monogram assets and use them in Desktop packaging.
- [x] Make Python and Desktop path resolution agree on POSIX and Windows.
- [x] Run targeted tests, the full Desktop suite, typecheck, production build,
      Linux unpacked packaging, lint, and real temporary-root CLI smoke tests.

P1 is complete. Its source implementation is recorded in commit
34f1d8c2472e6b70b71bbdbfc9d3292761dbb67b. The P1 exit condition is satisfied:
normal Hafiye use has no user-facing Hermes branding except legal/upstream
attribution and retained compatibility machinery.

## P2 execution status

- [x] Add a user-scoped `hafiye-gateway.service` without replacing the upstream
      `hermes-gateway.service`.
- [x] Bind the persistent Hafiye JSON-RPC/WebSocket backend to loopback at
      stable `127.0.0.1:9120`.
- [x] Store the local Desktop token and connection descriptor in the Hafiye
      XDG state root with owner-only permissions.
- [x] Make Desktop detect and authenticate to the existing persistent backend;
      retain ephemeral local spawn as an install/development fallback.
- [x] Verify Desktop shutdown does not terminate the persistent backend.
- [x] Route Desktop gateway restart control through the persistent systemd
      topology.
- [x] Verify the real service, authenticated HTTP/WS connection, Desktop boot,
      Desktop shutdown persistence, and restart control.

P2 is complete. The source implementation is recorded in commit
e2e22c10b49ec01ef7d8420f1158668718b03fa9. P3 follows below; after its
completion the next incomplete phase is P4 — llama.cpp managed local runtime.

## P3 execution status

- [x] Add the Hafiye Composer surface on top of Hermes Quick Entry.
- [x] Set the mandated default shortcut to `Super+Shift+Space` and keep it
      configurable through the real Desktop settings state.
- [x] Implement `HOTKEY_ONLY`, `SHOW_ON_LOGIN`, and `PINNED` lifecycle modes.
- [x] Add compact activity/task/tool/model/progress states, microphone/voice
      forwarding through the existing Desktop voice path, and stop forwarding
      through the existing cancellation path.
- [x] Add a functional Hafiye tray with Composer, Desktop, task, session,
      settings, logs, gateway restart/stop, and Desktop quit actions. Features
      from later phases remain explicitly disabled rather than fake toggles.
- [x] Add an owner-safe XDG autostart entry and systemd user-service login
      enablement controlled by Composer settings.
- [x] Verify the real Wayland launch, tray creation, exact autostart command,
      Alt+F4-to-tray behavior, and persistent gateway survival.

P3 source implementation is recorded in commit `e33bb456d109`. Composer
unit/store tests, the complete Desktop UI/Electron test projects, typecheck,
clean production build, and the real Wayland checks passed. The host's GNOME
`switch-input-source-backward` binding currently owns the mandated shortcut;
Hafiye reports this conflict and leaves the user binding unchanged. The
shortcut remains configurable, and the issue is recorded as KI-012. A full
reboot was not performed during this session; the exact XDG autostart command
was launched directly with `--hidden` and recorded as the non-disruptive login
equivalent. See KI-013 for that operational follow-up.

## P4 execution status

- [x] Add the Hafiye-managed llama.cpp source/build/runtime manifest under the
      Hafiye XDG data root.
- [x] Implement the fixed `AUTO` compute policy with CUDA primary, Vulkan
      fallback, and CPU fallback, plus explicit backend selection.
- [x] Implement GGUF import, checksum/size registry, resumable Hugging Face
      download, list, delete, load, unload, and model switching.
- [x] Implement loopback llama-server start/stop/restart/health/version and
      the authenticated gateway REST boundary.
- [x] Add real Desktop model settings for backend selection, runtime install,
      GGUF import/download, model selection, context/GPU layers, load, and
      unload.
- [x] Build the managed runtime on the real host with CPU and CUDA support;
      AUTO selects CUDA on the RTX 3080.
- [x] Verify real GGUF chat, Hermes provider connectivity, model switching,
      loopback health, GPU use, and persistent gateway API exposure.
- [x] Complete the corrected full backend regression comparison and record its
      exact result before phase closure.

P4 source implementation is recorded in `87cbfb34337f043363ba8851c485fea5ea66de0b`;
the follow-up shared subprocess-environment correction is
`d912a85ee5fa21afb1c5304e28c6e3651fb16433`, and the final cross-platform
process correction is `ae24562fb9dfeeb4dd58752849b4778b2c8606e8`. The managed
llama.cpp checkout is separately pinned to source commit
`c060ca974c773c7c3d17fd1b66dc9d312bc292c0`. The real runtime, Desktop API,
and corrected full backend regression checks pass under the documented
baseline rule. The follow-up source commit
`213247d70804ffe9350ad5d0874f79a494fd7dc0` exposes the already-supported GGUF
download contract from the Desktop Models page; this is a local-model-runtime
UI completion detail, not a new phase or a change to the managed llama.cpp
architecture. P7 followed this phase and is closed below.

## P5 execution status

- [x] Reuse Hermes provider registry, resolution, fallback, native Gemini, and
      credential lifecycle contracts.
- [x] Add the Hafiye provider-secret boundary: provider-owned credentials use
      Linux Secret Service and config stores only profile-scoped keyring
      references; generic channel/tool `.env` compatibility remains intact.
- [x] Verify provider-secret deletion, stale-reference cleanup, legacy raw
      config migration, runtime hydration, and shared provider-alias edge cases.
- [x] Verify the managed local llama.cpp OpenAI-compatible provider against the
      real CUDA endpoint on the host.
- [x] Verify a remote OpenAI-compatible provider through a real local HTTP test
      server, including authenticated model validation, save, and chat.
- [x] Expose provider/key/model/custom-endpoint behavior through the existing
      Hafiye Desktop surface and pass its provider tests, typecheck, and build.
- [x] Exercise Hermes Gemini registration/resolution and automated credential
      paths without inventing a second provider implementation.
- [x] Configure a real Gemini credential and pass the live Gemini test
      connection on the host.

P5 is complete. The real host credential is stored in Linux Secret Service;
the active Hafiye config contains only its keyring reference. The live Gemini
model-list request returned HTTP 200 with 50 models, and the Hafiye one-shot
call returned the required `HAFIYE_GEMINI_LIVE_OK` marker. The default-XDG
credential lifecycle fix is recorded in source commit `45294d3f7` and covered
by a regression test. The latest full backend comparison covered 3,218 files:
37,156 passed, 4 failed, and 244 skipped; all four failures are members of
the accepted upstream baseline, with no new or different Hafiye regression.

## P6 execution status

- [x] Add the eight Hafiye route slots: `default`, `fast`, `reasoning`,
      `coding`, `vision`, `long_context`, `memory_aux`, and `compression_aux`.
- [x] Add route provider/model/fallback/locality policy resolution on top of
      Hermes runtime/provider resolution.
- [x] Add the three privacy modes: `NORMAL`, `LOCAL_ONLY`, and `OFFLINE`.
- [x] Add task-scoped natural-language overrides for local, remote, Gemini,
      and route-slot requests without mutating conversation history.
- [x] Enforce privacy at route resolution, AIAgent initialization, fallback
      activation, tool-schema generation, and tool execution boundaries.
- [x] Wire the native gateway, API server, one-shot CLI path, interactive CLI
      setup, and Desktop settings to the shared Hafiye policy.
- [x] Verify local, remote, Gemini, LOCAL_ONLY, OFFLINE, and legal-fallback
      behavior with targeted tests.

P6 is complete. Its routing/privacy source implementation is recorded in
`cf6457678b6083c4f783c1a80eef9eba3875ccc0`, with the gateway cache/fallback
contract follow-up in `62b3d5762`. Targeted P6 tests, the affected backend
matrix, Desktop typecheck/settings tests, and the full regression comparison
were run. The only different full-suite failure was reproduced before P6 and
is documented as KI-019; no Hafiye regression remains. P7 followed this
phase and is now closed below.

## P7 execution status

- [x] Keep Hermes local terminal, process, and filesystem tools as the final
      real-host execution environment.
- [x] Add the binding policies `FULL_AUTONOMOUS`, `PRIVILEGED_CONFIRM`,
      `WRITE_CONFIRM`, and `READ_ONLY`, with `FULL_AUTONOMOUS` as the default.
- [x] Enforce the policy at the shared tool-dispatch boundary and combine
      terminal policy findings with Hermes' existing approval/guard surface.
- [x] Make confirmation policies fail closed when no interactive approval
      surface exists; make `READ_ONLY` block mutating host operations.
- [x] Expose `hafiye.execution_policy` through the real Desktop config schema
      and settings control; the existing config API persists changes.
- [x] Verify harmless real host terminal, file-read, and background-process
      operations through the live Hafiye dispatcher.
- [x] Run policy, host-tool, full backend, Desktop, typecheck, build, lint,
      and whitespace checks and record the exact results in TEST_MATRIX.md.

P7 is complete. The source implementation is recorded in commit
`404197560629cde55232518c21d3d98b3cbe4988`. The policy/default, shared
approval boundary, Desktop setting, real host smoke, targeted tests, and
production build pass. The full backend comparison measured 3,219 files,
37,160 passed, 7 failed, and 244 skipped: four are the current accepted
upstream baseline; the two cold-start failures pass with the persistent
Hafiye service stopped and remain KI-016 topology diagnostics; the browser
reconnect failure is the existing KI-019 scheduling diagnostic and passed on
an immediate isolated retry. No new Hafiye regression was found. P8 is closed
below.

## P8 execution status

- [x] Add `hafiye-rootd` as a dedicated system service without running the
      main Hafiye process as root.
- [x] Use a local Unix socket at `/run/hafiye/root.sock` with Linux
      `SO_PEERCRED` authentication and an exact configured local UID allowlist.
- [x] Enforce strict length-prefixed JSON framing, duplicate-key rejection,
      request/argument validation, size limits, timeouts, and fail-closed
      malformed/unauthorized responses.
- [x] Implement `package.install`, `package.remove`, `service.start`,
      `service.stop`, `service.restart`, `file.write_privileged`,
      `power.action`, and `root.exec` through the broker.
- [x] Audit accepted, rejected, failed, and closed requests with peer
      identity, durations, and redacted arguments; expose no TCP/UDP listener.
- [x] Add the Hafiye CLI root-broker management commands and packaged
      `hafiye-rootd` entrypoint.
- [x] Install the real system service with normal interactive sudo and verify
      the root/non-root process boundary on the host.
- [x] Run broker unit/security, packaging, CLI-registry, lint/compile, real
      privileged-operation, malformed-request, unauthorized-peer, and audit
      checks and record exact results in TEST_MATRIX.md.

P8 is complete. The source implementation is recorded in commit
`4972645e07c408a8f0856bc4f1ee1b1cd62cd63a`. The service is enabled and active;
the root broker returns UID 0 while the Hafiye gateway remains UID 1000. Real
privileged file-write and `root.exec` smoke tests passed, malformed duplicate
JSON failed closed, an actual `nobody` peer received `permission_denied`, and
audit records contained peer/lifecycle/duration data without raw command text.
The affected CLI/packaging matrix passed with no new Hafiye regression.

## P9 execution status

- [x] Reuse the pinned `agent-sh/computer-use-linux` source checkout and
      resolve its real installed binary through a Hafiye-managed boundary.
- [x] Connect `computer-use-linux` automatically as the built-in
      `hafiye-computer-use-linux` MCP provider without requiring a user
      `mcp_servers` configuration edit.
- [x] Expose real source identity, doctor readiness, blockers, and MCP
      diagnostics in Desktop `Settings → Computer`.
- [x] Preserve the existing Hermes MCP lifecycle and model toolset resolver;
      add focused regression coverage for managed-provider injection and
      host-independent upstream config tests.
- [x] Run the targeted Python/MCP matrix, the Desktop Computer settings test,
      the full Desktop UI suite, typecheck, lint, and a clean production build.
- [x] Run the required E2E flow on the actual GNOME Wayland session:
      enumerate windows, read an accessibility tree, launch Calculator and
      verify `12*7 = 84`, create and navigate a Firefox tab, switch apps,
      launch VS Code, and interact with Files.

P9 is complete. The source implementation is recorded in commit
`6d3672e498e1bcb9316e5c7d88c9fc896714630c`. The pinned Hermes upstream commit
and baseline merge commit are unchanged. The managed provider doctor reports
all four required readiness booleans true with `blockers=[]`; real MCP
discovery registered 18 tools; the real desktop E2E passed. Firefox's
AT-SPI focus warning and VS Code's sparse accessibility tree are documented as
KI-022 and KI-023 warnings, not P9 blockers.

## P10 execution status

- [x] Reuse Hermes structured browser automation as Hafiye's structured lane;
      keep the current Hermes backend selection behavior intact.
- [x] Add the structured browser download operation using the current
      official `agent-browser` command and absolute destination validation.
- [x] Add an explicit native desktop-browser route through the managed
      `computer-use-linux` MCP provider for an existing authenticated browser
      session; do not create a second browser profile or cookie path.
- [x] Preserve the existing browser extension-router boundary and Hafiye
      `NORMAL`/`LOCAL_ONLY`/`OFFLINE` policy behavior for both routes.
- [x] Test structured navigation, page extraction, and download on a real
      local fixture.
- [x] Test native operation on the real existing Firefox Wayland window,
      including exact-window binding, navigation, focus/title readback, and
      temporary-tab cleanup.
- [x] Run the affected browser regression matrix, focused tests, lint,
      compilation, and whitespace checks.

P10 is complete. The source implementation is recorded in commit
`5d2354095562d149ff54e58d664c1b042cf50c3e`. The structured path passed real
navigation, extraction, and download; the native path passed through the
managed `computer-use-linux` MCP tools against the existing Firefox Wayland
window with `blockers=[]`. The browser regression matrix measured 504 passed
and 7 deselected with no failure. KI-022 remains a measured Firefox AT-SPI
warning only; there is no P10 blocker or new/different regression. P11 is
complete and P12 — Custom Hafiye wake word is now complete; P13 is the next
incomplete phase.

## P13 execution status

- [x] Add one gateway-owned cancellation controller for TTS, desktop actions,
      active sessions, delegations, registered processes, and the durable
      emergency-stop/root-RPC gate.
- [x] Route Desktop Stop, Composer Stop, tray Stop, Turkish `Hafiye dur`, CLI
      `emergency-stop`, and `Ctrl+Super+Escape` through the shared mechanism.
- [x] Add Electron global-shortcut registration and the real GNOME Wayland
      custom-keybinding fallback used when Electron cannot register the global
      accelerator on this host.
- [x] Verify pause/new-work rejection/resume, TTS interruption, desktop-action
      cancellation seams, long-task/process cancellation, root-broker blocking,
      and the real GNOME fallback trigger/cleanup.
- [x] Run the targeted Python and Desktop tests, typecheck, production build,
      lint, compilation, and whitespace checks.
- [x] Start and stop a real OpenHands delegation through `coding_delegate`.

P13 is complete. The shared cancellation implementation and all available real
stop paths pass, including the master-specific live OpenHands acceptance. The
managed OpenHands V1 runtime and `coding_delegate` are recorded in source
commit `dfb0d29c7ba80efadd5a517bac07aa949e517a5a`; a real Gemini-backed fixture
delegation edited `bug.py`, returned its result/change record, and the fixture
test returned `1 passed`. A second live worker was stopped through the shared
controller and resumed intentionally with no active process remaining. KI-027
is resolved. P14 — Memory + project registry followed and is now complete;
P15 followed and is complete; P16 is the next incomplete phase.

The OpenHands implementation was a P13 prerequisite. The complete P15
bootstrap, delegation, and Task Center progress acceptance is recorded below.

## P14 execution status

- [x] Use Hermes memory and FTS5 session search for recent conversation context.
- [x] Persist deterministic per-profile projects and resolve a saved path by
      project slug/name after a fresh backend process.
- [x] Exercise the real project tool boundary (`project_create` and
      `project_switch`) with a session-search recall assertion.
- [x] Exercise Desktop project grouping, project-picker search, rename, and
      destructive delete through the live gateway; preserve the repository
      directory after metadata deletion.
- [x] Run the targeted Python/Desktop matrices, E2E typecheck, real Electron
      acceptance, production build, lint, compilation, and whitespace checks.

P14 is complete. The pinned Hermes project registry/session-search surfaces
already supplied the runtime behavior; Hafiye source/test commit
`831405dcec4abcba033d8ccc18308804868ecb1f` adds the acceptance coverage and
isolated Desktop E2E wiring. The fresh-process memory/path E2E and real
Electron project acceptance passed, with no new or different regression.

## P15 execution status — complete

- [x] Pin and bootstrap the official OpenHands V1 source/runtime in a
      user-scoped Hafiye runtime with exact package versions.
- [x] Add `hafiye runtime openhands install` and `doctor`, including exact
      source checkout and package readiness verification.
- [x] Run `coding_delegate` through Hafiye's `coding` route against a local
      repository path and preserve process/emergency-stop ownership.
- [x] Record safe coding-task lifecycle/progress/tool/command/file-change and
      result metadata in the shared Task Center bridge.
- [x] Expose `tasks.list`, `tasks.cancel`, and `task.update` through the
      gateway and render the real Task Center panel in Desktop.
- [x] Pass the real natural-language fixture E2E: identify, delegate, edit,
      verify, return result, and report result.
- [x] Run the P15 Python/Desktop tests, typecheck, build, lint, compile, and
      whitespace checks.

P15 is complete. Source/test commit
`54b4ee49569267b21e10b357acdde427a8a844ff` added the managed bootstrap and
Task Center bridge. The real Hafiye fixture E2E changed `bug.py` and returned
`pytest -q` result `1 passed`; the real gateway smoke observed `RUNNING`, final
`COMPLETED`, 18 progress records, and 22 `task.update` events. No new or
different upstream regression was found. P16 followed and is now complete;
its durable Task Center acceptance is recorded below.

## P16 execution status — complete

- [x] Persist the master Task Center record and safe progress history in the
      Hafiye XDG state root with thread-safe SQLite WAL writes.
- [x] Preserve completed/failed history across a new gateway process and
      recover in-flight worker states explicitly after restart; retain queued
      work as `QUEUED`.
- [x] Show current/queued/completed/failed states, current step, provider,
      model, route/privacy, tools, commands, modified files, subagent state,
      elapsed time, result/error, and cancellation in Desktop.
- [x] Keep transcript/private chain-of-thought out of persistence and UI.
- [x] Run the focused Python/RPC/UI/typecheck/lint/build checks and a real
      Electron + gateway acceptance against persisted records.

P16 is complete. The implementation commit is `c72c94418`; the queued-state
recovery fix and real Desktop acceptance are in
`f93d9183544581636c6af5b619d62d221040391d`. The real Electron acceptance
rendered completed, failed, and queued tasks and cancelled a queued task via
the real gateway. The separate-process restart smoke preserved completed
history, failed stale in-flight work honestly, and retained queued work. No
new or different upstream regression was found. P17 followed and is now
complete; P18 followed and is now complete; P19 is the next incomplete phase.

## P17 execution status — complete

- [x] Add the Hafiye Control Center overlay route and expose all 19 roadmap
      pages: Overview, Chat, Tasks, Models, Providers, Routing, Voice,
      Computer, Browser, Coding, Memory, Skills, MCP, Automation, Permissions,
      Privacy, Logs, Developer, and About.
- [x] Reuse the real Hermes/Hafiye backend boundaries for config, providers,
      skills/MCP, scheduler, logs, computer-use readiness, Task Center, and
      About instead of introducing a second state system.
- [x] Add the real `NORMAL` / `LOCAL_ONLY` / `OFFLINE` privacy selector and
      verify that it persists through the gateway config path.
- [x] Add Settings navigation and route classification while preserving the
      existing Hermes Settings surface and deep links.
- [x] Run the focused UI/typecheck/lint/build checks and real Electron/gateway
      acceptance.

P17 is complete. Source/test commit
`2dc541d09367b895744b512d99b058506d7f78d2` adds the Control Center and its
real acceptance test. The Electron test opened all 19 pages and persisted
Privacy Mode through a renderer reload. No new or different upstream
regression was found. P18 followed and is complete.

## P18 execution status — complete

- [x] Reuse Hermes cron storage, scheduler execution, recurring state, skills,
      toolset catalog, and MCP safety handling.
- [x] Persist and validate per-job Hafiye route and privacy selections through
      the profile-aware gateway REST boundary.
- [x] Resolve route/provider/model/privacy/fallback policy in the real
      scheduled `AIAgent` path without weakening the configured privacy mode.
- [x] Expose route, privacy mode, and enabled-toolset choices in the real
      Desktop cron editor, with values surviving edit/reload.
- [x] Verify a recurring local task through two real scheduler ticks.
- [x] Run the focused backend/Desktop matrix, clean production build, and real
      Electron/gateway acceptance.

P18 is complete. Source/test commit
`fd17e6533894a568744b82454635a8e6bf02709b` adds the scheduler policy boundary,
Desktop controls, and real acceptance tests. The two-tick local task produced
two completed execution-ledger records. No new or different upstream
regression was found. P19 followed and is complete.

## P19 execution status — complete

- [x] Preserve Hermes' existing prompt-injection, redaction, provider outage,
      loop-detector, checkpoint, and config-recovery boundaries.
- [x] Add bounded llama-server crash recovery with saved-state reuse and safe
      redacted diagnostics.
- [x] Add bounded whisper/Piper crash recovery and structured computer-use
      failure classification.
- [x] Add a per-task action budget and retain the existing exact-call loop
      detector.
- [x] Add audit-log retention, checkpoint retention integration, disk-space
      diagnostics, and a single `hafiye hardening doctor|prune` operator path.
- [x] Run the focused backend/adjacent matrix, real runtime/voice/
      computer-use doctors, and the canonical backend comparison.

P19 is complete. Source/test commit `0f45abb9c` adds the hardening boundary and
tests. The real hardening doctor returned `ok=true` with 12/12 checks true and
`blockers=[]`; the exact upstream comparison reduced the current baseline to
items 2, 3, and 5 of the historical five. No new P19-specific regression was
found. P20 — Packaging — followed and is complete; P21 — First-run Onboarding —
is now the next incomplete phase.

## P20 execution status — complete

- [x] Build the real Electron Linux output and wrap it in the Ubuntu/Debian
      `.deb` package required by the master roadmap.
- [x] Include the Hafiye backend, launchers, user gateway unit, explicit
      per-user root-broker activation path, XDG autostart/desktop entries,
      icons, notices, and dependency doctor/installer.
- [x] Keep managed model, voice, and computer-use runtimes as first-run/setup
      downloads rather than pretending they are statically bundled.
- [x] Validate package metadata, manifest commit identities, extracted doctor,
      rootless dpkg unpack/configure, and the real Electron pack.
- [x] Run the focused packaging/rootd tests and the exact five-ID upstream
      comparison. The comparison remains `3 failed, 2 passed`, with only
      accepted historical IDs 2, 3, and 5 failing.

P20 is accepted. Source/test commit
`964fc49b5f564f25588894374ea83e81cc2f58c7` contains the implementation and
tests; no Hermes upstream commit or history was changed. P21 — First-run
Onboarding — followed and is now complete.

## P21 execution status — complete

- [x] Implement the exact 20-step first-run onboarding state machine and
      persist its progress in the XDG Hafiye state root.
- [x] Add authenticated backend endpoints for environment, computer-use,
      runtime/model, voice, autostart, and final doctor checks.
- [x] Add the real packaged-install Electron/React wizard, including compute
      selection, local GGUF/model server setup, optional provider skips,
      microphone/STT, Piper/TTS, wake word, Hafiye test, execution policy,
      autostart, and final doctor controls.
- [x] Fix normal-XDG user-service generation so the persistent gateway and
      CLI share the same Hafiye state root; preserve explicit profile overrides.
- [x] Build and inspect the current `.deb`, run package doctor, run focused
      backend/Desktop checks, and compare the exact five upstream baseline IDs.
- [x] Verify the live authenticated onboarding doctor: all computer-use,
      local-server, voice, and autostart readiness fields pass with no blockers.
- [x] Replay all 20 steps through the real packaged Desktop GUI on the real
      host, including the microphone/STT, Piper/TTS, wake-word choice, Hafiye
      test, autostart, and final doctor transitions.

P21 implementation/source-test commits are `48860ee5f` and
`a87eaaba7373a2c23fa73b7ef498b64d67c989f5`. The pinned upstream commit and
baseline merge remain `f293e7206b4ddd66042329442c6afebc19a8808d` and
`2ac06b131a237916432503ac67bbcada6dbea39e`; no Hermes history was rewritten.
The P21-closure exact five-ID comparison was `3 failed, 2 passed`, with only
accepted historical IDs 2, 3, and 5 failing. The packaged Electron replay
reached all 20 steps and completed the wizard. After the temporary acceptance
gate was removed, the normal live service and CUDA local server were restored
and the authenticated final doctor remained green. P22 — CLI — followed and is
complete; P23 is now the first incomplete phase.

## P22 execution status — complete

- [x] Expose the Hafiye product command vocabulary while retaining the
      upstream Hermes CLI compatibility surface.
- [x] Route `hafiye ask` through the existing one-shot agent path and keep
      explicit provider/model selections effective even when onboarding has
      populated the default route slot.
- [x] Reuse the existing persistent gateway service, local GGUF runtime,
      provider catalog, route/privacy policy, durable Task Center, and
      computer-use-linux doctor boundaries.
- [x] Add the product aliases `projects` and `automation` without creating
      second project or scheduler implementations.
- [x] Run targeted Python tests, lint/compile/whitespace checks, real CLI
      parser/help checks, service/model lifecycle checks, computer-use doctor,
      and real Gemini one-shot validation.
- [x] Compare the exact five upstream baseline tests after the source change;
      the accepted set remained unchanged and no new regression was found.

P22 source/test commit: `e031162fd`. Its exact five-ID comparison returned
`3 failed, 2 passed`; only accepted historical IDs 2, 3, and 5 failed. The
small local Qwen one-shot's 4K-context rejection is retained as historical
KI-014 evidence; the managed Qwen2 64K compatibility path is recorded in the
open P23 work below. The explicit Gemini `hafiye ask` path passed. P23 — Final
E2E Suite — is now the first incomplete phase.

## P23 execution status — in progress

- [x] Run the P23 backend target matrix: `251 passed, 2 skipped, 1 warning`.
- [x] Re-run the exact five-ID upstream comparison after KI-043 source
      hardening; the direct canonical run returned `3 failed, 2 passed`, with
      only accepted historical IDs 2, 3, and 5 failing. No new/different
      failure was found.
- [x] Unify native gateway and Electron/TUI route resolution with the normal
      Hafiye XDG config root; source/test commit `ba113121f`.
- [x] Launch the real packaged Composer and observe the Firefox operation under
      a forced Gemini route; the operation executed, but a later request hit
      Gemini HTTP 429 and remains a documented warning.
- [x] Restore the user's local custom/Qwen route, restart the user service, and
      verify the CUDA runtime and computer-use readiness.
- [x] Recheck the root broker/main-process UID boundary, direct local endpoint,
      and packaged Desktop boot after a gateway restart.
- [x] Exercise the structured browser and native Firefox routes; the real
      native screenshot verified the P23.10 fixture UI and the prior browser
      tab was restored. Retain the host's root-only AT-SPI focus warning as
      KI-022, without treating it as a failed UI-task acceptance.
- [x] Execute the P23.9 desktop sequence through the managed
      `computer-use-linux` MCP boundary: real VS Code windows were switched,
      mouse/keyboard input was sent, the marker was saved and visually
      verified, and fixture windows were closed. KI-044 records the separate
      Gemini natural-language tool-selection warning.
- [x] Probe two pinned 64K-capable GGUF candidates; restore the original
      Qwen/CUDA runtime after recording their historical KI-040 diagnostics
      (one CUDA OOM, one non-terminating agent response).
- [x] Add and test the narrowly scoped managed Qwen2 YaRN/context-metadata
      compatibility path; verify the live CUDA runtime reports 65,536 context
      and that direct AIAgent plus packaged Desktop terminal calls pass.
- [x] Register the official Qwen3-14B Q4_K_M GGUF candidate and add the
      managed llama.cpp Jinja/reasoning, 65K YaRN metadata, fit-aware CUDA,
      and CPU-KV compatibility path. The isolated real Hafiye AIAgent replay
      passed exact Firefox activation, file create/read/move, VS Code managed
      input, multi-step terminal, OpenHands delegation, and same-session
      multi-turn tools. The measured VRAM/RAM/swap envelope remains KI-046;
      Qwen3 is selectable but is not made the default route.
- [x] Freshly recheck project alias/session persistence, OpenHands readiness,
      root-broker UID, and voice-runtime readiness; the exact P23.13 OpenHands
      fixture delegation also completed through the Gemini coding route and
      passed its independent pytest verification. Exact voice acceptance
      remains open.
- [x] Verify the real `LOCAL_ONLY` fail-closed boundary against a configured
      Gemini route; the request was blocked before provider execution and the
      original local route/privacy state was restored.
- [x] Rotate the Gemini credential through Linux Secret Service and verify a
      real Gemini one-shot plus the target packaged Composer Firefox action.
- [x] Execute a real authenticated Desktop session before and after restarting
      `hafiye-gateway.service`; durable `session.resume` and the post-restart
      prompt completed with marker `P23_RESTART_RECONNECT_OK`.
- [x] Resolve KI-043 at the shared source boundary: normal terminal/process
      execution detects direct and wrapped privilege escalation, routes
      FULL_AUTONOMOUS operations through `hafiye-rootd`, keeps READ_ONLY and
      confirmation policies intact, and adds regression/audit coverage.
- [x] Persist the evidence-backed local model capability state: Qwen2.5-0.5B
      is `validation=true, agent=false`; Qwen3-14B is
      `agent=true, tool_calling=true, validation=false` with `KI-046`; Qwen3
      remains selectable and is not the default route.
- [x] Complete the P23.1 reboot preflight: `hafiye-gateway.service` is
      enabled/active, `/api/health` returned HTTP 200, the validated packaged
      XDG autostart entry exists, and voice/computer-use doctors are green.
      This is pre-reboot evidence only; it does not pass the real reboot/login
      acceptance.
- [x] Fix the post-reboot managed computer-use MCP startup gate exposed by the
      real Composer path: the in-memory Hafiye provider now opens shared MCP
      discovery. Source/test commit `dc962963e`; the targeted discovery set
      returned `40 passed`, focused gateway discovery returned `3 passed`, and
      the restarted gateway registered 18 managed tools.
- [x] Isolate the P23.1 post-reboot autostart failure: GNOME did execute the
      entry, but Electron exited because `chrome-sandbox` was `tolga:tolga
      0755`; the journal captured the exact fatal message.
- [x] Fix the Debian packaging boundary so `chrome-sandbox` is shipped with
      setuid mode `4755`; source/test commit
      `a1271a93277e6ac0747c1c5c31b586c2e883e55a`; packaging tests returned
      `4 passed`. The current unpacked helper was repaired through rootd to
      `root:root 4755` and a sandbox-enabled short launch passed.
- [x] P23.1 fresh real reboot/login acceptance passed on boot
      `db40c0c5-f5b3-4dcf-8d01-7cf425e15323`: GNOME launched the packaged
      Desktop from `~/.config/autostart/hafiye.desktop` without manual
      startup; gateway/health, tray, Composer, voice doctor, and computer-use
      doctor were green. `chrome-sandbox` was `root:root 4755` and no SUID
      sandbox fatal was recorded. KI-013 is RESOLVED.
- [ ] Re-run the clean Gemini Composer text acceptance with the resolved
      KI-043 boundary; this final real-machine replay remains explicitly
      deferred below and is not represented as passed.
- [x] Complete the real 23.8 file organize-and-verify replay through the
      authenticated Gemini route; the required files were moved and verified.
      KI-041 retains the earlier local-Qwen multi-step tool-calling warning.
- [ ] Complete the local-route 23.2 natural-language Desktop task; after the
      managed-MCP startup fix, the agent-qualified Qwen3 Composer replay exposed
      18 managed tools but produced no tool call during the approximately
      265-second observation, while the Qwen2 validation fixture also returned
      text without computer use. Keep KI-042 and KI-047 open.
- [x] Complete a clean Gemini-backed packaged Composer task after the quota
      recheck: the real Desktop created/read `/tmp/hafiye-p23-gemini/ok.txt`,
      returned `P23_GEMINI_COMPOSER_OK`, and independent content verification
      passed without a privileged command or password dialog. This passes
      P23.6; the exact Firefox P23.2 replay remains open separately.
- [x] Replace the inherited root README with Hafiye-specific first-install,
      source-update, package-reinstall, GUI model, security, diagnostics, and
      contribution guidance. The documented install dry-run exposed and fixed
      the current Ubuntu Python 3.14 Debian bootstrap conflict in source/test
      commit `fd435cc85`; targeted packaging/metadata tests returned 13 passed,
      the rebuilt real artifact resolved under `apt --simulate`, and extracted
      package doctor returned no blockers. The exact upstream comparison
      remained 3 failed/2 passed with only historical IDs 2, 3, and 5. This
      maintenance does not complete any open P23 final-machine row.
- [x] Add the persisted Turkish Desktop locale through the existing i18n
      boundary. `Türkçe` is selectable under Appearance, core Desktop surfaces
      are translated, locale persistence/runtime tests pass, the full UI suite
      is 5,558/5,558 green, and the final package is stamped from source commit
      `684227f6ebbf` with Electron `40.10.6` aligned across dependency, builder,
      installed module, and packaged runtime. The `.deb` was installed through
      the graphical sudo path and the new packaged Desktop/gateway were
      verified live. Advanced English fallback remains the non-blocking KI-052
      coverage warning and does not complete P23.
- [x] Resolve Settings/Composer/new-chat model drift at the real session
      boundary. New Chat now derives from the target profile's Settings model,
      deliberate Composer picks remain per-session overrides, and the gateway
      no longer replaces an explicit Desktop provider/model with the Hafiye
      default route. Source `197e4ca8f`; targeted Desktop/backend tests, full
      Desktop tests, typecheck/lint, package build/install, live gateway health,
      and model-info checks passed. KI-053 is resolved; this maintenance does
      not complete a deferred P23 final-machine row.
- [ ] Execute and record the remaining real-machine items 23.3, 23.5,
      23.14, and the long-running managed desktop portion of 23.15 from the
      master roadmap. P23.4 was explicitly skipped by the user and is not
      passed; P23.5 has no configured remote endpoint. Earlier phase evidence
      is not silently promoted to final P23 acceptance; 23.1 and 23.16 now
      have fresh real reboot/reconnect evidence.
- [ ] Mark P23 complete and create its completion commit only after every
      acceptance row has fresh evidence.

P23 is still the first incomplete phase. The current state, exact commands,
and unverified acceptance rows are recorded in `STATE.md` and `TEST_MATRIX.md`.

## Post-roadmap implementation audit

- [x] Correct bare-metal container detection, package-aware gateway/rootd
      provenance, Hafiye status/doctor identity, persistent XDG component
      logging, onboarding test isolation, and canonical audit events.
- [x] Make package launchers independent of the caller checkout/CWD and make
      package doctor recognize the installed Hafiye launcher without requiring
      a development venv entry point.
- [x] Build/install the package from source `822448ade`; verify live gateway
      health, all required doctors, real root RPC/audit events, model route,
      backend/Desktop regression matrices, and the exact upstream comparison.

This maintenance is complete but does not create a phase or complete P23. The
current exact upstream result is `2 failed, 3 passed`, with only historical IDs
2 and 3 failing.

## Deferred P23 acceptance reminder

Per the user's explicit instruction on 2026-08-25, the following remaining
real-machine acceptance steps are intentionally deferred. The completed P23.1
row is retained for the audit trail; open rows are not passed and must be
replayed before P23 is ever marked complete:

- [x] P23.1 reboot/login, gateway/Desktop/tray/Composer boot. The second
      real replay passed on boot `db40c0c5-f5b3-4dcf-8d01-7cf425e15323`; see
      the execution record above and `TEST_MATRIX.md`.
- [ ] P23.2 clean Composer text behavior using the resolved KI-043 safety
      boundary.
- [ ] P23.3 live Turkish wake-word, voice command, and spoken response.
- [ ] P23.4 actual disconnected-network local chat and computer operation.
      User explicitly instructed to skip this replay on 2026-08-25; it remains
      unaccepted and must not be marked PASS.
- [ ] P23.5 configured OpenAI-compatible remote GPU route. No real endpoint is
      currently configured; see KI-048.
- [x] P23.6 clean Gemini task result. The packaged Composer file task returned
      `P23_GEMINI_COMPOSER_OK` and passed independent content verification.
- [ ] P23.14 live spoken barge-in with `Hafiye dur.`.
- [ ] P23.15 long-running managed desktop action stopped by
      `Ctrl+Super+Escape`.
These deferred checks must not be silently converted into a completed P23.
P24 may remediate gaps exposed by these rows, after which affected P23 evidence
must be replayed from the installed post-P24 package.

## P24 execution plan — Hafiye Jarvis experience convergence

Status: SOURCE IMPLEMENTATION COMPLETE; INSTALLED REAL-MACHINE ACCEPTANCE OPEN.
Added by binding user direction on 2026-08-27. The current source checkpoint is
`8b7c29aa8197595a479e35bb85ef081cec2b7a11`; these implementation marks do not
promote the physical P24.14 acceptance to PASS. The installed package now
carries this same source checkpoint.

- [x] P24.1 Capture the installed-product baseline: package/source identity,
      login/autostart state, current wake/voice settings, Composer behavior,
      agent route, and real microphone/browser/tool readiness.
- [x] P24.2 Implement one canonical interaction state machine spanning
      `IDLE_ARMED → WAKE_DETECTED → LISTENING → TRANSCRIBING → ACKNOWLEDGING
      → THINKING/WORKING → SPEAKING → COMPLETED/ERROR → REARMING`.
- [x] P24.3 Auto-arm the local wake listener after graphical login and prior
      microphone consent, while preserving an explicit persisted user disable.
- [x] P24.4 Make a real `wake.detected` event open/focus Hafiye Composer on the
      active display without opening the full Desktop or requiring the hotkey.
- [x] P24.5 Show the final Turkish whisper.cpp transcript in the Composer field
      before normal submission; preserve failed transcripts for correction and
      never submit empty speech.
- [x] P24.6 Add the short spoken-assistant presentation contract: concise
      acknowledgement before work, concise verified completion/blocker after
      work, detailed output visual only, Piper Turkish TTS, no long automatic
      model-response reading.
- [x] P24.7 Feed real session/task/tool/model/progress/cancellation state into
      Composer instead of reducing voice work to a generic busy boolean.
- [x] P24.8 Make tool-backed work and postcondition verification mandatory for
      actionable voice requests; preserve rootd, privacy, audit, stop and
      emergency boundaries.
- [ ] P24.9 Implement and verify the coding-assistant flow for “Randevu
      projesini açıp bug fix yapalım”: project/memory resolution, real IDE,
      diagnosis, OpenHands when editing is required, tests and concise speech.
- [ ] P24.10 Implement and verify the browser/media flow for “YouTube'dan
      Mertcan Bahar'ın son videosunu aç”: correct channel, latest video,
      open/playback verification and concise speech. The installed package's
      Gemini replay reached the correct video/playback state, but did not
      terminate as a clean Composer task; final acceptance remains open.
- [ ] P24.11 Qualify and select a practical agent-capable local-first default
      through registry capability metadata. Keep Qwen2 validation-only and
      retain Qwen3 KI-046/non-default status unless host evidence changes.
- [ ] P24.12 Make completion, failure, cancellation, no-speech, provider/tool
      error, restart and suspend/resume converge on clean microphone release,
      Composer lifecycle and verified wake re-arm.
- [x] P24.13 Add automated state, Desktop, gateway, voice, policy, tool,
      package and regression tests specified by the master roadmap.
- [ ] P24.14 Run the installed real-machine acceptance: reboot/login, physical
      wake, visible transcript, short acknowledgement, coding flow, YouTube
      flow, truthful blocker, three repeated turns, barge-in, local/offline,
      restart recovery, affected P23 replays and exact upstream comparison.
- [ ] Mark P24 complete only after every P24.14 item is genuinely green and
      create separate source and documentation closure identities.

P24.1–P24.8 and P24.13 are source-level implementation checkpoints backed by
targeted tests and the installed package smoke check. The native browser
focus-recovery correction is in source checkpoint `8b7c29aa` and has a real
GNOME/AT-SPI tool-boundary replay, but it does not itself satisfy P24.10.
P24.9–P24.12 and P24.14 remain open until their real task/voice/recovery
evidence exists. The user's explicitly deferred offline replay is not marked
PASS.

P24 is not a new generic runtime or technology-selection phase. It converges
the existing Hermes, Composer, gateway, llama.cpp, whisper.cpp, Piper,
computer-use-linux, OpenHands and rootd machinery into Hafiye's primary Jarvis
assistant loop.
