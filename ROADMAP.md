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
- [ ] P12 Custom Hafiye wake word
- [ ] P13 Barge-in + emergency stop
- [ ] P14 Memory + project registry
- [ ] P15 OpenHands coding delegate
- [ ] P16 Task Center
- [ ] P17 Control Center
- [ ] P18 Scheduler / skills / MCP
- [ ] P19 Hardening
- [ ] P20 Packaging
- [ ] P21 First-run onboarding
- [ ] P22 CLI
- [ ] P23 Final E2E suite

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
real Electron voice smoke also passed. KI-025 is resolved; P12 is now the next
incomplete phase.

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
`ACCEPTED_UPSTREAM_BASELINE`; the current post-P5 comparison baseline is the
four members that reproduced. A later full run contained four of those IDs
plus the separately investigated KI-019 browser reconnect diagnostic; the accepted
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
      GGUF import, model selection, context/GPU layers, load, and unload.
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
baseline rule. P7 followed this phase and is closed below.

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
complete and P12 — Custom Hafiye wake word is now the next incomplete phase.
