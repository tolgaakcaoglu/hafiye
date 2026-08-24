# Known Issues

These are measured issues and accepted baseline findings. They are not
silently treated as passing.

## KI-001 — ACCEPTED_UPSTREAM_BASELINE: exact five upstream failures

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
- A later corrected post-source run temporarily measured 3,213 files with
  37,009 passed, 6 failed, and 291 skipped; the browser-control baseline test
  passed in that run.
- The latest post-P5-source-fix full parallel run measured 3,218 files with
  37,156 passed, 4 failed, and 244 skipped in 541.8 seconds. Four failures were
  members of the original five; the original remote browser-control ID did
  not reproduce in that run.
- The current exact-comparison baseline after P19 is the three reproduced IDs
  (original IDs 2, 3, and 5 below); original IDs 1 and 4 passed. The original
  five-ID set remains the historical accepted whitelist. This reduction is
  recorded as a baseline update, not a Hafiye regression.
- A different browser-control reconnect test appeared in that run. It is
  tracked separately as KI-019 after reproducing in the P6-parent checkout;
  it is not added to this exact five-ID baseline.
- The same exact five after future Hafiye changes are not new regressions. A
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
  disabled during the P0 setup. A later host probe found a separate root-owned
  `/run/user/0/.ydotool_socket` process again; the current user socket remains
  healthy. That current observation is tracked as KI-039 and is not a Hafiye
  readiness blocker.
- sudo requires normal interactive authentication; no passwordless sudo or
  NOPASSWD sudoers rule was created.

## KI-007 — Baseline npm audit reports vulnerabilities

- Status: UPSTREAM BASELINE WARNING.
- The original root npm install reported 3 high-severity vulnerabilities and
  deprecated packages. The current `hafiye doctor` also reports 4 findings in
  `web` and 3 findings in `ui-tui`.
- npm audit fix was not run because it could rewrite upstream dependencies and
  the lockfile outside the prescribed P1 scope.

## KI-008 — Two full-suite async diagnostics are timing-sensitive

- Status: DIAGNOSTIC; not accepted baseline and not a confirmed Hafiye
  regression.
- The post-source full backend run timed out in:
  1. tests/gateway/test_browser_control_api.py::test_real_browser_action_routes_through_controller_without_legacy_fallback
  2. tests/gateway/test_turn_lease.py::test_full_dispatch_rejects_lease_timeout_without_running_goal_hook
- Both tests passed when run in isolation, including repeated isolated checks.
- The exact current five accepted baseline failures remain KI-001. These two
  tests require investigation if they reproduce outside the full-suite
  scheduling context or appear after later Hafiye changes.

## KI-015 — Full-suite timing flake passed on retry

- Status: DIAGNOSTIC; no confirmed Hafiye regression.
- `tests/gateway/test_turn_lease.py::test_full_dispatch_rejects_lease_timeout_without_running_goal_hook`
  failed once during the latest full parallel run, then passed on the runner's
  retry and in an isolated 12-test run. It is retained here because the runner
  reported it as flaky.
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
- In the P7 full comparison, the service was intentionally left active for the
  normal-host run and both cold-start tests failed as expected; stopping the
  service and rerunning the file produced 2/2 passes. The service was started
  again and verified active afterward.

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

- Status: TEST-FIXTURE LIMITATION; not a runtime, P4, or P22 blocker.
- The real Gemma and Qwen validation files report a trained context limit of
  32,768 tokens, while Hermes' default local-agent configuration can request a
  larger context. The CUDA endpoint and Hermes one-shot were verified by using
  an explicit compatible server context and disabling auxiliary compression for
  the small Qwen smoke model.
- The real P22 `hafiye ask` attempt against the onboarding-selected Qwen
  fixture was rejected because the running fixture advertised a 4,096-token
  context below Hermes' 64K minimum agent context. This is the same fixture
  limitation, not a new CLI/runtime regression. The explicit Gemini
  `hafiye ask` path returned `P22_GEMINI_CLI_OK`.
- A P23 recovery attempt loaded the same GGUF with `--context-size 65536`.
  llama.cpp correctly capped the slot at the model's trained 32,768-token
  limit; the real `hafiye ask` then rejected 32,768 against Hermes' 64K
  minimum. The runtime was restored to its prior 4,096-token setting. A
  compatible production GGUF/model context remains required for local-agent
  final E2E acceptance.
- Production model entries must advertise a context window compatible with the
  requested Hafiye agent configuration. This is a model-selection/configuration
  concern, not a reason to weaken the managed runtime contract.

## KI-017 — P5 live Gemini credential was previously unavailable

- Status: RESOLVED 2026-08-24; no longer a P5 blocker.
- The live Gemini credential is now stored in the Hafiye Linux Secret Service;
  the raw value is intentionally not recorded in this repository. `hafiye
  status` reports Google/Gemini configured with a masked preview.
- A real Gemini model-list request returned HTTP 200 with 50 models, and the
  Hafiye one-shot test returned `HAFIYE_GEMINI_LIVE_OK`.
- Investigation found that the default XDG config/data split could write
  provider references under the data root while runtime hydration read the
  config root. Source commit `45294d3f77a3929731ac29d89d54f5d53c70957d`
  aligns save, refresh, and remove operations with the active config root and
  adds regression coverage. No plaintext credential was introduced.

## KI-018 — Optional extras are not fully installable on CPython 3.13

- Status: UPSTREAM OPTIONAL-PACKAGING/TOOLCHAIN WARNING; not a P5 blocker.
- `uv sync --locked --all-extras --python 3.13` cannot install
  `tflite-runtime==2.14.0`, which publishes only a CPython 3.11-compatible
  wheel for this environment. Excluding `wake` succeeds.
- The `matrix` extra remains excluded because `python-olm==3.2.16` fails with
  the current CMake toolchain's legacy minimum-version requirement. The
  relevant P5 and full backend tests run with all other optional extras
  installed; these two upstream optional packaging issues are recorded rather
  than substituted around.

## KI-019 — Upstream browser reconnect full-suite scheduling diagnostic

- Status: INVESTIGATED UPSTREAM; not a Hafiye regression or P6 blocker.
- The latest post-P6 full run failed:
  `tests/gateway/test_browser_control_api.py::test_local_api_same_identity_reconnect_completes_command_started_on_old_socket`.
- The same browser-control full-file failure reproduced in a clean checkout at
  the P6 parent commit `28e751f9b`, before Hafiye routing/privacy source
  changes. The selected reconnect test passed in both the P6 checkout and the
  P6-parent checkout when run with `-k` through `scripts/run_tests.sh`.
- The P6 diff does not modify the browser-control broker or extension router.
  Do not add this test to `ACCEPTED_UPSTREAM_BASELINE` or fix unrelated
  upstream browser-control behavior in P6. Re-run it in isolation if it
  reproduces outside the full-file scheduling context.

## KI-020 — P7 full-suite comparison diagnostics

- Status: DOCUMENTED DIAGNOSTICS; no P7 acceptance blocker and no Hafiye
  regression.
- The P7 full backend comparison measured 3,219 files with 37,160 passed, 7
  failed, and 244 skipped. The seven failures were the four current members
  of `ACCEPTED_UPSTREAM_BASELINE`, the two KI-016 persistent-service
  cold-start failures, and the KI-019 browser reconnect scheduling failure.
- P7 source changes are limited to host-tool policy/approval boundaries and the
  Desktop config setting; they do not modify the failing upstream browser,
  Windows lifecycle, FTS, execution-flag, Termux, or doctor implementations.
- The cold-start file passed after service isolation, and the browser test
  passed on the immediate isolated retry. Future full runs must continue to
  classify the exact failure IDs against the historical five and investigate
  any new or different ID.

## KI-021 — P8 editable-v-env systemd entrypoint (resolved)

- Status: RESOLVED 2026-08-24; not a P8 blocker.
- The first normal-sudo installation generated a unit using
  `python -m hafiye_rootd`. The editable venv's generated finder did not map
  the new top-level module when systemd started it outside the repository
  working directory, so the service repeatedly exited with `No module named
  hafiye_rootd`.
- The service generator now executes the installed `hafiye_rootd.py` entry file
  directly, and the package declares both the module and the `hafiye-rootd`
  console entrypoint. After the unit was regenerated, `hafiye-rootd.service`
  became active/enabled and the real broker acceptance tests passed.

## KI-022 — Firefox AT-SPI focus feedback warning during P9 E2E

- Status: MEASURED WARNING; not a P9 acceptance blocker.
- On the real GNOME Wayland session, targeted `press_key`/`type_text` calls
  for Firefox reported that AT-SPI could not identify a focused element in the
  Firefox application. The managed input calls still completed, the window
  title changed to the expected Example Domain page, and application focus
  switching was verified through `list_windows`/`focused_window`.
- Future browser-phase work should improve Firefox focus diagnostics and rerun
  the native browser acceptance path. This warning does not justify replacing
  the prescribed computer-use-linux backend.

## KI-023 — VS Code exposes a sparse AT-SPI tree in the current session

- Status: MEASURED WARNING; not a P9 acceptance blocker.
- The real VS Code window launched and accepted compositor focus, but its
  `get_app_state` response exposed only the application/frame nodes in this
  session. Files exposed a full accessible tree (137 nodes) and was interacted
  with successfully, satisfying the P9 acceptance requirement.
- Semantic VS Code interaction should be revisited if a later phase needs it;
  P9 only requires launching VS Code and interacting with Files.

## KI-024 — Browser wiring fixture launched a real agent-browser daemon (resolved)

- Status: RESOLVED 2026-08-24; test-harness issue, not a runtime or P10
  acceptance blocker.
- P10 expanded the browser registry-wiring test with `browser_download` and
  the real user-space `agent-browser` Chrome cache became discoverable. The
  fixture's legacy fallbacks were therefore able to launch a detached daemon;
  the following cleanup test hit the repository live-system guard while
  trying to terminate its foreign PID.
- The wiring fixture now stubs `_run_browser_command` for every legacy fallback,
  preserving the purpose of the test without launching a browser. The exact
  browser matrix then passed with 504 passed, 7 deselected, and 0 failed.
- No production browser route or user browser session was left running; the
  P10 native probe's temporary Firefox tab was closed and a post-cleanup
  window query found no P10 marker.

## KI-025 — Real Turkish microphone speech acceptance was initially not met

- Status: RESOLVED 2026-08-24; P11 acceptance passed.
- The final real capture used `pw-record --target 37 --rate 16000 --channels 1
  --format s16 --container wav` for `Trust GXT 232 Microphone Mono`; the WAV
  was 9.982 seconds, 16 kHz mono S16, with measured mean volume `-15.5 dB`.
- The prompted sentence was: “Merhaba Hafiye, bugün nasılsın? Bana Türkçe
  cevap ver.” The managed CUDA whisper.cpp path returned repeated/nonsensical
  text instead of the sentence, including:
  `Ha ha ha ... Sona da işe olup onun üstüne başka bir iddi ha daha konuşurum
  Abi de sen ne işle yok`.
- A synchronized follow-up capture after a short countdown used the same
  default node 37 and returned `Merhaba hafiye, bugün nasılsın bana Türkçe
  cevap ver?` through CUDA whisper.cpp. The same WAV returned the same correct
  text through Hafiye's `transcribe_audio()` hook with `provider: local_command`.
- The initial bad samples remain recorded as capture-window/low-level audio
  observations; no broader device defect is asserted. This was not an
  upstream baseline failure and no new upstream regression was added.

## KI-026 — openWakeWord packaging and local PortAudio diagnostics

- Status: MANAGED WARNING; not a P12 acceptance blocker.
- The openWakeWord 0.6.0 package metadata requires `tflite-runtime`, but the
  current CPython 3.13 environment has no compatible wheel. The official
  openWakeWord source checkout was installed with `--no-deps`, and its ONNX
  runtime path is the accepted Linux setup. The reproducible training source,
  model hash, and validation results are recorded in ENVIRONMENT.md.
- The repository venv's `sounddevice` import reports `PortAudio library not
  found`, so the gateway's local PortAudio capture reports a diagnostic and
  does not claim local input readiness. PipeWire/WirePlumber enumeration and
  Electron client capture are available; the real P12 minimized-Desktop
  acceptance passed through client PCM feeding.
- Future packaging work may add a compatible optional dependency path, but P12
  must not silently replace the prescribed openWakeWord/ONNX architecture or
  fabricate local-capture readiness.

## KI-027 — OpenHands stop acceptance was not executable before P15 integration

- Status: RESOLVED.
- The master P13 acceptance requires starting and stopping a real OpenHands
  delegation. The Hafiye-managed OpenHands V1 runtime and `coding_delegate`
  path now exist in source commit
  `dfb0d29c7ba80efadd5a517bac07aa949e517a5a`.
- A real Gemini-backed fixture delegation edited `bug.py`, returned its result
  and changed-file record, and the fixture test passed. A second live worker
  was stopped by the shared cancellation controller, returned
  `status=cancelled`, and was followed by an explicit successful resume with
  no active worker remaining.
- This issue no longer blocks P13 or P15. It does not authorize a substitute
  coding backend or a change to the master architecture. The real P15 Task
  Center progress bridge is accepted; durable generic task history remains
  explicitly scoped to P16.

## KI-029 — OpenHands runtime bootstrap is not yet exposed by Hafiye setup

- Status: RESOLVED 2026-08-24.
- `hafiye runtime openhands install` now performs a user-scoped official
  OpenHands source checkout at exact commit
  `6d38810359827823e62a5e1043d0d78d0bafb6de`, installs the exact
  `openhands-sdk`, `openhands-tools`, `openhands-workspace`, and
  `openhands-agent-server` `1.41.0` pins, and writes a manifest.
- `hafiye runtime openhands doctor` verifies the source, packages, managed
  Python, and manifest. On the actual host it returned `ready=true` with
  `blockers=[]`. A fresh runtime still reports actionable blockers until the
  install command runs; readiness is not fabricated.
- The remaining durable generic Task Center work belongs to P16 and is not a
  P15 blocker.

## KI-028 — Upstream generic `cua-driver` is absent on this host

- Status: MANAGED WARNING; not a Hafiye Linux computer-use blocker.
- A real direct upstream `tools.computer_use` smoke reported that the generic
  `cua-driver` executable is not installed. That path is separate from Hafiye's
  accepted managed `agent-sh/computer-use-linux` MCP provider, whose pinned
  source doctor, 18-tool discovery, and real GNOME Wayland E2E are green.
- Hafiye did not install an unrelated generic CUA binary or replace the
  prescribed Linux provider. Revisit this warning only if a later phase
  explicitly requires the upstream generic lane.

## P14 Desktop E2E isolation note

- Status: RESOLVED 2026-08-24; test-harness diagnostic, not a product blocker.
- On this Linux host, the normal Desktop launch prefers the real user-scoped
  `hafiye-gateway.service`, while project acceptance must use its temporary
  `HERMES_HOME`. The shared E2E fixture now sets
  `HAFIYE_DESKTOP_DISABLE_PERSISTENT_GATEWAY=1` so the isolated gateway owns
  the test state. The local Electron binary is resolved from the Desktop
  package when it is not installed at the repository root.
- The final real Electron P14 run passed 1/1 with no product error banner; the
  host persistent service remained outside the sandbox and was not changed.

## KI-030 — Task Center durable state and restart behavior

- Status: RESOLVED 2026-08-24; no P16 acceptance blocker.
- Task Center uses user-scoped SQLite WAL at
  `~/.local/state/hafiye/task_center.db`.
- Completed and failed history survives the gateway process boundary; active
  in-flight worker states are explicitly failed on restart; `QUEUED` work
  remains queued.
- Real separate-process RPC smoke and real Electron plus gateway E2E pass.
  No secrets, transcript, or private chain-of-thought are stored or shown.

## KI-031 — Privacy Mode initially rendered as a free-form field in Control Center

- Status: RESOLVED 2026-08-24; no P17 acceptance blocker.
- The backend schema describes `hafiye.privacy_mode` as a string. Before the
  P17 Desktop enum mapping, the shared config renderer therefore exposed a
  free-form input instead of the fixed roadmap modes.
- Desktop now supplies the real `NORMAL`, `LOCAL_ONLY`, and `OFFLINE` options
  through the existing config renderer. A real Electron test selected
  `LOCAL_ONLY` and verified the value after a renderer reload from the gateway.

## KI-032 — P18 scheduler policy validation

- Status: RESOLVED 2026-08-24; no P18 acceptance blocker.
- Hermes cron storage, recurring scheduler execution, skills/toolset
  discovery, and MCP safety merging remain the implementation boundaries.
  Hafiye route and privacy fields are validated at persistence time and are
  carried into the real scheduled agent; privacy overrides cannot weaken the
  configured policy.
- The real Desktop/gateway acceptance persisted Coding, Local only, and a
  custom enabled-toolset allowlist through an edit round-trip. The real local
  recurring-task acceptance completed two scheduler ticks and produced two
  execution-ledger records. No new or different upstream regression was
  observed. The two async resource warnings in the cron matrix are existing
  scheduler/test-harness diagnostics, not Hafiye failures.

## KI-033 — P19 hardening validation

- Status: RESOLVED 2026-08-24; no P19 acceptance blocker.
- Hermes' existing prompt-injection boundary, forced secret redaction,
  provider outage classifier/backoff policy, exact-call loop detector,
  checkpoint rollback, and corrupt-config backup/recovery remain the source of
  truth. Hafiye adds bounded managed-runtime recovery, action-budget admission,
  computer-use failure codes, and retention/doctor composition around them.
- Focused hardening tests passed: 111 tests in the P19 matrix and 104 adjacent
  browser/voice/config/audit tests. Ruff and patch hygiene passed.
- Real `.venv/bin/hafiye hardening doctor`, `runtime doctor`, `voice doctor`,
  `runtime server recover --attempts 1`, and the pinned computer-use-linux
  readiness check passed. The four required computer-use readiness fields are
  true and blockers is empty.
- No host service, package, credential, sudo rule, group, device permission,
  or root execution model changed during P19.

## KI-034 — P19 canonical full-suite scheduling/environment diagnostics

- Status: DIAGNOSTIC; not a P19 acceptance blocker.
- `./scripts/run_tests.sh` completed 3,231 files with 37,218 passed, 16
  failed, and 244 skipped in 847.8 seconds. The exact five comparison command
  separately returned 3 failed/2 passed, with only historical IDs 2, 3, and 5
  failing; IDs 1 and 4 passed.
- Twelve of the sixteen selected full-suite failures reproduce in a clean
  detached P18 baseline worktree (`139f5aadf`), including the existing Hermes
  state/execution/doctor failures, venv-footgun guards, TUI toolset assertions,
  and delegate/run-agent diagnostics. They are not introduced by P19.
- The four additional observations are parallel/host-state diagnostics:
  browser stale-socket detach and Termux inconclusive-audio passed in isolated
  reruns; the two Windows cold-start assertions are suppressed by the active
  Desktop lifecycle ledger on this host. No P19 code path owns those tests.
- This item must not be added to the historical five-ID regression whitelist.

## KI-035 — P20 package install validation scope

- Status: DIAGNOSTIC; no P20 acceptance blocker.
- The final `.deb` was built, the extracted package doctor returned `ok=true`
  with `blockers=[]`, and rootless fakeroot dpkg unpack/configure passed in a
  temporary package root. The temporary dpkg database reports expected unmet
  host-package dependencies because it contains no live host package database.
- A privileged live-host install was not run because it would mutate `/usr`
  and require interactive sudo. No success is claimed for that live mutation.
- The optional `cargo` check remains a diagnostic warning only. The exact
  accepted upstream baseline is unchanged: historical IDs 2, 3, and 5 fail;
  IDs 1 and 4 pass; no new/different regression was found.

## KI-036 — P21 full packaged onboarding replay

- Status: RESOLVED 2026-08-25; no P21 acceptance blocker and not an upstream
  or Hafiye regression.
- The P21 onboarding boundary, focused backend/UI tests, current package
  doctor, live authenticated onboarding doctor, and a real Electron partial
  flow all pass. The live doctor reports computer-use readiness, local model
  server readiness, voice readiness, and user autostart with no blockers.
- The real `release/linux-unpacked/hafiye-desktop` binary replayed the complete
  20-step sequence against the live authenticated gateway and returned
  `PACKAGED_ONBOARDING_RESULT PASS 20/20`. The final live doctor returned
  `ok=true` with an empty blocker array.
- Existing P11/P12 real microphone, Turkish STT, Piper, and wake-word evidence
  was supplemented by the wizard-level replay. The temporary acceptance gate
  was removed afterward and the normal service/CUDA local server were restored.

## KI-037 — P23 live Gemini route hit provider quota

- Status: LIVE PROVIDER WARNING; P23.2/P23.6 final acceptance remains open.
- On 2026-08-25 the default route was temporarily forced to
  `gemini-flash-lite-latest` through the real Hafiye route configuration. The
  packaged Electron Composer accepted `Firefox'u aç.`, the transcript reported
  `Firefox tarayıcısı açıldı.`, and a real Firefox window was observed.
- A later Gemini request in the same turn returned HTTP 429
  `RESOURCE_EXHAUSTED` for the provider's free-tier quota. This confirms the
  Desktop route/config boundary is active, but the turn is not a clean final
  P23 result. The earlier P22 explicit Gemini one-shot remains valid evidence;
  no API key is stored in this repository or in this issue record.
- The default route was restored to local `custom`/Qwen and the user gateway
  was restarted and verified active/enabled. Re-run the clean Composer/Gemini
  acceptance when provider quota is available; do not change the architecture
  or treat the quota error as a Hafiye routing regression.

## KI-038 — Doctor reports intentional Secret Service/.env and workspace audit diagnostics

- Status: DIAGNOSTIC; not a P23 blocker.
- The live `.venv/bin/hafiye doctor` reports a missing
  `~/.local/share/hafiye/.env`. Provider credentials for this installation are
  intentionally stored in Linux Secret Service, so creating a plaintext `.env`
  is not the normal product fix. The diagnostic should be made more aware of
  the Secret Service-backed provider path in a later hardening pass.
- The same doctor run reports the workspace audit counts recorded in KI-007:
  4 findings in `web` and 3 findings in `ui-tui`. No dependency rewrite or
  `npm audit fix` was run during P23.

## KI-039 — Separate root-owned ydotoold process in the host user-manager namespace

- Status: HOST DIAGNOSTIC; current Hafiye computer-use readiness remains green.
- The 2026-08-25 live probe showed the managed user daemon
  `/usr/bin/ydotoold` as PID `13797` with socket
  `/run/user/1000/.ydotool_socket`, plus a separate root-owned `/usr/bin/ydotoold`
  as PID `3195645` under a root `systemd --user` manager with socket
  `/run/user/0/.ydotool_socket`.
- The two processes use different sockets; the required user readiness doctor
  returned all four booleans true and `blockers=[]`. No attempt was made to
  stop or alter the root user-manager process because it may belong to another
  host service and would require privileged operator coordination.

## KI-040 — No compatible 64K local agent GGUF currently fits this host test path

- Status: P23 LOCAL-INFERENCE BLOCKER; no Hafiye source regression.
- The existing Qwen fixture is healthy on CUDA and the direct local endpoint
  returned `P23_LOCAL_ENDPOINT_OK`, but its runtime/trained context is below
  Hermes' 64K agent minimum (KI-014).
- A pinned `NousResearch/Hermes-3-Llama-3.2-3B-GGUF` Q4_K_M download was
  attempted at revision `3cd927095d8cbab12c743f932aa63b6f7bbfa141`. With
  AUTO/CUDA and 65,536 context, llama.cpp failed the CUDA KV-cache allocation
  (`7168 MiB`) on the RTX 3080. The test model was removed from the registry.
- A pinned `bartowski/Llama-3.2-1B-Instruct-GGUF` Q4_K_M download was also
  tested. It fit at 65,536 context and reported `n_ctx_train=131072`, but a
  real `hafiye ask` generated unbounded output (39,822 generated tokens before
  interruption) instead of completing the marker request. It was removed from
  the registry as unsuitable for the agent runtime.
- The registry and live runtime were restored to the original Gemma/Qwen
  models with Qwen active at 4,096 context and CUDA selected. A compatible
  production GGUF must be evaluated before P23 local-agent acceptance can pass;
  the architecture and backend policy are unchanged.
