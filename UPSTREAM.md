# Upstream Hermes State

## Remotes

origin   https://github.com/tolgaakcaoglu/hafiye.git
upstream https://github.com/NousResearch/hermes-agent.git

## Separate commit identities

- Pinned upstream commit:
  f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit:
  2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye source HEAD (pinned Qwen3.8 security-research catalog/download
  checkpoint;
  earlier Jarvis interaction-loop, implementation-audit, model identity,
  Debian bootstrap, Desktop local-GGUF download, Electron packaging,
  computer-use MCP startup-gate, and KI-043 source/test commits remain below):
  53e783e8c8ee6c88b2ecff2cff4954512deb386a

These SHA values are intentionally separate. The first is the Hermes source
pin, the second is the history-preserving Hafiye baseline merge, and the third
is the latest Hafiye product source commit. Documentation closure commits
after the source commit do not change the product source pin.

## Pinned Hermes base

- Upstream ref: upstream/main
- Pinned commit subject:
  fix(dashboard): detect stale code after hermes update and refuse model picker
  with clear 503 (#86207)
- Last fetch: 2026-08-23
- Hafiye integration branch: main

Development began on `hafiye/p0`, created from upstream/main and merged with
the original Hafiye documentation history using --allow-unrelated-histories.
On 2026-08-26, local `main` was fast-forwarded to the completed Hafiye history.
The historical `hafiye/p0` pointer is retained temporarily as a safety
reference. Both original histories remain reachable; Hermes history is not
rewritten.

## Sync and conflicts

- The initial merge had one add/add conflict in AGENTS.md. The current file
  carries the Hafiye binding instructions first and preserves the upstream
  Hermes development guide below them.
- Hafiye source implementation was added after the P0 baseline in separable
  commits; no upstream commit was rewritten.
- `main` tracks origin/main. The separate upstream remote remains the Hermes
  source of truth for fetches and future upstream comparisons.
- Internal Hermes names remain where they are part of upstream compatibility:
  Python module names, IPC keys, HERMES_* environment names, the legacy Hermes
  protocol scheme, and the upstream npm package name.

## Hafiye patch groups

The Hafiye source history contains these separable logical groups:

- branding: normal user-facing CLI and Desktop identity boundary.
- xdg-paths: shared Hafiye config, data, state, and cache roots.
- legacy-migration: conservative non-destructive import from ~/.hermes.
- desktop-assets: neutral H monogram assets and package identity.
- desktop-remote-roots: Desktop and remote lifecycle root alignment.
- persistent-gateway: user-scoped authenticated Hafiye backend service.
- composer-tray-autostart: Composer lifecycle, tray, and XDG autostart.
- local-model-runtime: managed llama.cpp/GGUF runtime, registry, server,
  Desktop controls, the Hugging Face GGUF download surface, and a backend-owned
  integrity-pinned production catalog.
- gateway-environment-guard: shared subprocess environment construction for the
  persistent gateway child process.
- providers-secret-service: provider credential ownership, Linux Secret
  Service references, local/remote provider paths, and Desktop provider wiring.
- providers-secret-service-xdg: bind provider Secret Service references to the
  active config root under the default XDG config/data split.
- routing-privacy: Hafiye route slots, task-scoped routing overrides, privacy
  modes, legal fallback filtering, and OFFLINE tool enforcement.
- gateway-contract-follow-up: tolerate non-mapping cache fixtures and preserve
  upstream fallback-refresh call contracts while applying per-turn Hafiye
  fallback routes.
- host-execution-policy: shared Hafiye host-tool policy classification,
  existing Hermes approval-surface enforcement, fail-closed read-only and
  confirmation behavior, and the real Desktop execution-policy setting.
- root-broker: strict local Unix-socket privileged-operation broker,
  `hafiye-rootd.service`, peer authentication, audit trail, root-broker CLI,
  and packaged `hafiye-rootd` entrypoint.
- packaged-runtime-integrity: package-aware gateway/rootd launchers, caller-CWD
  isolation, package-source manifest checks, and packaged doctor recognition.
- product-observability: Hafiye status/doctor identity, persistent component
  logs, and the owner-only canonical redacted audit stream for shell, route,
  privacy, cancellation, and root-RPC events.
- browser-routing: structured Hermes browser reuse and explicit native browser
  routing through the managed computer-use-linux MCP provider; the P24
  follow-up also recovers one unique visible browser when Composer owns focus
  and refuses ambiguous target selection.
- structured-browser-download: current official agent-browser download
  command, absolute destination validation, and user-cache Chromium discovery.
- voice-local-stack: managed whisper.cpp source/build/model runtime with
  CUDA→Vulkan→CPU selection, Hermes local-STT command routing, managed Piper
  process boundary, Turkish voice API/preview, and Desktop microphone/voice
  settings.
- hafiye-wakeword: official openWakeWord training checkout, reproducible
  Turkish Piper-based `hafiye.onnx` export, default wake configuration,
  Desktop wake settings, and minimized-window client capture.
- cancellation-emergency-stop: one gateway-owned cancellation controller,
  durable ESTOP/root-RPC gating, Desktop/voice/tray/CLI stop surfaces, and
  GNOME Wayland global-keybinding fallback.
- jarvis-interaction-loop: one canonical Desktop interaction reducer,
  wake-to-Composer activation, visible Turkish transcript publication,
  concise Piper acknowledgement/completion speech, task/tool/model/progress
  locality state, local-Qwen compatibility, native-browser preference, and
  installed-package regression coverage.
- desktop-emergency-binding-repair: repair an owned legacy GNOME emergency
  binding during Desktop startup without overwriting unrelated user shortcuts.

Future changes should remain separable under the roadmap groups:

- persistent-gateway
- composer-tray-autostart
- local-model-runtime
- routing
- linux-computer-use
- root-broker
- browser-routing
- structured-browser-download
- voice-local-stack
- hafiye-wakeword
- project-registry
- openhands
- control-center
- packaging

## Accepted upstream test baseline

Before Hafiye source changes, the canonical backend suite with relevant
optional SDKs completed with 36,903 passed, 5 failed, and 320 skipped. The
exact five test IDs were:

1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

After the P24 native-browser source checkpoint
`8b7c29aa8197595a479e35bb85ef081cec2b7a11`, the latest exact-node comparison
measured `2 failed, 3 passed`. Only historical items 2 and 3 reproduced; items
1, 4, and 5 passed. No new or different Hafiye regression was found. The
earlier local browser reconnect diagnostic is tracked as KI-019, and the
current observed comparison subset is therefore items 2 and 3.
The exact five remain the historical accepted whitelist; fewer failures update
the current baseline, while any new/different ID is investigated as a
regression. The upstream baseline bugs are not fixed by Hafiye.

## Computer-use-linux pinned source

- Repository: https://github.com/agent-sh/computer-use-linux
- Pinned source commit:
  94736dc3e0dca56acfc89752c26869fb9ed01202
- Source checkout used for final setup:
  /home/tolga/.cache/hafiye/computer-use-linux
- Source package version: 0.4.10
- Official final P0 setup path: the pinned checkout's ./install.sh flow,
  including its official system-dependency, Rust, build, AT-SPI, ydotoold, and
  GNOME extension steps. The setup and setup-window-targeting commands remain
  available where the installer or doctor requires them.
- Setup result: ./install.sh --package-manager apt installed required Debian
  packages, Rustup stable/Cargo 1.98.0, source-built binaries, AT-SPI,
  ydotool/ydotoold, and the GNOME window-targeting extension. After relogin,
  the checkout reran ./install.sh --skip-system-deps
  --skip-gnome-extension; source build, AT-SPI, user-service setup, and doctor
  passed.
- sudo usermod -aG input tolga was completed; /dev/uinput is root:input 0660
  and read/write access is verified in the new session.
- Ubuntu's packaged /usr/lib/systemd/user/ydotool.service was already active
  and owns the ydotool socket. The duplicate generated ydotoold.service was
  disabled/removed after its same-socket collision; a separate root
  user-manager ydotoold instance was also disabled.
- The source's expected 0.4.10 GitHub release asset returned HTTP 404. Released
  npm 0.4.9 was used only for historical diagnostic evidence and is not the
  final setup path.
- Historical and final doctor reports are saved under docs/p0:
  computer-use-linux-doctor-report.json,
  computer-use-linux-source-setup-doctor-report.json, and
  computer-use-linux-final-doctor-report.json.
- Final pinned-source doctor output has all required readiness booleans true and
  blockers=[]; a real computer-use-linux windows query returned the focused
  desktop window through gnome-shell-extension.

P0 computer-use acceptance requires:

- can_register_mcp_tools = true
- can_build_accessibility_tree = true
- can_send_development_input = true
- can_query_windows = true
- blockers = []

## P1 source validation

- Current source commit: 34f1d8c2472e6b70b71bbdbfc9d3292761dbb67b.
- Python identity/XDG targeted tests: 153 passed, 6 skipped.
- Desktop full suite: 691 files passed, 7,149 tests passed, 3 skipped.
- Desktop typecheck, clean production build, and Linux unpacked packaging passed.
- The clean Desktop build stamp records the current source commit and dirty=false.
- The source changes are limited to the P1 identity/path boundary and tests;
  upstream internal compatibility identifiers remain intentionally intact.

## P2 source validation

- Current Hafiye source commit: e2e22c10b49ec01ef7d8420f1158668718b03fa9.
- The persistent gateway is a Hafiye lifecycle layer; the upstream Hermes
  gateway service and internal module names remain intact.
- Hafiye adds a separate user-scoped `hafiye-gateway.service`, stable loopback
  binding at `127.0.0.1:9120`, owner-only token/descriptor files in the Hafiye
  XDG state root, and a service-first Desktop connection path with an existing
  ephemeral fallback for installation/development scenarios.
- The persistent-gateway Python tests, Desktop tests/typecheck/build, real
  systemd service, authenticated HTTP/WS probe, Desktop close persistence, and
  authenticated restart control passed. No upstream commit was rewritten.

## P3 source validation

- Current Hafiye source commit: e33bb456d109.
- Hermes Quick Entry remains the implementation base; Hafiye adds the
  Composer lifecycle policy, Hafiye naming/surfaces, tray actions, and XDG
  autostart integration without mass-renaming upstream modules or IPC keys.
- The Composer settings are main-process-owned and persisted in the Desktop
  user-data root. The persistent `hafiye-gateway.service` remains independent
  of Desktop window lifetime.
- Composer lifecycle tests, the complete Desktop UI/Electron test projects,
  typecheck, clean production build, real Wayland tray startup, close-to-tray
  behavior, persistent service survival, and exact autostart command passed.
- The host GNOME input-source-backward binding currently conflicts with the
  mandated default `Super+Shift+Space`; Hafiye reports the conflict and leaves
  the user binding unchanged. This is an environment warning, not an upstream
  source change.

## P4 source validation

- Local runtime source commit: `87cbfb34337f043363ba8851c485fea5ea66de0b`.
- Follow-up gateway environment guard commit:
  `d912a85ee5fa21afb1c5304e28c6e3651fb16433`.
- Final cross-platform local-runtime process fix:
  `ae24562fb9dfeeb4dd58752849b4778b2c8606e8`.
- Managed llama.cpp repository: `https://github.com/ggml-org/llama.cpp.git`.
- Managed llama.cpp source commit:
  `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`.
- The runtime manifest records the source repository/commit, requested backend,
  selected backend, compiled backends, binary path, and environment evidence.
  This managed runtime pin is separate from the Hermes upstream pin above.
- The real host build compiled CPU and CUDA; Hafiye AUTO selected CUDA on the
  NVIDIA RTX 3080. The loopback server, GGUF registry, model lifecycle,
  authenticated gateway API, and Desktop settings boundary were verified.
- The clean Desktop production build after P4 closure passed with build stamp
  `955a9c3818fa`; Vite, Electron main/preload bundles, native staging, and
  `assert-dist-built` all passed.
- The corrected full backend regression command completed with the accepted
  upstream baseline and documented timing diagnostics; no new or different
  Hafiye failure was found, and no upstream Hermes bug is being fixed as part
  of P4.
- Follow-up Desktop source/test commit
  `213247d70804ffe9350ad5d0874f79a494fd7dc0` adds the Models-page control for
  the existing Hafiye GGUF download API. It does not change the pinned Hermes
  source, managed llama.cpp architecture, or upstream history.

## P5 source validation

- Provider boundary source commits: `c771c95318516e03450720b5f009dce4017f8600`
  and the shared provider-alias correction
  `15cbe1f6556addbaf694c36999e0c496730a1730`.
- Default-XDG Secret Service lifecycle correction: `45294d3f77a3929731ac29d89d54f5d53c70957d`.
  The lifecycle now writes and hydrates provider references from the active
  config root; the change is covered by a regression test and does not alter
  the upstream Hermes history.
- `keyring==25.7.0` is the Hafiye provider-secret dependency. The real Linux
  Secret Service round-trip passed; Hafiye config retained only keyring refs,
  and no secret value was recorded in project documentation or test output.
- Local CUDA llama.cpp, remote OpenAI-compatible HTTP, provider parity,
  automated Gemini, and Desktop provider/key tests pass. Desktop typecheck and
  production build pass.
- Live Gemini model listing returned HTTP 200 with 50 models and a real Hafiye
  one-shot returned `HAFIYE_GEMINI_LIVE_OK`; P5 is closed. The credential value
  is not recorded here.

## P6 source validation

- Hafiye source commits: `cf6457678b6083c4f783c1a80eef9eba3875ccc0`
  (routing/privacy) and `62b3d5762d49b1ce2872d142c8e5318239b01c5c`
  (gateway cache/fallback contract follow-up).
- The source patch keeps Hermes provider/runtime resolution as the execution
  base and adds the shared `hafiye_policy.py` boundary used by the native
  gateway, API server, one-shot/interactive CLI, AIAgent, tool executor, and
  Desktop settings schema.
- The eight route slots, three privacy modes, task-scoped overrides, route
  locality policy, legal fallback filtering, and OFFLINE network-tool deny
  boundary are covered by targeted tests. No upstream commit was rewritten.

## P7 source validation

- Current Hafiye source commit:
  `404197560629cde55232518c21d3d98b3cbe4988`.
- Hermes remains the execution base: local terminal, process, and filesystem
  tools retain their real non-root host behavior under the default
  `FULL_AUTONOMOUS` policy. Hafiye adds the shared
  `hafiye_execution_policy.py` classifier and config resolver, dispatch-level
  enforcement in `model_tools.py`, combined terminal approval warnings, and
  the `execute_code` one-shot policy grant.
- The existing Hermes approval/guard transport remains the only confirmation
  surface; Hafiye does not create a second prompt or bypass layer. The
  Desktop select is backed by the existing config schema/API and uses the
  exact four policy values.
- P7 targeted Python tests, existing host-tool regression tests, real host
  terminal/file/process smoke, Desktop settings tests, typecheck, and
  production build passed. The full comparison retained only the documented
  accepted baseline plus KI-016/KI-019 diagnostics.
- The pinned Hermes commit
  `f293e7206b4ddd66042329442c6afebc19a8808d` and baseline merge commit
  `2ac06b131a237916432503ac67bbcada6dbea39e` are unchanged. No upstream
  commit was rewritten.

## P8 source validation

- Current Hafiye source commit:
  `4972645e07c408a8f0856bc4f1ee1b1cd62cd63a`.
- `hafiye_rootd.py` is a standard-library-only broker implementation. Its
  wire protocol is one 4-byte length-prefixed strict JSON request per local
  Unix-stream connection; duplicate keys, oversized frames, unknown fields,
  malformed requests, unauthorized peers, and unsupported operations fail
  closed.
- The system service is installed at
  `/usr/lib/systemd/system/hafiye-rootd.service`, runs as `root`, binds only
  `/run/hafiye/root.sock`, and allows only UID 1000 on this host. The socket is
  mode `0600` and no TCP/UDP listener is configured.
- Supported operations are the roadmap-prescribed package, service, privileged
  file-write, power, and root-exec operations. Requests are audited as JSONL
  with peer identity, lifecycle status, durations, and redacted arguments.
- The normal Hafiye CLI remains non-root and exposes the root-broker commands;
  the real broker smoke returned UID 0 to a UID 1000 client, while the real
  `nobody` peer failed with `permission_denied`.
- The first development-v-env `-m hafiye_rootd` systemd entrypoint exposed
  the editable-install/cwd boundary. The service generator now executes the
  packaged module file directly; the corrected unit is active and the issue is
  recorded as resolved KI-021.
- The pinned Hermes commit
  `f293e7206b4ddd66042329442c6afebc19a8808d` and baseline merge commit
  `2ac06b131a237916432503ac67bbcada6dbea39e` remain unchanged. No upstream
  commit was rewritten.

## P9 managed computer-use-linux integration

- External repository: `https://github.com/agent-sh/computer-use-linux`.
- Pinned source commit: `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- Managed checkout: `/home/tolga/.cache/hafiye/computer-use-linux`.
- Resolved binary: `/home/tolga/.local/bin/computer-use-linux`.
- Hafiye source commit: `6d3672e498e1bcb9316e5c7d88c9fc896714630c`.
- Integration boundary: Hafiye adds a reserved in-memory MCP entry to the
  existing Hermes MCP loader and toolset resolver. The user does not need to
  edit `mcp_servers`; session display/DBus/XDG routing variables are passed to
  the stdio child without copying secret environment variables.
- Real discovery connected `hafiye-computer-use-linux` and registered 18 MCP
  tools. The doctor contract normalizes the four roadmap-required readiness
  fields and blockers for the Desktop `Settings → Computer` diagnostics page.
- Real GNOME Wayland E2E passed for window enumeration, AT-SPI tree access,
  Calculator input/result verification, Firefox tab/navigation and app
  switching, VS Code launch, and Files interaction. Firefox focus feedback and
  VS Code's sparse tree are documented as KI-022/KI-023 warnings.
- The pinned Hermes commit
  `f293e7206b4ddd66042329442c6afebc19a8808d` and baseline merge commit
  `2ac06b131a237916432503ac67bbcada6dbea39e` are unchanged. No upstream
  Hermes commit was rewritten.

## P10 browser integration

- Hafiye source commit:
  `5d2354095562d149ff54e58d664c1b042cf50c3e`.
- Structured browser automation remains Hermes' existing `browser_*` path;
  current Hermes Browser Use CLI selection remains intact. Hafiye adds
  `browser_download`, calling the current official
  `agent-browser download <ref> <absolute-path>` command and preserving the
  existing browser extension-router wrapper. The real P10 structured probe
  selected the built-in lane with `browser.backend: off`.
- The current official user-space Chrome cache is recognized under
  `~/.agent-browser/browsers/`; this matches the installed
  `agent-browser@^0.26.0` CLI path without changing Hermes' backend choice.
- Native desktop-browser control is an explicit `browser_native` Hafiye
  adapter. It dispatches only to the already-managed
  `mcp__hafiye_computer_use_linux__*` tools, binds an exact existing window,
  and does not launch a new profile or inspect cookies.
- The native route uses the existing pinned source commit
  `94736dc3e0dca56acfc89752c26869fb9ed01202`; no CUA implementation was
  copied or made the Linux primary path.
- Real structured navigation/extraction/download and real native Firefox
  navigation/focus/title-readback passed. The Firefox AT-SPI focus warning is
  the existing KI-022 diagnostic, not a new upstream divergence.
- The pinned Hermes commit
  `f293e7206b4ddd66042329442c6afebc19a8808d` and baseline merge commit
  `2ac06b131a237916432503ac67bbcada6dbea39e` are unchanged. No upstream
  Hermes commit was rewritten.

## P11 voice-local-stack validation

- Hafiye source commit: `6f2b982159a37d9fb73d460c19279ea06d06efa0`.
- The Hermes upstream pin `f293e7206b4ddd66042329442c6afebc19a8808d` and
  history-preserving baseline merge `2ac06b131a237916432503ac67bbcada6dbea39e`
  are unchanged; no upstream Hermes commit was rewritten.
- The managed whisper.cpp checkout is from
  `https://github.com/ggml-org/whisper.cpp.git` at source commit
  `c122757fddf358397bb7f33b6ac3aab24a5bca04`. Separate CPU, CUDA, and Vulkan
  builds are published under the Hafiye runtime root and selected by the
  fixed CUDA→Vulkan→CPU policy.
- Piper remains an external managed process, not a linked Hafiye library.
  `piper-tts==1.7.0` and `tr_TR-dfki-medium` are installed under the Hafiye
  runtime root. The public voice-list response strips local runtime paths.
- The Hafiye patch uses Hermes' custom local-STT command hook and existing TTS
  boundary; it does not mass-rename Hermes modules or copy unrelated upstream
  code. Real runtime doctor, Piper synthesis, Desktop settings smoke, and
  synchronized microphone-to-correct-Turkish-text acceptance pass. The initial
  capture-window observation is resolved as KI-025.

## P12 Hafiye wake-word validation

- Hafiye source commit:
  `d1c5f4c9c5254ba34844e583e5486972e33bdd6b`.
- The Hermes upstream pin
  `f293e7206b4ddd66042329442c6afebc19a8808d` and history-preserving baseline
  merge `2ac06b131a237916432503ac67bbcada6dbea39e` are unchanged; no Hermes
  commit was rewritten.
- Training provenance uses the official
  `https://github.com/dscripka/openWakeWord` source checkout at commit
  `368c03716d1e92591906a84949bc477f3a834455`, package version 0.6.0, and its
  `openWakeWord.train.Model` pipeline. Turkish positive speech is generated by
  the managed Piper `tr_TR-dfki-medium` voice; the reproducible training entry
  point is `scripts/train_hafiye_wakeword.py`.
- The shipped Linux asset is the standalone ONNX model
  `tools/wakewords/hafiye.onnx` (216,102 bytes; SHA-256
  `9eb0e8c9fd509900ba5d33b4c43906817265605846564af76232daeea194ba50`). Its
  default runtime configuration is threshold `0.6` and three confirmation
  frames. Legacy `hey_hermes`/`hermes` aliases resolve to the Hafiye asset for
  compatibility.
- A normal-room music recording produced no fires; a real Turkish Hafiye
  recording fired the direct detector and opened a new Desktop session. The
  same client capture remained active after the actual Electron window was
  minimized. No cloud or remote service was used for wake detection.
- The openWakeWord package metadata/CPython 3.13 and PortAudio observations
  are documented as KI-026. The official source checkout with ONNX runtime and
  Desktop client capture are the accepted host path; no unrelated alternative
  wake implementation was introduced.

## P13 cancellation and emergency-stop validation

- Hafiye source commit:
  `dfb0d29c7ba80efadd5a517bac07aa949e517a5a`.
- Pinned Hermes upstream commit:
  `f293e7206b4ddd66042329442c6afebc19a8808d`.
- Baseline merge commit:
  `2ac06b131a237916432503ac67bbcada6dbea39e`.
- No Hermes upstream commit was rewritten or amended. P13 is a separable
  Hafiye patch group on top of the preserved baseline.
- The gateway controller fans out to TTS, managed computer-use sessions,
  active gateway sessions, async delegations, registered processes, and the
  durable ESTOP sentinel. The root broker rejects new privileged calls while
  the sentinel exists; `emergency.resume` deliberately clears that pause.
- Desktop native/tray/Composer, voice stop phrase, CLI, and the mandated
  `Ctrl+Super+Escape` surface use the same authenticated stop RPC. Electron
  global shortcut registration is attempted first. On this GNOME Wayland
  host, the real Electron registration was unavailable, so the implementation
  used a private GNOME custom keybinding that invoked the Hafiye CLI and was
  verified with real `ydotool` input. Existing custom bindings were preserved
  and the Hafiye binding was removed on clean shutdown.
- The generic upstream `cua-driver` path remains untouched and was not ready
  on this host. Hafiye's prescribed Linux path remains the managed pinned
  `computer-use-linux` MCP provider; this observation is KI-028, not an
  architecture substitution.
- The master P13 acceptance now passes with a real OpenHands delegation: a
  Gemini-backed fixture run edited `bug.py` and returned the real verification
  result; a separate live worker was stopped through the shared controller and
  explicitly resumed with no active process remaining. KI-027 is resolved.

## OpenHands V1 managed runtime and coding delegate

- Hafiye's OpenHands implementation is based on the official
  [OpenHands software-agent SDK repository](https://github.com/OpenHands/software-agent-sdk/)
  at source commit `6d38810359827823e62a5e1043d0d78d0bafb6de`. The current
  managed user runtime records that source and pins
  `openhands-sdk==1.41.0`, `openhands-tools==1.41.0`,
  `openhands-workspace==1.41.0`, and `openhands-agent-server==1.41.0` in
  `~/.local/share/hafiye/runtimes/openhands/manifest.json`.
- The official V1 API path is used: Hafiye creates an OpenHands `LLM`, obtains
  the official default agent, and runs a local `Conversation` against the
  supplied host repository. The worker is a one-shot managed subprocess so
  Hafiye retains route/privacy ownership, process tracking, and emergency-stop
  control; OpenHands is not made into a second Hafiye runtime.
- `coding_delegate` inherits Hafiye's configured `coding` route and passes the
  local repository path to the worker. Credentials are injected only at the
  private process boundary, consumed before OpenHands terminal subprocesses
  are created, and omitted from command lines and progress records.
- The worker emits redacted progress metadata and a result containing execution
  status, summary, changed files, and event count. Its process is registered in
  Hermes' existing process registry, so the P13 cancellation controller can
  kill it and an explicit resume can clear the pause state.
- The managed checkout is materialized at
  `~/.local/share/hafiye/runtimes/openhands/source` by
  `hafiye runtime openhands install`; source pinning and package pinning are
  verified separately by `hafiye runtime openhands doctor`. The source
  checkout is not used as an unpinned replacement for the exact managed
  package set.
- P15 adds a shared process-local `TaskCenterRegistry` that receives safe
  coding lifecycle/progress/tool/command/file-change/result summaries. The
  gateway exposes `tasks.list` and `tasks.cancel`, broadcasts `task.update`,
  and the Desktop Maintenance Task Center panel consumes the same contract.
  Private OpenHands transcript/reasoning is not persisted or displayed.
- Real P15 acceptance evidence: a natural-language Hafiye Gemini fixture run
  identified the coding task, delegated to OpenHands, changed `bug.py`, and
  returned the external `pytest -q` result `1 passed in 0.00s`. A separate
  real gateway smoke observed `RUNNING`, final `COMPLETED`, 18 progress
  records, and 22 `task.update` events; the Desktop Task Center test/build
  passed. P15, P16, and P17 are complete. P16's durable Task Center
  implementation and P17's real Control Center acceptance are recorded in the
  current Hafiye commits; P18, P19, and P20 are complete and P21 is the
  current onboarding phase. No Hermes upstream commit changed.

## P18 Scheduler / skills / MCP patch group

- Hafiye source/test commit:
  `fd17e6533894a568744b82454635a8e6bf02709b`.
- The patch reuses Hermes cron persistence, scheduler claim/execution and
  recurring state, the real skills/toolset catalog, and the existing MCP
  safety merge. It adds validated Hafiye route/privacy fields to the existing
  profile-aware REST boundary and carries the effective route/policy into
  scheduled `AIAgent` runs.
- Desktop's real cron editor now exposes route slots, privacy mode, and a
  gateway-backed enabled-toolset allowlist. The two-tick local recurring-task
  acceptance and real Electron/gateway edit round-trip passed.
- No Hermes upstream commit changed and no upstream history was rewritten.

## P19 Hardening patch group

- Hafiye source/test commit: `0f45abb9c`.
- The patch composes Hermes' existing prompt-injection, redaction, outage,
  loop-detector, checkpoint, and config-recovery primitives. It adds bounded
  Hafiye-managed llama/voice recovery, action-budget admission, structured
  computer-use failures, and audit/disk retention diagnostics without creating
  a second runtime or configuration store.
- The exact five-ID upstream comparison after the patch reproduced only
  historical items 2, 3, and 5; items 1 and 4 passed. No upstream Hermes
  commit changed, no upstream history was rewritten, and no upstream baseline
  bug was fixed as part of P19.

## P20 Packaging patch group

- Hafiye source/test commit:
  `964fc49b5f564f25588894374ea83e81cc2f58c7`.
- The patch adds an outer Ubuntu/Debian package assembler around the real
  Electron `linux-unpacked` output. The package contains the Hafiye backend,
  stable launchers, the user gateway unit, explicit per-user root-broker
  activation, XDG desktop/autostart entries, icons, notices, and a manifest
  recording the source, pinned upstream, and baseline merge commits.
- Managed model/voice/computer-use runtimes remain first-run downloads. The
  package doctor and installer operate through the package boundary without a
  second runtime or configuration store.
- The real final artifact was inspected, extracted-package doctor returned
  `ok=true` with `blockers=[]`, and rootless fakeroot dpkg unpack/configure
  passed. The exact five-ID comparison remained historical IDs 2, 3, and 5
  only. No Hermes upstream commit changed and no upstream history was rewritten.
- Current-host package-bootstrap hardening commit
  `fd435cc85fe018ca238256fb19547db2e7064565` removes only the Debian system
  Python `<3.14` bootstrap conflict and provisions managed Python 3.11 through
  the existing package installer. The rebuilt artifact resolves on the real
  Python 3.14 apt database, extracted package doctor is green, and the exact
  five-ID comparison remains historical IDs 2, 3, and 5 only. This changes no
  Hermes upstream source or architecture.

## P21 First-run Onboarding patch group

- Hafiye implementation commit: `48860ee5f`.
- Hafiye Desktop/Electron acceptance-test commit:
  `a87eaaba7373a2c23fa73b7ef498b64d67c989f5`.
- The patch adds the exact 20-step GUI onboarding state machine, an atomic
  XDG-state progress file, and authenticated REST operations that reuse the
  existing Hafiye environment, computer-use, local-runtime, voice, config,
  autostart, and doctor boundaries. It does not add a second configuration or
  runtime store.
- The real packaged-install wizard exposes compute selection, GGUF/model
  setup, optional provider skips, microphone/STT, Piper/TTS, wake word,
  stateless Hafiye, execution policy, autostart, and final doctor transitions.
  The real `release/linux-unpacked/hafiye-desktop` binary passed all 20 steps
  against the live authenticated gateway, including real microphone/STT,
  Piper/TTS, wake-word choice, Hafiye request, autostart, and final doctor.
- Normal-XDG systemd generation was corrected to omit a forced `HERMES_HOME`,
  while explicit environment/profile overrides remain supported. Package
  launchers propagate `HAFIYE_PACKAGE_ROOT` so the packaged-only boundary is
  detected by the same backend.
- The exact five-ID comparison after P21 remained `3 failed, 2 passed`; only
  accepted historical IDs 2, 3, and 5 failed. No Hermes upstream commit
  changed and no upstream history was rewritten. P21 is accepted; P22 — CLI —
  followed and is complete, with P23 as the next incomplete phase.

## P22 CLI patch group

- Hafiye source/test commit: `e031162fd`.
- The product CLI vocabulary is a thin adapter over existing Hermes/Hafiye
  boundaries: one-shot agent execution, the persistent user service, the
  managed local GGUF runtime, provider catalog, route/privacy policy, durable
  Task Center, and the pinned computer-use-linux doctor. No second backend,
  configuration store, project registry, or scheduler was introduced.
- `projects` and `automation` are aliases for the existing project and cron
  implementations. Explicit one-shot provider/model flags are allowed to win
  over an onboarding-populated default route slot; normal gateway route-slot
  behavior remains unchanged.
- Real P22 validation passed for the parser/help surface, service restart,
  CUDA model unload/load, provider/routing/privacy/task/computer surfaces, and
  the explicit Gemini one-shot. The computer-use doctor returned all four
  required readiness fields true with an empty blocker list.
- The exact five-ID comparison after P22 remained `3 failed, 2 passed`, with
  only accepted historical IDs 2, 3, and 5 failing. No Hermes upstream commit
  changed and no upstream history was rewritten.

## P23 Desktop route/config patch group (in progress)

- Hafiye source/test commits:
  `ba113121f275bf1ff8258037bb79eed0aa36e2bf` (route/config boundary) and
  `5af73434e5ab36786a306966fa926b7cbbe08914` (managed Qwen2 compatibility),
  followed by `ac42575db2986a2f8be677a9d1272121ff533294` (managed Qwen3
  compatibility and explicit managed-MCP toolset selection), followed by
  `f9ebf814b53b0a3c71f932713db0e217af17cb1c` (KI-043 privileged terminal
  boundary, regression tests, and local-model capability metadata), followed
  by `dc962963e6040f792e3f74fcd459d41da425d8d` (managed computer-use MCP
  startup-gate fix and regression test), followed by
  `197e4ca8fe864faaf48dd695cc25d7c89e2c6e33` (explicit Desktop model-route
  precedence and Settings-derived New Chat state).
- The P23 packaging checkpoint is
  `a1271a93277e6ac0747c1c5c31b586c2e883e55a`. It fixes Hafiye's Debian
  packaging boundary exposed by P23.1: the Linux Electron `chrome-sandbox`
  helper is staged with setuid mode `4755`, so
  `dpkg-deb --build --root-owner-group` installs it as `root:root 4755`.
  `tests/packaging/test_hafiye_deb.py` verifies the extracted package mode
  (`4 passed`). This is Hafiye packaging code; the Hermes upstream pin and
  history remain unchanged.
- The native gateway's normal configuration lookup now follows Hafiye's XDG
  config root, while explicit `HERMES_HOME` and profile/context overrides keep
  the upstream-compatible single-root behavior. The Desktop/TUI agent factory
  applies the same Hafiye route slot, privacy mode, and fallback resolution
  before creating `AIAgent`.
- This is a Hafiye boundary adapter and test coverage change; no Hermes source
  commit, upstream pin, baseline merge, or upstream history changed. The
  latest direct exact five-ID comparison after KI-043 returned `3 failed, 2
  passed`; only accepted historical IDs 2, 3, and 5 failed, with no
  new/different regression. The five-ID historical whitelist is unchanged.
- A real packaged Composer operation under a temporarily forced Gemini route
  reached Firefox, but the provider later returned HTTP 429 free-tier quota;
  the P23 final acceptance remains open and is tracked as KI-037.
- The managed runtime compatibility patch is deliberately narrow: when a
  Qwen2 model is requested above its 32K native context, Hafiye passes the
  current llama.cpp YaRN flags and an explicit Qwen2 context metadata override.
  Other model families retain their native metadata behavior. A live CUDA
  runtime reported 65,536 context, and direct AIAgent plus packaged Desktop
  terminal calls passed. This is a Hafiye integration patch; the pinned Hermes
  source, baseline merge, and upstream history did not change.
- The Qwen3 patch is likewise identity-scoped: the managed runtime uses the
  official Jinja/DeepSeek path, Qwen3 YaRN/context metadata, fit-aware CUDA
  layers, and CPU KV storage at 65K. An isolated real Hafiye AIAgent replay
  passed the six local-agent workflows, while the measured VRAM/RAM/swap
  pressure remains KI-046 and keeps Qwen3 selectable rather than default.
- The local model registry now carries capability metadata for the two
  qualified identities. Qwen2.5-0.5B is a validation fixture (`validation=true,
  agent=false`); Qwen3-14B is a qualified local agent
  (`agent=true, tool_calling=true, validation=false, resource_warning=KI-046`).
  This does not change the default route or the upstream pin.
- The managed Hafiye computer-use provider is injected in memory rather than
  persisted as a user MCP entry. The startup gate now recognizes that
  provider, so a fresh gateway/Desktop process starts shared MCP discovery and
  registers the managed tools. This is a narrow Hafiye integration fix in
  `dc962963e`; Hermes upstream history and the pinned upstream state are
  unchanged. A subsequent real Qwen3 Composer replay still failed to emit a
  tool call and remains a P23 acceptance warning, not an upstream change.
- The Desktop model-identity patch keeps upstream routing architecture intact:
  explicit `session.create` provider/model values now use the existing
  `explicit_overrides` policy input, while default-derived new chats resolve
  the existing profile model-info API before creation. No provider, local
  runtime, privacy policy, upstream commit, or history was changed. The exact
  five-ID comparison remains 3 failed/2 passed with only accepted IDs 2, 3,
  and 5.
- The selected-route endpoint hardening commit is
  `10bd0b8f32b99b9a7ad91317dfb2f88b5204b927`. It resolves the matching
  custom-provider loopback endpoint for a selected local route even when the
  global model URL describes Gemini, and carries that endpoint through CLI,
  gateway, Desktop/TUI, API, and cron callers. Policy/native-gateway tests and
  real source and installed `LOCAL_ONLY` Qwen3-4B terminal replays passed. This
  is a Hafiye routing integration change; the pinned Hermes source, baseline
  merge, and upstream history remain unchanged.

## P24 Desktop emergency-binding repair patch group

- Hafiye source/test commit:
  `ee380ba75a21b8559ccb523b77b8cd511359a9ff`.
- The Electron GNOME fallback now repairs the command for an existing reserved
  Hafiye binding when its ownership marker (name plus accelerator) matches, even
  if an older install still points at the legacy Hermes launcher. It continues
  to reject a binding whose name or accelerator differs, so the upgrade path
  does not overwrite unrelated user shortcuts.
- The patch is covered by the focused Electron regression test and was verified
  in the installed package: a real launch changed the live gsettings command
  to `/usr/bin/hafiye emergency-stop --reason=global-hotkey`. The pinned Hermes
  commit, baseline merge, and upstream history were not changed.

## P24 packaged managed STT module-path repair patch group

- Hafiye source/test commit:
  `139f5f9491aa46adebbca932b255ad2b87141702`.
- The patch is Hafiye packaging/runtime glue, not an upstream Hermes change.
  It restores the exact installed Hafiye backend root for the managed
  `hermes_cli.voice_runtime` child after generic subprocess environment
  sanitization, while leaving user-supplied STT command environments
  sanitized.
- The installed authenticated `/api/audio/transcribe` path returned HTTP 200
  after the patch, and the broad voice/gateway regression set returned
  `311 passed, 12 skipped, 2 warnings`. The pinned Hermes commit, baseline
  merge commit, and upstream history are unchanged.

## P24 pinned Qwen3.8-27B catalog patch group

- Hafiye source/test commit:
  `e00da6acd52d00a6bdb0f4c7094d01d154b26d57`.
- Follow-up Desktop presentation fix:
  `beec5bd9c061b4c538e7916ee152c29264f6b8ad` (correct IEC byte-unit
  formatting for the multi-gigabyte catalog card).
- The existing managed llama.cpp/GGUF boundary now publishes a backend-owned
  production catalog entry for the exact Unsloth Qwen3.8-27B UD-IQ1_S file,
  pinned by Hugging Face commit, SHA-256 and byte size. Desktop Settings and
  onboarding consume that same catalog; no second configuration system was
  added.
- The patch keeps the model unqualified/non-default pending real Hafiye agent
  evidence, preserves resumable downloads, rejects model-ID overwrite, and
  avoids applying the original Qwen3 40,960-token YaRN workaround to the
  Qwen3.5/Qwen3.8 native-context family.
- The installed Hafiye package exposes the entry as downloadable. The pinned
  Hermes commit, baseline merge commit, and upstream history are unchanged.

## P24 security-research model catalog extension patch group

- Hafiye source/test commit:
  `53e783e8c8ee6c88b2ecff2cff4954512deb386a`.
- The existing Hafiye-managed llama.cpp/GGUF catalog now includes the immutable
  text/tool GGUF layer from Ollama tag
  `orcarouter/Qwen3.8-27B-Uncensored:q4_K_M` and both pinned IQ2_M shards from
  gated Hugging Face repository
  `orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF`.
- Ollama remains an acquisition source, not a second inference runtime. The
  renderer sends only catalog IDs; backend-owned metadata, per-file SHA-256,
  resumable transfer, gated `HF_TOKEN` handling and split-shard repair remain
  inside the Hafiye adapter boundary.
- Both entries remain unqualified/non-default with explicit host-resource and
  security-research warnings. The fixed upstream pin, baseline merge, remotes,
  history, llama.cpp architecture and model qualification semantics are
  unchanged.

## P17 Control Center patch group

- Hafiye source/test commit:
  `2dc541d09367b895744b512d99b058506d7f78d2`.
- The patch adds a Hafiye-specific Control Center overlay route and composes
  the existing real Hermes/Hafiye config, provider, skills/MCP, scheduler,
  logs, computer-use, Task Center, and About surfaces. The shared privacy
  enum is exposed as `NORMAL`, `LOCAL_ONLY`, and `OFFLINE`.
- No Hermes upstream commit changed and no upstream history was rewritten.

## P14 memory and project registry validation

- The pinned Hermes source already contains the per-profile `projects.db`,
  deterministic project slug/name resolution, `project_list/create/switch`,
  gateway `projects.*` RPCs, the authoritative project tree, and the FTS5
  `session_search` tool. Hafiye keeps these upstream surfaces and does not
  introduce a second project store.
- Hafiye source/test commit
  `831405dcec4abcba033d8ccc18308804868ecb1f` adds the real backend fresh-
  process assertion and the real Electron project browser/search/rename/delete
  acceptance. The Desktop E2E fixture opts out of the host's persistent
  gateway so its isolated `HERMES_HOME` is the backend under test; the real
  user service remains untouched.
- A fresh process resolved `pocket-world` to the exact saved repository path
  and `session_search` returned recent Pocket World context. The real Electron
  flow passed 1/1; the P14 targeted backend/UI matrices passed 127 and 114
  tests respectively. No Hermes upstream commit was rewritten, and the
  pinned commit and baseline merge commit remain unchanged.

## Baseline divergence

The upstream Hermes baseline contains its own cua-driver computer-use
integration. Hafiye retains that upstream path for platforms where it remains
applicable, while the prescribed Linux path is now managed through the pinned
agent-sh/computer-use-linux MCP provider above. Hafiye did not copy unrelated
code from alternative repositories or replace the existing Hermes MCP client.
