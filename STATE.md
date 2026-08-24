# Hafiye State

Last updated: 2026-08-24

## Repository and commit state

- Branch: hafiye/p0
- origin: https://github.com/tolgaakcaoglu/hafiye.git
- upstream: https://github.com/NousResearch/hermes-agent.git
- Pinned upstream commit: f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit: 2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye source HEAD: 6d3672e498e1bcb9316e5c7d88c9fc896714630c
  (P9 managed computer-use-linux MCP integration; source commit)

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

P9 — Linux computer use: complete. P10 — Browser is the next incomplete
phase.

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

## Regression status

The P7 full backend comparison covered 3,219 files and reported 37,160 passed,
7 failed, and 244 skipped in 598.3 seconds. Four failures are members of the
current `ACCEPTED_UPSTREAM_BASELINE`: Hermes state FTS, execution-flag
detection, Termux audio detection, and Vercel doctor diagnostics. The two
cold-start failures passed 2/2 when the persistent Hafiye service was stopped
and are the existing KI-016 topology diagnostic. The browser reconnect test
is the existing KI-019 scheduling diagnostic; it passed on an immediate
isolated retry. No new Hafiye regression was found.

The P5 targeted Python matrix now passes 468 tests, alongside the Desktop
provider tests/typecheck/build, real Secret Service round-trip, local CUDA
endpoint, remote OpenAI-compatible path, live Gemini model listing, and live
Gemini one-shot. P6 targeted policy/gateway/agent tests and Desktop settings
validation pass.

P8 targeted broker, packaging, startup-registry, emergency-stop, lint, and
compile checks pass. The real system service is active/enabled, the non-root
broker smoke passed, malformed and unauthorized clients failed closed, and
audit records were read through the broker without exposing raw command text.
The accepted five-ID upstream whitelist and current four-ID comparison baseline
are unchanged; no new P8 regression was found in the affected CLI/packaging
matrix.

P9 targeted computer-use/MCP tests passed (258 tests), the full Desktop UI
suite passed (579 files, 5,548 tests), the Desktop typecheck and clean
production build passed, and the real Wayland/GNOME acceptance flow passed.
The only observations were Firefox's AT-SPI focus warning (KI-022) and the
sparse VS Code accessibility tree (KI-023); neither is a P9 blocker and both
are documented.

## Active blockers

P5, P6, P7, P8, and P9 have no open acceptance blockers. The user service and
`hafiye-rootd.service` are active
and the local CUDA runtime doctor is green. `loginctl` reports `Linger=no`,
and a full reboot was not performed; GNOME's `Super+Shift+Space` conflict
remains the existing operational warning. The initial development-v-env
systemd `-m hafiye_rootd` entrypoint failure was corrected by using the
packaged source entrypoint and is recorded as resolved KI-021.

The accepted upstream failures, KI-019 browser scheduling diagnostic, KI-022
Firefox focus warning, KI-023 VS Code accessibility warning, npm audit
warnings, missing pactl, missing vulkaninfo, and optional-extra packaging
warnings are documented diagnostics. They are not silently treated as passes.

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

## ACCEPTED_UPSTREAM_BASELINE

The original five upstream failures were accepted before Hafiye source
changes. The exact five IDs remain the historical accepted regression
whitelist. The current post-P5 comparison baseline is the four IDs that
reproduced:

1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

The accepted remote browser-control ID (item 1) did not reproduce in the latest
run, so the current baseline was reduced to items 2–5. The separate local
reconnect scheduling failure is documented in KI-019 and is not added to the
historical whitelist. Future failures within the historical five are classified
against that upstream whitelist; any new or different ID is a regression to
investigate. The upstream bugs are not being fixed by Hafiye.

## Exact next actions

1. Keep the verified P9 source commit
   `6d3672e498e1bcb9316e5c7d88c9fc896714630c` separate from the pinned
   upstream and baseline merge SHAs.
2. Keep the historical five-ID `ACCEPTED_UPSTREAM_BASELINE` whitelist and the
   current four-ID comparison baseline for future phases; reduce the current
   baseline again if failures disappear, and investigate any new/different ID.
3. Start P10 — Browser. Preserve the P8 root-broker boundary: the main Hafiye
   process remains non-root and only explicitly privileged operations cross
   the local `hafiye-rootd` socket. Keep the P9 managed MCP provider enabled
   while wiring browser routing.

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
P5's live Gemini credential was saved to Linux Secret Service and hydrated from
the canonical Hafiye config root; no plaintext credential was added to the
repository or configuration. The provider lifecycle/XDG fix is source commit
`45294d3f77a3929731ac29d89d54f5d53c70957d`.

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
