# Hafiye State

Last updated: 2026-08-27

## Repository and commit state

- Branch: main (local integration branch; tracks origin/main)
- origin: https://github.com/tolgaakcaoglu/hafiye.git
- upstream: https://github.com/NousResearch/hermes-agent.git
- Pinned upstream commit: f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit: 2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye source HEAD: 9f315f6a6b20d7f37e5a933b6f810c3b8ef975e0
  (The loaded Model page and managed Local GGUF Runtime/catalog surface use
  the active Desktop locale; the Turkish package is installed and visually
  verified.)
  Earlier source identities remain recorded below.
- Current repository/documentation closure HEAD:
  `baf0a3d2203b4580d25546d4e979bef7f1712b12` (substantive documentation
  closure; this metadata pointer is kept separate from the source HEAD).
- Earlier documentation closure HEAD:
  `e460e672d542ab866a2be258092529515cdd8ed4`; documentation commits do not
  change the Hafiye source checkpoint or installed package source.

The three SHA values above are intentionally separate: the first is the
upstream source pin, the second is the history-preserving baseline merge, and
the third is the current Hafiye product source commit. Documentation closure
commits after the source commit do not change the product source pin.

## Current phase

P0 — Fork, pin, verify environment: complete.

P1 — Hafiye external identity and data root: complete.

P2 — Persistent gateway + Desktop connection: complete.

P3 — Hafiye Composer + tray + autostart: complete with host warning KI-012;
KI-013 is resolved by the P23.1 packaging fix and real reboot/login replay.

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
upstream-baseline comparison are recorded below. P23 — Final E2E Suite —
remains open, with P23.4 explicitly user-deferred. The user explicitly
authorized P24 while P23 remains open; the isolated Qwen3-14B local-agent
qualification subtask is complete with a measured host resource warning.
Unaccepted P23 rows remain open and must not be represented as passed.

P24 — Hafiye Jarvis experience convergence: source implementation and
automated verification are complete at `139f5f949`, but the phase remains open
for installed real-machine acceptance. The user explicitly added this binding
phase on 2026-08-27 to make the installed product operate as one assistant
loop: login auto-arm, “Hafiye” wake, visible Composer, visible Turkish
transcript, short spoken acknowledgement, real tool execution and
verification, concise completion, then clean wake re-arm. P24 reuses the
fixed architecture and does not create a second agent/runtime.

Current active checkpoint (2026-08-27): the active Gemini credential is
correctly hydrated from Linux Secret Service and model discovery succeeds, but
fresh generation is rejected by the provider with HTTP 429
`RESOURCE_EXHAUSTED` / `prepayment credits are depleted` (KI-059). The
installed packaged Desktop has also completed a real Qwen3-14B Composer
tool-path smoke through the local CUDA runtime; the tool result and independent
file verification are recorded below, but the bounded capture did not reach a
stable final assistant response, so no P24 acceptance row is promoted.

The installed package is `hafiye 0.20.5-1` and its
`/usr/lib/hafiye/package-manifest.json` now carries source
`53e783e8c8ee6c88b2ecff2cff4954512deb386a`, the pinned upstream commit, and
the baseline merge commit. The package was rebuilt and reinstalled through the
existing `hafiye-rootd` boundary; the selected-route endpoint, emergency
binding, and packaged managed-STT module-path fixes are now in the installed
package. The live Desktop process remains under
`/usr/lib/hafiye/desktop`, the user autostart entry targets that installed
binary, `hafiye-gateway.service` is enabled/active, and the health endpoint
returns `ok=true`. P24 implementation and automated checks pass; P24.14 is
not yet accepted because physical wake/microphone/barge-in/emergency actions,
the real coding scenario, clean browser-task completion, and the user's
deferred offline replay still require final real-machine evidence. A new
installed Gemini coding replay resolved `randevu`, ran its real `tests/run.php`
suite (`165 passed, 0 failed`) and searched for TODO/bug markers without
changing the user's dirty worktree; it found no concrete defect to delegate to
OpenHands, so P24.9 remains open. A new clean-session Gemini 3.5 browser replay
created the real provider client and ran `web_search`, but its first provider
call took 131.8 seconds and the turn was stopped before native browser work;
P24.10 remains open.

The KI-043 source-level privileged-command boundary is now resolved: normal
terminal escalation attempts route through `hafiye-rootd`, READ_ONLY and
confirmation policies remain enforced, and the normal route is not changed.
The clean Gemini Composer file-task replay still passes P23.6. The exact
`Firefox'u aç.` replay remains unaccepted because Gemini performed unrelated
privileged package remediation. The pre-patch installed Qwen3 browser replay
ended without a verified video result. The replacement package is now
installed and its native browser focus-recovery path has been exercised. A
Gemini 3.5 replay reached the correct latest-video state, but the model then
continued into unnecessary file/search tooling and did not close as a clean
Composer task; P24 browser acceptance therefore remains open. The Qwen3-14B
Randevu replay resolved the project and ran real read-only inspection, but
timed out before an evidence-backed diagnosis/OpenHands verification. Neither
P24 coding nor P24 YouTube acceptance is claimed.

The source-level local-first route defect found during P24 was fixed in
`10bd0b8f32b99b9a7ad91317dfb2f88b5204b927`: when the selected Hafiye slot
uses `custom/qwen3-4b` while the global model still points at Gemini, route
policy now resolves the matching custom-provider endpoint (including an
absolute `.gguf` catalog key) instead of reusing the stale Gemini URL. The
fix is covered by policy and native-gateway regression tests and has passed a
real source CLI run in `LOCAL_ONLY`: Qwen3-4B on CUDA executed `terminal`,
verified `P24_LOCAL_ONLY_QWEN3_OK`, and exited 0. The live route was restored
to `gemini/gemini-3.1-flash-lite` with `NORMAL` privacy afterward. The same
installed `/usr/bin/hafiye` path later completed
`P24_INSTALLED_LOCAL_ROUTE_OK` through the loopback Qwen3-4B/CUDA server under
`LOCAL_ONLY`, then restored Gemini/NORMAL again. The subsequent browser
failure-classification hardening is in source commit `2a56c25e`; its rebuilt
package is installed and the installed native-browser recovery tests pass.

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
- The local GGUF registry exposes evidence-backed capability metadata: the
  Qwen2.5-0.5B validation fixture is `validation=true, agent=false`; Qwen3-14B
  is `agent=true, tool_calling=true, validation=false` with
  `resource_warning=KI-046`. The current test route is
  `gemini/gemini-3.1-flash-lite`; Qwen3 is selectable and not default.
- The selected-route endpoint fix is source-verified: a custom route matched
  its configured loopback provider by model/GGUF identity even while the
  global model URL was Gemini; the real `LOCAL_ONLY` Qwen3-4B agent call
  returned `P24_LOCAL_ONLY_QWEN3_OK` through `terminal`, with no cloud route.
- The Desktop Models settings page now exposes the existing managed
  `/api/local-runtime/models/download` contract: a Hugging Face repo, GGUF
  filename, optional model id/revision/SHA-256, and a Download GGUF action.
  A successful download is registered in the private llama.cpp model
  registry and becomes selectable for Load / start.
- The backend-owned Desktop/onboarding catalog now also exposes the exact
  `orcarouter/Qwen3.8-27B-Uncensored:q4_K_M` text/tool GGUF layer and the
  gated two-shard `orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF` IQ2_M
  security-research model. Ollama is an acquisition source only; inference
  remains Hafiye-managed llama.cpp. Both entries are `qualification=pending`,
  non-default, integrity-pinned, and carry current-host resource warnings.
- KI-043 source hardening is present at the shared terminal boundary. Direct,
  absolute, env/command-wrapped, quoted, shell-wrapped, and chained
  escalation binaries are not executed by the normal terminal; FULL_AUTONOMOUS
  uses `hafiye-rootd`, while READ_ONLY and confirmation policies retain their
  existing semantics.
- Native gateway and Electron/TUI Desktop agent creation now read the normal
  Hafiye XDG config root and apply the same route-slot/privacy policy before
  constructing `AIAgent`. The change is covered by native-gateway and
  Desktop-agent tests. A real packaged Composer run with the default route
  temporarily forced to Gemini executed the Firefox operation; the turn then
  received a Gemini free-tier HTTP 429 and remains a P23 warning, not a clean
  final acceptance.
- The active Gemini credential was revalidated on 2026-08-27 through the real
  Linux Secret Service: both configured aliases resolved to the same value and
  a direct `generateContent` probe for `gemini-3.1-flash-lite` returned HTTP
  200 with `GEMINI_KEY_OK`; `.venv/bin/hafiye ask --safe-mode` on the same
  route returned `HAFIYE_ACTIVE_GEMINI_KEY_OK`. Temporary real packaged
  Composer replays with `gemini-3.5-flash` also created the Gemini client and
  executed native browser calls; the credential is not the current P24
  blocker. The route was restored to `gemini-3.1-flash-lite` after the
  comparison.
- A second credential recheck used the same profile-scoped Secret Service
  references: both aliases resolved to the same non-empty value, the direct
  `gemini-3.1-flash-lite` `generateContent` probe returned HTTP 200 with the
  expected marker, and the real Hafiye CLI returned
  `HAFIYE_ACTIVE_GEMINI_KEY_OK`. No credential value was printed or persisted
  in the repository.
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
the `ACCEPTED_UPSTREAM_BASELINE`; the P7 exact comparison reproduced only
items 2, 3, and 5 (Hermes state FTS, execution-flag detection, and Vercel
doctor diagnostics). Items 1 and 4 passed in that P7 comparison. The two
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
  operations, safely recovers one unique visible browser when Composer owns
  focus, and does not create a profile or read cookies.
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

1. Perform the remaining physical P24 acceptance: consent-enabled wake,
   Turkish transcript/short speech, three clean cycles, barge-in, and
   long-running managed-desktop emergency stop. Keep the explicitly deferred
   offline replay unaccepted.
2. Re-run the real Randevu and YouTube Composer scenarios with the installed
   `139f5f949` package once the Gemini quota is usable. Do not promote a
   partial tool trace to P24 acceptance.
3. Run the final P24/P23 regression matrices and close P24 only if every
   installed real-machine acceptance item is genuinely green; do not create
   P25 or a release tag.

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
- Current Hafiye source/test commits:
  `f9ebf814b53b0a3c71f932713db0e217af17cb1c` (KI-043 boundary and model
  capability state), followed by
  `dc962963e6040f792e3f74fcd459d41da425d8d` (managed computer-use MCP
  startup gate).
- The native gateway now uses the normal Hafiye XDG config root while
  retaining explicit `HERMES_HOME`/profile single-root behavior. The
  Electron/TUI `_make_agent` boundary now resolves the same Hafiye route slot,
  privacy mode, and fallback metadata before creating `AIAgent`. No Hermes
  upstream commit or upstream history changed. The same source/test commit
  adds a narrowly scoped Qwen2 context compatibility argument builder: above
  32K it passes YaRN scaling from 32K and an explicit Qwen2 context metadata
  override; other model families retain native metadata behavior.
- The shared terminal boundary now detects direct, absolute, env/command-
  wrapped, quoted, shell-wrapped, and chained `sudo`, `sudoedit`, `su`,
  `pkexec`, `doas`, and `runuser` forms. FULL_AUTONOMOUS sends privileged
  terminal work through `hafiye-rootd`; READ_ONLY blocks it and confirmation
  policies require approval before the broker call. Direct Python
  subprocess/os escalation in `execute_code` is fail-closed.
- The local model registry now persists capability state. The Qwen2.5-0.5B
  fixture is `validation=true, agent=false`; Qwen3-14B is
  `agent=true, tool_calling=true, validation=false` with `resource_warning=KI-046`.
  At this qualification point the default route was
  `custom/qwen2.5-0.5b-instruct-q4`; the current installed default is the
  configured Gemini route recorded in the audit closure below.

### P23.2 managed computer-use MCP startup fix — 2026-08-25

- After the real reboot, a fresh gateway/Desktop process skipped MCP discovery
  because `_has_configured_mcp_servers()` only considered persisted MCP
  configuration and portable plugins. Hafiye's prescribed
  `hafiye-computer-use-linux` provider is injected from its managed binary in
  memory, so this was a genuine Hafiye startup-gate defect exposed by the
  final Composer acceptance.
- Source/test commit:
  `dc962963e6040f792e3f74fcd459d41da425d8d`. The shared startup probe now
  recognizes the managed provider without writing user configuration or
  changing the computer-use architecture.
- Targeted verification passed: the MCP startup, Hafiye computer-use, TUI
  MCP-owner, discovery-timing, one-shot toolset, and browser integration
  tests returned `40 passed`; the focused gateway discovery tests returned
  `3 passed`; Ruff and `git diff --check` were clean.
- After `systemctl --user restart hafiye-gateway.service`, the user journal
  recorded registration of `hafiye-computer-use-linux` with 18 tools. A real
  packaged Electron Composer replay with the exact `Firefox'u aç.` prompt and
  agent-qualified Qwen3 route exposed 38 core/visible tools plus 18 deferred
  MCP tools, but Qwen3 remained in reasoning for approximately 265 seconds
  without emitting a tool call. The replay was stopped; it is not P23.2
  acceptance evidence. Qwen2/default route was restored and its CUDA runtime
  remains healthy. This observed behavior is tracked as KI-047, while the
  Qwen3 qualification and KI-046 resource warning remain unchanged.

### P23.4–P23.6 live rechecks — 2026-08-25

- P23.4 was started with a real disconnected-network setup: `nmcli networking
  off` reported `disabled`, the default route disappeared, and the local
  gateway health endpoint still returned HTTP 200. The Qwen3 packaged
  Composer task had not completed after the initial observation. The user
  then explicitly instructed to skip the offline test, so it was stopped and
  is **not** marked PASS. `nmcli networking on` restored connectivity, and the
  default route/runtime were restored to Qwen2/CUDA.
- P23.5 is not accepted: `hafiye routing --json` has an empty `remote` task
  override, `/home/tolga/.config/hafiye/config.yaml` contains only the local
  `127.0.0.1:11435/v1` OpenAI-compatible endpoint, and onboarding records
  `remote_provider_skipped=true`. No real remote self-hosted endpoint was
  available to test. This is recorded as KI-048, not replaced by a localhost
  fixture.
- P23.6 clean Gemini Composer acceptance passed on the real packaged Desktop.
  With the default route temporarily set to Gemini, the task created and read
  `/tmp/hafiye-p23-gemini/ok.txt`, returned `P23_GEMINI_COMPOSER_OK`, and an
  independent filesystem check confirmed the exact 22-byte content. No
  privileged command or password dialog occurred; route was restored to
  Qwen2/CUDA afterward.
- The separate exact Gemini `Firefox'u aç.` replay is not clean: Gemini opened
  Firefox, then started an unrelated `sudo apt`/`sudo snap` remediation. The
  command crossed `hafiye-rootd` (no OS password dialog), but it changed the
  host package state. Emergency stop was engaged, the root operation ended,
  and the prior Firefox Snap revision `8763` was restored through rootd; the
  temporary Mozilla apt source/preference files were removed. This remains
  NOT ACCEPTED for P23.2 and is tracked as KI-049; KI-043 remains RESOLVED.

### P23.1 reboot preflight — 2026-08-25

The real reboot/login acceptance has not been claimed yet. The read-only
preflight completed at `2026-08-25T06:10:10+03:00`, before the required
reboot:

- `systemctl --user is-enabled hafiye-gateway.service` returned `enabled`.
- `systemctl --user is-active hafiye-gateway.service` returned `active`.
  `MainPID=3033612`, `ExecMainStartTimestamp=Tue 2026-08-25 04:28:40 +03`,
  and the unit is loaded from
  `/home/tolga/.config/systemd/user/hafiye-gateway.service`.
- `curl --fail-with-body --silent --show-error
  http://127.0.0.1:9120/api/health` returned HTTP 200 with
  `{"ok":true,"version":"0.20.5","auth_required":false}`.
- `/home/tolga/.config/autostart/hafiye.desktop` exists, is owner-owned with
  mode `0644`, passes `desktop-file-validate`, and contains the packaged
  executable entry
  `Exec="/home/tolga/projects/hafiye/apps/desktop/release/linux-unpacked/hafiye-desktop" --hidden`.
  The target is an executable x86-64 ELF (`0755`, SHA-256
  `86be74e1f15b848f32112a994a381363a1f295ea50f0b2a761da86017f8b5109`).
- The live session is Ubuntu GNOME 50.1 on Wayland. `hafiye voice doctor`
  returned `ok=true`, `blockers=[]`, Piper `ready=true`, and whisper.cpp
  `selected_auto_backend=CUDA`. `hafiye computer doctor --json` returned
  all four required P0 readiness fields true and `blockers=[]`.
- The machine had been up since `2026-08-23 18:29:15 +0300`, with boot ID
  `d5d3b71c-b8f2-4975-9131-c06e449ab1cc`. A currently running development
  Electron process was observed before reboot; that is explicitly not P23.1
  evidence. The fresh post-login process must come from the packaged
  autostart entry without manual terminal startup.

The preflight next action was the real system reboot/login. Its post-login
result is recorded immediately below; P23.1 remains unaccepted because the
Desktop did not start from the login autostart path.

### P23.1 post-reboot result — 2026-08-25

The requested real reboot/login was performed with `systemctl reboot -i`.
The post-login boot evidence is:

- New boot ID: `17a11ea7-41ed-4b74-a4fc-8f4e9c3dc7eb`; boot time
  `2026-08-25 06:14:00 +0300`.
- `hafiye-gateway.service` is enabled and active. Its new
  `MainPID=8925` entered active state at `06:14:19 +03`; the user
  journal records `HERMES_BACKEND_READY port=9120`. The real
  `/api/health` request returned HTTP 200.
- The validated
  `/home/tolga/.config/autostart/hafiye.desktop` was executed by GNOME: the
  journal contains `app-gnome-hafiye-10171.scope`. Electron then exited before
  creating the tray because the unpacked artefact's `chrome-sandbox` was
  `tolga:tolga 0755`; Electron reported that the helper must be root-owned and
  setuid `4755`.
- This is not counted as P23.1 acceptance. The exact helper was verified as a
  regular file and repaired through `hafiye-rootd` to `root:root 4755`. A
  short sandbox-enabled launch then stayed up without the Electron sandbox
  fatal error. The Debian package builder was fixed in source/test commit
  `a1271a93277e6ac0747c1c5c31b586c2e883e55a` and its packaging regression set
  returned `4 passed`.
- A fresh real reboot/login is still required after this repair. Until that
  replay produces the process, tray, Composer, gateway connection, and
  voice/computer readiness without manual startup, P23.1 remains unaccepted.
- Voice doctor remained `ok=true`, with Piper and whisper.cpp ready and
  AUTO selecting CUDA. Computer-use doctor remained `ok=true`, with all
  required readiness fields true and `blockers=[]`.

This first replay remains unaccepted and is retained as the KI-013 defect
discovery. The repaired second real reboot/login acceptance is recorded below;
the short sandbox-enabled launch in this section is not used as reboot
acceptance evidence.

### P23.1 second real reboot/login acceptance — PASS — 2026-08-25

The repaired packaged artefact was verified through a second real operating
system reboot/login. This replay is the acceptance evidence; the earlier
failed replay above remains recorded as the defect discovery.

- New boot ID: `db40c0c5-f5b3-4dcf-8d01-7cf425e15323`.
- GNOME launched the owner-created entry as
  `app-gnome-hafiye-3143760.scope`; no manual terminal launch was used.
- `hafiye-gateway.service` was `enabled` and `active/running`, with
  `MainPID=3142580` and `ExecMainStartTimestamp=Tue 2026-08-25 21:32:51 +03`.
  The real health request returned
  `{"ok":true,"version":"0.20.5","auth_required":false}`.
- The packaged Desktop process remained alive as
  `.../release/linux-unpacked/hafiye-desktop --hidden`. The journal and
  `/home/tolga/.local/state/hafiye/logs/desktop.log` recorded
  `[tray] Hafiye tray ready`, backend resolution, and persistent backend
  readiness. The StatusNotifier item had tooltip `Hafiye`, status `Active`,
  and was independently mapped to Desktop PID `3143760` over the user D-Bus.
- The live helper was `root:root 4755`; the Electron child
  `chrome-sandbox` was alive, and the new-boot journal contained no SUID
  sandbox fatal error.
- A real packaged Desktop startup observation after the reboot captured the
  configured login Composer window through
  `computer-use-linux windows --json`: title `Hafiye`, app id `window:30`,
  PID `3212308`, bounds `640x220`. The observation used the packaged app and
  did not alter the Composer mode; the app source/default remains
  `SHOW_ON_LOGIN` with the brief welcome reveal.
- `hafiye voice doctor` returned `ok=true`, `blockers=[]`, Piper ready,
  whisper.cpp ready, and AUTO selecting CUDA. `hafiye computer doctor --json`
  returned `ok=true`, `blockers=[]`, and all required readiness fields true:
  `can_register_mcp_tools`, `can_build_accessibility_tree`,
  `can_send_development_input`, and `can_query_windows`.

P23.1 is accepted. KI-013 is resolved: the Debian packaging fix preserves
the Linux Electron sandbox helper's `4755` mode, and the second real
reboot/login proved the autostart path, tray, Composer, gateway, and readiness
checks without manual Desktop startup.

### P23 verification completed so far

- The P23 backend target matrix completed with `251 passed, 2 skipped, 1
  warning in 22.66s`, including the managed local-runtime compatibility test.
- `.venv/bin/ruff check` on the route/config source and tests, Python
  compilation, and `git diff --check` passed.
- The latest exact five-ID upstream comparison after KI-043 source hardening
  used the documented direct `.venv/bin/pytest` command and returned
  `3 failed, 2 passed`: historical IDs 2, 3, and 5 failed; IDs 1 and 4 passed.
  Every failure is inside the exact historical five-ID
  `ACCEPTED_UPSTREAM_BASELINE`; there is no new or different failure and no
  Qwen3/Hafiye regression. The per-file wrapper replay also produced only
  failures from that same five-ID set, but its file-granular `-k` behavior is
  not used as the canonical exact-node result.
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
  The model remains registered and selectable; the normal route was restored
  to the Qwen2 smoke fixture after the isolated qualification run.
- Managed Qwen3 startup now uses the official embedded Jinja template and
  DeepSeek reasoning parser, and for a requested 65,536-token context uses
  YaRN from the model's 40,960-token native context, an explicit
  `qwen3.context_length` override, fit-aware `-ngl auto`, and CPU KV storage.
  Full-GPU 65K and 4K fit probes were CUDA-OOM diagnostics; the managed
  compatibility command reached `n_ctx=65536`, `n_ctx_train=65536`, and
  `ready=true` on CUDA.
- The isolated Qwen3 local-agent acceptance replay used the actual Hafiye
  `AIAgent` path against the managed CUDA endpoint, with `LOCAL_ONLY` on the
  parent agent and the managed computer-use-linux MCP boundary where needed.
  All six required workflows passed:
  - exact `Firefox'u aç.`: `list_apps`, `list_windows`, and
    `activate_window`; Firefox was focused; 51.303 seconds;
  - isolated create/read/move fixture: real terminal/file calls moved
    `notes.txt` and `photo.jpg`, preserved `keep.bin`, and independent content
    verification passed in 73.703 seconds. The model first sent `read_file` to
    the `.jpg` fixture and received the expected binary-file error; it then
    completed the operation and the external verification is the acceptance
    authority for that binary content;
  - real VS Code Wayland action: managed `list_windows`, exact activation,
    Ctrl+A, `type_text`, Ctrl+S, and targeted screenshot; the saved marker was
    independently verified; 48.849 seconds;
  - multi-step terminal task: five successful terminal calls created two
    inputs, performed sorted-unique aggregation, read the result, and the
    independent comparison passed; 58.319 seconds;
  - OpenHands coding delegation: `coding_delegate` used the Hafiye coding
    route `custom/qwen3-14b-q4_k_m`; the managed worker returned
    `status=completed`, 14 progress events, changed `bug.py`, and the
    independent fixture pytest returned `1 passed`; 423.879 seconds;
  - multi-turn workflow: the same `AIAgent` kept session
    `20260825_042420_3f0fe8`, completed two terminal turns, and the independent
    two-line file verification passed; 71.845 seconds.
- Qwen3 runtime evidence: Q4_K Medium, 14,768,307,200 parameters,
  `n_ctx=65536`, `n_ctx_train=65536`, managed llama.cpp commit
  `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`, selected backend `CUDA`,
  `-ngl auto`, and `--no-kv-offload`. The final Qwen3 sample recorded 8,614
  MiB of 10,240 MiB VRAM, server `VmRSS=7,749,188 kB`,
  `VmSwap=7,609,128 kB`, and host memory `11 GiB/14 GiB` in use; an earlier
  load sample reached approximately 11.3 GiB RSS. llama-server timing logs
  showed prompt processing about 228–827 tokens/s (cache-dependent) and
  generation about 4.59–5.39 tokens/s. The full workflow is therefore
  functionally qualified for this local-agent acceptance objective, but the
  measured VRAM/RAM/swap pressure and full-GPU CUDA-OOM diagnostics remain a
  resource warning; Qwen3 stays selectable and is not made the default route.
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
  restored to local custom/Qwen. KI-049 records why this is not a clean final
  P23.2 acceptance; the later clean Gemini file-task replay separately passed
  P23.6.
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

### P23 final source hardening — KI-043

- Source/test commit: `f9ebf814b53b0a3c71f932713db0e217af17cb1c`.
- Targeted command:
  `scripts/run_tests.sh tests/test_hafiye_execution_policy.py
  tests/test_hafiye_privileged_boundary.py tests/test_hafiye_rootd.py
  tests/hermes_cli/test_local_runtime.py -q` → `35 passed, 0 failed`.
- `.venv/bin/ruff check` on the changed source and tests passed; `git diff
  --check` passed.
- The regression matrix covers direct/absolute/env/command/quoted/shell-
  wrapped/chained `sudo`, `sudoedit`, `su`, `pkexec`, and `doas`; Gemini's
  `sudo chown root:root /usr/libexec/snapd/snap-confine` scenario; normal
  terminal execution; FULL_AUTONOMOUS rootd routing; rootd audit; READ_ONLY;
  confirmation; and local-model registry metadata.
- The exact upstream comparison returned `3 failed, 2 passed`; only accepted
  historical IDs 2, 3, and 5 failed. The five-ID historical whitelist is
  unchanged and no new/different failure was found.
- KI-043 is resolved at source level. The exact Firefox Gemini replay remains
  unaccepted under KI-049; the separate clean Gemini file-task replay is
  recorded as P23.6 PASS.

### Desktop local model download UI — 2026-08-26

- Source/test/E2E commit:
  `213247d70804ffe9350ad5d0874f79a494fd7dc0`.
- The persistent Models settings surface uses the existing Hafiye-managed
  llama.cpp endpoint. It downloads one `.gguf` file from Hugging Face,
  forwards optional revision/model-id/checksum values, refreshes the registry,
  and selects the returned model without silently starting it.
- The fixed local-runtime boundary is unchanged: Hafiye manages llama.cpp and
  GGUF. An Ollama manifest/blob model directory is not a Hafiye local-runtime
  input; use a compatible single-file GGUF through this form or Import GGUF.
- Verification completed:
  - `cd apps/desktop && ../../node_modules/.bin/vitest run src/app/settings/local-runtime-settings.test.tsx --project ui` — 1 passed.
  - `cd apps/desktop && npm run test:ui` — 584 files and 5,557 tests passed.
  - `cd apps/desktop && npm run typecheck` — passed.
  - `cd apps/desktop && npm exec playwright test e2e/p17-control-center.spec.ts --reporter=list` — real Electron Models page check passed, 1 test in 10.4s.
  - `cd apps/desktop && npm run pack` — production build and Linux unpacked package passed; build stamp `213247d70804`.
  - Targeted ESLint for the changed source/test files exited 0 with existing padding warnings. Full `npm run lint` remains non-green because of seven unrelated repository errors; no error was reported in the changed files.
  - `git diff --check` passed before this documentation update.
- No live external model download was performed during this source change;
  the backend download lifecycle was already covered by the P4 runtime tests,
  while this change verifies the real Desktop control and its API payload.

### README and Python 3.14 package bootstrap — 2026-08-26

- The root README is now Hafiye-specific. It documents the real first install,
  source-development restart path, production `.deb` rebuild/reinstall path,
  GUI GGUF management, provider/privacy controls, security boundaries, XDG
  roots, testing discipline, troubleshooting, project documents, and upstream
  attribution. The inherited Windows-first Hermes install and obsolete
  `avifenesh/computer-use-linux` reference were removed.
- While dry-running the documented package install, the real host reported
  `/usr/bin/python3` as Python `3.14.4`. The previous Debian metadata required
  `python3 (<< 3.14)`, so `apt install --simulate` correctly rejected the
  package. This was a genuine current-host Hafiye packaging defect, not a
  documentation-only warning.
- Source/test commit `fd435cc85fe018ca238256fb19547db2e7064565`
  removes the Debian bootstrap interpreter upper bound while preserving the
  Hafiye runtime requirement `>=3.11,<3.14`. `hafiye package install` now uses
  a supported existing managed interpreter or provisions managed Python 3.11
  through `uv` when the system interpreter is 3.14.
- Verification completed:
  - `uv sync --locked --python 3.11 --extra all --extra dev` — completed from
    the committed lockfile.
  - `.venv/bin/python -m pytest -q tests/packaging/test_hafiye_deb.py
    tests/test_packaging_metadata.py` — `13 passed in 48.19s`.
  - `.venv/bin/python -m ruff check packaging/debian/dependency_doctor.py
    tests/packaging/test_hafiye_deb.py` — passed.
  - Python bytecode compilation and `git diff --check` — passed.
  - Real combined artifact rebuilt at `dist/hafiye_0.20.5_amd64.deb`; manifest
    source commit is `fd435cc85fe018ca238256fb19547db2e7064565`, with pinned
    upstream and baseline merge identities unchanged.
  - `apt install --reinstall --simulate` against that real artifact on the
    Python 3.14 host — package selected/configured successfully with no
    dependency conflict.
  - Extracted real-artifact `hafiye package doctor --json` under the managed
    Python 3.11 environment — `ok=true`, `blockers=[]`; optional missing
    `cargo` remained a warning.
  - Exact historical upstream five-ID comparison after source commit
    `fd435cc85` — `3 failed, 2 passed`; only accepted IDs 2, 3, and 5 failed.
    No new or different regression was found.
  - README bash-fence syntax, local links, current Ubuntu package names, CLI
    parser/help surfaces, and `git diff --check` were checked.
- No live `/usr` package installation, sudo prompt, service mutation, route
  change, model change, or P23 real-machine acceptance claim was made. KI-051
  records the resolved package bootstrap defect; P23 remains in progress.

### Turkish Desktop interface locale — 2026-08-26

- Source/test commit: `3c2ea9a7a9c119475aa0cee471b6cf982677d8a6`.
- Settings → Appearance → Language now offers `Türkçe`; selecting it persists
  `display.language: tr`, updates the document locale to LTR Turkish, and
  applies without restarting the Desktop.
- Turkish coverage includes common actions, boot/error recovery, notifications,
  voice controls, navigation, Composer, model selection, Appearance and Model
  settings, session/file/terminal surfaces, approvals, and primary tool status.
  Advanced untranslated upstream surfaces use the i18n framework's deliberate
  English fallback and are tracked as the non-blocking KI-052 coverage warning.
- Verification completed:
  - Targeted locale/context/switcher/runtime matrix: `26 passed`.
  - Full Desktop UI suite: `584 files, 5,558 tests passed`.
  - Desktop renderer/Electron/E2E TypeScript typecheck: passed.
  - Targeted ESLint for all changed locale/test files: passed.
  - Final production pack: passed with source stamp `684227f6ebbf` on `main`;
    dependency, builder pin, installed module, and packaged runtime all report
    Electron `40.10.6`.
  - Combined package `/home/tolga/projects/hafiye/dist/hafiye_0.20.5_amd64.deb`
    was built from source `684227f6ebbfeed2bc9ea2e08e6723e54edef073`,
    installed through an interactive graphical Ptyxis/sudo prompt, and verified
    as installed package `0.20.5-1`.
  - The installed `app.asar` contains the `Türkçe` option, Turkish catalog, and
    `tr` aliases. The packaged Desktop was restarted and logged install stamp
    `684227f6ebbf (main)`; gateway health returned HTTP 200 with `ok=true` and
    the user service remained enabled/active with `NRestarts=0`.
  - `git diff --check`: passed before documentation update.
- This source maintenance does not alter or complete any deferred P23
  real-machine acceptance row.

### Settings / Composer model identity hardening — 2026-08-26

- Source/test commit: `197e4ca8fe864faaf48dd695cc25d7c89e2c6e33`.
- A real pre-fix Desktop session displayed/selected the stale local Qwen model
  while the runtime inherited Gemini's endpoint, producing a Gemini 404 for
  `qwen2.5-0.5b-instruct-q4`. Two causes were fixed at their owning boundaries:
  an explicit Desktop `session.create` provider/model now has precedence over
  the configured Hafiye default route, and New Chat resets a prior manual
  Composer override then resolves the target profile's Settings model before
  session creation. Privacy/locality policy continues to apply and manual
  picker choices remain explicit per-session overrides.
- Verification completed:
  - Desktop targeted model/session matrix: `4 files, 171 passed`.
  - Full Desktop Vitest matrix: `700 passed, 1 skipped`; `7,175 passed, 3
    skipped`.
  - Desktop renderer/Electron/E2E TypeScript typecheck and changed-file ESLint:
    passed.
  - Backend route/agent matrix: `17 passed`; Ruff passed.
  - Exact historical upstream five-ID comparison: `3 failed, 2 passed`; only
    accepted IDs 2, 3, and 5 failed, with no new/different regression.
  - Production `npm run pack` passed with clean build stamp `197e4ca8fe86`;
    the combined `.deb` manifest records the full source commit above.
  - The package was installed through a visible Ptyxis/sudo prompt. Installed
    package `0.20.5-1` carries the clean source stamp, gateway health returns
    `ok=true`, the service is active with `NRestarts=0`, the installed Desktop
    is running, and `/api/model/info` reports
    `gemini/gemini-3.1-pro-preview`, matching Settings.
- A broad host-sensitive TUI-gateway diagnostic run returned 1,140 passed and
  four failures: two exact-toolset expectations observed the real managed
  computer-use provider, while two order-sensitive tests passed when rerun in
  isolation. None is a new model-route failure; KI-053 is resolved.
- This maintenance does not mark any deferred P23 real-machine acceptance row
  as passed and does not complete P23.

### P23 final acceptance ledger

The following are deliberately not marked passed merely because earlier phase
tests exist. The master roadmap requires the final real-machine sequence.

| Master item | Current evidence | Final status |
|---|---|---|
| 23.1 Boot | Second real reboot/login boot `db40c0c5-f5b3-4dcf-8d01-7cf425e15323`; GNOME autostart launched packaged Desktop PID `3143760`, tray D-Bus item reported `Hafiye`/`Active`, gateway was enabled/active and health returned `ok=true`, packaged Composer window was observed, voice/computer doctors were green, and `chrome-sandbox` was `root:root 4755` without a fatal error | PASS / KI-013 RESOLVED |
| 23.2 Text | The managed-MCP startup gate was fixed and a fresh packaged Composer replay registered 18 computer-use tools, but the agent-qualified Qwen3 route stayed in reasoning for approximately 265 seconds without a tool call; the older Qwen2 validation replay also returned text without computer use | NOT ACCEPTED / KI-042 + KI-047 |
| 23.3 Voice | P11/P12 real microphone, STT, TTS, and wake evidence exists; exact P23 spoken command is not replayed here | NOT FINAL-CHECKED |
| 23.4 Local inference | Managed Qwen2 compatibility path reports 65,536 context; direct AIAgent and packaged Desktop terminal markers passed. The real disconnected-network replay was started, then explicitly skipped by the user and restored without a PASS claim | PASS FOR LOCAL ROUTE / OFFLINE ACCEPTANCE DEFERRED |
| 23.5 Remote inference | No real self-hosted endpoint is configured: remote route override is empty and onboarding records the remote provider was skipped | NOT ACCEPTED / KI-048 OPERATIONAL BLOCKER |
| 23.6 Gemini | Real packaged Composer with Gemini created/read `/tmp/hafiye-p23-gemini/ok.txt`, returned `P23_GEMINI_COMPOSER_OK`, and independent content verification passed without privilege escalation | PASS / CLEAN FILE TASK |
| 23.7 Privacy | Real Gemini-configured route under global `LOCAL_ONLY` exited before provider call with the policy-block message; settings restored | PASS / FAIL-CLOSED |
| 23.8 Files | Authenticated Gemini fixture replay performed and verified the required moves and final paths; KI-041 retains the earlier local-Qwen warning | PASS / GEMINI ROUTE |
| 23.9 Desktop | Managed computer-use-linux MCP opened two real VS Code windows, switched focus, sent mouse/keyboard input, saved the marker, and visually verified the final UI | PASS / KI-044 MODEL WARNING |
| 23.10 Browser | Structured local navigation passed; native managed route navigated a real Wayland Firefox window, screenshot verified the fixture title/marker, and the original tab was restored | PASS / KI-022 AT-SPI DIAGNOSTIC |
| 23.11 Root | Fresh `hafiye root exec id -u` returned 0; gateway EUID 1000 and rootd EUID 0 | PASS / FRESH RECHECK |
| 23.12 Memory | Fresh `test_project_alias_and_session_context_survive_fresh_process` returned `1 passed in 1.36s` | PASS / FRESH PROCESS |
| 23.13 OpenHands | Fresh managed doctor plus Gemini-backed `coding_delegate` fixture; Task Center `COMPLETED`, 28 progress events, `bug.py` changed, independent `pytest -q` returned `1 passed` | PASS |
| 23.14 Barge-in | P13 real stop evidence remains green; exact final phrase is not replayed here | INHERITED / RECHECK |
| 23.15 Emergency shortcut | Real `Ctrl+Super+Escape` reached the GNOME fallback, paused the emergency state, and `emergency.resume` restored it; the model selected `terminal` instead of a long-running managed desktop action. The later Gemini remediation was stopped through the same emergency path, but that was not the required desktop-action acceptance | PARTIAL / KI-045 |
| 23.16 Restart recovery | Authenticated desktop session completed before restart; service restarted; same durable session resumed; post-restart prompt completed; service remained active; marker `P23_RESTART_RECONNECT_OK` | PASS / REAL SESSION RESUME |
| Qwen3 local-agent qualification | Isolated managed Qwen3 Q4_K_M AIAgent replay passed exact Firefox, file organize/read/move, real VS Code MCP input, multi-step terminal, OpenHands delegation, and same-session multi-turn tool workflows; resource envelope recorded separately | PASS / RESOURCE WARNING KI-046 |

### Exact next actions

1. Re-run P23.2 with an agent-qualified route after the managed-MCP startup
   fix, and retain KI-042/KI-047/KI-049 until a real Firefox tool call and
   clean verification pass.
2. Complete the physical P23.3 voice, P23.14 barge-in, and P23.15
   long-running managed-desktop emergency-stop replays; keep P23.4 deferred
   by the user's instruction and P23.5 blocked until a real remote endpoint is
   configured.
3. Do not mark P23 complete or create a P23 completion commit until every
   required acceptance row has fresh evidence. P24 was defined at this
   historical checkpoint; its later implementation and open acceptance ledger
   are recorded below.

### Post-roadmap implementation audit closure — 2026-08-26

- Current Hafiye source HEAD:
  `822448adee3c4fce570cbda2323bebc18ab5c792`.
- Installed package `0.20.5-1` has the same source commit in
  `/usr/lib/hafiye/package-manifest.json`. The user gateway imports the packaged
  backend, is enabled/active, and `GET http://127.0.0.1:9120/api/health`
  returned HTTP 200 with `ok=true`.
- `/usr/bin/hafiye doctor` reports all checks passed. Package doctor reports
  `ok=true`, `blockers=[]`; the only package warning is optional Cargo absence.
  Hardening and voice doctors report `ok=true`; computer-use doctor retains
  all four required readiness booleans and an empty blocker list.
- The current default route is the configured Gemini route
  `gemini/gemini-3.1-pro-preview`. The managed Qwen2 validation fixture remains
  `validation=true, agent=false`; qualified Qwen3 remains selectable,
  non-default, and carries resource warning KI-046.
- A live `hafiye root exec 'id -u'` returned `0`. The canonical product audit
  at `~/.local/state/hafiye/logs/audit.log` is owner-only mode `0600` and now
  contains real `root_rpc` and `provider_model_switch` events.
- Final test commands/results:
  - broad backend/package matrix covering constants, status, identity, doctor,
    logging, onboarding, packaging, rootd, audit, execution and model policy:
    `190 passed, 7 skipped in 102.51s`;
  - focused audit/root/doctor matrix: `70 passed in 44.04s`;
  - Desktop session/model matrix: `171 passed`; `npm run typecheck` passed;
  - Ruff, compileall, `git diff --check`: passed;
  - exact historical five-node comparison: `2 failed, 3 passed`; failures are
    only accepted historical IDs 2 and 3, with no new/different regression.
- KI-054 is resolved. KI-046 remains a non-blocking resource warning. P23 is
  still the first incomplete phase; deferred P23.2/P23.3/P23.4/P23.5/P23.14/
  P23.15 evidence remains unaccepted exactly as recorded in ROADMAP.md.

### Previous exact next action

The earlier implementation-audit action was to authenticate Git for the
Hafiye GitHub origin and run a normal, non-force `git push origin main`. That
operational credential blocker is unchanged; no remote mutation was attempted
by this session.

### P24 planning record — 2026-08-27

- The user clarified the primary product contract: an installed Hafiye starts
  after graphical login, waits locally for “Hafiye”, opens Composer on wake,
  displays the Turkish transcript in its field, gives a short assistant-style
  spoken acknowledgement, performs and verifies the task with real tools,
  gives a concise spoken result, then returns to wake waiting.
- Current pre-P24 evidence shows the product is not yet converged: live config
  has `wake_word.enabled=false` and `voice.auto_tts=false`; `wake.detected`
  activates a separate small indicator and the main voice hook but does not
  open Quick Entry; the compact Composer receives generic busy state rather
  than authoritative voice/tool phases; and the current default route is
  Gemini rather than a practical local agent-qualified default.
- The master roadmap now defines P24.1–P24.14, including the coding scenario
  “Randevu projesini açıp bug fix yapalım” and browser/media scenario
  “YouTube'dan Mertcan Bahar'ın son videosunu aç”.
- No source code, package, service, runtime setting, wake setting, voice setting,
  provider route, or P23 acceptance status was changed in this planning step.
- Exact next implementation action when authorized: capture the P24.1 installed
  baseline, add failing tests for wake-to-Composer/state/transcript/speech
  contracts, then implement the single canonical interaction state machine.

### P24 implementation and installed-package verification — 2026-08-27

- Source checkpoint: `8b7c29aa8197595a479e35bb85ef081cec2b7a11`
  (`fix(browser): recover native target when Composer owns focus`). It adds a
  conservative `list_windows` recovery to the native browser wrapper when
  Composer owns focus, plus nested-envelope parsing and ambiguous-target
  fail-closed behavior. This source is now also the installed package
  baseline.
- The clean Electron package was built with `cd apps/desktop && npm run pack`;
  the build wrote clean install stamp `8b7c29aa8197` on `main`. The real
  combined package was built with
  `python scripts/build_deb.py --output dist/hafiye_0.20.5_amd64.deb
  --desktop-dir apps/desktop/release/linux-unpacked --json`; its manifest
  records source `8b7c29aa`, the pinned upstream commit, and the baseline
  merge commit.
- `dpkg-query` and `/usr/lib/hafiye/package-manifest.json` now report the
  installed source `8b7c29aa8197595a479e35bb85ef081cec2b7a11`. The live
  installed Desktop process remains `/usr/lib/hafiye/desktop/hafiye-desktop`
  and the user autostart entry still targets that installed binary.
- The installed package doctor returned `ok=true` with `blockers=[]`. The user
  gateway is enabled/active and
  `curl http://127.0.0.1:9120/api/health` returned
  `{"ok":true,"version":"0.20.5","auth_required":false}`. Voice doctor
  and OpenHands doctor are green; computer-use-linux reports
  `can_register_mcp_tools=true`, `can_build_accessibility_tree=true`,
  `can_send_development_input=true`, `can_query_windows=true`, and an empty
  blockers list.
- Installed-binary Electron smoke opened the real `/usr/lib/hafiye/desktop`
  binary, rendered a Hafiye document with one root child, and matched the
  `8b7c29aa` install stamp. The workspace packaged Electron acceptance remains
  green: 116 files, 1,615 tests passed, 3 skipped; the P24 targeted UI suite
  passed 93/93 and Desktop typecheck passed. The P24 backend/local/browser/
  policy/OpenHands/project matrix passed 793 tests after excluding three
  unrelated existing gateway fixture failures; the exact P23 backend target
  matrix passed 261 tests with 2 skips.
- The exact historical five-ID comparison after this source checkpoint was
  `2 failed, 3 passed`. Only whitelist IDs 2 and 3 failed; IDs 1, 4, and 5
  passed. This is an improvement within `ACCEPTED_UPSTREAM_BASELINE`, not a
  new/different regression.
- Real source-level native browser integration was replayed against the live
  GNOME/AT-SPI environment with another desktop window owning focus. The
  wrapper selected the unique Firefox target, executed the four-step
  navigation sequence, and `computer-use-linux windows` verified the real
  title `YouTube — Mozilla Firefox`. This is a tool-boundary integration
  pass, not the required natural-language latest-video acceptance.
- The pre-patch installed Qwen3-14B browser Composer replay used installed
  source `0d98610a`; it made native calls but ended without a verified channel,
  latest-video, or playback result and was terminated. The Qwen3-14B Randevu
  replay resolved the project and ran real read-only inspection, but timed out
  before evidence-backed diagnosis/OpenHands verification. Neither is
  promoted to P24 acceptance. Qwen3-14B remains qualified/selectable but
  non-default with `KI-046` resource warning; Qwen2.5-0.5B remains
  validation-only.
- A post-install Gemini replay used `gemini-3.5-flash` through the real
  packaged Composer. Native `windows → navigate → state → click → state`
  succeeded; the final persisted browser state showed the exact latest video
  title `YAYINCI KIŞKIRTMA : EVE DÖNÜŞ`, `Mevtcan Bahav`, a concrete
  `youtube.com/watch` URL, and `Pause`/playing evidence. The model then
  continued into unnecessary `search_files`/`execute_code` tooling instead of
  closing the turn cleanly, so this remains supporting evidence rather than a
  P24.10 acceptance.
- After the source browser patch, focused native-browser tests returned
  `16 passed`; the broader relevant P24 backend subset returned `212 passed`;
  packaging tests returned `15 passed`; Ruff and `git diff --check` passed.
  These source/package checks do not replace installation or physical voice
  evidence.
- P24 remains open. Live configuration still has
  `wake_word.enabled=false` and `voice.auto_tts=false`; auto-arm therefore
  remains correctly consent/setting gated. No physical “Hafiye” wake,
  microphone transcript, audible barge-in, emergency-stop during a real
  managed desktop action, three-turn replay, final coding replay, final
  YouTube replay, or offline replay was claimed. P23 remains open and P23.4
  remains explicitly user-deferred.

### P24 route-endpoint hardening — 2026-08-27

- Source commit: `10bd0b8f32b99b9a7ad91317dfb2f88b5204b927`.
- Red-first evidence: the new policy regression reproduced the real defect as
  `1 failed, 12 passed` when a `LOCAL_ONLY` custom Qwen3 route inherited the
  global Gemini URL.
- After the fix, policy/native-gateway/Desktop route tests passed `23`; the
  combined CLI/provider/route tests passed `91`; API server tests passed
  `133` (72 framework warnings); and the agent/cron/persistence group passed
  `121` (only existing async resource warnings).
- The wider P24 source matrix passed `806` tests. Three unchanged
  `tests/test_tui_gateway_server.py` fixture/order assumptions failed because
  the live managed MCP surface is present; these remain diagnostics, not new
  Hafiye route regressions. Ruff, compileall, and `git diff --check` passed.
- Real source CLI acceptance used the running Qwen3-4B CUDA llama.cpp server:
  temporary `custom/qwen3-4b-q4_k_m` + `LOCAL_ONLY` route, exact terminal
  marker `P24_LOCAL_ONLY_QWEN3_OK`, exit code 0, session DB tool result, then
  restoration to Gemini/NORMAL. No raw Gemini credential was printed or
  persisted.
- The exact historical five-node upstream comparison returned `3 passed, 2
  failed`; only accepted whitelist IDs 2 and 3 failed. IDs 1, 4, and 5 passed;
  no new/different failure was introduced.
- The Desktop was repacked with `npm run pack`, the unified
  `dist/hafiye_0.20.5_amd64.deb` was rebuilt, and the package was reinstalled
  through `hafiye-rootd` using `apt-get --reinstall`. The installed manifest
  reports source `2c749c93d643d22c0e16ca2318aab4473094a4ef`, while the pinned
  upstream and baseline merge values remain unchanged. Installed package
  doctor returned `OK` with only the existing optional `cargo: not found`
  warning; gateway health remained HTTP 200 and the new Desktop logged install
  stamp `2c749c93d643`.
- A real installed `/usr/bin/hafiye ask --safe-mode` replay temporarily set
  `custom/qwen3-4b` plus `LOCAL_ONLY`; Qwen3-4B/CUDA executed `terminal`,
  verified `P24_INSTALLED_LOCAL_ROUTE_OK`, and exited 0. The route/privacy
  configuration was restored to Gemini/NORMAL after the replay.

### Exact next actions

1. Explicitly enable wake listening after granting microphone consent. Do not
   infer consent from source or doctor output.
2. Replay P24.14's physical wake/transcript/short-speech, coding, YouTube,
   repeated re-arm, barge-in, emergency-stop, reconnect, and affected P23
   checks. Keep the offline item deferred as instructed by the user.
3. Run the final regression matrix after those replays. Mark P24 complete only
   when every required installed real-machine item is green; do not create
   P25 or a release tag.

### P24 installed browser hardening and Gemini credential recheck — 2026-08-27

- A genuine Hafiye source defect was found during the installed Composer
  replay. `browser_native` returned an explicit `success:false` envelope, but
  the shared tool-failure classifier did not inspect nested `success`/`ok`
  flags, and a later model text response could therefore look successful.
  Source commit `2a56c25e8f050cec25259197097bb116919844ae` fixes the shared
  classifier and adds a bounded per-turn native-browser verification gate: a
  failed browser action must be followed by a fresh successful `state` before
  final success; otherwise Hafiye returns a truthful blocker.
- Red-first evidence was `7 passed, 1 failed` in
  `tests/agent/test_display_tool_failure.py`. After the fix, the focused
  browser/agent guard suite returned `72 passed in 3.17s`; changed-file Ruff
  and `git diff --check` passed. The new tests cover explicit and nested
  failure envelopes, failed-browser/no-fresh-state finalization, and recovery
  after fresh state.
- The installed package was rebuilt with `cd apps/desktop && npm run pack`,
  rebuilt with `.venv/bin/python scripts/build_deb.py --json`, and reinstalled
  through the existing `hafiye-rootd` boundary using `apt-get --reinstall`.
  `/usr/lib/hafiye/package-manifest.json` now reports source
  `2a56c25e8f050cec25259197097bb116919844ae`, pinned upstream
  `f293e7206b4ddd66042329442c6afebc19a8808d`, and baseline merge
  `2ac06b131a237916432503ac67bbcada6dbea39e`. Package doctor is OK with only
  the existing optional `cargo: not found` warning; gateway health is HTTP
  200 with `ok=true`.
- A real Playwright launch of the installed Desktop rendered the Hafiye UI,
  showed `Gateway ready`, and showed the active Composer model as
  `gemini: gemini-3.5-flash`. This confirms the installed Desktop is not
  silently using the Qwen model for that session.
- The active profile's Linux Secret Service contains both Gemini aliases and
  they resolve to the same non-empty credential; the raw value was not
  printed or written to repository files. Fresh installed CLI probes for
  `gemini-3.5-flash` and `gemini-3.1-flash-lite`, and the real packaged
  Composer turn, all received Gemini `HTTP 429 RESOURCE_EXHAUSTED` with the
  provider message `prepayment credits are depleted`. This is recorded as
  operational issue KI-059, not as a missing-key or Hafiye routing defect.
- Because the provider rejected the call before any browser tool event, the
  latest packaged YouTube Composer attempt is NOT ACCEPTED. P24.10 and the
  complete P24.14 acceptance remain open; no browser success is inferred from
  earlier partial evidence.
- The exact historical five-ID comparison after source commit `4bfe7add`
  returned `3 failed, 2 passed`: only accepted whitelist IDs 2 and 3 failed;
  IDs 1, 4, and 5 passed. No new or different upstream regression was found.

The next actionable external step is to restore usable Gemini API quota for
the active key/project (or configure another credential through the normal
Secret Service-backed Hafiye setup), then repeat the installed clean Composer
browser acceptance. Physical voice, barge-in, emergency-stop, coding,
re-arm, and the explicitly deferred offline acceptance remain open as listed
in P24 and P23; no phase is closed here.

### P24 local Desktop route and current Gemini credential recheck — 2026-08-27

- The installed Desktop model picker was used to select the agent-capable local
  Qwen3-4B GGUF route (`custom:local-(127.0.0.1:11435)`) rather than relying on
  a model-name UI shortcut. A real packaged Composer session
  (`20260827_103330_17e54f`) used the loopback CUDA llama.cpp endpoint, executed
  two real `terminal` tool calls, wrote/read the exact marker
  `P24_LOCAL_DESKTOP_REAL_20260827`, returned a final response, and was
  recorded by the gateway as `status=complete`. This is installed local
  Desktop terminal evidence, not browser/coding qualification.
- A second installed local Qwen3-4B Composer browser attempt
  (`20260827_104500_767eb1`) submitted through the real `Gönder` button and
  reached the actual Firefox window through `browser_native`:
  `windows → focused → navigate(https://www.youtube.com/) → state`. The
  default Firefox accessibility state was 1,102,848 characters; Qwen3-4B then
  repeated the same `state` call and never reached channel search, video
  selection, playback or a clean final response before the 360-second test
  deadline. This is NOT ACCEPTED as P24.10 and is recorded as the operational
  limitation KI-060; no source change was made.
- The current profile-scoped Secret Service credential was re-read through the
  configured `/home/tolga/.config/hafiye` profile reference without printing
  its value. `GEMINI_API_KEY` and `GOOGLE_API_KEY` are both present, equal, and
  match the user-provided credential fingerprint (length 53; SHA-256 recorded
  only in the private diagnostic output). Fresh Gemini requests still return
  HTTP 429 `RESOURCE_EXHAUSTED` / `prepayment credits are depleted`, so this is
  a provider project/quota response rather than a wrong-key or Qwen-route
  result.
- The product route was restored after local testing with
  `gemini/gemini-3.1-flash-lite` and `NORMAL`; gateway health remains HTTP 200.

P24 remains open. P24.9 coding, P24.10 clean browser, P24.12 recovery/re-arm,
physical voice/barge-in/emergency acceptance, and the explicitly deferred
offline replay remain unaccepted. No P25 or release tag was created.

### P24 Gemini credential and Desktop model-selection recheck — 2026-08-27

- The installed Hafiye Python environment reports the Linux Secret Service
  backend (`keyring.backends.SecretService.Keyring`). In the active product
  profile `/home/tolga/.config/hafiye`, both `GEMINI_API_KEY` and
  `GOOGLE_API_KEY` references resolve to the same non-empty credential and
  match the credential supplied by the user; only masked metadata was used.
  The `/home/tolga/.local/share/hafiye` compatibility profile has only its
  `GOOGLE_API_KEY` alias, and it resolves to that same credential rather than
  to a second/old key. No raw credential was printed or written to the
  repository.
- With that key, the real Gemini `GET /v1beta/models` request returned HTTP
  200 and listed `gemini-3.1-flash-lite`,
  `gemini-3.1-flash-lite-preview`, and `gemini-3.5-flash-lite`. Current direct
  `generateContent` probes for those three model IDs all returned HTTP 429
  `RESOURCE_EXHAUSTED` with Google's exact `Your prepayment credits are
  depleted` message. An earlier immediate direct/Hafiye marker probe did
  return HTTP 200, but subsequent independent calls reproduced the 429;
  authentication and model discovery are therefore proven, while current
  generation availability is not.
- A clean isolated launch of the installed Desktop used the actual model
  picker, searched `gemini-3.1-flash-lite`, and selected the real model ID
  `gemini-3.1-flash-lite-preview` (the UI display text omits the `-preview`
  suffix). The Composer marker was submitted through the installed UI; the
  gateway used `gemini-3.1-flash-lite-preview` and received the same 429 after
  three retries before any browser tool event. This rules out the earlier
  suspicion that the clean test was silently using Qwen or the Settings
  `gemini-3.5-flash` default.
- The route was left restored as `gemini/gemini-3.1-flash-lite` with `NORMAL`
  locality; `hafiye-gateway.service` remains active and its health endpoint
  returns `ok=true`. KI-059 remains the exact operational blocker for a clean
  Gemini Composer/browser acceptance. Hafiye cannot infer the Google Console
  project's credit ledger from an API key; the provider's current response
  must be resolved in the project attached to this key before retrying.

### P24 Gemini quota-scope recheck — 2026-08-27

- The key's live model catalog still returned HTTP 200 and advertised
  `generateContent` for current Gemini 3 families. Direct probes for
  `gemini-3-flash-preview`, `gemini-3.6-flash`, and `gemini-3.7-flash` all
  returned HTTP 429 `RESOURCE_EXHAUSTED` with the same prepayment-credit
  message. The installed Hafiye CLI also reproduced the 429 on a fresh
  `gemini-3.1-flash-lite` retry.
- This rules out a single-model retirement/selection problem as the current
  Gemini blocker. The configured credential authenticates and discovers the
  catalog, but the provider currently refuses generation across the tested
  current model families. The same key/model through Google's documented
  OpenAI-compatible endpoint also returned HTTP 429, so this is not a native
  Gemini transport defect. No source change or route change was made.

### P24 latest exact upstream comparison — 2026-08-27

- The canonical five-node comparison was rerun after the Gemini and installed
  runtime checks. It returned `3 passed, 2 failed`; only accepted historical
  IDs 2 and 3 failed, while IDs 1, 4, and 5 passed. This is a reduction from
  the earlier `3 failed, 2 passed` observation inside the accepted historical
  whitelist, not a new or different regression.
- The two failing nodes were the FTS5 context-enrichment projection test and
  the `sort` leading-dash program-payload test. The exact command and raw
  result are retained in the session evidence; no upstream bug was changed.
- A fresh deterministic read-only check of the registered Randevu project
  returned `Tests: 165 passed, 0 failed.` A bounded installed Qwen3-4B coding
  qualification request was also attempted with explicit no-edit/no-OpenHands
  constraints, but produced no final agent response before it was stopped;
  the project worktree was unchanged. This is supporting evidence only, not a
  P24.9 coding-agent acceptance.

### P24 bounded native-browser replay and local runtime recovery — 2026-08-27

- The installed package was rebuilt from source `4bfe7add708935f9d364dc65364e5c58e58c9144` and its manifest was verified against the pinned upstream commit and baseline merge. The source browser suite returned `17 passed`; the broader targeted Hafiye suite returned `153 passed`; Ruff and `git diff --check` were clean.
- A fresh installed Desktop Composer run used the actual model picker to select `LOCAL (127.0.0.1:11435) → Qwen3 4b Q4_k_m.Gguf`, which resolved to `custom:local-(127.0.0.1:11435)` and the GGUF model path. The real Composer submission reached the local provider path but ended with the visible provider error `Context length exceeded (136 tokens)` before a verified browser result or clean final response. P24.10 remains NOT ACCEPTED.
- Gateway evidence for that run recorded local Qwen3 context failures at approximately 6,571 and 3,868 input tokens. The managed llama.cpp log also recorded stale long-running slots, KV-cache allocation failures, and context overflow. This is retained as KI-060 host/model-runtime pressure; it is not evidence of a wrong Gemini key or a new Hafiye routing defect.
- The managed local server was then recovered with `/usr/bin/hafiye runtime server restart qwen3-4b-q4_k_m --backend AUTO --context-size 65536`. The post-recovery health check reported the Qwen3 model ready on port 11435, requested backend `AUTO`, selected backend `CUDA`, and HTTP health 200. No route configuration was changed; the product route remains `gemini/gemini-3.1-flash-lite` with `NORMAL` privacy.
- The new bounded-state source mitigation prevents the previously observed unbounded accessibility payload at the tool boundary, but it does not by itself satisfy the local browser acceptance. P24.9, P24.10, P24.12, physical voice/recovery checks, P23 replays, and the explicitly deferred offline replay remain open. No P25 or release tag was created.
- Final post-source regression rerun after `4bfe7add` completed with targeted backend `153 passed`, P24 UI `93 passed`, Desktop `npm run typecheck` exit 0, packaging tests `15 passed`, and the canonical upstream comparison `3 passed, 2 failed`. The two failures are accepted historical whitelist IDs 2 and 3; no new/different failure was found. The repository was clean before this documentation update.

### P24 local runtime slot hardening — 2026-08-27

- A real installed Qwen3-4B comparison isolated a resource contribution in the
  managed llama.cpp server. With the upstream automatic slot count, the server
  initialized four 65K slots and a terminal agent attempt repeatedly invoked
  the same tool until the 120-second bound. With `LLAMA_ARG_N_PARALLEL=1`, the
  same installed Hafiye path wrote/read a `/tmp` marker and returned its final
  marker in about 24 seconds.
- Source commit `bc8151b42f0e35d4e9b908b5696adeb51a92d86b` now applies
  `--parallel 1` to Qwen3 contexts above 40,960 only. The change is covered by
  `tests/hermes_cli/test_local_runtime.py` (`14 passed`) and leaves other model
  families and smaller contexts on llama.cpp's upstream behavior.
- The package was rebuilt and installed through the existing root broker. The
  installed manifest reports source `bc8151b42f0e35d4e9b908b5696adeb51a92d86b`,
  pinned upstream `f293e7206b4ddd66042329442c6afebc19a8808d`, and baseline merge
  `2ac06b131a237916432503ac67bbcada6dbea39e`. An environment-free Qwen3-4B
  restart logged `n_slots=1`, selected `CUDA` under `AUTO`, and returned
  ready/HTTP-200 health; package doctor remains `ok=true`, `blockers=[]`.
- The subsequent installed local Qwen3 attempt still repeated a `log` action
  instead of returning a clean final response, and the bounded native-browser
  attempt still lacked an actionable AT-SPI tree. No browser/coding acceptance
  is claimed; KI-060 remains open as a practical local-model limitation.
- Post-change targeted local/browser/policy/runtime tests returned `213 passed`.
  The exact historical upstream comparison returned `3 passed, 2 failed`; only
  accepted whitelist IDs 2 and 3 failed. Gemini remains the configured
  `NORMAL` route, with the same Secret-Service credential and current provider
  quota blocker KI-059; no credential was printed or written to the repository.

### P24 installed Qwen3-14B Composer smoke and Gemini credential probe — 2026-08-27

- A real isolated launch of the installed `/usr/lib/hafiye/desktop/hafiye-desktop`
  used the actual Composer UI, the installed gateway, and the agent-qualified
  Qwen3-14B GGUF route. The UI showed `Qwen3 14b Q4_k_m.Gguf · Med` and
  `Gateway ready`. The natural-language Composer task created
  `/tmp/hafiye-p24-qwen14-composer-20260827-2.txt`; the visible tool trace
  showed the file write and `Read ... 79ms`, and independent host inspection
  found the exact expected file content. This is real installed tool-path
  evidence, but the 130-second bounded capture still showed an
  `assistant-stream` at its boundary; a stable final assistant response was
  not accepted, so P24.9/P24.11/P24.14 remain open.
- The latest installed `/usr/bin/hafiye ask --provider gemini
  --model gemini-3.1-flash-lite` probe used the configured Secret Service
  credential and returned the provider's HTTP 429
  `RESOURCE_EXHAUSTED` / `prepayment credits are depleted` response after
  retries. `hafiye config check` reported both Gemini aliases hydrated; no raw
  credential was printed or written.
- After the tests, the temporary 14B catalog entry was removed and the
  managed server was restored to Qwen3-4B. Health is HTTP 200 with
  `requested_backend=AUTO`, `selected_backend=CUDA`; the product route is
  restored to `gemini/gemini-3.1-flash-lite` with `NORMAL` privacy.
- No source changed in this checkpoint. The current Hafiye source remains
  `bc8151b42f0e35d4e9b908b5696adeb51a92d86b`; pinned upstream and baseline
  merge identities remain unchanged. P24 is still open.

### P24 wake configuration and backend readiness recheck — 2026-08-27

- To align the installed Jarvis behavior with the requested always-ready
  workflow, the supported config command set `wake_word.enabled=true` and
  `voice.auto_tts=true`. The live values are now enabled; the configured wake
  phrase is `Hafiye`, the provider is `openwakeword`, STT remains local, and
  voice barge-in remains enabled. This is configuration evidence only and does
  not replace the required physical microphone acceptance.
- An authenticated local JSON-RPC probe against the real gateway called
  `wake.start` with the GUI/client-capture path and then `wake.status`. It
  returned `started=true`, followed by `listening=true`, `owned_by_caller=true`,
  `available=true`, `enabled=true`, phrase `Hafiye`, and `capture=client`.
  The probe transport was closed afterward, so no synthetic event is counted
  as P24 physical wake acceptance.
- `hafiye-gateway.service` remains enabled/active and `/api/health` returns
  HTTP 200. The helper command `hafiye gateway restart` declined because user
  linger is disabled; no linger or sudoers change was made. The systemd user
  service was not considered unhealthy and was left running.
- The active Gemini Secret Service credential still passes model discovery,
  but fresh generation calls return provider HTTP 429
  `RESOURCE_EXHAUSTED` / `prepayment credits are depleted`; this is KI-059,
  not a key-identity mismatch. P24 remains open.

### P24 legacy GNOME emergency binding repair and credential confirmation — 2026-08-27

- Source commit `ee380ba75a21b8559ccb523b77b8cd511359a9ff` repairs the
  reserved GNOME `Control+Super+Escape` binding when an earlier Hafiye
  installation still points at the legacy Hermes launcher. The fallback now
  treats the reserved name plus accelerator as the ownership marker, rewrites
  only that stale command, and continues to reject unrelated user keybindings.
- The focused Electron command
  `npm exec vitest run electron/gnome-emergency-stop.test.ts
  electron/emergency-stop-shortcut.test.ts --project electron --reporter=dot`
  passed with the configured Electron project (`111` files passed; `1,559`
  tests passed, `3` skipped). `npm run typecheck` exited 0. The added test
  covers repair of the legacy Hermes target and preservation of the emergency
  argument.
- The production Desktop was repacked, `dist/hafiye_0.20.5_amd64.deb` was
  rebuilt, and it was reinstalled through the existing `hafiye-rootd` path
  with `apt-get --reinstall`. The installed manifest now reports source
  `ee380ba75a21b8559ccb523b77b8cd511359a9ff`, pinned upstream
  `f293e7206b4ddd66042329442c6afebc19a8808d`, and baseline merge
  `2ac06b131a237916432503ac67bbcada6dbea39e`. Packaging tests returned
  `15 passed in 63.38s`; package doctor is OK with only the existing optional
  `cargo: not found` warning, and the gateway health endpoint is HTTP 200.
- A real launch of the installed binary updated the live GNOME value to
  `'/usr/bin/hafiye' emergency-stop --reason=global-hotkey`. The Desktop is
  running as the normal user, visible in the GNOME window list, and connected
  to the active `hafiye-gateway.service`. This is binding-repair evidence; a
  physical emergency shortcut during an active managed desktop action is still
  required before P24.14/P23.15 can be accepted.
- The user-supplied Gemini credential is correctly resolved through Linux
  Secret Service and model discovery remains HTTP 200. Current Gemini
  generation attempts still return HTTP 429 `RESOURCE_EXHAUSTED` / `prepayment
  credits are depleted`; this remains KI-059 and is not a wrong-key diagnosis.
- The exact five historical upstream nodes returned `3 passed, 2 failed`:
  only accepted whitelist IDs 2 and 3 failed; IDs 1, 4, and 5 passed. No new
  or different upstream regression was found. P24 remains open; no P25 or
  release tag was created.

### P24 installed Qwen3-14B coding replay and Gemini credential recheck — 2026-08-27

- A controlled installed Desktop replay used the real Composer `Gönder` path,
  the installed gateway, and the agent-qualified Qwen3-14B GGUF route. The
  temporary model registration exposed a 65,536-token context and the managed
  llama.cpp server selected `AUTO → CUDA` with one slot.
- Exact prompt `Randevu projesini açıp bug fix yapalım` created session
  `20260827_143425_5bddd9`. The gateway recorded the local custom provider,
  the real Randevu project path, two model calls, and one `project_switch`
  tool call. Project registry resolution succeeded and returned
  `/home/tolga/projects/randevu-musteri-saas`; the agent then asked for more
  bug details. It did not reach IDE/workspace focus, repository diagnosis,
  diagnostics/tests, OpenHands delegation, independent verification, or a
  stable coding completion. This is supporting real-agent evidence only, not
  a P24.9 or P24.14 acceptance. No Hafiye source change was made.
- The temporary 14B catalog mapping was removed after the replay. The installed
  configuration again exposes only the Qwen3-4B GGUF custom model; the managed
  server is ready on `127.0.0.1:11435`, and its command/log reports
  `n_slots=1`, requested backend `AUTO`, selected backend `CUDA`, and HTTP
  health 200. The product route remains `gemini/gemini-3.1-flash-lite` with
  `NORMAL` privacy. `hafiye-gateway.service` is enabled/active and its health
  endpoint is HTTP 200.
- `hafiye config check` exited 0 and showed both `GEMINI_API_KEY` and
  `GOOGLE_API_KEY` hydrated through Linux Secret Service. A fresh installed
  `hafiye ask --provider gemini --model gemini-3.1-flash-lite` used that
  credential and again received Gemini HTTP 429
  `RESOURCE_EXHAUSTED` / `prepayment credits are depleted` after retries.
  This confirms the credential is the configured key and the current blocker
  is provider-side generation/quota availability; no raw credential was
  printed or written.
- P24 remains open. Gemini generation, coding/browser completion, physical
  voice/barge-in/emergency acceptance, reconnect/re-arm, and the explicitly
  deferred offline replay remain unaccepted. No P25 or release tag was created.

### P24 installed acceptance recheck — 2026-08-27

- Fresh targeted regression checks after restoring the test runtime passed:
  backend policy/routing/native-browser `35 passed`; voice, gateway command,
  TTS-stream, completion and voice-reply coverage `255 passed, 12 skipped,
  2 warnings`; Desktop Jarvis/wake/composer/voice UI `113 passed`; and
  Electron Composer/wake/emergency coverage `40 passed`.
- Installed checks report llama.cpp `ok=true`, `blockers=[]`, Qwen3-4B ready
  with `AUTO → CUDA` and one server slot; whisper.cpp/Piper are ready with
  local CUDA selection; computer-use-linux readiness booleans remain true
  with `blockers=[]`; package doctor is OK with only the existing optional
  `cargo: not found` warning. `hafiye-gateway.service` is enabled/active and
  `/api/health` returns HTTP 200.
- These are support/regression results only. The real physical wake,
  transcript, short acknowledgement, coding/browser completion, three-cycle
  re-arm, barge-in, emergency-stop and gateway-recovery acceptances remain
  unverified; the offline replay remains explicitly deferred. P24 is still
  open and no release tag or P25 was created.

### P24 gateway restart/reconnect support recheck — 2026-08-27

- A real `systemctl --user restart hafiye-gateway.service` was performed from
  the installed environment. The gateway main PID changed from `17216` to
  `87501`; after the normal startup delay, `/api/health` returned HTTP 200 with
  `ok=true`, and the service remained `enabled` and `active`.
- A fresh authenticated WebSocket connection received `gateway.ready`. A
  follow-up `wake.status` reported `owner_surface=gui`, `enabled=true`,
  `available=true`, and `capture=client`; the diagnostic connection itself
  reported `owned_by_caller=false`, so it did not steal the Desktop wake lease.
  The installed Desktop process remained running and the gateway log recorded
  the expected Secret Service hydration of two provider aliases.
- This is real gateway/reconnect/re-arm support evidence. It is not the full
  P24.12 acceptance because no recoverable long-running Composer task was
  active during the restart, and it does not replace the required physical
  wake, voice, barge-in, emergency-stop, coding, browser, or repeated-cycle
  acceptance. The route was not changed: Gemini/NORMAL remains configured.

### P24 post-restart local route verification — 2026-08-27

- The corrected installed command
  `/usr/bin/hafiye --reasoning none ask --provider custom --model
  /home/tolga/.local/share/hafiye/models/qwen3-4b-q4_k_m.gguf --toolsets
  terminal ...` exited `0` after the gateway restart. The real agent used the
  local Qwen3-4B route to create and read a fresh `/tmp` marker; independent
  host inspection matched `P24_RESTART_LOCAL_CUDA_TOOL_OK` exactly.
- The installed manifest still reports source
  `ee380ba75a21b8559ccb523b77b8cd511359a9ff`, pinned upstream
  `f293e7206b4ddd66042329442c6afebc19a8808d`, and baseline merge
  `2ac06b131a237916432503ac67bbcada6dbea39e`. Computer-use readiness through
  `/home/tolga/.local/bin/computer-use-linux doctor` remains true for all four
  required capabilities with `blockers=[]`.
- This is local route and recovery support evidence only. Qwen3 practical
  browser/coding qualification, physical voice acceptance, and active-turn
  restart recovery remain open; the persistent product route remains
  Gemini/NORMAL.

### P24 packaged managed STT module-path repair — 2026-08-27

- A real installed Desktop log exposed a Hafiye packaging defect: the managed
  local STT child failed with `ModuleNotFoundError: No module named
  'hermes_cli'` when launched from outside the source checkout. The generic
  subprocess environment sanitizer correctly removed the backend's internal
  `PYTHONPATH`, but the Hafiye-owned managed `hermes_cli.voice_runtime` child
  still needed that exact installed module root.
- Source commit `139f5f9491aa46adebbca932b255ad2b87141702` adds a narrow managed
  runtime path helper. It restores only the exact Hafiye backend root for the
  managed local STT command after sanitization; user-supplied STT commands keep
  the ordinary sanitized environment.
- The focused source and voice/gateway regression command returned `311 passed,
  12 skipped, 2 warnings`. The production Desktop was repacked, the Debian
  package was rebuilt and reinstalled through `hafiye-rootd`, and package doctor
  remained OK with only the existing optional `cargo: not found` warning.
- From `/tmp`, an authenticated real installed `/api/audio/transcribe` request
  returned HTTP 200 with `provider=local_command` and the managed transcript
  (`[...müzik çalıyor...]`); the former `hermes_cli` import error did not recur.
  Gateway health remained HTTP 200 and the installed manifest carries source
  `139f5f949`, pinned upstream `f293e7206b4ddd66042329442c6afebc19a8808d`, and
  baseline merge `2ac06b131a237916432503ac67bbcada6dbea39e`.
- Post-fix Desktop verification passed: the seven-file Jarvis/voice UI matrix
  returned `93 passed`, `npm run typecheck` exited 0, the Electron project
  returned `1,616 passed, 3 skipped`, and packaging tests returned `15 passed`.
  The exact historical five-node comparison returned `3 passed, 2 failed`;
  only accepted whitelist IDs 2 and 3 failed. `git diff --check` is clean.
- This repairs the packaged STT boundary but is not a physical P24 wake,
  transcript, speech, barge-in, or full Jarvis acceptance. P24 remains open.

## P24 pinned Qwen3.8-27B catalog integration — 2026-08-27

- Source commit `e00da6acd52d00a6bdb0f4c7094d01d154b26d57` adds
  `unsloth/Qwen3.8-27B-GGUF` / `Qwen3.8-27B-UD-IQ1_S.gguf` to the
  backend-owned production catalog. The catalog pins Hugging Face revision
  `4ca720788d1e01f1bff70c033e0d0028fd02e502`, SHA-256
  `3895b6eaa91e705c06ad1938d16c22e86f073c6a67df86260a1da79be3d1f887`,
  and size `6,192,222,208` bytes.
- Settings and first-run onboarding now expose one-click verified download.
  Existing manual GGUF import/download remains available. The Desktop uses a
  six-hour bounded request for multi-gigabyte downloads while the backend
  keeps resumable `.part` behavior and refuses to overwrite a conflicting
  registered model ID.
- Catalog membership is not qualification: Qwen3.8 is
  `qualification=pending`, is not selected as the active/default agent route,
  and will remain so until the existing registry qualification contract has
  real tool/coding/browser evidence. Qwen3-14B qualification and KI-046 are
  unchanged.
- The original Qwen3 40,960-token YaRN workaround is no longer applied to the
  Qwen3.5/Qwen3.8 family, whose GGUF metadata supplies its larger native
  context. The managed pinned llama.cpp checkout contains the `qwen35`
  architecture implementation.
- Follow-up source commit `beec5bd9c061b4c538e7916ee152c29264f6b8ad`
  fixes the shared Desktop byte formatter so the catalog displays this file as
  `5.8 GiB`, not an incorrectly skipped-unit value; its UI regression test
  passed and Desktop typecheck remained clean.
- Verification: local-runtime pytest `17 passed`; focused Settings/onboarding
  Vitest `6 passed`; full Desktop UI `5,575 passed`; Desktop typecheck exit 0;
  Ruff and Python compilation passed; production `npm run pack` and Debian
  build passed. The exact historical five-node comparison returned `3 passed,
  2 failed`, only accepted whitelist IDs 2 and 3.
- The Debian package was rebuilt/reinstalled through `hafiye-rootd`. Installed
  manifest source is `beec5bd9c`, package doctor is OK with only the existing
  optional `cargo: not found` warning, gateway is active/HTTP 200, and the
  authenticated installed `/api/local-runtime/models` response reports the
  pinned entry as `downloadable`. The 6.19 GB model was intentionally not
  auto-downloaded.
- P24 remains open. This catalog integration does not satisfy P24.9–P24.12 or
  the physical P24.14 acceptance, and the user-deferred offline replay remains
  unaccepted.

## P24 security-research model catalog extension — 2026-08-27

- Source commit `53e783e8c8ee6c88b2ecff2cff4954512deb386a` adds two
  backend-owned catalog entries without adding Ollama as an inference runtime:
  `orcarouter/Qwen3.8-27B-Uncensored:q4_K_M` is imported from its immutable
  Ollama model-layer digest into Hafiye-managed llama.cpp, while
  `orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF` uses the exact gated Hugging
  Face revision and both IQ2_M shards.
- Desktop Settings and first-run onboarding send only the trusted catalog ID.
  The backend owns URLs, revisions, filenames, byte sizes and SHA-256 values;
  downloads resume, verify every shard, reject conflicting IDs, repair a
  missing split shard, and remove corrupt partial content. Gated downloads use
  the Secret-Service-hydrated `HF_TOKEN` and do not expose it to the renderer.
- Neither model was automatically downloaded. Both report
  `qualification=pending` and remain non-default. The Ollama model layer is
  16,810,714,496 bytes and omits the separate vision projector; Flash Next
  IQ2_M totals 80,086,292,992 bytes and requires approved Hugging Face access.
  Their uncensored/security-research purpose does not bypass KI-043, rootd,
  privacy, audit, or emergency-stop boundaries. KI-046 remains open.
- Verification: local-runtime backend `20 passed`; focused Settings/onboarding
  UI `7 passed`; full Desktop UI `586 files / 5,576 passed`; Desktop typecheck,
  Ruff, Python compilation and `git diff --check` passed. The canonical
  upstream comparison returned `3 passed, 2 failed`, only accepted historical
  IDs 2 and 3. Packaging tests returned `8 passed`.
- The production Desktop and Debian package were rebuilt and installed through
  `hafiye-rootd`. Package manifest and Desktop stamp carry source `53e783e8c`;
  package doctor is OK with only optional `cargo: not found`; gateway is
  enabled/active and healthy. The authenticated installed catalog reports both
  new entries as `downloadable`, `qualification=pending`, with exact source and
  auth metadata. The installed Desktop was restarted from the packaged binary.
- P24 remains open; no phase, release tag, default route, or model qualification
  state changed.

## P24 installed system-tray hardening — 2026-08-27

- Source/test commit `25f1d0fd6bbf7c646534509cd2d00c9717a0b2c9`
  replaces the stale P3 tray placeholders with a stateful menu. New Task,
  Settings and Recent Tasks reveal/focus the hidden primary window; microphone
  enablement uses persisted `wake.start/stop`; voice pause stops active TTS and
  persists `voice.auto_tts`; privacy mode writes the existing
  `hafiye.privacy_mode`; computer-control pause/resume uses the existing
  `emergency.stop/resume` gate. Emergency Stop, core lifecycle, Composer,
  Desktop and Logs retain their existing boundaries.
- The menu state is renderer-owned and pushed through the preload IPC bridge;
  Electron only renders normalized cached labels. `FULL_AUTONOMOUS` does not
  bypass emergency/root gating, and no root-capable path was added.
- Verification: targeted tray/wake/emergency tests `29 passed`; Desktop
  typecheck passed; full UI `587 files / 5,579 passed`; full Electron `117
  passed, 1 skipped / 1,618 passed, 3 skipped`; packaging contract `8 passed`;
  exact upstream comparison `3 passed, 2 failed`, only accepted IDs 2 and 3.
- The Debian package was rebuilt/reinstalled through `hafiye-rootd`. Installed
  stamp is clean source `25f1d0fd6`; gateway is active/listening on
  `127.0.0.1:9120`; packaged Desktop PID `2803441` is running hidden. GNOME's
  real StatusNotifier watcher reports Hafiye `Active`, and its live dbusmenu
  exposes enabled Composer/Desktop/task/microphone/voice/emergency/computer-
  control/privacy/settings/log/core lifecycle entries with stateful labels.
- Direct synthetic `com.canonical.dbusmenu.Event` injection was rejected by
  Electron's Linux tray adapter and is not recorded as a click PASS. The real
  callback/IPC/action boundaries are covered by source tests; a user can now
  click the installed menu for final physical confirmation. KI-064 is resolved
  at source/package level. P24 remains open for its unrelated physical Jarvis
  acceptance items.

## P24 Local GGUF catalog visibility repair — 2026-08-27

- The user's real Model-page screenshot proved that `Local GGUF Runtime` was
  absent even though the installed backend returned all three Qwen3.8 catalog
  entries. Root cause: `ModelSettingsSkeleton` rendered
  `LocalRuntimeSettings`, but the successful/non-loading `ModelSettings` tree
  omitted it entirely.
- Source commit `ecace19727b8f26d372e1ea6e18ed05706ad5ef9`
  mounts the same component between main-model defaults and auxiliary models in
  the real loaded page. A regression test asserts that the heading and both
  runtime API calls remain present after model-page loading completes.
- Focused Model/local-runtime UI tests returned `26 passed`; full Desktop UI
  returned `588 files / 5,581 passed`; Desktop typecheck passed. The exact
  historical comparison returned `3 passed, 2 failed`, only accepted IDs 2
  and 3.
- Production Desktop/package build and rootd reinstall passed. Installed stamp
  is clean source `ecace1972`; gateway is active; the packaged Hafiye window is
  visible on the Models route. Its authenticated local-runtime response lists
  Qwen3.8 UD-IQ1_S, Qwen3.8 Uncensored Q4_K_M and Flash Next Uncensored IQ2_M
  as downloadable. KI-065 is resolved; no model was downloaded or promoted to
  qualified/default state.

## P24 managed local-runtime Turkish localization repair — 2026-08-27

- Source commit `9f315f6a6b20d7f37e5a933b6f810c3b8ef975e0` removes the
  hard-coded English boundary from the loaded Model page's managed GGUF
  controls. Runtime headings, actions, placeholders, status copy, trusted
  catalog purpose/resource warnings and conflict/auth messages now resolve
  through the existing Desktop i18n state. The Settings navigation entries
  now render `Hafiye Kontrol Merkezi` and `Bilgisayar` in Turkish.
- Trusted catalog localization is keyed by the backend-owned catalog ID and
  does not alter model capability, qualification, default-route or download
  state. Unknown catalog entries continue to display backend-provided copy.
- Verification: focused i18n/runtime UI `13 passed`; full Desktop UI `588
  files / 5,582 passed`; Desktop typecheck and changed-file ESLint passed;
  `git diff --check` passed. The repository-wide lint still reports nine
  unrelated pre-existing errors outside this patch.
- The exact historical five-node comparison returned `3 passed, 2 failed`;
  only accepted whitelist IDs 2 and 3 failed. No new/different regression was
  found.
- Production pack/deb and root-broker reinstall passed. Installed manifest
  and Desktop stamp carry source `9f315f6a6`; package doctor is OK with only
  the existing optional `cargo: not found` warning. A real installed Electron
  render showed all target Turkish labels and catalog warnings; DOM inspection
  confirmed `Download verified GGUF` was absent and
  `Doğrulanmış GGUF’u indir` was present. KI-066 is resolved.
- P24 remains open. No model was downloaded, qualified or made default, and
  none of the deferred physical Jarvis acceptance rows were promoted.
