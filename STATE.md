# Hafiye State

Last updated: 2026-08-25

## Repository and commit state

- Branch: hafiye/p0
- origin: https://github.com/tolgaakcaoglu/hafiye.git
- upstream: https://github.com/NousResearch/hermes-agent.git
- Pinned upstream commit: f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit: 2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye source HEAD: ac42575db2986a2f8be677a9d1272121ff533294
  (Qwen3 candidate compatibility and managed-MCP explicit-toolset source/test
  commit)

The three SHA values above are intentionally separate: the first is the
upstream source pin, the second is the history-preserving baseline merge, and
the third is the current Hafiye product source commit. Documentation closure
commits after the source commit do not change the product source pin.

## Current phase

P0 — Fork, pin, verify environment: complete.

P1 — Hafiye external identity and data root: complete.

P2 — Persistent gateway + Desktop connection: complete.

P3 — Hafiye Composer + tray + autostart: complete with host warnings KI-012
and KI-013.

P4 — llama.cpp managed local runtime: complete. The source implementation,
real CUDA runtime validation, corrected full backend regression comparison, and
documentation closure are complete.

P5 — Providers + Gemini + remote OpenAI-compatible: complete. Local llama.cpp,
remote OpenAI-compatible validation/save, Hermes Gemini provider reuse,
Desktop provider/key UI, Secret Service storage, and the live Gemini
connection are verified.

P6 — Model router + privacy modes: complete.

P7 — Full host tools + execution policy: complete.

P8 — Hafiye root broker: complete.

P9 — Linux computer use: complete.

P10 — Browser: complete.

P11 — Local Turkish voice stack: complete. Managed whisper.cpp/Piper, the
Hafiye transcription hook, Desktop voice settings, real Piper playback, and
real Turkish microphone transcription are accepted.

P12 — Custom Hafiye wake word: complete. The bundled Turkish openWakeWord
model, persisted tuning controls, local/client capture path, synthetic and
real-room validation, and minimized-window Desktop activation are accepted.

P13 — Barge-in + emergency stop: complete. The real OpenHands delegation
start/stop/resume acceptance now passes; KI-027 is resolved.

P14 — Memory + project registry: complete. The pinned Hermes project registry,
session-search path, gateway project RPCs, and Desktop project browser were
validated against the P14 acceptance criteria.

P15 — OpenHands coding delegate: complete. The managed official source/runtime,
real coding delegation, gateway Task Center progress bridge, Desktop Task
Center panel, and the master fixture E2E all pass. P16, P17, P18, P19, and P20
are complete; P21 and P22 are also complete, and P23 is now the first
incomplete phase.

P16 — Task Center: complete. The durable generic task record, restart/reconnect
behavior, complete required Desktop fields/actions, and real Electron
acceptance pass.

P17 — Control Center: complete. The real 19-page Hafiye surface, shared
config/backend boundaries, privacy selector, and Electron acceptance pass.

P18 — Scheduler / skills / MCP: complete. Hermes cron/skills/MCP were reused;
scheduled route, privacy, and enabled-toolset choices persist through the
gateway and the real recurring local-task acceptance passes.

P19 — Hardening: complete. Prompt-injection and redaction boundaries, provider
outage policy, bounded llama/voice recovery, computer-use failure contracts,
loop/action budgets, checkpoint/config recovery, audit retention, and disk
limits are implemented and verified.

P20 — Packaging: complete. The real Linux Electron build is wrapped in a
Debian package containing the Hafiye backend, launchers, user gateway unit,
root-broker activation path, XDG entries, icons, notices, and dependency
doctor/installer. Rootless dpkg unpack/configure and the extracted package
doctor pass.

P21 — First-run onboarding: complete. The implementation, backend boundary,
packaged runtime validation, and complete 20-step real packaged Electron GUI
replay are accepted.

P22 — CLI: complete. The product command vocabulary, shared backend adapters,
real service/model/computer checks, explicit Gemini one-shot, and accepted
upstream-baseline comparison are recorded below. P23 — Final E2E Suite — is
now the first incomplete phase. On 2026-08-25 the user explicitly instructed
that the remaining real-machine acceptance checks be deferred and reminded at
the end of the roadmap. They remain unaccepted and must not be represented as
passed.

## Verified working

- Git history, remotes, upstream pin, and baseline merge are preserved.
- Normal Hafiye CLI invocation is available as .venv/bin/hafiye.
- Normal POSIX roots resolve to:
  - ~/.config/hafiye
  - ~/.local/share/hafiye
  - ~/.local/state/hafiye
  - ~/.cache/hafiye
- Explicit HERMES_HOME and context/profile overrides retain upstream
  single-root behavior for compatibility.
- The one-time, non-destructive legacy-home migration command is implemented
  and tested.
- Desktop user-facing title, menus, Quick Entry, onboarding, notifications,
  update/bootstrap messages, app identifiers, and docs use Hafiye. Upstream
  IPC keys, Python module names, compatibility environment names, and legal
  attribution remain unchanged.
- Neutral H monogram assets are installed for Desktop.
- Desktop normal data and state roots follow the same XDG policy as Python.
- The pinned computer-use-linux source doctor remains accepted from P0:
  all four required readiness booleans are true and blockers is empty.
- The real user-scoped `hafiye-gateway.service` is enabled and active on
  `127.0.0.1:9120`; its owner-only token and descriptor are under
  `~/.local/state/hafiye/gateway/`.
- The P22 product CLI is available through `.venv/bin/hafiye`: `ask`, service
  lifecycle (`start|stop|restart`), GGUF model listing/load/unload, provider
  listing, routing/privacy, Task Center, and computer-use doctor all use the
  existing Hafiye runtime/configuration boundaries.
- Native gateway and Electron/TUI Desktop agent creation now read the normal
  Hafiye XDG config root and apply the same route-slot/privacy policy before
  constructing `AIAgent`. The change is covered by native-gateway and
  Desktop-agent tests. A real packaged Composer run with the default route
  temporarily forced to Gemini executed the Firefox operation; the turn then
  received a Gemini free-tier HTTP 429 and remains a P23 warning, not a clean
  final acceptance.
- A real `hafiye restart` left `hafiye-gateway.service` active and enabled; a
  real model unload/load cycle restored the Qwen GGUF server with
  `selected_backend=CUDA` and `ready=true`.
- A real explicit `hafiye ask --safe-mode --provider gemini
  --model gemini-flash-lite-latest ...` returned the marker
  `P22_GEMINI_CLI_OK`. The local small-Qwen one-shot remains limited by KI-014
  because that fixture reports a 4,096-token runtime context below Hermes'
  64K minimum agent context.
- Desktop boot authenticated to the persistent backend, and closing the real
  Electron process left the service active with `NRestarts=0` and the endpoint
  reachable.
- An authenticated Desktop gateway restart request restarted the service and
  returned after the new backend PID was reachable.
- Hafiye Composer now owns the Desktop Quick Entry lifecycle with
  `HOTKEY_ONLY`, `SHOW_ON_LOGIN`, and `PINNED` modes; the mandated default is
  `Super+Shift+Space` and the setting remains configurable.
- The real Desktop creates a Hafiye tray and keeps running after the main
  window is closed with Alt+F4; the persistent gateway stayed active.
- The real XDG entry at `~/.config/autostart/hafiye.desktop` contains the
  development-safe Electron executable, app path, and `--hidden` flag. The
  exact entry command was launched successfully in the Wayland session.
- The tray's later-phase controls are visibly disabled and labeled; there are
  no fake privacy, microphone-mute, or computer-control toggles.
- The managed llama.cpp source checkout is installed under the Hafiye data
  root at source commit `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`.
- The managed runtime manifest records CPU and CUDA builds, with AUTO selecting
  CUDA on the real RTX 3080 host. The current llama-server is healthy on
  loopback `127.0.0.1:11435` and reports the CUDA device.
- Two real GGUF models are registered under the Hafiye model root. The server
  was started, health-checked, unloaded, restarted with the second model, and
  queried through the OpenAI-compatible chat endpoint.
- Hermes one-shot connected to the real local llama-server endpoint and
  returned a non-empty response. The Desktop model settings expose the same
  runtime lifecycle through the authenticated gateway API.
- Provider credentials for provider-owned variables are stored in the real
  Linux Secret Service; Hafiye config contains only profile-scoped keyring
  references and runtime hydration is explicit. Generic channel/tool secrets
  retain Hermes' `.env` compatibility path.
- A real local OpenAI-compatible HTTP server passed `/v1/models` validation and
  chat; the Hafiye custom-endpoint save/validate path stored no raw provider
  secret in config and returned a real `P5_REMOTE_OK` response.
- Automated Gemini provider registration, resolution, credential lifecycle,
  and Desktop surfaces pass. The active `gemini-flash-lite-latest` credential
  is stored in Linux Secret Service and the default XDG config contains only a
  keyring reference; no raw key is stored in the repository or config file.
  A real Gemini model-list request returned HTTP 200 with 50 models, and the
  real Hafiye one-shot returned `HAFIYE_GEMINI_LIVE_OK`.
- The provider lifecycle now binds Secret Service references to the active
  Hafiye config root under the normal XDG config/data split. This prevents a
  saved credential from being invisible to the next process and is covered by
  `test_default_xdg_provider_lifecycle_uses_config_root`.
- Hafiye route slots are configured under the shared `hafiye` config namespace;
  task-scoped natural-language overrides resolve before native gateway/API
  agent construction and do not mutate conversation history.
- `NORMAL`, `LOCAL_ONLY`, and `OFFLINE` are enforced by the shared policy at
  route resolution, AIAgent initialization, fallback filtering, tool-schema
  generation, and tool execution. OFFLINE retains local terminal/filesystem
  capability while removing network-capable tools.
- The native gateway, API server, one-shot CLI path, interactive CLI setup, and
  Desktop settings all use the same Hafiye route/privacy policy. The Desktop
  exposes the global privacy mode and route locality controls.
- Hafiye host execution policy defaults to `FULL_AUTONOMOUS` and supports
  `PRIVILEGED_CONFIRM`, `WRITE_CONFIRM`, and `READ_ONLY` through the shared
  config/API boundary.
- Hermes local terminal, process, and filesystem tools execute against the real
  non-root host by default. Confirmation policies reuse Hermes' existing
  approval surface; `READ_ONLY` blocks mutating operations.
- The Desktop Hafiye settings surface exposes the real
  `hafiye.execution_policy` select and persists it through the existing config
  API; it is not a mock-only control.
- Real dispatcher smoke passed for a host terminal command, a temporary-file
  read, and a background process start/wait cycle.
- `hafiye-rootd.service` is installed at `/usr/lib/systemd/system/`, enabled,
  and active as EUID 0. It listens only on `/run/hafiye/root.sock`, owned by
  `tolga` with mode `0600`; the main Hafiye gateway remains EUID 1000.
- The real non-root broker client completed `root.exec id -u` with broker UID
  `0`, performed a privileged temporary-file write, and received a strict
  `malformed_request` response for duplicate JSON keys.
- The real system socket rejected a `nobody` peer with `permission_denied`.
  Broker audit records contain peer identity, request lifecycle, duration, and
  redacted arguments; no raw acceptance command text was present.
- Hafiye automatically manages the pinned
  `agent-sh/computer-use-linux` source binary at
  `/home/tolga/.local/bin/computer-use-linux` as the reserved built-in MCP
  provider `hafiye-computer-use-linux`; no `mcp_servers` edit is required.
- A real Hermes MCP discovery registered 18 tools from the managed provider.
  The provider was exercised on the actual GNOME Wayland session: windows were
  enumerated, Calculator's AT-SPI tree was read, `12*7` was entered and the
  result `84` was read back, Firefox navigation and application switching were
  verified, and VS Code/Files windows were opened and queried.
- Desktop Settings includes a real `Settings → Computer` diagnostics page
  showing the managed binary, source pin, MCP provider, the four required
  readiness booleans, blockers, and a recheck action. Its component test and
  the full Desktop UI suite pass.
- The default local wake model is the bundled Turkish `Hafiye` ONNX asset at
  `tools/wakewords/hafiye.onnx`; the default threshold is `0.6` with three
  confirmation frames. Legacy Hermes model aliases resolve to the Hafiye
  asset for compatibility.
- The real client-capture path fed PCM from Electron's fake microphone into the
  persistent gateway; a normal-room music recording produced zero fires and a
  real Turkish Hafiye recording opened a fresh session. The same flow passed
  after the Hafiye window was actually minimized (`minimized=true`,
  `visible=false`).
- The per-profile Hermes project registry persists deterministic project names
  and slugs with repository paths in `projects.db`; a fresh Python backend
  process resolved `pocket-world` back to the exact saved path.
- The real `session_search` FTS5 path returned the seeded recent Pocket World
  context after that process boundary. The targeted project/memory matrix
  passed 127 tests.
- The real Electron Desktop project flow rendered project grouping, searched
  the project picker, renamed a project through `projects.update`, deleted it
  through the destructive confirmation, and preserved the repository folder.
  The acceptance used the live gateway and passed 1/1.
- The user-scoped OpenHands runtime is installed under
  `~/.local/share/hafiye/runtimes/openhands/`: official source commit
  `6d38810359827823e62a5e1043d0d78d0bafb6de`, all four managed packages pinned
  to `1.41.0`, and `hafiye runtime openhands doctor` reports `ready=true` with
  `blockers=[]`.
- A real natural-language Hafiye Gemini run identified a coding task, invoked
  `coding_delegate`, had OpenHands edit a failing fixture's `bug.py`, and
  returned the actual changed-file and `pytest -q` result (`1 passed`).
- The real gateway Task Center boundary exposed the worker as `RUNNING`, then
  `COMPLETED`, with 18 progress records and 22 `task.update` events. The
  Desktop Task Center panel consumes the same RPC/event contract and its
  focused UI test passes.
- Task Center records persist in the user-scoped SQLite WAL database at
  `~/.local/state/hafiye/task_center.db` (or the active explicit HERMES_HOME
  root). Completed history survives a new gateway process; in-flight worker
  records are marked failed with an explicit gateway-restart reason, while
  unstarted `QUEUED` work remains queued.
- The real Electron Task Center acceptance rendered persisted completed,
  failed, and queued records, showed provider/model, current step, tool,
  command, modified file, subagent state, and elapsed/cancellation surfaces,
  then cancelled a queued task through the real gateway RPC.
- P19 hardening doctor is green on the real host: all 12 checks pass and
  `blockers=[]`; the configured task-action cap is 200 and audit/disk floors
  are reported from the active Hafiye config/state roots.
- Real local runtime doctor reports the RTX 3080/CUDA llama-server healthy and
  AUTO-selected CUDA. Bounded `runtime server recover --attempts 1` correctly
  returned `runtime_already_ready` without restarting a healthy server.
- Real voice doctor reports whisper CUDA/Vulkan/CPU manifests and Piper Turkish
  voice ready. The pinned computer-use-linux doctor reports all four required
  readiness booleans true and `blockers=[]`.
- The unified P20 artifact `dist/hafiye_0.20.5_amd64.deb` was built from the
  real Electron `linux-unpacked` output. Its package manifest keeps the
  current Hafiye source commit, pinned Hermes commit, and baseline merge
  separate. Extracted-package `hafiye package doctor --json` returned
  `ok=true` with `blockers=[]`.

## Regression status

The P7 full backend comparison covered 3,219 files and reported 37,160 passed,
7 failed, and 244 skipped in 598.3 seconds. The historical five failures are
the `ACCEPTED_UPSTREAM_BASELINE`; the latest exact comparison reproduces only
items 2, 3, and 5 (Hermes state FTS, execution-flag detection, and Vercel
doctor diagnostics). Items 1 and 4 pass in the latest comparison. The two
cold-start failures passed 2/2 when the persistent Hafiye service was stopped
and are the existing KI-016 topology diagnostic. The browser reconnect test
is the existing KI-019 scheduling diagnostic; it passed on an immediate
isolated retry. No new Hafiye regression was found.

P14's 127-test backend project/memory matrix, 114-test Desktop UI matrix, real
Electron project acceptance, E2E typecheck, and production build passed. The
P14 source/test commit introduced no new or different upstream failure; the
historical five-ID whitelist and current three-ID comparison baseline are
unchanged.

P15's targeted Python matrix, Desktop Task Center test, typecheck, production
build, lint, compile, real OpenHands doctor, natural-language fixture E2E, and
gateway Task Center RPC/event smoke passed. The P15 source/test commit
introduced no new or different upstream failure; the historical five-ID
whitelist and current three-ID comparison baseline are unchanged.

P16's durable Task Center Python/RPC matrix, separate-process restart smoke,
Desktop component test, E2E typecheck, typecheck, lint, production build, and
real Electron + gateway acceptance passed. The P16 source/test commits
introduced no new or different upstream failure; the historical five-ID
whitelist and current three-ID comparison baseline are unchanged.

P17's Control Center navigation contract, Desktop typecheck, clean production
build, and real Electron/gateway acceptance passed. The P17 source/test commit
introduced no new or different upstream failure; the historical five-ID
whitelist and current three-ID comparison baseline are unchanged.

P18's cron persistence/scheduler matrix, Desktop model/typecheck/lint checks,
clean production build, real Electron/gateway scheduler acceptance, and two-
tick recurring local-task acceptance passed. The P18 source/test commit
introduced no new or different upstream failure; the historical five-ID
whitelist and current three-ID comparison baseline are unchanged.

P19's hardening matrix passed 111 focused backend tests plus 104 adjacent
browser/voice/config/audit tests. Ruff, bytecode/patch hygiene, the real
hardening/runtime/voice/computer-use doctors, and bounded llama recovery
passed. The canonical full backend run completed with 37,218 passed, 16
failed, and 244 skipped; 12 of the 16 selected failures reproduce on the
P18 source baseline and the four additional full-suite observations are
timing/active-desktop diagnostics. The exact five comparison command reduced
the current baseline to historical items 2, 3, and 5; items 1 and 4 passed.
No P19-specific regression was found.

P20's package metadata/manifest tests, root-broker handoff test, rootless
dpkg install test, and real Electron pack passed. The exact five-ID comparison
after the packaging changes remained `3 failed, 2 passed`, with only accepted
historical items 2, 3, and 5 failing. No packaging-specific or new upstream
regression was found.

The P5 targeted Python matrix now passes 468 tests, alongside the Desktop
provider tests/typecheck/build, real Secret Service round-trip, local CUDA
endpoint, remote OpenAI-compatible path, live Gemini model listing, and live
Gemini one-shot. P6 targeted policy/gateway/agent tests and Desktop settings
validation pass.

P8 targeted broker, packaging, startup-registry, emergency-stop, lint, and
compile checks pass. The real system service is active/enabled, the non-root
broker smoke passed, malformed and unauthorized clients failed closed, and
audit records were read through the broker without exposing raw command text.
The accepted five-ID upstream whitelist and current three-ID comparison
baseline are unchanged; no new P8 regression was found in the affected
CLI/packaging matrix.

P9 targeted computer-use/MCP tests passed (258 tests), the full Desktop UI
suite passed (579 files, 5,548 tests), the Desktop typecheck and clean
production build passed, and the real Wayland/GNOME acceptance flow passed.
The only observations were Firefox's AT-SPI focus warning (KI-022) and the
sparse VS Code accessibility tree (KI-023); neither is a P9 blocker and both
are documented.

P12 targeted wake-word Python/Desktop tests, the production build, the real
openWakeWord detector, and the minimized Electron acceptance all passed. The
only P12 observations are the existing PortAudio local-capture warning and
the CPython 3.13 openWakeWord optional-packaging warning documented in
KI-026; Desktop client capture is verified and P12 has no acceptance blocker.

P13 implementation tests pass and the process-wide stop fan-out is wired
through the persistent gateway. The authenticated real gateway sequence
engaged the durable ESTOP sentinel, returned prompt rejection code 4091 while
paused, and resumed successfully. Real TTS stop, process-registry kill, root
broker block/resume, and GNOME Wayland fallback keybinding checks passed. The
Desktop Electron and UI test subsets, typecheck, and production build also
pass. The managed OpenHands runtime doctor is green with official source
commit `6d38810359827823e62a5e1043d0d78d0bafb6de` and all four required
packages at `1.41.0`. A real Gemini-backed fixture delegation edited `bug.py`,
returned a result/change record, and the external fixture test returned
`1 passed in 0.00s`. A second live OpenHands worker was stopped through the
shared controller, returned `status=cancelled`, and was followed by an
intentional resume with no active worker remaining. No new or different
upstream regression was found.

## Active blockers

P5, P6, P7, P8, P9, P11, P12, and P21 have no open acceptance blockers. The user service and
`hafiye-rootd.service` are active
and the local CUDA runtime doctor is green. `loginctl` reports `Linger=no`,
and a full reboot was not performed; GNOME's `Super+Shift+Space` conflict
remains the existing operational warning. The initial development-v-env
systemd `-m hafiye_rootd` entrypoint failure was corrected by using the
packaged source entrypoint and is recorded as resolved KI-021.

The accepted upstream failures, KI-019 browser scheduling diagnostic, KI-022
Firefox focus warning, KI-023 VS Code accessibility warning, npm audit
warnings, missing pactl, missing vulkaninfo, optional-extra packaging
warnings, and KI-026 are documented diagnostics. KI-025 is resolved after the
synchronized real-microphone rerun recorded below. KI-027 is resolved by the
real OpenHands delegation acceptance recorded below. The direct upstream
generic `cua-driver` lane is unavailable on this host (KI-028), but the managed
computer-use-linux MCP provider remains accepted and is not replaced.

## Last tests and commands

### Backend and P1 identity

- .venv/bin/python -m pytest -q tests/hermes_cli/test_hafiye_identity.py tests/test_hermes_constants.py tests/hermes_cli/test_gateway_service.py
  — 153 passed, 6 skipped.
- Historical P4 closure `./scripts/run_tests.sh`
  — 3,213 files; 37,009 passed, 6 failed, 291 skipped in 515.9 seconds; exit 1
  because of the then-documented baseline/diagnostic failures. The run stopped
  the persistent Hafiye gateway and managed local model server temporarily and
  restored both by the exit trap. The latest P5 comparison is recorded below.
- .venv/bin/ruff check on all changed Python files
  — All checks passed.
- ./scripts/run_tests.sh tests/hermes_cli/test_local_runtime.py -q
  — 6 passed.
- ./scripts/run_tests.sh tests/agent/test_subprocess_env_guard.py
  tests/hermes_cli/test_persistent_gateway.py -q
  — 6 passed after routing the persistent gateway through the shared
  subprocess environment factory.
- `.venv/bin/ruff check hermes_cli/local_runtime.py
  hermes_cli/subcommands/runtime.py hermes_cli/main.py hermes_cli/web_server.py
  hermes_cli/persistent_gateway.py tests/hermes_cli/test_local_runtime.py`
  — All checks passed.

### Desktop

- cd apps/desktop && npm run test
  — 691 test files passed, 1 skipped; 7,149 tests passed, 3 skipped.
- cd apps/desktop && npm run typecheck
  — passed.
- cd apps/desktop && npm run build
  — Vite, Electron main/preload bundle, native dependency staging, and
  assert-dist-built passed. The clean build stamp is 34f1d8c2472e.
- cd apps/desktop && npm run builder -- --dir --publish never
  — Linux unpacked package passed.
- file apps/desktop/release/linux-unpacked/hafiye-desktop
  — x86-64 ELF; resources/icon.ico exists and the executable bit is set.

### Real XDG CLI smoke

With HERMES_HOME unset and all four XDG base variables pointed at a temporary
directory:

- hafiye --help rendered Hafiye usage and command names.
- hafiye config set model.default smoke-test-model wrote config/hafiye/config.yaml.
- The command created the expected config, data, state, and cache roots.

### Computer-use-linux P0 acceptance

- Pinned source commit:
  94736dc3e0dca56acfc89752c26869fb9ed01202.
- ~/.local/bin/computer-use-linux doctor
  — can_register_mcp_tools=true,
  can_build_accessibility_tree=true,
  can_send_development_input=true,
  can_query_windows=true, blockers=[].
- ~/.local/bin/computer-use-linux windows
  — returned the focused real desktop window through the GNOME extension.

### P2 persistent gateway and Desktop connection

- `./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py -q`
  — 4 passed.
- `./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_dashboard_admin_endpoints.py tests/hermes_cli/test_spawn_gateway_restart_cooldown.py tests/hermes_cli/test_web_server_profile_unification.py -q`
  — 75 passed.
- `cd apps/desktop && npm exec vitest run electron/hafiye-paths.test.ts --project electron`
  — Electron project completed with 108 files, 1,546 passed, 3 skipped.
- `cd apps/desktop && npm run typecheck`
  — passed.
- `cd apps/desktop && npm run build`
  — Vite, Electron bundles, native staging, and assert-dist-built passed; the
  build stamp recorded `e2e22c10b49ec01ef7d8420f1158668718b03fa9`.
- `.venv/bin/hafiye gateway service install`
  — installed/enabled the real user service; systemd reported enabled, active,
  and `NRestarts=0` on loopback port 9120.
- Real authenticated HTTP/WS probe against `127.0.0.1:9120`
  — HTTP request succeeded, backend version `0.20.5` returned, and the
  authenticated WebSocket reached `OPEN`.
- Real Electron launch/close with `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1`
  — Desktop log recorded persistent backend readiness; service remained active
  and reachable after Electron exit.
- Authenticated `POST /api/gateway/restart`
  — returned success, systemd reported a new active backend PID, and the
  endpoint became reachable again.

### P3 Composer, tray, and autostart

- `cd apps/desktop && ../../node_modules/.bin/vitest run electron/quick-entry.test.ts electron/composer-lifecycle.test.ts --project electron`
  — 2 files, 29 passed.
- `cd apps/desktop && ../../node_modules/.bin/vitest run src/store/quick-entry.test.ts --project ui`
  — 1 file, 17 passed.
- `cd apps/desktop && npm run test:ui`
  — 578 files, 5,547 passed.
- `cd apps/desktop && npm run test:desktop:platforms`
  — 114 files, 1,609 passed, 3 skipped.
- `cd apps/desktop && npm run typecheck`
  — renderer, Electron, and E2E checks passed.
- `cd apps/desktop && npm run build`
  — clean Vite renderer, Electron bundles, native staging, and
  `assert-dist-built` passed; clean stamp `e33bb456d109`.
- Real Wayland launch with `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1`
  — Desktop log recorded `Hafiye tray ready`, `Super+Shift+Space is already
  taken`, and persistent backend readiness.
- Real `ydotool` Alt+F4 against the Hafiye window
  — Electron process remained resident and `hafiye-gateway.service` remained
  active/listening on `127.0.0.1:9120`.
- Exact `~/.config/autostart/hafiye.desktop` `Exec=` command with `--hidden`
  — launched successfully in the current Wayland session.

### P4 managed local runtime

- `./scripts/run_tests.sh tests/hermes_cli/test_local_runtime.py -q`
  — 6 passed, including AUTO CUDA → Vulkan → CPU resolution, private GGUF
  registry/checksum handling, resumable downloads, and safe server health.
- `.venv/bin/hafiye runtime install --backend AUTO`
  — real llama.cpp source build completed; manifest records source commit
  `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`, compiled backends `CPU,CUDA`,
  and selected backend `CUDA`.
- `.venv/bin/hafiye runtime doctor`
  — `ok=true`, `blockers=[]`, `warnings=[]`, expected backend `CUDA`, current
  server ready with selected backend `CUDA`.
- Real model download/import evidence:
  `gemma-3-270m-it-q8` (291,545,600 bytes, SHA-256
  `0ef57d2c838458a1952664260dcba38e5bdda37494f3af732f06e4add24068e3`) and
  `qwen2.5-0.5b-instruct-q4` (397,808,192 bytes, SHA-256
  `6eb923e7d26e9cea28811e1a8e852009b21242fb157b26149d3b188f3a8c8653`).
- Real CUDA server: `llama-server` health and `/v1/models` returned HTTP 200;
  `--list-devices` reported `CUDA0: NVIDIA GeForce RTX 3080`; `nvidia-smi`
  showed the managed server using GPU memory. OpenAI-compatible chat returned
  `CUDA LOCAL OK`.
- Real lifecycle: Gemma CPU smoke returned `HERMES LOCAL OK`, the second model
  returned `SECOND MODEL OK`, and a Hermes one-shot against the CUDA endpoint
  returned a non-empty agent response. The model switch required no Hafiye
  reinstall.
- `systemctl --user restart hafiye-gateway.service` followed by an authenticated
  `GET /api/local-runtime` — returned `ok=true`, expected `CUDA`, selected
  `CUDA`; Desktop's model-settings API is therefore served by the persistent
  backend.
- `cd apps/desktop && ../../node_modules/.bin/vitest run
  src/app/settings/model-settings.test.tsx --project ui`
  — 1 file, 22 passed.
- `cd apps/desktop && npm run typecheck`
  — passed after the P4 Desktop API/settings integration.

- `cd apps/desktop && npm run build`
  — clean working-tree build passed; Vite, Electron main/preload bundles,
  native dependency staging, and `assert-dist-built` passed. Build stamp:
  `955a9c3818fa`.

- `systemctl --user is-active hafiye-gateway.service && systemctl --user is-enabled hafiye-gateway.service && .venv/bin/hafiye runtime doctor`
  — active, enabled; `ok=true`, `blockers=[]`, `warnings=[]`, expected and
  selected backend `CUDA`, managed server ready on `127.0.0.1:11435`.

### P5 providers, Gemini, and credential storage

- `./scripts/run_tests.sh tests/hermes_cli/test_hafiye_keyring.py
  tests/hermes_cli/test_p5_provider_paths.py
  tests/hermes_cli/test_credential_lifecycle.py
  tests/hermes_cli/test_prompt_api_key.py tests/hermes_cli/test_web_server.py
  tests/hermes_cli/test_runtime_provider_resolution.py
  tests/hermes_cli/test_model_switch_custom_providers.py
  tests/agent/test_credential_pool.py
  tests/hermes_cli/test_secret_source_bootstrap.py
  tests/secret_sources/test_secret_source_registry.py
  tests/secret_sources/test_profile_secrets.py
  tests/test_env_loader_secret_sources.py tests/hermes_cli/test_provider_parity.py
  tests/hermes_cli/test_gemini_provider.py
  tests/agent/test_gemini_native_adapter.py -q`
  — 15 files, 468 passed, 0 failed. This includes the default-XDG config-root
  lifecycle regression test.
- `./scripts/run_tests.sh tests/hermes_cli/test_env_export_line_lifecycle.py
  tests/hermes_cli/test_set_config_value.py
  tests/hermes_cli/test_hafiye_keyring.py
  tests/hermes_cli/test_p5_provider_paths.py -q`
  — 4 files, 93 passed, 0 failed; includes the default-XDG config-root
  lifecycle regression test.
- Real host Secret Service round-trip — provider secret was written, read,
  deleted, and removed from the keyring; config contained no secret value.
- Real managed local endpoint — `/v1/models` and `/v1/chat/completions`
  returned HTTP 200 with non-empty model/reply data; runtime doctor remained
  `ok=true`, `blockers=[]`, selected backend `CUDA`.
- Real remote OpenAI-compatible path — a local HTTP test server passed model
  validation, custom-endpoint save, authenticated chat, and no-raw-config
  assertions; reply marker was `P5_REMOTE_OK`.
- `cd apps/desktop && npm run test` — 692 test files passed, 1 skipped;
  7,156 tests passed, 3 skipped; exit 0. The run emitted only the known Vite,
  npm, and optional canvas test-environment warnings.
- `cd apps/desktop && npm run typecheck && npm run build` — typecheck and
  production build passed.
- `.venv/bin/hafiye status` — Linux Secret Service applied one provider
  secret; Google/Gemini is configured with a masked preview only.
- Real Gemini model probe — `GET
  https://generativelanguage.googleapis.com/v1beta/models` with the resolved
  Secret Service credential returned HTTP 200 and 50 models.
- `.venv/bin/hafiye -z "Reply with exactly HAFIYE_GEMINI_LIVE_OK and nothing else." --provider gemini --model gemini-flash-lite-latest --safe-mode`
  — returned exactly `HAFIYE_GEMINI_LIVE_OK`.

### P6 model router and privacy modes

- `./scripts/run_tests.sh tests/test_hafiye_policy.py
  tests/run_agent/test_hafiye_agent_policy.py tests/gateway/test_hafiye_routing.py
  -q` — 3 files, 17 passed, 0 failed. This covers normal local routing,
  explicit remote/Gemini overrides, all privacy boundaries, route locality,
  and legal fallback activation.
- `./scripts/run_tests.sh tests/test_web_server.py
  tests/hermes_cli/test_web_server.py tests/hermes_cli/test_config_validation.py
  tests/gateway/test_api_server.py tests/gateway/test_api_server_runs.py
  tests/hermes_cli/test_fallback_config.py -q` — 6 files, 321 passed, 3
  skipped, 0 failed.
- `cd apps/desktop && npm run test -- --run
  src/app/settings/helpers.test.ts src/app/settings/settings-search.test.ts
  src/app/settings/voice-provider-fields.test.ts` — 3 files, 47 passed.
- `cd apps/desktop && npm run typecheck` — passed after the Hafiye routing and
  privacy settings wiring.
- `.venv/bin/ruff check` on all P6 changed Python files — all checks passed;
  the existing upstream invalid `# noqa` warning in `run_agent.py` remains.
- `git diff --check` and Python bytecode compilation of all P6 changed Python
  files — passed.

### Latest full backend comparison

- `./scripts/run_tests.sh` with the persistent gateway and managed local model
  server stopped temporarily — 3,218 files; 37,156 passed, 4 failed, 244
  skipped in 541.8 seconds, exit 1. All four failures are accepted-baseline
  IDs; the accepted remote browser-control ID did not reproduce. The
  persistent services were restored by the exit trap.
- `./scripts/run_tests.sh tests/gateway/test_browser_control_api.py -q -k local_api_same_identity_reconnect_completes_command_started_on_old_socket`
  — 1 selected test passed in the P6 checkout.
- `HERMES_PYTHON=/home/tolga/projects/hafiye/.venv/bin/python /tmp/hafiye-pre-p6/scripts/run_tests.sh tests/gateway/test_browser_control_api.py -q -k local_api_same_identity_reconnect_completes_command_started_on_old_socket`
  — 1 selected test passed in the P6-parent checkout; the temporary checkout
  was removed after comparison.
- `./scripts/run_tests.sh tests/gateway/test_compression_failure_session_sync.py tests/gateway/test_fallback_chain_reload.py -q`
  — 2 files, 6 passed, 0 failed after the P6 gateway contract fix.

### P7 host tools and execution policy

- `.venv/bin/python -m pytest -q tests/test_hafiye_execution_policy.py tests/test_model_tools.py`
  — 31 passed, 0 failed.
- `.venv/bin/python -m pytest -q tests/tools/test_terminal_tool.py
  tests/tools/test_code_execution.py tests/tools/test_approval.py
  tests/tools/test_process_registry.py tests/tools/test_file_tools.py`
  — 285 passed, 6 skipped, 1 warning, 5 subtests passed.
- `.venv/bin/ruff check` on all P7 changed Python files — all checks passed;
  Python bytecode compilation and `git diff --check` also passed.
- Runtime schema smoke — `hafiye.execution_policy` is a real select with
  `FULL_AUTONOMOUS`, `PRIVILEGED_CONFIRM`, `WRITE_CONFIRM`, and `READ_ONLY`.
- Real Hafiye dispatcher host smoke — terminal returned
  `HAFIYE_P7_HOST`; a temporary file was read successfully; a background
  process returned `HAFIYE_P7_PROCESS` and exited cleanly.
- `cd apps/desktop && npx vitest run --project ui
  src/app/settings/helpers.test.ts src/app/settings/settings-search.test.ts
  src/app/settings/terminal-backend-panel.test.tsx` — 3 files, 46 passed.
- `cd apps/desktop && npx vitest run --project ui
  src/app/settings/gateway-settings.test.tsx
  src/app/settings/providers-settings.test.tsx
  src/store/session-unread-tile.test.ts
  src/app/settings/toolset-config-panel.test.tsx
  src/app/messaging/index.test.tsx src/app/skills/index.test.tsx`
  — 6 files, 58 passed after the contaminated parallel run was discarded.
- `cd apps/desktop && npm run typecheck` — renderer, Electron, and E2E
  TypeScript checks passed.
- `cd apps/desktop && npm run build` — Vite renderer, Electron main/preload,
  native staging, and `assert-dist-built` passed; existing npm/Vite warnings
  remain documented diagnostics.
- `./scripts/run_tests.sh` — 3,219 files; 37,160 passed, 7 failed, 244
  skipped in 598.3 seconds; four accepted baseline failures plus KI-016 and
  KI-019 diagnostics, with no new Hafiye regression.
- `.venv/bin/python -m pytest -q
  tests/hermes_cli/test_update_cold_start_gateway_liveness.py` with the
  persistent service stopped — 2 passed; the service was started again.
- `.venv/bin/python -m pytest -q tests/gateway/test_browser_control_api.py
  -k test_local_api_same_identity_reconnect_completes_command_started_on_old_socket`
  — first run timed out; immediate retry passed 1/1, matching KI-019.
- `.venv/bin/hafiye runtime doctor` after restoration — `ok=true`,
  `blockers=[]`, selected backend `CUDA`; `hafiye-gateway.service` active.

### P8 privileged root broker

- `.venv/bin/python -m pytest -q tests/test_hafiye_rootd.py
  tests/test_packaging_metadata.py` — 13 passed, 0 failed.
- `.venv/bin/python -m pytest -q tests/hermes_cli/test_startup_plugin_gating.py
  tests/test_estop.py tests/test_packaging_metadata.py tests/test_hafiye_rootd.py`
  — 39 passed, 0 failed.
- `.venv/bin/ruff check hafiye_rootd.py hermes_cli/main.py
  tests/test_hafiye_rootd.py`; `py_compile`; and `git diff --check` — all
  passed.
- `uv pip install --python .venv/bin/python -e . --no-deps` — editable
  package refreshed; `.venv/bin/hafiye-rootd --help` and `.venv/bin/hafiye
  root --help` rendered successfully.
- Normal visible-terminal sudo install — `/usr/lib/systemd/system/
  hafiye-rootd.service` enabled and active; rootd PID EUID 0; socket
  `/run/hafiye/root.sock` mode 0600 owned by `tolga`.
- Real `.venv/bin/python` broker smoke — client EUID 1000, `root.exec id -u`
  returned broker UID 0, privileged temporary write succeeded, duplicate-key
  request returned `malformed_request`, and `nobody` returned
  `permission_denied` on the real system socket.
- Audit verification through `RootBrokerClient` — 33 records sampled, 11
  complete request groups, accepted/rejected plus closed lifecycle events,
  peer and duration fields present, and raw test command text absent.

### P9 Linux computer use

- `.venv/bin/python -m pytest -q tests/test_hafiye_computer_use.py` and the
  MCP configuration tests — 9 passed in the focused run.
- `.venv/bin/python -m pytest -q tests/tools/test_mcp_tool.py
  tests/hermes_cli/test_tools_config.py tests/cron/test_scheduler.py
  tests/hermes_cli/test_mcp_tools_config.py tests/test_hafiye_computer_use.py`
  — 258 passed; one pre-existing async resource warning was emitted by the
  scheduler test.
- `cd apps/desktop && npx vitest run --project ui
  src/app/settings/computer-settings.test.tsx` — 1 file, 1 passed.
- `cd apps/desktop && npm run test:ui` — 579 files, 5,548 tests passed.
  Existing jsdom canvas warnings were emitted; no test failed.
- `cd apps/desktop && npm run typecheck` — renderer, Electron, and E2E
  TypeScript checks passed.
- `cd apps/desktop && npm run build` — clean source build passed; the build
  stamp recorded `6d3672e498e1` and `assert-dist-built` passed. Existing Vite,
  Babel, and chunking warnings remain documented upstream build diagnostics.
- Real managed readiness probe through `computer_use_linux_status()` —
  source `94736dc3e0dca56acfc89752c26869fb9ed01202`, all four required
  readiness booleans true, `ready=true`, `blockers=[]`.
- Real `discover_mcp_tools()` with the managed entry — provider connected and
  18 `mcp__hafiye_computer_use_linux__*` tools registered without a user
  `mcp_servers` configuration edit.
- Real MCP E2E through `model_tools.handle_function_call()` on Wayland/GNOME:
  Calculator exposed a 66-node initial and 70-node post-input AT-SPI tree;
  the focused editable value became `84` after `12*7` and Enter. Firefox
  created a tab, navigated to an Example Domain marker, and switched focus to
  and from Calculator. VS Code and Files launched; focus was verified and Files
  exposed 137 accessible nodes without an accessibility error.
- Cleanup verification — Calculator, VS Code, and Files test windows were
  closed through the managed input path; the user's existing Firefox windows
  remained open.

## P10 browser

- Status: complete; no blocker and no new/different regression.
- Source commit: `5d2354095562d149ff54e58d664c1b042cf50c3e`.
- Structured browser path: Hermes `browser_*` tools remain Hafiye's
  structured automation lane. When the current Hermes configuration selects
  its Browser Use CLI backend, that existing `browser_exec` behavior remains
  intact; the real P10 structured acceptance selected the built-in lane with
  `browser.backend: off`. Hafiye adds the dedicated
  `browser_download` operation using the current official
  `agent-browser download` command and recognizes the user-space Chrome
  cache installed by `agent-browser@^0.26.0`.
- Native browser path: `browser_native` is an explicit route through the
  already-managed `hafiye-computer-use-linux` MCP tools. It enumerates and
  binds an exact existing Firefox window, performs focus/state/navigation/key
  operations, and does not create a profile or read cookies.
- Real structured probe: an isolated `HERMES_HOME` with
  `browser.backend: off` served a local page; navigation, extraction marker,
  and `browser_download` all passed. The downloaded content was
  `HAFIYE_STRUCTURED_DOWNLOAD_OK`.
- Real native probe: `discover_mcp_tools()` plus
  `model_tools.handle_function_call("browser_native", ...)` controlled the
  existing Firefox Wayland window, opened a temporary tab, navigated to a
  local marker page, read the focused window title, and closed only the test
  tab. Result: `native_navigation=true`, `blockers=[]`; post-cleanup window
  query found no `Hafiye P10 Native` marker window.
- Firefox's existing AT-SPI focus warning remains KI-022; compositor focus,
  ydotool input, navigation, and title readback passed. No authenticated page
  content or cookies were inspected.
- Final browser regression: `.venv/bin/python -m pytest -q
  tests/tools/test_browser_*.py tests/tools/test_hafiye_browser.py` — 504
  passed, 7 deselected, 0 failed. Focused Hafiye/policy/router matrix — 49
  passed, 0 failed. Ruff, `py_compile`, and `git diff --check` passed.

## ACCEPTED_UPSTREAM_BASELINE

The original five upstream failures were accepted before Hafiye source
changes. The exact five IDs remain the historical accepted regression
whitelist. The current post-P19 comparison baseline is the three IDs that
reproduced:

1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

The accepted remote browser-control ID (item 1) and Termux ID (item 4) passed
the exact comparison command after P19, so the current baseline was reduced to
items 2, 3, and 5. The separate local reconnect scheduling failure is
documented in KI-019 and is not added to the historical whitelist. Future
failures within the historical five are classified against that upstream
whitelist; any new or different ID is a regression to investigate. The upstream
bugs are not being fixed by Hafiye.

## Exact next actions

1. Keep the pinned Hermes commit, baseline merge commit, and current Hafiye
   source/test commit `a87eaaba7373a2c23fa73b7ef498b64d67c989f5` separate in
   all state documents.
2. Keep the historical five-ID `ACCEPTED_UPSTREAM_BASELINE` whitelist and the
   current three-ID comparison baseline; investigate any new/different ID.
3. Begin P22 — CLI — against the accepted P21 backend/Desktop boundary while
   preserving the shared gateway and Desktop business-logic boundary.

## Environment changes

P2 installed and enabled the user-scoped `hafiye-gateway.service`; P3 added
the owner-safe `~/.config/autostart/hafiye.desktop` entry and Composer settings
under the Desktop user-data root. P4 added the managed llama.cpp source/build
and model roots and the real CUDA toolkit development packages were installed
by the user in a visible terminal. No sudo, root, passwordless sudo, or NOPASSWD
sudoers change was made. User-manager linger remains disabled. P1's XDG
alignment and P0's real Ubuntu, GNOME Wayland, NVIDIA/CUDA,
PipeWire/WirePlumber, Python, Node, Rust, systemd-user, AT-SPI, ydotool, and
uinput observations remain in ENVIRONMENT.md. P5 added the Hafiye Linux Secret
Service provider-credential path, `keyring==25.7.0`, provider/key UI wiring,
and the remote OpenAI-compatible test boundary. No sudo, root, passwordless
sudo, or NOPASSWD sudoers change was made during P5.
P6 added only user-configured route/privacy policy and shared enforcement code;
the follow-up gateway cache/fallback contract fix is in commit
`62b3d5762d49b1ce2872d142c8e5318239b01c5c` and
made no system package, sudo, service, or password change. The managed local
server was restored through `.venv/bin/hafiye runtime server start
qwen2.5-0.5b-instruct-q4 --backend AUTO --context-size 4096 --gpu-layers 99`;
the runtime doctor then reported `ok=true`, `blockers=[]`, and selected backend
`CUDA`.
P7 added only the shared host execution-policy classifier/dispatch enforcement,
the existing Hermes approval-surface integration, and the real Desktop config
select; no system package, sudo, service, or password change was made.
P8 installed and enabled `/usr/lib/systemd/system/hafiye-rootd.service` using
normal interactive sudo in a visible terminal. The service runs as root only
for brokered privileged operations, permits the configured local UID 1000 over
`/run/hafiye/root.sock`, and uses no TCP/UDP listener. No passwordless sudo or
`NOPASSWD` sudoers rule was created.
P9 did not require sudo or system-package changes. It reused the P0-pinned
computer-use-linux checkout/binary, added only the Hafiye-managed MCP/provider
and Desktop diagnostics wiring, and closed the real Calculator, VS Code, and
Files test windows after acceptance. The user's existing Firefox windows were
left open.
P10 required no sudo or system-package changes. It installed the official
`agent-browser@^0.26.0` Chrome payload under the user cache
`~/.agent-browser/browsers/`, added structured download/native browser routing,
and closed the temporary native Firefox tab. Existing Firefox windows and
authenticated state were not inspected or modified.
P5's live Gemini credential was saved to Linux Secret Service and hydrated from
the canonical Hafiye config root; no plaintext credential was added to the
repository or configuration. The provider lifecycle/XDG fix is source commit
`45294d3f77a3929731ac29d89d54f5d53c70957d`.
P12 added only the user-owned openWakeWord training runtime and the bundled
standalone ONNX asset. The official source checkout and training venv live
under `~/.local/share/hafiye/runtimes/openwakeword-training/`; no sudo,
system-package, systemd, group, device-permission, or password change was
required. The host's missing PortAudio library remains a diagnostic for local
PortAudio capture; PipeWire/WirePlumber-backed Desktop client capture was
verified instead. The training dependency metadata warning is recorded as
KI-026, not hidden by a fake readiness result.
P14 required no sudo, system-package, service, device-permission, or credential
changes. Desktop acceptance sandboxes explicitly disabled the normal
persistent-gateway preference so each test used its isolated `HERMES_HOME`;
the host `hafiye-gateway.service` was not modified.
P15 added a user-scoped official OpenHands source checkout and managed virtual
environment under `~/.local/share/hafiye/runtimes/openhands/`. The checkout is
pinned to source commit
`6d38810359827823e62a5e1043d0d78d0bafb6de`; the SDK, tools, workspace, and
agent-server packages are each pinned to `1.41.0`. The install/doctor flow
required no sudo, system package, service, device-permission, or password
change. Task Center records are process-local in P15; durable generic task
history is explicitly deferred to P16.
P16 added the user-scoped Task Center SQLite WAL store at
`~/.local/state/hafiye/task_center.db`, plus restart recovery and the real
Desktop acceptance path. This required no sudo, system package, service,
device-permission, credential, or password change.
P17 added the Hafiye Control Center overlay route and reused the real Hermes
config, provider, skills/MCP, scheduler, logs, computer-use, Task Center, and
About surfaces. The isolated Electron/gateway acceptance changed only its
temporary HERMES_HOME; no host service, credential, sudo, package, or device
permission was changed.
P18 added only the scheduler policy persistence/resolution and Desktop cron
editor controls. It reused Hermes cron storage, scheduler claims/execution,
skills/toolset catalog, and MCP safety merge. The backend test sandbox and
isolated Electron/gateway acceptance changed no host service, credential,
sudo, package, or device permission.

### P4 source validation

- Current source commits: P4 local runtime `87cbfb34337f043363ba8851c485fea5ea66de0b`; shared gateway environment guard fix `d912a85ee5fa21afb1c5304e28c6e3651fb16433`; cross-platform process fix `ae24562fb9dfeeb4dd58752849b4778b2c8606e8`.
- The managed runtime is a separable Hafiye patch group. It uses XDG data/state
  roots, a private model registry, atomic model/runtime publication, loopback
  `127.0.0.1:11435`, and the current upstream `llama-server` CLI.
- A rebuild stops the managed server before publishing the binary, avoiding
  Linux `ETXTBSY` when a live server maps the old executable.
- The corrected P4 closure suite was a historical baseline/diagnostic run; the
  latest P5 comparison and exact current five-ID baseline are recorded above.
  No new or different Hafiye regression was found.

### P5 source validation

- Provider credential boundary source commit:
  `c771c95318516e03450720b5f009dce4017f8600`; shared tool/provider alias
  classification fix: `15cbe1f6556addbaf694c36999e0c496730a1730`.
- `keyring==25.7.0` is a core dependency. The real GNOME/Linux Secret Service
  round-trip passed without recording secret values; config retained only
  keyring references.
- Local llama.cpp, remote OpenAI-compatible, provider parity, automated Gemini,
  and Desktop provider tests pass as recorded above.
- The default-XDG Secret Service lifecycle correction is source commit
  `45294d3f77a3929731ac29d89d54f5d53c70957d`; its regression test passes.
- Live Gemini model listing returned HTTP 200 with 50 models and the real
  Hafiye one-shot returned `HAFIYE_GEMINI_LIVE_OK`. P5 is complete.

### P6 source validation

- Source commits: `cf6457678b6083c4f783c1a80eef9eba3875ccc0` (routing/privacy)
  and `62b3d5762d49b1ce2872d142c8e5318239b01c5c` (gateway cache/fallback
  contract follow-up).
- `hafiye_policy.py` owns route slots, task overrides, privacy normalization,
  local-runtime classification, legal fallback filtering, OFFLINE tool
  filtering, and dispatcher denial messages.
- Agent, native gateway, API server, one-shot CLI, interactive CLI setup, and
  Desktop settings consume that shared policy. No second provider or config
  system was introduced.
- P6 targeted tests and the affected backend/config matrix pass as recorded
  above. The only different full-suite failure was reproduced in the
  P6-parent checkout and is tracked as KI-019; no Hafiye source regression was
  found.

## P11 execution status — complete

The commit identities remain separate and are recorded here explicitly:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- P11 Hafiye source commit: `6f2b982159a37d9fb73d460c19279ea06d06efa0`.

### Verified working

- Managed whisper.cpp source checkout/builds are installed under
  `~/.local/share/hafiye/runtimes/whisper.cpp/` at source commit
  `c122757fddf358397bb7f33b6ac3aab24a5bca04`.
- CPU, CUDA, and Vulkan `whisper-cli` builds exist; the real doctor selected
  CUDA under the binding `AUTO` policy on the RTX 3080.
- The Turkish `tr_TR-dfki-medium` Piper voice is installed in the separate
  managed runtime under `~/.local/share/hafiye/runtimes/piper/` using
  `piper-tts==1.7.0`.
- The managed STT hook, managed Piper process boundary, real Piper preview
  API, microphone-device persistence/hotplug path, and Desktop Voice settings
  controls are implemented.

### Acceptance

- Real voice doctor returned `ok: true`, `blockers: []`, with CUDA selected,
  all three whisper backends compiled, and the Turkish Piper voice ready.
- Direct Piper synthesis and the Hermes TTS path both produced Turkish WAV/MP3
  audio; `pw-play` completed the real playback smoke.
- The synchronized real microphone capture used the default PipeWire node 37
  (`Trust GXT 232 Microphone Mono`) at 16 kHz, mono, signed 16-bit WAV. CUDA
  whisper.cpp returned the prompted Turkish sentence correctly, and the same
  file passed through Hafiye's `transcribe_audio()` hook with
  `provider: local_command`. The real Turkish microphone acceptance passed;
  the earlier unsynchronized samples remain historical KI-025 evidence.

### P11 test record

- `.venv/bin/python -m pytest -q tests/hermes_cli/test_voice_runtime.py tests/tools/test_hafiye_voice_runtime_hooks.py tests/tools/test_transcription.py tests/tools/test_transcription_command_providers.py tests/tools/test_transcription_tools.py tests/tools/test_tts_piper.py tests/hermes_cli/test_voice_wrapper.py tests/test_voice_max_recording_seconds.py`
  — 131 passed in 6.19s.
- `.venv/bin/python -m hermes_cli.voice_runtime doctor`
  — `ok: true`, `blockers: []`, expected/selected `CUDA`, whisper
  `CPU/CUDA/VULKAN`, Piper `1.7.0`, `tr_TR-dfki-medium` ready.
- `cd apps/desktop && npm run test:ui -- src/app/settings/voice-provider-fields.test.ts src/app/settings/voice-field-visible.test.ts src/app/settings/helpers.test.ts src/lib/voice-input-device.test.ts`
  — 4 files, 50 passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npm run build` — Vite, Electron bundles, native staging,
  and `assert-dist-built` passed; existing npm/Vite/Babel warnings remain.
- `cd apps/desktop && npx playwright test e2e/boot.spec.ts --reporter=line`
  — 5 passed; `npx playwright test e2e/voice-settings.spec.ts --reporter=line`
  — 1 passed in the real Electron path.
- `.venv/bin/python -m hermes_cli.voice_runtime stt --input /tmp/hafiye-p11-mic-20260824-countdown.wav --output-dir /tmp/hafiye-p11-stt-countdown --language tr --backend AUTO`
  — CUDA/local command returned the correct Turkish sentence.
- `.venv/bin/python` calling `tools.transcription_tools.transcribe_audio()` on
  the same WAV — `success: True`, `provider: local_command`, correct Turkish
  sentence returned.
- The first combined boot+voice run had one parallel boot-readiness timeout;
  isolated reruns passed, so it is recorded as a test-topology observation,
  not a source regression.
- Ruff, Python bytecode compilation, and `git diff --check` passed.

## P12 execution status — complete

The commit identities remain separate and are recorded here explicitly:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- P12 Hafiye source commit: `d1c5f4c9c5254ba34844e583e5486972e33bdd6b`.

### Verified working

- Official openWakeWord source checkout:
  `~/.local/share/hafiye/runtimes/openwakeword-training/source` at commit
  `368c03716d1e92591906a84949bc477f3a834455`.
- The reproducible training script
  `scripts/train_hafiye_wakeword.py` uses official `openWakeWord.train.Model`,
  Turkish Piper `tr_TR-dfki-medium`, 384 synthetic samples per class, seed
  `20260824`, and 900 training steps. It exports the standalone ONNX asset
  `tools/wakewords/hafiye.onnx`.
- The default runtime config is phrase `Hafiye`, model `hafiye`, sensitivity
  `0.6`, and confirmation frames `3`. The Desktop Voice settings expose the
  real persisted tuning fields and an RPC-backed enable/disable control.
- The client capture path signals Electron to keep its renderer unthrottled
  only while the wake audio graph is active, so minimize does not pause PCM
  delivery. Stopping capture restores normal idle throttling.

### Acceptance

- Synthetic validation at threshold `0.6`: accuracy `1.0`; negative maximum
  `0.04943939670920372`; positive minimum `0.9991450309753418`.
- `/tmp/hafiye-p12-positive-20260824.wav` (normal-room music) produced zero
  wake fires with three-frame confirmation.
- `/tmp/hafiye-p12-positive-20260824-take2.wav` contained five spoken Hafiye
  activations; direct openWakeWord detection fired four times under the
  two-second cooldown and managed Turkish STT recognized the repeated phrase.
- The real Electron bundle armed the persistent Hafiye gateway through client
  capture, then detected the same recording after the Hafiye window was
  actually minimized: `minimized=true`, `visible=false`, and the route changed
  from `#/settings?tab=config%3Avoice` to `#/`.

### P12 test record

- `.venv/bin/python -m pytest -q tests/tools/test_wake_word.py`
  — 26 passed, 3 skipped.
- `cd apps/desktop && npx vitest run --project ui src/store/wake-word.test.ts src/app/chat/composer/controls.test.tsx`
  — 2 files, 37 passed.
- `cd apps/desktop && npx vitest run --project electron electron/stream-throttle.test.ts`
  — 1 file, 5 passed.
- `cd apps/desktop && npm run typecheck`
  — renderer, Electron, and E2E TypeScript checks passed.
- `cd apps/desktop && npm run build`
  — Vite, Electron main/preload bundles, native dependency staging, and
  `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain.
- `.venv/bin/ruff check scripts/train_hafiye_wakeword.py tools/wake_word.py tests/tools/test_wake_word.py hermes_cli/config_defaults.py`; `.venv/bin/python -m py_compile scripts/train_hafiye_wakeword.py tools/wake_word.py tests/tools/test_wake_word.py hermes_cli/config_defaults.py`; `git diff --check`
  — all passed.
- Real Desktop acceptance used the built Electron bundle with
  `--use-fake-ui-for-media-stream`, `--use-fake-device-for-media-stream`, and
  `--use-file-for-fake-audio-capture=/tmp/hafiye-p12-positive-20260824-take2.wav`;
  the minimized-window result was recorded above. The persistent wake config
  was reset to `wake_word.enabled: false` after the test.

P12 is accepted. The exact five historical upstream failures remain the
`ACCEPTED_UPSTREAM_BASELINE`; the P12 targeted matrix introduced no new or
different regression.

## P13 execution status — complete

The P13 source implementation is recorded in commit
`dfb0d29c7ba80efadd5a517bac07aa949e517a5a`. The pinned Hermes commit,
history-preserving baseline merge, and current Hafiye source commit are kept
separate above and here:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- P13 Hafiye source commit: `dfb0d29c7ba80efadd5a517bac07aa949e517a5a`.

### Implemented and verified

- One gateway-owned `CancellationController` now fans out emergency stop to
  TTS, managed desktop-action backends, active gateway sessions, async
  delegations, registered processes, and the durable ESTOP/root-RPC gate.
- Desktop GUI/tray/Composer stop, the Turkish `Hafiye dur` voice path, CLI
  `emergency-stop`, and `Ctrl+Super+Escape` converge on the same stop RPC.
- Electron global shortcut registration is attempted first. On this real
  GNOME Wayland session Electron reported the accelerator unavailable, so a
  private GNOME custom keybinding fallback was installed, triggered with real
  `ydotool`, created the ESTOP sentinel, and cleaned itself up on exit without
  disturbing unrelated bindings.
- The authenticated persistent-gateway smoke engaged pause, rejected a new
  prompt with code `4091`, and resumed intentionally. The root broker blocked
  a new privileged request while the sentinel existed and resumed afterward.
- Real TTS stop and process-registry kill smokes passed. Managed
  `computer-use-linux` MCP gates and cancellation tests pass; the generic
  upstream `cua-driver` path is unavailable on this host and is documented as
  KI-028 rather than substituted.
- The managed OpenHands V1 runtime is installed under
  `~/.local/share/hafiye/runtimes/openhands/`, with official source commit
  `6d38810359827823e62a5e1043d0d78d0bafb6de`, package pins at `1.41.0`, and
  doctor result `ready=true`, `blockers=[]`.
- `coding_delegate` resolves the Hafiye `coding` route, starts an official
  OpenHands V1 conversation in a managed worker, and tracks it in the shared
  process registry. The worker boundary consumes the credential without
  placing it in the command line or redacted progress records.
- A real Gemini-backed fixture repository contained a failing test. The live
  delegate corrected `bug.py`; an external `pytest -q` returned
  `1 passed in 0.00s`, and the parent received the real summary and changed
  file record.

### P13 acceptance

- The master P13 OpenHands-specific acceptance passed in one live Python
  process: a long-running `coding_delegate` worker was visible in
  `process_registry`, `CancellationController.emergency_stop(...)` killed it,
  the delegate returned `status=cancelled`, the thread ended, and an explicit
  `controller.resume()` returned `paused=false` with no active worker left.
- KI-027 is resolved. P13 and P14 are complete; P15 is also complete and P16
  is now the first incomplete phase.

### P13 test record

- `.venv/bin/python -m pytest -q tests/test_estop.py tests/test_hafiye_rootd.py tests/tools/test_mcp_tool.py tests/tools/test_computer_use.py tests/tui_gateway/test_protocol.py` — 298 passed, 1 known coroutine warning.
- `.venv/bin/python -m py_compile ...` over all changed P13 Python files — pass.
- `.venv/bin/ruff check ...` over all changed P13 Python files — `All checks passed!`.
- `cd apps/desktop && npx vitest run --project electron electron/emergency-stop-shortcut.test.ts electron/gnome-emergency-stop.test.ts electron/stream-throttle.test.ts` — 3 files, 11 passed.
- `cd apps/desktop && npx vitest run --project ui src/lib/voice-stop-word.test.ts src/store/wake-word.test.ts src/app/chat/composer/controls.test.tsx src/app/chat/composer/hooks/use-voice-conversation.test.tsx src/app/chat/composer/hooks/use-voice-conversation-rearm.test.tsx` — 5 files, 58 passed.
- `cd apps/desktop && npm run typecheck` — pass.
- `cd apps/desktop && npm run build` — Vite, Electron bundles, native staging, and `assert-dist-built` passed; existing toolchain warnings remain.
- `.venv/bin/python - <<'PY' ... openhands_runtime_doctor() ... PY` —
  `ready=true`, `blockers=[]`; official OpenHands packages
  `openhands-sdk`, `openhands-tools`, `openhands-workspace`, and
  `openhands-agent-server` all `1.41.0`.
- Real Gemini route through `model_tools.handle_function_call("coding_delegate", ...)`
  against `/tmp/hafiye-openhands-e2e` — OpenHands edited the fixture's
  `bug.py`; external `.venv/bin/python -m pytest -q` — `1 passed in 0.00s`;
  the parent result included `status=completed`, `event_count=36`, and
  `changed_files=["bug.py"]`.
- Real same-process OpenHands cancellation harness — started a live worker,
  called `tui_gateway.server._get_cancellation_controller().emergency_stop(...)`,
  then `controller.resume()` — `status=cancelled`, `killed_processes=1`,
  `thread_alive_after_stop=false`, `paused=false`, and no active process.
- Real result-return rerun through the same `coding_delegate` route — parent
  summary contained the exact fixture result `1 passed in 0.00s`.
- `git diff --check` — pass.

## P14 execution status — complete

The P14 source/test commit is
`831405dcec4abcba033d8ccc18308804868ecb1f`. The pinned Hermes source already
provided the per-profile `projects.db`, deterministic slug/name project tools,
gateway project RPCs, project tree, and FTS5 `session_search`; Hafiye added the
acceptance coverage and isolated Desktop E2E wiring without replacing that
upstream store or rewriting Hermes history.

The commit identities remain separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `831405dcec4abcba033d8ccc18308804868ecb1f`.

### P14 test record

- `.venv/bin/python -m pytest -q tests/tools/test_project_tools.py tests/hermes_cli/test_projects_db.py tests/hermes_cli/test_projects_cli.py tests/tui_gateway/test_projects_rpc.py tests/tui_gateway/test_project_tree.py tests/tools/test_session_search.py` — 127 passed in 3.38s.
- `cd apps/desktop && ../../node_modules/.bin/vitest run --project ui src/store/projects.test.ts src/app/chat/sidebar/project-dialog.test.tsx src/app/chat/sidebar/projects/project-menu.test.tsx src/app/chat/sidebar/projects/overview-row.test.tsx src/app/chat/sidebar/projects/workspace-groups.test.ts src/lib/session-search.test.ts` — 6 files, 114 passed.
- `cd apps/desktop && ../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` — passed.
- `cd apps/desktop && ../../node_modules/.bin/playwright test e2e/p14-project-registry.spec.ts --reporter=list` — real Electron plus live isolated gateway, 1 passed in 12.2s.
- `cd apps/desktop && npm run build` — Vite, Electron main/preload bundles, native staging, and `assert-dist-built` passed; existing npm/Vite/Babel/chunking warnings remain.
- Fresh-process project-memory E2E — `project_create("Pocket World", path)` followed by a separate process `project_switch("pocket-world")` resolved the exact path, and `session_search("Pocket World")` returned the recent seeded context with marker `P14_PROJECT_MEMORY_E2E_OK`.

The P14 acceptance criteria passed: project alias/path persistence across a
backend process boundary, deterministic path resolution, recent session
context recall, and real Desktop browse/search/rename/delete behavior. No new
or different regression was found; the accepted historical five-ID whitelist
  and current three-ID comparison baseline are unchanged.

## P15 execution status — complete

The P15 source/test commit is
`54b4ee49569267b21e10b357acdde427a8a844ff`. The pinned Hermes commit, the
history-preserving baseline merge, and the current Hafiye source commit remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `54b4ee49569267b21e10b357acdde427a8a844ff`.

### Implemented and verified

- `hafiye runtime openhands install` performs an idempotent user-scoped
  checkout of the official OpenHands Software Agent SDK at source commit
  `6d38810359827823e62a5e1043d0d78d0bafb6de`, installs the exact `1.41.0`
  pins for `openhands-sdk`, `openhands-tools`, `openhands-workspace`, and
  `openhands-agent-server`, and writes a runtime manifest.
- `hafiye runtime openhands doctor` verifies the managed Python, package
  versions, manifest, and detached source checkout. On the actual host it
  returned `ready=true` and `blockers=[]` after the install.
- `coding_delegate` uses the Hafiye `coding` route, local repository paths,
  the official OpenHands V1 worker, and Hermes process tracking. It records
  safe lifecycle/progress/tool/file-change/result metadata without exposing
  credentials or private chain-of-thought.
- The shared process-local `TaskCenterRegistry` exposes coding task lifecycle,
  current step, provider/model/route/privacy, progress events, commands,
  tools, changed files, result/error, elapsed timestamps, and cancellation.
  Gateway `tasks.list`/`tasks.cancel` RPCs and global `task.update` events are
  wired to the Desktop Task Center panel in Command Center → Maintenance.
- A real natural-language Hafiye Gemini run against a fresh fixture identified
  the coding task, delegated to OpenHands, changed only `bug.py`, and returned
  the actual `pytest -q` result; the external fixture verification returned
  `1 passed in 0.00s`.
- A real gateway integration smoke observed `RUNNING` through `tasks.list`,
  received the final `COMPLETED` record with 18 progress events and
  `file_changes=["bug.py"]`, and captured 22 `task.update` events. The
  Desktop component test and production build passed against this contract.

### P15 test record

- `.venv/bin/pytest -q tests/hermes_cli/test_openhands_runtime.py tests/tools/test_task_center.py tests/tools/test_coding_delegate.py tests/tui_gateway/test_tasks_rpc.py` — 10 passed in 1.87s.
- `cd apps/desktop && npm run test:ui -- src/app/command-center/task-center.test.tsx` — 1 passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npx eslint src/app/command-center/task-center.tsx src/app/command-center/maintenance.tsx` — passed.
- `cd apps/desktop && npm run build` — Vite, Electron main/preload bundles,
  native staging, and `assert-dist-built` passed; existing toolchain warnings
  remain.
- Ruff, `py_compile`, and `git diff --check` passed on all P15 changed files.
- The real OpenHands doctor returned `ready=true`, `blockers=[]`; the real
  natural-language Hafiye fixture E2E and gateway Task Center RPC/event smoke
  both passed with external fixture `pytest -q` returning `1 passed`.

P15 acceptance passed. No new or different upstream regression was found.
The in-memory Task Center registry is intentionally the P15 bridge; P16 owns
durable generic task history and the complete Task Center product surface.

## P16 execution status — complete

The P16 implementation is recorded in source commit
`c72c94418` and the queued-state recovery fix plus real Desktop acceptance are
recorded in source/test commit
`f93d9183544581636c6af5b619d62d221040391d`. The commit identities remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `f93d9183544581636c6af5b619d62d221040391d`.

### Implemented and verified

- Task Center records now persist the master task model and safe history in
  `task_center.db` under the Hafiye XDG state root, with SQLite WAL and
  thread-safe writes shared by worker/gateway/UI paths.
- Completed, failed, and queued records survive a new gateway process. Only
  in-flight worker states (`PLANNING`, `RUNNING`, `WAITING`, `PAUSED`, and
  `CANCELLING`) are recovered as explicit failures after a restart; `QUEUED`
  work remains queued because no worker has started.
- The record and Desktop surface show current/queued/completed/failed states,
  current step, provider/model/route/privacy, tools, commands, modified files,
  subagent state, elapsed time, result/error, and real cancellation. No
  transcript or private chain-of-thought is persisted or displayed.
- A separate-process gateway RPC smoke returned persisted completed history
  and verified restart recovery with marker `P16_TASK_CENTER_RESTART_OK`.
- A real Electron + gateway E2E rendered all persisted state categories and
  cancelled the queued record through `tasks.cancel`; it passed 1/1.

### P16 test record

- `.venv/bin/pytest -q tests/hermes_cli/test_openhands_runtime.py tests/tools/test_task_center.py tests/tools/test_coding_delegate.py tests/tui_gateway/test_tasks_rpc.py` — 12 passed.
- `.venv/bin/pytest -q tests/tools/test_task_center.py tests/tui_gateway/test_tasks_rpc.py` — 6 passed.
- Separate-process gateway/RPC smoke — completed record survived, in-flight
  record became `FAILED / INTERRUPTED_BY_GATEWAY_RESTART`, queued behavior was
  preserved, and `P16_TASK_CENTER_RESTART_OK` was emitted.
- `cd apps/desktop && npm run test:ui -- src/app/command-center/task-center.test.tsx` — 1 passed.
- `cd apps/desktop && ../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` — passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npx eslint src/app/command-center/task-center.tsx src/app/command-center/maintenance.tsx` — passed.
- `cd apps/desktop && npm run build` — clean build stamp at `f93d91835445`,
  Vite/Electron bundles, native staging, and `assert-dist-built` passed;
  existing Vite/Babel/chunking warnings remain.
- `cd apps/desktop && npx playwright test e2e/p16-task-center.spec.ts --reporter=list` — real Electron plus real gateway, 1 passed in 9.2s.
- Ruff, `py_compile`, and `git diff --check` passed on P16 changes.

P16 acceptance passed. No new or different upstream regression was found.

## P17 execution status — complete

The P17 implementation and acceptance are recorded in source/test commit
`2dc541d09367b895744b512d99b058506d7f78d2`. The commit identities remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `2dc541d09367b895744b512d99b058506d7f78d2`.

### Implemented and verified

- Added the real Hafiye Control Center overlay route with every roadmap page:
  Overview, Chat, Tasks, Models, Providers, Routing, Voice, Computer,
  Browser, Coding, Memory, Skills, MCP, Automation, Permissions, Privacy,
  Logs, Developer, and About.
- Reused existing backend/state boundaries instead of adding a second config
  system: config-backed pages write through `ConfigSettings`, providers use
  the provider APIs, Skills/MCP use the capabilities APIs, Automation uses
  the persistent scheduler APIs, Logs use the gateway log API, and Tasks use
  the durable Task Center/RPC contract.
- Added the roadmap privacy enum (`NORMAL`, `LOCAL_ONLY`, `OFFLINE`) to the
  shared Desktop config control. No new dead switch or mock success state was
  added.
- Added a Settings entry and route classification for Control Center while
  preserving the existing Hermes Settings surface and deep links.

### P17 test record

- `cd apps/desktop && npm run test:ui -- src/app/control-center/index.test.tsx src/app/routes.test.ts` — 7 passed.
- `cd apps/desktop && npm run typecheck` — renderer, Electron, and E2E typechecks passed.
- `cd apps/desktop && npx eslint src/app/control-center/index.tsx src/app/settings/constants.ts e2e/p17-control-center.spec.ts` — passed.
- `cd apps/desktop && npm run build` — clean build stamp `2dc541d09367`, Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain.
- `cd apps/desktop && npx playwright test e2e/p17-control-center.spec.ts --reporter=list` — real Electron + real gateway, all 19 pages opened and Privacy Mode persisted across renderer reload; 1 passed in 12.7s.
- `git diff --check` — passed.

P17 acceptance passed. No new or different upstream regression was found.
P18 acceptance passed. No new or different upstream regression was found.

## P18 execution status — complete

The P18 implementation and acceptance are recorded in source/test commit
`fd17e6533894a568744b82454635a8e6bf02709b`. The commit identities remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `fd17e6533894a568744b82454635a8e6bf02709b`.

### Implemented and verified

- Reused Hermes cron job persistence, scheduler claims/execution ledger,
  recurring next-run updates, skills/toolset catalog, and MCP safety merge.
- Added validated per-job Hafiye `route` and `privacy_mode` fields to the
  existing cron persistence and profile-aware gateway REST boundary.
- Resolved a scheduled run's route slot before model/provider fail-fast and
  passed the effective provider/model/privacy/fallback policy into the real
  `AIAgent` construction. A per-job privacy override can only strengthen the
  installation/route policy.
- Added real Desktop cron-editor controls for Hafiye route slots, privacy
  mode, and the gateway toolset catalog. Custom toolsets persist as an
  explicit allowlist while Hermes' scheduler safety denylist remains active.
- Verified a real recurring local task through two scheduler ticks, with two
  completed execution-ledger records and recurring state preserved.

### P18 test record

- `.venv/bin/python -m pytest -q tests/cron/test_scheduler.py tests/cron/test_jobs.py tests/cron/test_p18_scheduler_acceptance.py` — 182 passed; two existing async resource warnings were emitted by the upstream scheduler/test harness.
- `.venv/bin/ruff check cron/jobs.py cron/scheduler.py hermes_cli/web_models.py hermes_cli/web_server.py tools/cronjob_tools.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/cron/test_p18_scheduler_acceptance.py` — All checks passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npm run test:ui -- src/app/cron/cron-job-model.test.ts` — 15 passed.
- `cd apps/desktop && npx eslint src/app/cron/index.tsx src/app/cron/cron-job-model.ts src/app/cron/cron-job-model.test.ts e2e/p18-scheduler.spec.ts` — passed.
- `cd apps/desktop && npm run build` — clean build stamp `fd17e6533894`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing npm/Vite/Babel/chunking warnings remain.
- `cd apps/desktop && npx playwright test e2e/p18-scheduler.spec.ts --reporter=list` — real Electron + real gateway created a job with Coding, Local only, and a custom toolset, then reloaded those values through Edit; 1 passed in 11.1s.
- `git diff --check` — passed before the source commit.

P18 acceptance passed. No new or different upstream regression was found.

## Exact next actions

1. Preserve the historical five-ID `ACCEPTED_UPSTREAM_BASELINE` whitelist and
   investigate any new or different failure in later phases.
2. Keep the pinned Hermes commit, baseline merge commit, and current Hafiye
   source/test commit `a87eaaba7373a2c23fa73b7ef498b64d67c989f5` separate in all
   subsequent state updates.
3. Begin P22 — CLI — against the accepted P21 backend/Desktop boundary; do not
   create a second configuration or business-logic path.

## P19 execution status — complete

The P19 implementation and acceptance are recorded in source/test commit
`0f45abb9c`. The commit identities remain separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `0f45abb9c`.

### Implemented and verified

- Reused Hermes prompt-injection, forced redaction, provider outage,
  checkpoint, corrupt-config, and exact-call loop-detector primitives.
- Added bounded llama-server recovery from saved state, whisper/Piper crash
  retry, structured computer-use failure codes, and a 200-action default task
  budget with atomic concurrent admission.
- Added `hafiye hardening doctor|prune` composition for audit/checkpoint
  retention, disk-space limits, and safe redacted diagnostics.

### P19 test record

- `.venv/bin/python -m pytest -q tests/agent/test_tool_guardrails.py tests/agent/test_stall_guards.py tests/tools/test_delegate_control_actions.py tests/hermes_cli/test_local_runtime.py tests/hermes_cli/test_voice_runtime.py tests/test_hafiye_computer_use.py tests/tools/test_hafiye_browser.py tests/test_hafiye_hardening.py` — 111 passed.
- `.venv/bin/python -m pytest -q tests/tools/test_browser_hardening.py tests/tools/test_hafiye_voice_runtime_hooks.py tests/hermes_cli/test_config.py tests/hermes_cli/test_dashboard_auth_audit.py` — 104 passed.
- `.venv/bin/ruff check` on all P19 source/test files and `git diff --check` — passed.
- `.venv/bin/hafiye hardening doctor`, `runtime doctor`, `voice doctor`, and
  `runtime server recover --attempts 1` — all real host checks passed; runtime
  recovery returned `runtime_already_ready` for the healthy server.
- Pinned computer-use-linux readiness — all required booleans true and
  `blockers=[]`.
- Exact five comparison command — `3 failed, 2 passed`; only historical IDs
  2, 3, and 5 failed, so the current comparison baseline was reduced to those
  three IDs. No new/different upstream failure was found.
- `./scripts/run_tests.sh` — 3,231 files; 37,218 passed, 16 failed, 244
  skipped in 847.8 seconds. The additional failures are documented in KI-034;
  the P19-focused and adjacent matrices passed.

P19 acceptance passed. P20 followed and is complete; P21 — First-run
Onboarding — followed and is now complete.

## P20 execution status — complete

The P20 implementation and acceptance are recorded in source/test commit
`964fc49b5f564f25588894374ea83e81cc2f58c7`. The commit identities remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `964fc49b5f564f25588894374ea83e81cc2f58c7`.

### Implemented and verified

- Added the Ubuntu/Debian outer package assembler at
  `scripts/build_deb.py`. It wraps the real Electron `linux-unpacked` tree
  with the backend source/lock metadata, stable launchers, user gateway unit,
  per-user root-broker activation path, XDG application/autostart entries,
  Hafiye icons, notices, and a package manifest.
- Added the stdlib-only `hafiye package doctor` and `hafiye package install`
  boundary. Dependency installation uses the copied lockfile and writes only
  to the user's Hafiye Python venv; managed model/voice/CUA runtimes remain
  first-run downloads.
- Made the root-broker sudo handoff use its absolute module file so a package
  install does not depend on sudo preserving `PYTHONPATH`.

### P20 test record

- `.venv/bin/python -m pytest -q tests/packaging/test_hafiye_deb.py tests/test_hafiye_rootd.py` — 10 passed.
- `.venv/bin/python -m pytest -q tests/test_packaging_metadata.py` — 7 passed.
- `.venv/bin/ruff check scripts/build_deb.py packaging/debian/dependency_doctor.py hafiye_rootd.py tests/packaging/test_hafiye_deb.py` — passed.
- `cd apps/desktop && npm run pack` — real Electron Linux unpacked build passed; clean build stamp `964fc49b5f56`; existing npm/Vite/Babel/chunking warnings remain.
- `.venv/bin/python scripts/build_deb.py --output dist/hafiye_0.20.5_amd64.deb --desktop-dir apps/desktop/release/linux-unpacked --json` — real `amd64` `.deb` built; final artifact is approximately 119 MB.
- Final artifact extract plus `hafiye package doctor --json` — `ok=true`,
  `blockers=[]`; manifest source is
  `964fc49b5f564f25588894374ea83e81cc2f58c7`, pinned upstream and baseline
  merge values are distinct and correct.
- Rootless `fakeroot dpkg --force-not-root --force-script-chrootless
  --force-depends --unpack/--configure` of the final artifact — passed. The
  temporary dpkg database reports expected unmet host-package dependencies;
  this does not change the package maintainer-script result.
- Exact five-ID upstream comparison after P20 — `3 failed, 2 passed`; only
  historical IDs 2, 3, and 5 failed. No new/different regression was found.

P20 acceptance passed. P21 — First-run Onboarding — followed and is now
complete. A privileged install on the live host was deliberately not
run by the build validation because it would mutate `/usr` and require an
interactive sudo password; the rootless Debian install path and extracted
package doctor are the recorded acceptance evidence.

## P21 execution status — complete

The P21 implementation is recorded in source/test commits `48860ee5f` and
`a87eaaba7373a2c23fa73b7ef498b64d67c989f5`. The commit identities remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `a87eaaba7373a2c23fa73b7ef498b64d67c989f5`.

### Implemented

- Added the exact 20-step onboarding state machine from the master roadmap,
  persisted atomically under the XDG Hafiye state root with owner-only
  permissions.
- Added the authenticated onboarding REST boundary for environment,
  computer-use, local runtime/model, voice runtime, autostart, and final doctor
  operations. Existing Hafiye config/runtime boundaries remain authoritative;
  onboarding does not create a second configuration system.
- Added the real packaged-install Desktop wizard with compute selection,
  local GGUF import/download, local server/model assignment, optional provider
  skips, microphone selection, STT/TTS/wake-word/Hafiye tests, execution
  policy, autostart, and final doctor controls.
- Corrected normal-XDG systemd unit generation so the user service does not
  force a stale `HERMES_HOME`; explicit profile/environment overrides remain
  supported. Package launchers propagate `HAFIYE_PACKAGE_ROOT` for packaged
  onboarding detection.

### Verified

- `.venv/bin/pytest -q tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_hafiye_onboarding_api.py tests/test_hafiye_onboarding.py tests/packaging/test_hafiye_deb.py tests/test_packaging_metadata.py tests/test_hafiye_rootd.py` — 30 passed.
- `.venv/bin/ruff check` on the P21 Python source/tests, `py_compile`, and
  `git diff --check` — passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npm run test:ui -- src/components/hafiye-onboarding/index.test.tsx` — 3 passed.
- `cd apps/desktop && npx playwright test e2e/hafiye-onboarding.spec.ts --workers=1 --reporter=list` — real Electron plus real isolated Hermes backend, 1 passed in 8.3s. The flow verified Welcome → Environment → computer-use doctor → Compute.
- Real packaged Electron replay using
  `apps/desktop/release/linux-unpacked/hafiye-desktop` and the live authenticated
  gateway — `PACKAGED_ONBOARDING_RESULT PASS 20/20`; all roadmap headings from
  Welcome through final doctor were reached, including real microphone/STT,
  Piper/TTS, wake-word choice, Hafiye request, autostart, and final doctor; the
  wizard disappeared after completion.
- Current `npm run pack` and `.venv/bin/python scripts/build_deb.py --output dist/hafiye_0.20.5_amd64.deb --desktop-dir apps/desktop/release/linux-unpacked --json` — real Electron input and `amd64` package built from source/test HEAD `a87eaaba7373a2c23fa73b7ef498b64d67c989f5`.
- Extracted current package backend — package doctor and authenticated onboarding doctor returned `ok=true`, `blockers=[]`; computer readiness, local model server, voice stack, and user autostart were all ready.
- Live `hafiye-gateway.service` after the XDG unit fix — authenticated
  `/api/hafiye/onboarding/doctor` returned `ok=true`, `blockers=[]`,
  `computer_ready=true`, `local_server_ready=true`, `voice_ok=true`, and
  `autostart_enabled=true`.
- Exact five-ID upstream comparison after P21 — `3 failed, 2 passed`; only
  accepted historical IDs 2, 3, and 5 failed. IDs 1 and 4 passed, so no new or
  different upstream regression was found.

### Acceptance closure

- [x] Replay all 20 roadmap steps through the real packaged Desktop GUI on the
      real host. The final state contains all 20 completed step IDs and
      `completed=true`.
- [x] Restore the normal user-manager environment after the acceptance gate,
      restart `hafiye-gateway.service`, restart the managed CUDA local server,
      and re-run the authenticated final doctor.

P21 acceptance passed. The final live doctor returned `ok=true`,
`blockers=[]`, `computer_ready=true`, `local_server_ready=true`, `voice_ok=true`,
and `autostart_enabled=true`.

## P22 execution status — complete

The P22 source/test commit is `e031162fd`. The commit identities remain
separate:

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit: `e031162fd`.

### Implemented and verified

- Added `hermes_cli/hafiye_cli.py` as a thin product vocabulary adapter. It
  reuses the existing one-shot agent, persistent gateway service, local
  runtime, provider catalog, Hafiye route/privacy policy, durable Task Center,
  and computer-use-linux doctor; it does not add a second backend or config.
- Exposed the P22 product commands and nested actions: `ask`,
  `start|stop|restart`, `models`, `model load|unload`, `providers`, `routing`,
  `privacy`, `tasks`, `task show|cancel`, and `computer doctor`. Existing
  `status`, `doctor`, `voice`, `root`, `memory`, `skills`, `mcp`, and `logs`
  surfaces remain available. `projects` and `automation` are aliases for the
  existing project and scheduler implementations.
- Preserved the normal gateway route-slot authority while allowing explicit
  one-shot CLI provider/model arguments to override an onboarding-populated
  default slot. The explicit path is covered by a policy regression test.

### P22 test and real-host record

- `.venv/bin/pytest -q tests/hermes_cli/test_hafiye_cli.py tests/test_hafiye_policy.py tests/gateway/test_hafiye_routing.py tests/hermes_cli/test_cron_parser_builder.py tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_projects_cli.py` — 32 passed, 1 warning.
- `.venv/bin/ruff check` on all changed P22 Python source/tests — passed.
- `.venv/bin/python -m py_compile` on all changed P22 Python source/tests —
  passed; `git diff --check` — passed.
- `.venv/bin/hafiye --help`, nested command help, parser smoke, and read-only
  `models/providers/routing/privacy/tasks/computer/projects/automation/root`
  commands — passed. Computer doctor returned all four required readiness
  booleans true and `blockers=[]`.
- `.venv/bin/hafiye restart` followed by `systemctl --user is-active` and
  `is-enabled hafiye-gateway.service` — active and enabled.
- `.venv/bin/hafiye model unload --json` — stopped the managed server;
  `.venv/bin/hafiye model load qwen2.5-0.5b-instruct-q4 --backend AUTO --json`
  — `running=true`, `ready=true`, `selected_backend=CUDA`.
- `timeout 120 .venv/bin/hafiye ask --safe-mode --model
  gemini-flash-lite-latest --provider gemini 'Reply with exactly
  P22_GEMINI_CLI_OK and nothing else.'` — exit 0 and exact marker returned.
- `.venv/bin/hafiye ask --model qwen2.5-0.5b-instruct-q4 --provider custom
  'Reply with exactly P22_CLI_OK'` — rejected by the existing Hermes 64K
  minimum against the small fixture's 4,096-token context; recorded under
  KI-014 and not treated as a P22 product regression.
- Exact five-ID upstream comparison after P22 — `3 failed, 2 passed`; IDs 2,
  3, and 5 failed exactly as in the accepted baseline, while IDs 1 and 4
  passed. No new or different failure was observed.

### Exact P22 baseline command

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q \
  tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip \
  tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries \
  'tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]' \
  tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning \
  tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics
```

Result: `3 failed, 2 passed`; this is the unchanged
`ACCEPTED_UPSTREAM_BASELINE`, not a P22 blocker. P23 — Final E2E Suite — is
now the first incomplete phase; its required real-machine checks are not yet
claimed as passed.

## P23 execution status — in progress

### Source and route-boundary fix

- Pinned Hermes upstream commit:
  `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Current Hafiye source/test commit:
  `5af73434e5ab36786a306966fa926b7cbbe08914`.
- The native gateway now uses the normal Hafiye XDG config root while
  retaining explicit `HERMES_HOME`/profile single-root behavior. The
  Electron/TUI `_make_agent` boundary now resolves the same Hafiye route slot,
  privacy mode, and fallback metadata before creating `AIAgent`. No Hermes
  upstream commit or upstream history changed. The same source/test commit
  adds a narrowly scoped Qwen2 context compatibility argument builder: above
  32K it passes YaRN scaling from 32K and an explicit Qwen2 context metadata
  override; other model families retain native metadata behavior.

### P23 verification completed so far

- The P23 backend target matrix completed with `251 passed, 2 skipped, 1
  warning in 22.66s`, including the managed local-runtime compatibility test.
- `.venv/bin/ruff check` on the route/config source and tests, Python
  compilation, and `git diff --check` passed.
- The exact five-ID upstream comparison after this source change returned
  `3 failed, 2 passed`: IDs 2, 3, and 5 failed, IDs 1 and 4 passed. This is
  exactly the accepted upstream baseline; no new or different failure was
  found.
- The real packaged Electron Composer path was launched from
  `apps/desktop/release/linux-unpacked/hafiye-desktop`. With the default
  route temporarily forced to `gemini-flash-lite-latest`, entering
  `Firefox'u aç.` produced the real transcript `Firefox tarayıcısı açıldı.`
  and a Firefox window was observed. A later Gemini request in the same turn
  returned HTTP 429 `RESOURCE_EXHAUSTED` (free-tier quota), so this is not a
  clean P23.2/P23.6 acceptance result; it is recorded as KI-037.
- After that live check, the configured default route was restored to
  `custom`/`qwen2.5-0.5b-instruct-q4`; `hafiye-gateway.service` was restarted
  and verified `active` and `enabled`. `hafiye runtime doctor` returned
  `ok=true`, `blockers=[]`, and `selected_backend=CUDA` on the RTX 3080 host.
- The live computer-use-linux `windows` query returned exit 0 and enumerated
  Firefox and Hafiye windows. The required readiness doctor remains green.
- A real `hafiye restart` followed by a fresh launch of the packaged
  `release/linux-unpacked/hafiye-desktop` reached the Hafiye title and visible
  Composer (`P23_BOOT_COMPOSER_READY Hafiye`). This covers restart-to-Desktop
  boot recovery, but not yet a full reboot/login replay.
- A direct request to the real local llama.cpp OpenAI-compatible endpoint
  returned the exact marker `P23_LOCAL_ENDPOINT_OK`. This confirms the local
  CUDA endpoint remains usable, but it is not being counted as the required
  disconnected-network Hafiye-agent test.
- An initial Qwen load with `--context-size 65536` did not remove KI-014:
  without the family-specific compatibility flags, llama.cpp capped the model
  at `n_ctx=32768` because its trained context is 32K, and real `hafiye ask`
  rejected it below Hermes' 64K minimum.
- Two pinned compatible-model probes were attempted and rolled back: the
  3B Hermes Q4_K_M model hit a 7,168 MiB CUDA KV-cache OOM at 65K, while the
  1B Llama Q4_K_M model fit at 65K but generated 39,822 tokens without
  completing a simple marker request. Both temporary registry entries/files
  were removed; KI-040 records these historical diagnostics.
- The new managed Qwen2 path was loaded with:
  `.venv/bin/hafiye model unload --json && .venv/bin/hafiye model load
  qwen2.5-0.5b-instruct-q4 --backend AUTO --context-size 65536 --json`.
  The live server reported `n_ctx=65536`, `n_ctx_train=65536`, `ready=true`,
  and `selected_backend=CUDA`. A direct AIAgent session made a real terminal
  tool call and returned `P23_QWEN64_TERMINAL_OK`. A real packaged Desktop
  Electron session then rendered an actual tool block for `/bin/printf
  P23_DESKTOP_DOM_OK`, with exit code 0 and the exact marker in the DOM. This
  is fresh local-route evidence; disconnected-network replay is still open.
- The official Qwen3-14B Q4_K_M candidate was downloaded through the managed
  Hafiye model boundary from `Qwen/Qwen3-14B-GGUF` revision
  `530227a7d994db8eca5ab5ced2fb692b614357fd`. The registered file is
  `/home/tolga/.local/share/hafiye/models/qwen3-14b-q4_k_m.gguf`,
  `9001752960` bytes, SHA-256
  `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`.
  The model remains registered for acceptance work but is not the default
  route; Qwen2 was restored after the probe.
- Managed Qwen3 startup now uses the official embedded Jinja template and
  DeepSeek reasoning parser, and for a requested 65,536-token context uses
  YaRN from the model's 40,960-token native context, an explicit
  `qwen3.context_length` override, fit-aware `-ngl auto`, and CPU KV storage.
  Full-GPU 65K and 4K fit probes were CUDA-OOM diagnostics; the managed
  compatibility command reached `n_ctx=65536`, `n_ctx_train=65536`, and
  `ready=true` on CUDA.
- A direct Qwen3 parser probe produced a real `tool_calls` response for
  `open_application`. A real Hafiye `AIAgent` run with the managed
  `hafiye-computer-use-linux` toolset then completed
  `tool_search → tool_describe → list_windows → activate_window` against the
  live Firefox window and ended with
  `text_response(finish_reason=stop)`, `api_calls=4`. This is candidate-model
  evidence, not a claim that all P23 local/offline workflows pass.
- The Qwen3 65K probe measured approximately 8.7 GiB VRAM used on the 10 GiB
  RTX 3080, about 10.9 GiB server RSS on a 14 GiB host, and swap pressure. The
  full P23 Qwen3 qualification and remaining real-machine checks are deferred
  per the user's explicit instruction and remain listed in the roadmap-end
  reminder.
- A real isolated file-organizing fixture was attempted through the same local
  AIAgent with `terminal` and `file` toolsets. The Qwen2 validation fixture did
  not complete the prescribed multi-step sequence: one run only created the
  directories and another returned without a tool call; the source files were
  not moved. This remains the local-Qwen warning in KI-041; the successful
  single-command terminal evidence above is not being generalized to
  multi-step local-Qwen file behavior.
- A follow-up isolated file fixture was run through the authenticated Gemini
  route with `.venv/bin/hafiye ask --provider gemini --model
  gemini-flash-lite-latest --toolsets terminal,file`. The real tool sequence
  created `organized/text` and `organized/media`, moved `notes.txt` and
  `photo.jpg`, left `incoming/keep.bin` in place, and verified the final paths
  before returning `P23_FILES_GEMINI_OK`. This is fresh acceptance evidence for
  master item 23.8; KI-041 retains the local-Qwen model-specific warning.
- A packaged Desktop replay against the managed local Qwen2 route with the
  exact P23.2 prompt `Firefox'u aç.` reached a ready Composer but returned the
  wrong text `Merhaba, FireFox'a açın!` without a computer-use call or observed
  Firefox task result. It is recorded as KI-042; local single-command terminal
  success does not establish natural-language desktop execution.
- The newly supplied Gemini credential was stored through the Hafiye Linux
  Secret Service boundary; no plaintext copy was written to the repository or
  normal config store. Explicit Gemini one-shot returned
  `P23_GEMINI_NEW_KEY_OK`. The packaged Composer, with the exact `Firefox'u
  aç.` prompt, reported `Firefox açıldı.` and opened Firefox, but then attempted
  an unapproved `sudo chown` remediation and stopped at the password dialog.
  No password was supplied, no privileged command completed, and the route was
  restored to local custom/Qwen. KI-043 records why this is not a clean final
  P23.2/P23.6 acceptance.
- Fresh supporting rechecks passed: the real project alias/session test
  returned `1 passed in 1.36s`; `hafiye runtime openhands doctor` returned
  `ready=true` with `blockers=[]` for OpenHands SDK `1.41.0`; `hafiye root exec
  id -u` returned `0`; and `hafiye voice doctor` returned `ok=true`,
  `blockers=[]`, Piper ready, Whisper ready, and AUTO selecting CUDA. These
  are supporting 23.3/23.11–23.13 evidence; the exact voice and emergency
  sequences remain open.
- A fresh Gemini-backed P23.13 OpenHands fixture was executed through
  `.venv/bin/hafiye ask --provider gemini --model gemini-flash-lite-latest
  --toolsets coding`. Hafiye invoked `coding_delegate` on a temporary local
  repository; the Task Center record reached `COMPLETED` on the `coding` route
  with 28 progress events and real terminal/file-editor tool history. The
  delegate changed `bug.py`, and an independent external `.venv/bin/python -m
  pytest -q` returned `1 passed in 0.00s`.
- An isolated Gemini natural-language Desktop replay for the P23.9 VS Code
  task returned `Explored 2 files` and the requested marker without opening a
  VS Code window; KI-044 records this model/tool-selection warning. The actual
  P23.9 acceptance then ran through Hafiye's managed
  `computer-use-linux` MCP boundary: two real VS Code windows were opened,
  focus switched first→second→first, a real mouse click and keyboard
  Ctrl+A/type/Ctrl+S sequence were sent, the fixture file contained
  `P23_DESKTOP_TARGET`, and the final managed screenshot showed the marker in
  VS Code. The temporary fixture windows were closed afterward.
- A real authenticated `source=desktop` gateway WebSocket session completed a
  local-Qwen prompt, `systemctl --user restart hafiye-gateway.service` was
  executed, the same durable session was reopened with `session.resume`, and a
  second prompt completed. The service returned `active`; the exact harness
  result was `P23_RESTART_RECONNECT_OK`. This is fresh 23.16 acceptance
  evidence.
- A real authenticated desktop session received the physical
  `Ctrl+Super+Escape` chord through the GNOME fallback and reported the
  emergency state paused, then resumed successfully. The model selected the
  `terminal` tool instead of a managed desktop action, so the required
  long-running desktop-task stop sequence is not claimed as passed; KI-045
  records this validation warning.
- A follow-up real local-Qwen probe using `.venv/bin/hafiye ask --toolsets
  computer_use` exited without producing a `computer_use` tool event, so no
  chord was sent and no P23.15 acceptance was claimed. This is retained as
  the same model/tool-selection warning, not a Hafiye source regression.
- The real P23.7 fail-closed check temporarily selected the configured Gemini
  route, set global `LOCAL_ONLY`, and ran `.venv/bin/hafiye ask` without an
  explicit provider/model. It exited 1 with `Hafiye LOCAL_ONLY policy blocked
  provider 'gemini'` before a provider call. Privacy was restored to `NORMAL`
  and the default route to custom/Qwen; `hafiye routing --json` confirmed the
  restored state.
- A fresh root-broker check returned UID `0`; the corresponding live gateway
  process remained EUID `1000` while `hafiye-rootd` was EUID `0`.
- The live computer doctor also observed a separate root-owned `ydotoold` on
  `/run/user/0/.ydotool_socket` in addition to the healthy user daemon on
  `/run/user/1000/.ydotool_socket`. They use different sockets and readiness
  stayed green; this host diagnostic is recorded as KI-039 and was not altered.
- The structured browser route navigated a local page successfully. The native
  Firefox route then targeted an exact existing Wayland window, navigated it to
  a local fixture, and returned successful activation/key/type/navigation
  steps. The real native screenshot showed the fixture title and
  `P23_NATIVE_BROWSER_OK`; the window was then restored to its prior Kick tab.
  Firefox still exposes only a root AT-SPI node in this host path, so KI-022 is
  retained as a diagnostic even though the required P23.10 UI task passed.

### P23 final acceptance ledger

The following are deliberately not marked passed merely because earlier phase
tests exist. The master roadmap requires the final real-machine sequence.

| Master item | Current evidence | Final status |
|---|---|---|
| 23.1 Boot | Packaged Desktop reached Composer after a real gateway restart; a fresh reboot/login replay is not recorded | PARTIAL / REBOOT REQUIRED |
| 23.2 Text | Rotated-key Gemini Composer opened Firefox, then attempted unapproved sudo remediation; local Qwen2 still failed tool execution (KI-042/KI-043) | TARGET PASSED / SAFETY WARNING |
| 23.3 Voice | P11/P12 real microphone, STT, TTS, and wake evidence exists; exact P23 spoken command is not replayed here | NOT FINAL-CHECKED |
| 23.4 Local inference | Managed Qwen2 compatibility path reports 65,536 context; direct AIAgent and packaged Desktop terminal markers passed | PASS FOR LOCAL ROUTE / OFFLINE REPLAY REQUIRED |
| 23.5 Remote inference | P5/P6 remote endpoint coverage exists; exact P23 forced-route replay is not recorded here | NOT FINAL-CHECKED |
| 23.6 Gemini | Rotated-key explicit one-shot passed; Composer reached Firefox but the same turn hit KI-043 sudo approval dialog | PASS WITH SAFETY WARNING |
| 23.7 Privacy | Real Gemini-configured route under global `LOCAL_ONLY` exited before provider call with the policy-block message; settings restored | PASS / FAIL-CLOSED |
| 23.8 Files | Authenticated Gemini fixture replay performed and verified the required moves and final paths; KI-041 retains the earlier local-Qwen warning | PASS / GEMINI ROUTE |
| 23.9 Desktop | Managed computer-use-linux MCP opened two real VS Code windows, switched focus, sent mouse/keyboard input, saved the marker, and visually verified the final UI | PASS / KI-044 MODEL WARNING |
| 23.10 Browser | Structured local navigation passed; native managed route navigated a real Wayland Firefox window, screenshot verified the fixture title/marker, and the original tab was restored | PASS / KI-022 AT-SPI DIAGNOSTIC |
| 23.11 Root | Fresh `hafiye root exec id -u` returned 0; gateway EUID 1000 and rootd EUID 0 | PASS / FRESH RECHECK |
| 23.12 Memory | Fresh `test_project_alias_and_session_context_survive_fresh_process` returned `1 passed in 1.36s` | PASS / FRESH PROCESS |
| 23.13 OpenHands | Fresh managed doctor plus Gemini-backed `coding_delegate` fixture; Task Center `COMPLETED`, 28 progress events, `bug.py` changed, independent `pytest -q` returned `1 passed` | PASS |
| 23.14 Barge-in | P13 real stop evidence remains green; exact final phrase is not replayed here | INHERITED / RECHECK |
| 23.15 Emergency shortcut | Real `Ctrl+Super+Escape` reached the GNOME fallback, paused the emergency state, and `emergency.resume` restored it; the model selected `terminal` instead of a long-running managed desktop action | PARTIAL / KI-045 |
| 23.16 Restart recovery | Authenticated desktop session completed before restart; service restarted; same durable session resumed; post-restart prompt completed; service remained active; marker `P23_RESTART_RECONNECT_OK` | PASS / REAL SESSION RESUME |

### Exact next actions

1. Defer the remaining real-machine P23 checks by explicit user instruction;
   do not mark them passed or create a P23 completion commit.
2. At the end of the roadmap, return to the deferred checklist in
   `ROADMAP.md`: P23.1, clean P23.2/P23.6 Gemini Composer behavior, P23.3
   voice, P23.4 offline, P23.5 remote endpoint, P23.14 barge-in, and the
   long-running managed desktop portion of P23.15. Also requalify the Qwen3
   candidate across the full local/offline workflow and resource envelope.
3. The current master roadmap defines no P24 phase. Do not invent one while
   treating the deferred P23 acceptance as complete; the roadmap-end reminder
   is the next recorded action.
