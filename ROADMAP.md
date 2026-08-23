# Roadmap

The authoritative phase definitions are in HAFIYE_MASTER_ROADMAP.md. This file
records execution status only.

- [x] P0 Fork + environment
- [x] P1 Hafiye external identity and data root
- [x] P2 Persistent gateway + Desktop connection
- [x] P3 Hafiye Composer + tray + autostart
- [ ] P4 llama.cpp managed local runtime
- [ ] P5 Providers + Gemini + remote OpenAI-compatible
- [ ] P6 Model router + privacy modes
- [ ] P7 Full host tools + execution policy
- [ ] P8 Hafiye root broker
- [ ] P9 Linux computer use
- [ ] P10 Browser
- [ ] P11 Local Turkish voice stack
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

P0 is complete. The original five-failure baseline was reduced to four current
accepted failures after Hafiye source changes; the browser-control baseline
failure now passes. The accepted failures, missing pactl, and missing
vulkaninfo are documented warnings/diagnostics and are not P0 blockers.

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
