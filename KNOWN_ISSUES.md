# Known Issues

These are measured issues and accepted baseline findings. They are not
silently treated as passing.

## KI-001 — ACCEPTED_UPSTREAM_BASELINE: reduced from five to four failures

- Status: ACCEPTED_UPSTREAM_BASELINE; not a Hafiye P0 blocker.
- The lean pre-change run completed 3,210 files with 36,814 passed, 80 failed,
  and 324 skipped.
- The canonical pre-change run with relevant optional SDKs completed 3,210
  files with 36,903 passed, 5 failed, and 320 skipped; exit 1.
- The exact original five failures were:
  1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
  2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
  3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
  4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
  5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics
- The corrected current post-source run completed 3,213 files with 37,009
  passed, 6 failed, and 291 skipped in 515.9 seconds. The browser-control
  failure now passes.
- Therefore the current exact regression comparison set is:
  1. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
  2. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
  3. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
  4. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics
- The original five are historical evidence; the measured smaller set is the
  updated baseline under the binding regression rule.
- The same current four failures are not new Hafiye regressions. A further
  reduction updates the baseline; any new or different failure must be
  investigated. Hafiye does not fix these upstream bugs.

## KI-002 — System Python is outside the Hermes constraint

- Status: WORKAROUND ACTIVE.
- System Python is 3.14.4; upstream pyproject.toml declares
  requires-python >=3.11,<3.14.
- The repository .venv uses uv-managed CPython 3.13.15.

## KI-003 — Compute hardware differs from the superseded AMD assumption

- Status: ARCHITECTURE AMENDMENT APPLIED; not a P0 blocker.
- The host has Intel UHD 770 and NVIDIA GeForce RTX 3080 with driver 595.84;
  no AMD GPU is present.
- The binding policy is AUTO: NVIDIA plus CUDA when available, otherwise
  Vulkan, otherwise CPU. Managed llama.cpp and whisper.cpp use CUDA primary
  with Vulkan/CPU fallback. This host is expected to select CUDA.
- nvidia-smi and NVIDIA OpenGL work. P4's real managed llama.cpp build and
  CUDA chat verification now pass; the later whisper.cpp CUDA runtime remains
  a separate voice-stack task.

## KI-004 — computer-use-linux readiness was incomplete before relogin

- Status: RESOLVED — P0 acceptance passed.
- Pinned source:
  agent-sh/computer-use-linux at
  94736dc3e0dca56acfc89752c26869fb9ed01202.
- The official pinned-source setup enabled AT-SPI, installed ydotool/ydotoold,
  installed the GNOME window-targeting extension, and prepared /dev/uinput.
- After logout/login, doctor reported all four mandated readiness booleans true
  and blockers=[].
- A real computer-use-linux windows query returned the focused desktop window.

## KI-005 — computer-use-linux release asset mismatch

- Status: UPSTREAM PACKAGING WARNING; not the final setup path.
- The pinned source is version 0.4.10, but its expected GitHub release asset
  returned HTTP 404.
- Released npm @agent-sh/computer-use-linux@0.4.9 was used only for historical
  diagnostic evidence.
- The final setup uses the pinned source checkout's official install flow.

## KI-006 — Optional diagnostic tools remain absent

- Status: SETUP COMPLETE; diagnostic warnings remain.
- pactl is absent, but PipeWire 1.6.2, WirePlumber 0.5.13, pipewire-pulse,
  and wpctl are present and enumerate microphones. This is not a P0 blocker.
- vulkaninfo is absent. Vulkan loader/ICD packages are present, and Vulkan is
  a fallback rather than the primary backend on this host. This is not a P0
  blocker.
- The official source setup provisioned Rust/Cargo 1.98.0 under
  /home/tolga/.cargo/bin and built the pinned source successfully.
- Ubuntu's packaged ydotool.service is enabled and active in the current user
  session. The duplicate generated ydotoold.service was disabled/removed after
  its same-socket collision, and the root user-manager ydotoold instance was
  disabled.
- sudo requires normal interactive authentication; no passwordless sudo or
  NOPASSWD sudoers rule was created.

## KI-007 — Baseline npm audit reports vulnerabilities

- Status: UPSTREAM BASELINE WARNING.
- Root npm install reported 3 high-severity vulnerabilities and deprecated
  packages.
- npm audit fix was not run because it could rewrite upstream dependencies and
  the lockfile outside the prescribed P1 scope.

## KI-008 — Two full-suite async diagnostics are timing-sensitive

- Status: DIAGNOSTIC; not accepted baseline and not a confirmed Hafiye
  regression.
- The post-source full backend run timed out in:
  1. tests/gateway/test_browser_control_api.py::test_real_browser_action_routes_through_controller_without_legacy_fallback
  2. tests/gateway/test_turn_lease.py::test_full_dispatch_rejects_lease_timeout_without_running_goal_hook
- Both tests passed when run in isolation, including repeated isolated checks.
- The exact current four accepted baseline failures remain KI-001. These two
  tests require investigation if they reproduce outside the full-suite
  scheduling context or appear after later Hafiye changes.

## KI-015 — One full-suite timing flake passed on retry

- Status: DIAGNOSTIC; no confirmed Hafiye regression.
- `tests/tools/test_zombie_process_cleanup.py` failed once during the corrected
  full run, then passed on the runner's retry. The final suite summary counts
  it as passed; it is retained here because the runner reported it as flaky.
- Re-run this file in isolation if it fails again or if the failure persists
  after later Hafiye changes.

## KI-016 — Persistent Hafiye service interferes with one upstream lifecycle test

- Status: TEST-TOPOLOGY DIAGNOSTIC; not a Hafiye product blocker.
- When the active `hafiye-gateway.service` is present, upstream
  `tests/hermes_cli/test_update_cold_start_gateway_liveness.py` detects a
  Desktop-owned gateway and its two cold-start tests fail. Stopping the
  Hafiye service makes both tests pass in isolation.
- The corrected full regression comparison stopped the Hafiye service and the
  managed local model server temporarily, then restored both after completion.
  This isolates the upstream lifecycle test from the intentionally persistent
  Hafiye topology.

## KI-009 — Hafiye P1 source regression

- Status: NONE OBSERVED.
- P1 targeted Python tests, the full Desktop suite, typecheck, clean build,
  Linux unpacked packaging, lint, and temporary-root CLI smoke tests passed.
- This entry is retained to make the P1 acceptance state explicit; it is not a
  workaround or a fabricated pass.

## KI-010 — User-systemd linger is disabled on this host

- Status: P2 warning; not a Desktop-close blocker.
- The `hafiye-gateway.service` is enabled and active in the current user
  session and remained active after the real Electron process closed.
- `loginctl show-user "$USER" -p Linger` reports `Linger=no`; full logout/reboot
  persistence is therefore not claimed by P2 and belongs to later Composer,
  onboarding, and packaging work.
- No passwordless sudo or NOPASSWD sudoers change was made. Any later linger
  change must use the normal user/system authorization path.

## KI-011 — Persistent gateway uses a fixed implementation port

- Status: diagnostic.
- P2 binds the persistent service to `127.0.0.1:9120` and records that port in
  the connection descriptor. A collision prevents startup and is handled by
  the systemd restart policy.
- This fixed loopback port is intentional for the P2 Desktop connection
  contract; user-facing port configuration is later work if the roadmap
  requires it.

## KI-012 — GNOME owns the mandated default Composer shortcut on this host

- Status: ENVIRONMENT WARNING; Hafiye does not change the user's binding.
- The roadmap-mandated default `Super+Shift+Space` is currently registered by
  GNOME as `org.gnome.desktop.wm.keybindings switch-input-source-backward`
  (`<Shift><Super>space`). Electron's real `globalShortcut` registration
  therefore reports `taken`.
- The Composer setting remains configurable and the real tray, login-mode
  Composer, and direct entry remain available. The host binding was inspected
  but not silently overwritten.
- If the user wants the mandated default to register, remove that GNOME
  binding (or choose another shortcut in Hafiye Desktop settings), then restart
  Desktop and verify the registration log.

## KI-013 — Full reboot/login acceptance was not performed in the P3 session

- Status: OPERATIONAL FOLLOW-UP; not a source blocker.
- A real Wayland Desktop launch used the exact generated XDG autostart command
  with `--hidden`; the process reached persistent-backend readiness and the
  autostart file is owner-created with mode 0644.
- A full reboot was intentionally not issued from the shared development
  session. The direct autostart invocation is recorded as the non-disruptive
  login-equivalent check; a later reboot/login should confirm the desktop
  session manager consumes the entry automatically.

## KI-014 — Small validation GGUFs have a lower trained context window

- Status: TEST-FIXTURE LIMITATION; not a runtime or P4 blocker.
- The real Gemma and Qwen validation files report a trained context limit of
  32,768 tokens, while Hermes' default local-agent configuration can request a
  larger context. The CUDA endpoint and Hermes one-shot were verified by using
  an explicit compatible server context and disabling auxiliary compression for
  the small Qwen smoke model.
- Production model entries must advertise a context window compatible with the
  requested Hafiye agent configuration. This is a model-selection/configuration
  concern, not a reason to weaken the managed runtime contract.
