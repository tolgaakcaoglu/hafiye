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
- The latest direct exact-node replay on 2026-08-25 after KI-043 source
  hardening returned `3 failed, 2 passed`: historical IDs 2, 3, and 5 failed;
  IDs 1 and 4 passed. This is a reduced observed subset inside the same
  accepted five-ID whitelist, not a new/different regression. A separate
  targeted `run_tests.sh` invocation also passed all 35 relevant tests.

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

## KI-013 — Electron autostart crashed on an incorrectly installed Linux sandbox helper

- Status: RESOLVED after the source packaging fix and second real reboot/login
  acceptance on 2026-08-25.
- On 2026-08-25 the requested real reboot/login was performed. The new boot
  ID was `17a11ea7-41ed-4b74-a4fc-8f4e9c3dc7eb`; the gateway started
  automatically at `06:14:19 +03` and its endpoint and supporting doctors
  were healthy.
- The user journal showed that GNOME did execute the valid entry as
  `app-gnome-hafiye-10171.scope`, but Electron aborted before tray creation:
  `The SUID sandbox helper binary was found, but is not configured correctly`;
  the helper was `tolga:tolga` with mode `0755` instead of `root:root 4755`.
- The current helper was verified as a regular file and repaired through the
  existing `hafiye-rootd` boundary. A sandbox-enabled short launch then ran
  without the fatal sandbox error. The Debian package builder now applies and
  tests mode `4755` in source/test commit
  `a1271a93277e6ac0747c1c5c31b586c2e883e55a` (`4 passed`).
- The second real boot ID was
  `db40c0c5-f5b3-4dcf-8d01-7cf425e15323`. GNOME launched the packaged
  Desktop from the real autostart entry; gateway health, tray/StatusNotifier,
  Composer observation, voice doctor, and computer-use doctor all passed.
  The helper was `root:root 4755`, and the new-boot journal contained no SUID
  sandbox fatal error. No manual Desktop startup was used.

## KI-014 — Small validation GGUFs have a lower trained context window

- Status: MEASURED COMPATIBILITY WARNING; the current Qwen2 path is usable for
  the P23 local-agent smoke test, but its native training metadata remains 32K.
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
- The initial P23 recovery attempt loaded the same GGUF with
  `--context-size 65536`; without a family-specific compatibility override,
  llama.cpp capped the slot at the model's trained 32,768-token limit and the
  real `hafiye ask` rejected it against Hermes' 64K minimum.
- Hafiye now applies an explicit, narrowly scoped Qwen2 compatibility path for
  requested contexts above 32K: YaRN scaling from the 32K origin plus an
  explicit `qwen2.context_length` metadata override. The managed runtime was
  loaded with `--context-size 65536`, reported `n_ctx=65536` and
  `n_ctx_train=65536`, and a real AIAgent terminal call plus packaged Desktop
  Composer terminal call both returned exact markers. This does not silently
  extrapolate other model families; they retain native metadata behavior.
- The trained-context caveat remains relevant for production model selection
  and for quality/long-context validation. It is no longer the current
  host-local agent blocker; offline and full P23 replay evidence remain tracked
  in `STATE.md` and `TEST_MATRIX.md`.
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

- Status: RESOLVED 2026-08-25 by credential rotation; the prior quota failure
  is no longer the active Gemini blocker. P23.6 now has a clean packaged file
  task pass; the exact Firefox P23.2 replay remains separately tracked under
  KI-049.
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
  was restarted and verified active/enabled. The old quota error is retained as
  historical evidence; it was not a Hafiye routing regression and is no longer
  the active provider blocker after credential rotation.
- A newly supplied Gemini credential was stored in Linux Secret Service (the
  raw value is not recorded here). A real explicit Gemini one-shot returned
  `P23_GEMINI_NEW_KEY_OK`; the packaged Composer also reached a real Firefox
  open result. The remaining clean acceptance issue is recorded separately.
- Separately, the real P23.7 fail-closed check temporarily selected this Gemini
  route, set global `LOCAL_ONLY`, and ran `hafiye ask` without explicit model
  overrides. The request exited 1 with `Hafiye LOCAL_ONLY policy blocked
  provider 'gemini'` before any provider call; route/privacy were restored to
  local custom/Qwen and `NORMAL` afterward.

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

## KI-040 — Pinned 64K candidate probes failed before Qwen2 compatibility path

- Status: RESOLVED FOR CURRENT QWEN2 PATH; historical diagnostic, no Hafiye
  source regression.
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
- The registry was cleaned back to the Gemma/Qwen entries. The managed Qwen2
  runtime is now active at 65,536 context with CUDA selected using the explicit
  compatibility flags documented in KI-014. A real local AIAgent tool call and
  a real packaged Desktop DOM inspection succeeded; the remaining P23 local
  acceptance work is offline/full-sequence replay, not a missing compatible
  candidate. The architecture and backend policy are unchanged.

## KI-041 — Qwen2 validation fixture did not complete multi-step file E2E

- Status: RESOLVED for the P23.8 acceptance fixture through the authenticated
  Gemini route; the local Qwen2 multi-step tool-calling limitation remains a
  validation warning. No Hafiye source regression is established.
- On 2026-08-25 an isolated temporary fixture was presented to a real
  AIAgent using the managed CUDA/Qwen2 endpoint with `terminal` and `file`
  toolsets. One attempt executed only the directory-creation portion and
  stopped; a second attempt returned the requested marker without invoking a
  tool. At that point the fixture's `notes.txt` and `photo.jpg` remained in
  `incoming/`, so the master 23.8 organize-and-verify acceptance was not yet
  passed by the local-Qwen replay.
- The same managed runtime and packaged Desktop already passed a real single
  terminal command, so the first result is limited to multi-step local fixture
  behavior. A follow-up isolated fixture replay through
  `.venv/bin/hafiye ask --provider gemini --model gemini-flash-lite-latest
  --toolsets terminal,file ...` performed and verified all required operations:
  `organized/text/notes.txt` and `organized/media/photo.jpg` existed, while
  `incoming/keep.bin` remained in place. The exact marker was returned only
  after verification. This closes the roadmap's 23.8 fixture acceptance while
  retaining the local-Qwen warning for future model-specific validation.

## KI-042 — Qwen2 validation fixture did not complete a natural-language desktop task

- Status: P23 VALIDATION WARNING; no Hafiye source regression established.
- On 2026-08-25 the real packaged Desktop was launched against the managed
  local Qwen2 route and given the exact P23 text request `Firefox'u aç.`. The
  Composer became ready, but the model returned a wrong natural-language reply
  (`Merhaba, FireFox'a açın!`) without a computer-use tool call; no new Firefox
  window or successful task transcript was observed. The 30-second replay was
  therefore not accepted as P23.2 text execution.
- The managed runtime's direct terminal tool call and packaged Desktop
  `/bin/printf` tool block remain valid narrow-path evidence. This issue covers
  the validation fixture's reliability for natural-language desktop/file
  tool-calling; the rotated-key Gemini replay is now separately tracked under
  KI-043 because of its unapproved sudo-remediation attempt.

## KI-043 — Privileged command boundary

- Status: RESOLVED at source level on 2026-08-25. The clean Gemini file-task
  Composer acceptance passes without privilege escalation; the separate exact
  Firefox replay's unrelated root remediation is tracked under KI-049.
- The historical trigger was the rotated-key Gemini Composer task with the
  exact prompt `Firefox'u aç.`. After opening Firefox, the model attempted
  `sudo chown root:root /usr/libexec/snapd/snap-confine`; no password was
  supplied and the route was restored to local custom/Qwen.
- The shared Hafiye terminal boundary now tokenizes and detects direct,
  absolute, `env`/`command`-wrapped, quoted, shell `-c`, and chained forms of
  `sudo`, `sudoedit`, `su`, `pkexec`, `doas`, and `runuser`. It never sends
  these through the ordinary terminal/process executor.
- `FULL_AUTONOMOUS` routes the operation through `hafiye-rootd`; an unavailable
  broker fails closed without an OS password prompt. `READ_ONLY` blocks it,
  and `PRIVILEGED_CONFIRM`/`WRITE_CONFIRM` require the existing approval
  surface before the broker call. Direct Python subprocess/os escalation in
  `execute_code` is also fail-closed.
- Regression coverage includes the Gemini command shape, normal harmless
  terminal commands, all required escalation forms, root-broker audit output,
  FULL_AUTONOMOUS routing, READ_ONLY, confirmation, and model-registry state.
  The targeted matrix returned `35 passed, 0 failed`.
- The post-fix exact Gemini Firefox replay produced no administrator-password
  dialog. Its privileged package command was executed only by `hafiye-rootd`,
  as required by `FULL_AUTONOMOUS`; this confirms the boundary semantics even
  though the overall Composer task was not clean.

## KI-044 — Gemini natural-language desktop prompt selected file tools

- Status: P23 VALIDATION WARNING; direct managed desktop acceptance passes and
  no Hafiye source regression is established.
- In an isolated local-gateway packaged Desktop replay on 2026-08-25, the
  authenticated Gemini route received a VS Code/window/keyboard/mouse task and
  returned the requested marker after reporting `Explored 2 files`; no VS Code
  window was opened. The prompt was not accepted as P23.9 model behavior.
- The required P23.9 real-machine behavior was then exercised directly through
  Hafiye's managed `computer-use-linux` MCP tools: two real VS Code windows
  were opened, exact window focus was switched first→second→first, a mouse
  click and keyboard select/type/save were sent through the managed backend,
  the saved fixture contained `P23_DESKTOP_TARGET`, and the final screenshot
  showed the marker in VS Code. This warning remains model/tool-selection
  specific and does not block the direct P23.9 acceptance evidence.

## KI-045 — Gemini desktop fixture selected terminal for the emergency-stop replay

- Status: P23 VALIDATION WARNING; the emergency state transition itself passed,
  but the exact P23.15 desktop-task acceptance was not established.
- In a real authenticated `source=desktop` gateway session on 2026-08-25, a
  prompt requiring a managed desktop wait action produced a `terminal` tool
  start instead. While that turn was active, the physical `Ctrl+Super+Escape`
  chord reached the GNOME fallback, the session reported
  `paused_after_task=true`, and `emergency.resume` restored operation. Because
  no long-running managed desktop action was selected, this run does not claim
  that the required desktop action sequence was stopped by the shortcut. No
  Hafiye source regression is established; direct managed P23.9 acceptance
  remains green.
- A follow-up real local-Qwen command using
  `.venv/bin/hafiye ask --provider custom --model
  qwen2.5-0.5b-instruct-q4 --toolsets computer_use` with an explicit 60-second
  `computer_use` wait request exited without producing a `computer_use` tool
  event. No emergency chord was sent in that probe, and no P23.15 acceptance
  is claimed.

## KI-046 — Qwen3-14B resource envelope warning

- Status: P23 MODEL QUALIFICATION WARNING; the isolated Qwen3 local-agent
  acceptance objective passed, no Hafiye source regression is established, and
  the normal Qwen2 route remains healthy after restoration.
- The official `Qwen/Qwen3-14B-GGUF` Q4_K_M file was registered from revision
  `530227a7d994db8eca5ab5ced2fb692b614357fd` as
  `/home/tolga/.local/share/hafiye/models/qwen3-14b-q4_k_m.gguf`,
  9,001,752,960 bytes, SHA-256
  `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`.
- The managed runtime uses Qwen3's embedded Jinja template and DeepSeek
  reasoning parser. For 65K it uses YaRN from the 40,960 native context,
  `qwen3.context_length` metadata override, fit-aware CUDA layer selection,
  and CPU KV storage. Full-GPU 65K and 4K probes hit CUDA OOM; the managed
  compatibility path itself reached 65,536 context and selected CUDA.
- The direct parser smoke and the six isolated real Hafiye AIAgent workflows
  passed: exact `Firefox'u aç.` managed activation, file create/read/move,
  real VS Code managed keyboard/input and screenshot, multi-step terminal
  verification, OpenHands `coding_delegate` (`custom/qwen3-14b-q4_k_m`, worker
  `completed`, 14 progress events, independent pytest `1 passed`), and a
  same-session multi-turn terminal workflow. Measured task wall times were
  51.303s, 73.703s, 48.849s, 58.319s, 423.879s, and 71.845s respectively.
- The 65K Qwen3 sample used 8,614 MiB of 10,240 MiB VRAM; the server reported
  `VmRSS=7,749,188 kB` and `VmSwap=7,609,128 kB`, while the host showed
  11 GiB/14 GiB RAM in use. Earlier loading reached approximately 11.3 GiB
  RSS. llama-server logs showed cache-dependent prompt processing of roughly
  228–827 tokens/s and generation of roughly 4.59–5.39 tokens/s.
- Full-GPU Qwen3 65K and 4K fit probes hit CUDA OOM. The managed compatibility
  path uses fit-aware `-ngl auto` and `--no-kv-offload`, reaches the Hafiye
  65,536 context contract, and passes the six functional workflows. Because
  of the measured swap/resource pressure, Qwen3 remains registered and
  selectable but is not the default route. This warning does not reopen the
  fixed compute-backend architecture or block the completed Qwen3 acceptance
  objective; the independent deferred P23 checklist remains at the roadmap
  end.
- The local GGUF registry records Qwen3 as `agent=true`, `tool_calling=true`,
  `validation=false`, and `resource_warning=KI-046`. The Qwen2.5-0.5B smoke
  fixture is recorded separately as `validation=true`, `agent=false`; these
  are registry capability states, not model-name UI hacks or route changes.

## KI-047 — Qwen3 packaged Composer replay did not emit a tool call

- Status: P23 VALIDATION WARNING; the managed-MCP startup defect is resolved in
  source, Qwen3's six-workflow local-agent qualification remains complete, and
  no new boundary regression is established.
- After the real reboot exposed that the in-memory
  `hafiye-computer-use-linux` provider did not open the shared MCP discovery
  gate, source/test commit `dc962963e` fixed `_has_configured_mcp_servers()`.
  The restarted gateway then logged registration of all 18 managed
  computer-use tools.
- A fresh real packaged Electron Composer replay used the exact prompt
  `Firefox'u aç.` with the agent-qualified Qwen3 route. The session exposed 38
  core/visible tools and 18 deferred managed MCP tools, but Qwen3 remained in
  reasoning for approximately 265 seconds without an emitted tool call. The
  replay was terminated to avoid further host pressure; no Firefox acceptance
  result is claimed. The normal Qwen2 route was restored afterward.
- This warning does not reopen KI-043, change the local-first architecture, or
  invalidate Qwen3 qualification. KI-046 remains the separate measured
  resource warning. P23.2 stays NOT ACCEPTED until a fresh agent-qualified
  Composer replay produces the real computer-use call and Firefox verification.

## KI-048 — P23.5 self-hosted remote endpoint is not configured

- Status: P23 OPERATIONAL BLOCKER; no Hafiye source defect is established.
- The live route state has an empty `remote` task override. The active
  `/home/tolga/.config/hafiye/config.yaml` exposes only the local
  `http://127.0.0.1:11435/v1` OpenAI-compatible endpoint, and onboarding
  records `remote_provider_skipped=true`. No real remote self-hosted endpoint
  was available for the required forced-route replay.
- P23.5 remains NOT ACCEPTED. A localhost fixture or the Gemini cloud provider
  is not counted as the required remote self-hosted evidence.

## KI-049 — Gemini exact Firefox Composer triggered unrelated package remediation

- Status: P23 VALIDATION WARNING; KI-043 remains RESOLVED and no password
  dialog was shown.
- In the fresh real packaged Composer replay with the exact `Firefox'u aç.`
  prompt, Gemini opened Firefox but then attempted a remediation chain through
  the normal privileged boundary: `sudo apt install -y firefox`, apt source/
  preference changes, and later Firefox package operations. The Hafiye root
  broker executed the privileged work as designed; it did not expose an OS
  password prompt. This was unrelated to the requested task, so the replay is
  not clean P23.2 acceptance.
- Emergency stop was engaged while the root broker operation was active. The
  operation ended; the prior Firefox Snap revision `8763` was restored through
  rootd, the temporary Debian Firefox package was removed, and the
  `mozillateam` source/preferences created by the remediation were removed.
  The host route was restored to custom/Qwen2 and the package state was
  rechecked. This issue is model/task-selection behavior, not a reason to
  weaken `FULL_AUTONOMOUS` or bypass `hafiye-rootd`.

## KI-050 — Ollama-native model stores are outside Hafiye's managed runtime

- Status: DOCUMENTED ARCHITECTURE CONSTRAINT; not a blocker.
- Hafiye's built-in local runtime is the managed llama.cpp server and its
  private GGUF registry. The Desktop Models page now provides the supported
  GUI download path for a single `.gguf` file from Hugging Face, plus Import
  GGUF for a compatible file already on disk.
- Ollama manifests and blob-store layouts are not accepted as direct Hafiye
  model-registry inputs. If an Ollama model is also published as a single-file
  GGUF, download that GGUF through Hafiye; otherwise provide a compatible
  GGUF produced outside Hafiye before using Import GGUF.
- This records the existing fixed runtime boundary; it does not add an Ollama
  runtime, create a new phase, or change the local-first architecture.

## KI-051 — Ubuntu system Python 3.14 blocked the Debian package bootstrap

- Status: RESOLVED 2026-08-26 in source/test commit
  `fd435cc85fe018ca238256fb19547db2e7064565`.
- The real host now exposes `/usr/bin/python3` as Python `3.14.4`. The original
  Debian control file required both `python3 (>= 3.11)` and
  `python3 (<< 3.14)`, so a real `apt install --simulate` of the Hafiye `.deb`
  failed before the user-scoped dependency installer could create the
  supported managed environment. Earlier P20/P21 rootless package checks did
  not use the live host apt database and therefore did not expose this conflict.
- The package now allows the distro Python 3.14 interpreter to serve only as
  the stdlib bootstrap. `hafiye package install` still enforces the actual
  Hafiye runtime range `>=3.11,<3.14` and provisions managed Python 3.11 with
  `uv` when the distro interpreter is too new. Existing supported 3.11–3.13
  interpreters remain preferred.
- The committed packaging/metadata suite returned 13 passed; Ruff, bytecode
  compilation, and patch hygiene passed. A rebuilt real artifact records the
  new source HEAD, resolves successfully through current-host
  `apt install --reinstall --simulate`, preserves `chrome-sandbox` mode 4755,
  and returns extracted package doctor `ok=true`, `blockers=[]` under managed
  Python 3.11. The post-fix exact upstream comparison remained 3 failed/2
  passed with only accepted historical IDs 2, 3, and 5.
- No live package install or sudo mutation was performed. This is resolved at
  the package dependency/bootstrap boundary and does not change P23's open
  final real-machine acceptance rows.

## KI-052 — Turkish locale retains English fallback on advanced surfaces

- Status: NON-BLOCKING LOCALIZATION COVERAGE WARNING.
- Source commit `3c2ea9a7a9c119475aa0cee471b6cf982677d8a6` adds a real,
  persisted `Türkçe` locale and translates the primary Desktop interaction
  surfaces. The existing `defineLocale` contract intentionally falls back to
  English for untranslated keys, so less-used advanced upstream screens may
  still contain English copy.
- The final package source is `684227f6ebbfeed2bc9ea2e08e6723e54edef073`;
  Electron is consistently pinned to `40.10.6`, and the rebuilt `.deb` was
  installed and restarted successfully. This does not change the remaining
  translation-coverage warning.
- Locale aliases, persistence, runtime resolution, full Desktop UI tests,
  typecheck, changed-file lint, and a clean production build all pass. This is
  a translation-completeness warning, not a broken language selector or a P23
  blocker.

## KI-053 — Settings and new-chat model identity drift

- Status: RESOLVED 2026-08-26 in source/test commit
  `197e4ca8fe864faaf48dd695cc25d7c89e2c6e33`.
- Before the fix, New Chat retained the prior Composer's manual Qwen selection
  even when Settings selected Gemini. The gateway then allowed the configured
  Hafiye default route to replace an explicit Desktop session model without
  consistently replacing the runtime endpoint. Real logs captured Qwen being
  requested from the Gemini endpoint and returning HTTP 404.
- New Chat now clears the old manual selection, marks the fresh draft as
  default-derived, and reads the target profile's Settings model immediately
  before `session.create`. A deliberate Composer picker choice is still frozen
  as a manual per-session override. The backend preserves explicit Desktop
  provider/model precedence while retaining privacy/locality enforcement.
- Targeted Desktop tests returned 171 passed, full Desktop tests returned 7,175
  passed with 3 skipped, backend route tests returned 17 passed, typecheck/lint/
  Ruff passed, and the exact upstream comparison remained 3 failed/2 passed
  with only accepted IDs 2, 3, and 5. The rebuilt package is installed and its
  live model API reports the Settings value
  `gemini/gemini-3.1-pro-preview`.
