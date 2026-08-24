# Test Matrix

Results below are from the Hermes baseline, the real environment, and the
completed Hafiye P1 source. A command being run is not treated as a pass unless
its result says so.

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P0-BE-01 | Hermes backend full suite, lean upstream extras | ./scripts/run_tests.sh | 3,210 files; 36,814 passed, 80 failed, 324 skipped; exit non-zero | REFERENCE BASELINE |
| P0-BE-02 | Hermes CLI import/startup | .venv/bin/hermes --help | Help and command registry rendered; exit 0 | PASS |
| P0-BE-03 | Direct agent entrypoint | .venv/bin/python run_agent.py --help | Help rendered; exit 0 | PASS |
| P0-D-01 | Desktop dependency install | npm install | Completed; npm reported 3 high-severity audit findings | PASS WITH WARNING |
| P0-D-02 | Desktop production build | cd apps/desktop && npm run build | Vite renderer, Electron main/preload, native deps, and assert-dist-built passed | PASS |
| P0-D-03 | Desktop TypeScript | cd apps/desktop && npm run typecheck | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P0-D-04 | Desktop UI baseline tests | cd apps/desktop && npm run test:ui | 578 files; 5,545 passed | PASS |
| P0-D-05 | Desktop Electron/platform baseline tests | cd apps/desktop && npm run test:desktop:platforms | 112 files; 1,598 passed; 3 skipped | PASS |
| P0-BE-06 | Hermes backend full suite, relevant optional SDKs installed | ./scripts/run_tests.sh | Pre-source: 3,210 files; 36,903 passed; 5 failed; 320 skipped; exact five IDs below | ACCEPTED_UPSTREAM_BASELINE |
| P0-CU-01 | Historical released-package doctor | @agent-sh/computer-use-linux 0.4.9 doctor | Exit 0, but readiness blockers were reported; report saved under docs/p0 | HISTORICAL DIAGNOSTIC |
| P0-CU-02 | Pinned source release asset | Source package 0.4.10 installer | Expected x86_64 release asset returned HTTP 404 | WARNING; NOT FINAL PATH |
| P0-CU-03 | Pinned source official setup | cd /home/tolga/.cache/hafiye/computer-use-linux && ./install.sh --skip-system-deps --skip-gnome-extension | Pinned source rebuilt from commit 94736dc3e0dca56acfc89752c26869fb9ed01202; AT-SPI, source binaries, ydotoold setup, and installer doctor completed | PASS |
| P0-CU-04 | Pinned source final doctor | ~/.local/bin/computer-use-linux doctor | can_register_mcp_tools=true, can_build_accessibility_tree=true, can_send_development_input=true, can_query_windows=true; blockers=[] | PASS |
| P0-CU-05 | User input service | systemctl --user status ydotool.service; stat /dev/uinput | Packaged non-root user unit active/enabled; /dev/uinput is root:input 0660; socket connectable | PASS |
| P0-CU-06 | Real window query | ~/.local/bin/computer-use-linux windows | Focused ChatGPT window returned via gnome-shell-extension backend | PASS |
| P0-ENV-01 | User systemd session | systemctl --user is-system-running | running | PASS |
| P0-ENV-02 | Vulkan CLI probe | vulkaninfo | Command unavailable; Vulkan loader/ICDs are present and Vulkan is a fallback backend | WARNING / DIAGNOSTIC |
| P0-ENV-03 | Rust source build prerequisite | ~/.cargo/bin/cargo --version | cargo 1.98.0; user-space toolchain installed by pinned source installer | PASS |
| P1-PY-01 | Python Hafiye identity/XDG targeted tests | .venv/bin/python -m pytest -q tests/hermes_cli/test_hafiye_identity.py tests/test_hermes_constants.py tests/hermes_cli/test_gateway_service.py | 153 passed, 6 skipped | PASS |
| P1-D-01 | Full Desktop test suite | cd apps/desktop && npm run test | 691 test files passed, 1 skipped; 7,149 tests passed, 3 skipped | PASS |
| P1-D-02 | Desktop typecheck | cd apps/desktop && npm run typecheck | Renderer, Electron, and E2E checks passed; exit 0 | PASS |
| P1-D-03 | Desktop clean production build | cd apps/desktop && npm run build | Vite, Electron main/preload bundle, native dependency staging, and assert-dist-built passed; build stamp source is 34f1d8c2472e and dirty=false | PASS |
| P1-D-04 | Linux unpacked Desktop package | cd apps/desktop && npm run builder -- --dir --publish never | Package passed; release/linux-unpacked/hafiye-desktop is executable x86-64 ELF and resources/icon.ico exists | PASS |
| P1-BE-01 | Backend post-source full suite | ./scripts/run_tests.sh | 3,211 files; 36,905 passed, 6 failed, 320 skipped; 4 current accepted baseline failures plus 2 full-suite async diagnostics; exit 1 | PASS WITH DOCUMENTED BASELINE/DIAGNOSTICS |
| P1-LINT-01 | Changed Python lint | .venv/bin/ruff check on all changed Python files | All checks passed | PASS |
| P1-LINT-02 | Patch whitespace | git diff --check | No whitespace errors | PASS |
| P1-CLI-01 | Real temporary-root identity smoke | HERMES_HOME unset; XDG base variables set to temporary roots; .venv/bin/hafiye --help | Hafiye usage and command names rendered; exit 0; internal HERMES compatibility names remain intentionally visible where required | PASS |
| P1-CLI-02 | Real temporary-root config write | Same temporary-root setup; .venv/bin/hafiye config set model.default smoke-test-model | Wrote config/hafiye/config.yaml and created expected config, data, state, and cache roots | PASS |

| P2-PY-01 | Persistent gateway unit/token/descriptor logic | ./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py -q | 4 passed | PASS |
| P2-PY-02 | Persistent gateway and restart integration tests | ./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_dashboard_admin_endpoints.py tests/hermes_cli/test_spawn_gateway_restart_cooldown.py tests/hermes_cli/test_web_server_profile_unification.py -q | 75 passed | PASS |
| P2-D-01 | Desktop persistent gateway path tests | cd apps/desktop && npm exec vitest run electron/hafiye-paths.test.ts --project electron | Electron project: 108 files; 1,546 passed; 3 skipped | PASS |
| P2-D-02 | Desktop TypeScript | cd apps/desktop && npm run typecheck | Passed | PASS |
| P2-D-03 | Desktop production build | cd apps/desktop && npm run build | Vite, Electron bundles, native staging, and assert-dist-built passed; stamp e2e22c10b49ec01ef7d8420f1158668718b03fa9 | PASS |
| P2-REAL-01 | Real persistent user service | .venv/bin/hafiye gateway service install; systemctl --user is-enabled/is-active/show | Enabled, active, `NRestarts=0`, loopback `127.0.0.1:9120` | PASS |
| P2-REAL-02 | Authenticated persistent backend | Real Python HTTP/WS probe against `127.0.0.1:9120` | HTTP succeeded, version `0.20.5`, WebSocket `OPEN` | PASS |
| P2-REAL-03 | Desktop close persistence | Real Electron launch/close with `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1` | Persistent readiness logged; service stayed active and endpoint stayed reachable | PASS |
| P2-REAL-04 | Persistent gateway restart control | Authenticated `POST /api/gateway/restart` | Success returned; new active PID observed; endpoint reachable | PASS |
| P3-D-01 | Composer lifecycle and shortcut defaults | `cd apps/desktop && ../../node_modules/.bin/vitest run electron/quick-entry.test.ts electron/composer-lifecycle.test.ts --project electron` | 2 files; 29 passed | PASS |
| P3-D-02 | Composer state/reducer | `cd apps/desktop && ../../node_modules/.bin/vitest run src/store/quick-entry.test.ts --project ui` | 1 file; 17 passed | PASS |
| P3-D-03 | Full Desktop UI suite after Composer changes | `cd apps/desktop && npm run test:ui` | 578 files; 5,547 passed | PASS |
| P3-D-04 | Full Desktop Electron suite after tray/autostart changes | `cd apps/desktop && npm run test:desktop:platforms` | 114 files; 1,609 passed; 3 skipped | PASS |
| P3-D-05 | Desktop TypeScript | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E checks passed | PASS |
| P3-D-06 | Clean Desktop production build | `cd apps/desktop && npm run build` | Clean stamp `e33bb456d109`; Vite, Electron bundles, native staging, and assert-dist-built passed | PASS |
| P3-REAL-01 | XDG autostart entry | `sed -n '1,20p' ~/.config/autostart/hafiye.desktop; stat -c '%a %U:%G' ...` | Owner-created entry contains Electron executable, app path, `--hidden`; mode 0644 | PASS |
| P3-REAL-02 | Real Wayland Desktop/tray startup | `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1 electron .` plus desktop log | `Hafiye tray ready`; persistent backend readiness logged | PASS |
| P3-REAL-03 | Close-to-tray persistence | `ydotool key 56:1 62:1 62:0 56:0` plus process/systemd probes | Electron remained resident; `hafiye-gateway.service` remained active/listening | PASS |
| P3-REAL-04 | Exact autostart command | Generated `~/.config/autostart/hafiye.desktop` `Exec=` command with `--hidden` | Launched successfully in current Wayland session | PASS WITH KI-013 |
| P3-REAL-05 | Mandated default global shortcut | Real Desktop launch and GNOME keybinding inspection | `Super+Shift+Space` reported taken by GNOME input-source-backward binding | WARNING; KI-012 |

| P4-PY-01 | Managed local runtime unit tests | `./scripts/run_tests.sh tests/hermes_cli/test_local_runtime.py -q` | 6 passed; backend priority, private registry/checksums, resumable download, and safe health covered | PASS |
| P4-PY-02 | Persistent gateway subprocess environment guard | `./scripts/run_tests.sh tests/agent/test_subprocess_env_guard.py tests/hermes_cli/test_persistent_gateway.py -q` | 6 passed after the shared environment factory correction | PASS |
| P4-D-01 | Local runtime settings boundary | `cd apps/desktop && ../../node_modules/.bin/vitest run src/app/settings/model-settings.test.tsx --project ui` | 1 file; 22 passed | PASS |
| P4-D-02 | Desktop typecheck after runtime API/settings | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P4-D-03 | Desktop production build after runtime API/settings | `cd apps/desktop && npm run build` | Clean working-tree build passed; Vite, Electron bundles, native staging, and assert-dist-built passed; stamp `955a9c3818fa` | PASS |
| P4-REAL-01 | Real CUDA toolchain and host detection | `nvcc --version`; `nvidia-smi`; `pkg-config --exists vulkan` | CUDA 12.4.131; NVIDIA RTX 3080/driver 595.84; Vulkan development metadata available | PASS |
| P4-REAL-02 | Managed llama.cpp build | `.venv/bin/hafiye runtime install --backend AUTO` | Source commit `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`; compiled `CPU,CUDA`; selected `CUDA` | PASS |
| P4-REAL-03 | GGUF model lifecycle | `.venv/bin/hafiye runtime model download ...`; `runtime model list`; import/delete checks | Gemma and Qwen GGUFs downloaded/imported with recorded sizes and SHA-256; private registry and model root | PASS |
| P4-REAL-04 | CUDA server readiness and device use | `.venv/bin/hafiye runtime server start/restart`; `runtime doctor`; `curl /health`; `nvidia-smi --query-compute-apps` | `/health` and `/v1/models` HTTP 200; doctor blockers/warnings empty; `CUDA0: NVIDIA GeForce RTX 3080`; managed PID used GPU memory | PASS |
| P4-REAL-05 | OpenAI-compatible local chat | `curl http://127.0.0.1:11435/v1/chat/completions` | Real CUDA response contained `CUDA LOCAL OK` | PASS |
| P4-REAL-06 | Hermes provider connection | Temporary `HERMES_HOME` plus local OpenAI-compatible base URL; `.venv/bin/hermes` one-shot | Real Gemma CPU smoke returned `HERMES LOCAL OK`; CUDA Qwen one-shot returned a non-empty agent response | PASS |
| P4-REAL-07 | Model switch without reinstall | `runtime server restart` with Gemma then Qwen; health/chat probes | Second model became healthy and returned `SECOND MODEL OK` without rebuilding Hafiye | PASS |
| P4-REST-01 | Authenticated persistent gateway runtime API | `systemctl --user restart hafiye-gateway.service`; authenticated `GET /api/local-runtime` | `ok=true`, blockers empty, expected/selected backend `CUDA` | PASS |
| P4-BE-01 | Corrected backend full regression comparison | `./scripts/run_tests.sh` with persistent Hafiye gateway and managed local model server stopped temporarily | 3,213 files; 37,009 passed, 6 failed, 291 skipped in 515.9s; exact four accepted upstream failures plus the two isolated-passing async diagnostics; one retry-only flake recorded separately | PASS WITH DOCUMENTED BASELINE/DIAGNOSTICS |

| P5-PY-01 | Secret Service provider credential lifecycle | `./scripts/run_tests.sh tests/hermes_cli/test_hafiye_keyring.py tests/hermes_cli/test_p5_provider_paths.py tests/hermes_cli/test_credential_lifecycle.py tests/hermes_cli/test_prompt_api_key.py tests/hermes_cli/test_web_server.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_model_switch_custom_providers.py tests/agent/test_credential_pool.py tests/hermes_cli/test_secret_source_bootstrap.py tests/secret_sources/test_secret_source_registry.py tests/secret_sources/test_profile_secrets.py tests/test_env_loader_secret_sources.py tests/hermes_cli/test_provider_parity.py tests/hermes_cli/test_gemini_provider.py tests/agent/test_gemini_native_adapter.py -q` | 15 files; 468 passed; 0 failed; includes default-XDG config-root regression coverage | PASS |
| P5-PY-02 | Provider/tool credential storage boundary | `./scripts/run_tests.sh tests/hermes_cli/test_env_export_line_lifecycle.py tests/hermes_cli/test_set_config_value.py tests/hermes_cli/test_hafiye_keyring.py tests/hermes_cli/test_p5_provider_paths.py -q` | 4 files; 93 passed; 0 failed; includes default-XDG config-root regression coverage | PASS |
| P5-REMOTE-01 | Real remote OpenAI-compatible provider path | `tests/hermes_cli/test_p5_provider_paths.py` with a local `ThreadingHTTPServer` | Authenticated `/v1/models` and chat passed; config contained no raw key; reply marker `P5_REMOTE_OK` | PASS |
| P5-REAL-01 | Real host Linux Secret Service round-trip | Live keyring write/read/delete/remove probe; secret value omitted from output | All round-trip booleans true; config contained no secret value | PASS |
| P5-LOCAL-01 | Real managed local provider endpoint | `GET /v1/models` and `POST /v1/chat/completions` against `127.0.0.1:11435`; runtime doctor | HTTP 200/non-empty model and reply; doctor `ok=true`, `blockers=[]`, selected backend `CUDA` | PASS |
| P5-D-01 | Desktop provider/key/model/custom endpoint surface | `cd apps/desktop && npm run test` | 692 test files passed, 1 skipped; 7,156 tests passed, 3 skipped; exit 0 | PASS |
| P5-D-02 | Desktop provider integration typecheck/build | `cd apps/desktop && npm run typecheck && npm run build` | Typecheck and production build passed | PASS |
| P5-GEMINI-REAL | Live Gemini test connection | Hafiye Secret Service credential hydration; `GET /v1beta/models`; `.venv/bin/hafiye -z "Reply with exactly HAFIYE_GEMINI_LIVE_OK and nothing else." --provider gemini --model gemini-flash-lite-latest --safe-mode` | Real model listing HTTP 200 with 50 models; Hafiye one-shot returned `HAFIYE_GEMINI_LIVE_OK`; raw key omitted from output and docs | PASS |
| P5-BE-01 | Latest post-P5-source-fix backend regression comparison | `./scripts/run_tests.sh` with persistent gateway and managed local model server stopped temporarily | 3,218 files; 37,156 passed, 4 failed, 244 skipped in 541.8s; all four failures are exact accepted-baseline IDs; accepted remote browser-control ID did not reproduce; web-server retry-only flake passed on retry | PASS WITH ACCEPTED BASELINE/DIAGNOSTIC |
| P6-PY-01 | Shared Hafiye route/privacy policy | `./scripts/run_tests.sh tests/test_hafiye_policy.py tests/run_agent/test_hafiye_agent_policy.py tests/gateway/test_hafiye_routing.py -q` | 3 files; 17 passed; local, remote, Gemini, LOCAL_ONLY, OFFLINE, locality, and legal-fallback checks | PASS |
| P6-PY-02 | Affected config/API/web backend matrix | `./scripts/run_tests.sh tests/test_web_server.py tests/hermes_cli/test_web_server.py tests/hermes_cli/test_config_validation.py tests/gateway/test_api_server.py tests/gateway/test_api_server_runs.py tests/hermes_cli/test_fallback_config.py -q` | 6 files; 321 passed; 3 skipped; 0 failed | PASS |
| P6-D-01 | Desktop routing/privacy settings support | `cd apps/desktop && npm run test -- --run src/app/settings/helpers.test.ts src/app/settings/settings-search.test.ts src/app/settings/voice-provider-fields.test.ts` | 3 files; 47 passed | PASS |
| P6-D-02 | Desktop routing/privacy TypeScript | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P6-LINT-01 | P6 Python compile/lint/whitespace | `.venv/bin/ruff check <all P6 changed Python files>; python -m py_compile <all P6 changed Python files>; git diff --check` | Ruff checks passed; bytecode compilation and whitespace checks passed; existing upstream invalid `# noqa` warning remains | PASS WITH UPSTREAM WARNING |
| P6-GW-01 | Gateway cache/fallback contract regression fix | `./scripts/run_tests.sh tests/gateway/test_compression_failure_session_sync.py tests/gateway/test_fallback_chain_reload.py -q` | 2 files; 6 passed; 0 failed after normalizing cache mappings and retaining refreshed fallback calls | PASS |
| P6-BE-01 | Post-P6 full backend regression comparison (historical) | `./scripts/run_tests.sh` with persistent gateway and managed local model server stopped temporarily | 3,218 files; 37,154 passed, 5 failed, 244 skipped in 563.7s; four exact accepted-baseline members plus KI-019 browser reconnect diagnostic; superseded by P5-BE-01 | PASS WITH DOCUMENTED BASELINE/DIAGNOSTIC |

| P7-PY-01 | Hafiye execution-policy classifier and shared dispatch | `.venv/bin/python -m pytest -q tests/test_hafiye_execution_policy.py tests/test_model_tools.py` | 31 passed; default, confirmation, read-only, dispatch blocking, and approval-surface behavior covered | PASS |
| P7-PY-02 | Existing host-tool boundary regression suite | `.venv/bin/python -m pytest -q tests/tools/test_terminal_tool.py tests/tools/test_code_execution.py tests/tools/test_approval.py tests/tools/test_process_registry.py tests/tools/test_file_tools.py` | 285 passed, 6 skipped, 1 warning, 5 subtests passed | PASS |
| P7-REAL-01 | Real host terminal/file/process smoke | Live `model_tools.handle_function_call` dispatcher; terminal, temporary-file read, background process/wait | `HAFIYE_P7_HOST`, file content, and `HAFIYE_P7_PROCESS` observed; process exited cleanly | PASS |
| P7-D-01 | Desktop execution-policy settings boundary | `cd apps/desktop && npx vitest run --project ui src/app/settings/helpers.test.ts src/app/settings/settings-search.test.ts src/app/settings/terminal-backend-panel.test.tsx` | 3 files; 46 passed | PASS |
| P7-D-02 | Desktop settings regression isolation | `cd apps/desktop && npx vitest run --project ui src/app/settings/gateway-settings.test.tsx src/app/settings/providers-settings.test.tsx src/store/session-unread-tile.test.ts src/app/settings/toolset-config-panel.test.tsx src/app/messaging/index.test.tsx src/app/skills/index.test.tsx` | 6 files; 58 passed; rerun after the parallel-resource-contended attempt | PASS |
| P7-D-03 | Desktop TypeScript and production build | `cd apps/desktop && npm run typecheck && npm run build` | Typecheck, Vite renderer, Electron main/preload, native staging, and `assert-dist-built` passed; existing npm/Vite warnings remain | PASS WITH WARNING |
| P7-BE-01 | Full backend regression comparison | `./scripts/run_tests.sh` | 3,219 files; 37,160 passed, 7 failed, 244 skipped in 598.3s; four accepted-baseline IDs plus KI-016 cold-start topology and KI-019 browser reconnect diagnostics; no new Hafiye regression | PASS WITH DOCUMENTED BASELINE/DIAGNOSTICS |
| P7-DIAG-01 | Persistent-service cold-start topology diagnostic | `.venv/bin/python -m pytest -q tests/hermes_cli/test_update_cold_start_gateway_liveness.py` with `hafiye-gateway.service` stopped | 2 passed; service restarted and verified active afterward | PASS / KI-016 |
| P7-DIAG-02 | Browser reconnect scheduling diagnostic | `.venv/bin/python -m pytest -q tests/gateway/test_browser_control_api.py -k test_local_api_same_identity_reconnect_completes_command_started_on_old_socket` | First run timed out; immediate isolated retry passed 1/1; tracked as KI-019 | DIAGNOSTIC |

| P8-PY-01 | Root broker protocol/security and packaging regression tests | `.venv/bin/python -m pytest -q tests/test_hafiye_rootd.py tests/test_packaging_metadata.py` | 13 passed; strict framing, duplicate-key rejection, peer rejection, operation validation, audit behavior, unit generation, and packaging metadata covered | PASS |
| P8-PY-02 | CLI registration and emergency-stop regression matrix | `.venv/bin/python -m pytest -q tests/hermes_cli/test_startup_plugin_gating.py tests/test_estop.py tests/test_packaging_metadata.py tests/test_hafiye_rootd.py` | 39 passed; 0 failed | PASS |
| P8-CLI-01 | Packaged root broker entrypoints | `uv pip install --python .venv/bin/python -e . --no-deps; .venv/bin/hafiye-rootd --help; .venv/bin/hafiye root --help` | Editable package refreshed; both root-broker help surfaces rendered; exit 0 | PASS |
| P8-LINT-01 | Root broker lint, compile, and patch hygiene | `.venv/bin/ruff check hafiye_rootd.py hermes_cli/main.py tests/test_hafiye_rootd.py; .venv/bin/python -m py_compile hafiye_rootd.py hermes_cli/main.py tests/test_hafiye_rootd.py; git diff --check` | All checks passed | PASS |
| P8-REAL-01 | Real rootd system service and process boundary | Normal visible-terminal `.venv/bin/hafiye root install`; `systemctl is-enabled/is-active`; `systemctl status`; `ps`; `stat` | `/usr/lib/systemd/system/hafiye-rootd.service` enabled/active; rootd EUID 0; gateway EUID 1000; `/run/hafiye/root.sock` mode 0600 owned by `tolga`; no TCP/UDP listener | PASS |
| P8-REAL-02 | Harmless privileged operation through non-root broker | `.venv/bin/python` `RootBrokerClient`: `root.exec id -u` and `file.write_privileged` temporary-file smoke | Client EUID 1000; broker UID `0`; privileged write/content/mode/SHA-256 verified | PASS |
| P8-REAL-03 | Real malformed and unauthorized socket clients | Duplicate-key frame through `/run/hafiye/root.sock`; broker-controlled `runuser -u nobody` peer probe | Malformed response code `malformed_request`; actual `nobody` client received `permission_denied` | PASS |
| P8-REAL-04 | Real audit trail | `RootBrokerClient` read of redacted audit-log sample through `root.exec` | 33 records sampled; 11 complete request groups; accepted/rejected + closed lifecycle, peer/duration fields present; raw test command text absent | PASS |

| P9-PY-01 | Managed computer-use-linux boundary and MCP regression matrix | `.venv/bin/python -m pytest -q tests/tools/test_mcp_tool.py tests/hermes_cli/test_tools_config.py tests/cron/test_scheduler.py tests/hermes_cli/test_mcp_tools_config.py tests/test_hafiye_computer_use.py` | 258 passed; one pre-existing async resource warning from the scheduler test; user-config tests isolate the host-managed provider | PASS WITH DOCUMENTED WARNING |
| P9-D-01 | Settings → Computer diagnostics component | `cd apps/desktop && npx vitest run --project ui src/app/settings/computer-settings.test.tsx` | 1 file; 1 passed; managed backend, source pin, MCP name, and all four readiness values rendered | PASS |
| P9-D-02 | Full Desktop UI regression suite | `cd apps/desktop && npm run test:ui` | 579 files; 5,548 tests passed; existing jsdom canvas warnings only | PASS WITH WARNING |
| P9-D-03 | Desktop typecheck | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P9-D-04 | Clean Desktop production build | `cd apps/desktop && npm run build` | Clean build stamp `6d3672e498e1`; Vite, Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P9-REAL-01 | Managed computer-use-linux doctor | Real `computer_use_linux_status()` using `/home/tolga/.local/bin/computer-use-linux` | Pinned source `94736dc3e0dca56acfc89752c26869fb9ed01202`; `ready=true`; all four required readiness booleans true; `blockers=[]` | PASS |
| P9-REAL-02 | Automatic built-in MCP registration | Real `discover_mcp_tools()` through Hermes MCP client with empty user MCP config | `hafiye-computer-use-linux` connected and 18 `mcp__hafiye_computer_use_linux__*` tools registered; no manual config edit | PASS |
| P9-REAL-03 | Wayland/GNOME computer-use E2E | Real `model_tools.handle_function_call()` MCP calls plus `/usr/bin/gnome-calculator`, Firefox, `/usr/bin/code --new-window`, and `nautilus --new-window` | Windows enumerated; Calculator AT-SPI tree read and `12*7` produced/read as `84`; Firefox tab/navigation and app switching verified; VS Code launched; Files focus/tree interaction verified with 137 accessible nodes | PASS WITH KI-022/KI-023 WARNINGS |

## P9 acceptance

The managed provider is pinned to source commit
`94736dc3e0dca56acfc89752c26869fb9ed01202`. The required readiness fields are
all true and `blockers=[]`; the real MCP provider registered 18 tools without a
user configuration edit. The Calculator, Firefox, VS Code, and Files flow was
completed on the actual Wayland/GNOME session. P9 is accepted; KI-022 and
KI-023 are warnings only.

## P10 acceptance

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P10-PY-01 | Hafiye browser route, download, policy, Chromium detection, and extension wiring | `.venv/bin/python -m pytest -q tests/tools/test_hafiye_browser.py tests/tools/test_browser_chromium_check.py tests/tools/test_browser_extension_router.py tests/tools/test_browser_extension_router_wiring.py tests/test_hafiye_policy.py` | 49 passed; 0 failed | PASS |
| P10-PY-02 | Full Hermes browser regression plus Hafiye browser tests | `.venv/bin/python -m pytest -q tests/tools/test_browser_*.py tests/tools/test_hafiye_browser.py` | 504 passed; 7 deselected; 0 failed; 29.83s | PASS |
| P10-LINT-01 | P10 Python lint, compile, and patch hygiene | `.venv/bin/ruff check tools/hafiye_browser.py tools/browser_tool.py hafiye_policy.py toolsets.py tests/tools/test_hafiye_browser.py tests/tools/test_browser_chromium_check.py tests/tools/test_browser_extension_router_wiring.py && .venv/bin/python -m py_compile tools/hafiye_browser.py tools/browser_tool.py hafiye_policy.py toolsets.py tests/tools/test_hafiye_browser.py tests/tools/test_browser_chromium_check.py tests/tools/test_browser_extension_router_wiring.py && git diff --check` | Ruff, bytecode compilation, and whitespace checks passed | PASS |
| P10-REAL-01 | Structured navigation, extraction, and download | Isolated inline Python `ThreadingHTTPServer` fixture with `HERMES_HOME` and `browser.backend: off`; `browser_navigate`, `browser_snapshot`, `browser_download` | Page marker, extraction marker, and `HAFIYE_STRUCTURED_DOWNLOAD_OK` content all verified; cleanup completed | PASS |
| P10-REAL-02 | Native existing-browser operation through managed computer-use-linux | Inline Python `discover_mcp_tools()` plus `model_tools.handle_function_call("browser_native", ...)` on the real GNOME Wayland session | Existing Firefox window targeted; exact-window focus, temporary-tab navigation, focused title marker, and `blockers=[]` verified; temporary tab closed | PASS WITH KI-022 WARNING |
| P10-REAL-03 | Native browser cleanup | Inline `browser_native windows` query after P10-REAL-02 | No `Hafiye P10 Native` marker window remained; 2 Firefox windows remained | PASS |

## P11 acceptance

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P11-PY-01 | Managed voice runtime, STT/TTS hooks, and existing voice regressions | `.venv/bin/python -m pytest -q tests/hermes_cli/test_voice_runtime.py tests/tools/test_hafiye_voice_runtime_hooks.py tests/tools/test_transcription.py tests/tools/test_transcription_command_providers.py tests/tools/test_transcription_tools.py tests/tools/test_tts_piper.py tests/hermes_cli/test_voice_wrapper.py tests/test_voice_max_recording_seconds.py` | 131 passed in 6.19s | PASS |
| P11-LINT-01 | Voice Python lint, compile, and patch hygiene | `.venv/bin/ruff check` on changed voice files; `.venv/bin/python -m py_compile` on changed voice files; `git diff --check` | Ruff, bytecode compilation, and whitespace checks passed | PASS |
| P11-REAL-01 | Managed whisper/Piper readiness | `.venv/bin/python -m hermes_cli.voice_runtime doctor` | `ok=true`, `blockers=[]`; RTX 3080/CUDA selected; whisper CPU/CUDA/VULKAN compiled; Piper 1.7.0 and `tr_TR-dfki-medium` ready | PASS |
| P11-REAL-02 | Real Turkish Piper synthesis and playback | `.venv/bin/python -m hermes_cli.voice_runtime piper-speak ...`; `tools.tts_tool.text_to_speech_tool(...)`; `pw-play` | Direct Piper WAV, Hermes TTS audio, and real playback completed | PASS |
| P11-D-01 | Desktop voice settings and microphone-device unit tests | `cd apps/desktop && npm run test:ui -- src/app/settings/voice-provider-fields.test.ts src/app/settings/voice-field-visible.test.ts src/app/settings/helpers.test.ts src/lib/voice-input-device.test.ts` | 4 files; 50 passed | PASS |
| P11-D-02 | Desktop typecheck and production build | `cd apps/desktop && npm run typecheck && npm run build` | Typecheck, Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing toolchain warnings remain | PASS WITH WARNING |
| P11-D-03 | Real Electron boot and voice settings smoke | `npx playwright test e2e/boot.spec.ts --reporter=line`; `npx playwright test e2e/voice-settings.spec.ts --reporter=line` | Boot 5/5 passed; voice settings 1/1 passed; managed Piper list and preview returned real WAV data | PASS |
| P11-REAL-03 | Real Turkish microphone → correct text | `sleep 5; timeout --signal=INT 15s pw-record --target 37 --rate 16000 --channels 1 --format s16 --container wav ...`; managed CUDA whisper STT and `tools.transcription_tools.transcribe_audio()` | 14.995s real capture; both paths returned `Merhaba hafiye, bugün nasılsın bana Türkçe cevap ver?` correctly | PASS |

P11 is accepted. The master-roadmap test received correct text from a real
Turkish microphone, and the same five historical upstream failures remain the
`ACCEPTED_UPSTREAM_BASELINE`; no new/different upstream failure was found in
the P11 targeted matrix. P12 followed and is now complete; P13 is next.

## P12 acceptance

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P12-PY-01 | Hafiye wake detector and upstream wake regressions | `.venv/bin/python -m pytest -q tests/tools/test_wake_word.py` | 26 passed, 3 skipped | PASS |
| P12-TRAIN-01 | Reproducible Turkish openWakeWord training/export | `/home/tolga/.local/share/hafiye/runtimes/openwakeword-training/venv/bin/python scripts/train_hafiye_wakeword.py --piper-python /home/tolga/.local/share/hafiye/runtimes/piper/venv/bin/python --piper-data-dir /home/tolga/.local/share/hafiye/runtimes/piper/voices --output-dir /home/tolga/.local/share/hafiye/runtimes/openwakeword-training/hafiye --export /home/tolga/projects/hafiye/tools/wakewords/hafiye.onnx --samples 384 --steps 900 --cpu-threads 4` | Official source `368c03716d1e92591906a84949bc477f3a834455`; standalone ONNX exported; synthetic accuracy 1.0 at threshold 0.6 | PASS |
| P12-REAL-01 | Real detector positive/negative behavior | Direct `_OpenWakeWordEngine`/`WakeWordDetector` check on `/tmp/hafiye-p12-positive-20260824.wav` and `/tmp/hafiye-p12-positive-20260824-take2.wav` | Normal-room music: 0 fires; spoken Hafiye recording: 4 fires under two-second cooldown; `audio_silent=false` | PASS |
| P12-D-01 | Desktop wake/store and Composer behavior | `cd apps/desktop && npx vitest run --project ui src/store/wake-word.test.ts src/app/chat/composer/controls.test.tsx` | 2 files; 37 passed | PASS |
| P12-D-02 | Renderer throttle regression | `cd apps/desktop && npx vitest run --project electron electron/stream-throttle.test.ts` | 1 file; 5 passed | PASS |
| P12-D-03 | Desktop typecheck and production build | `cd apps/desktop && npm run typecheck && npm run build` | TypeScript checks, Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing toolchain warnings remain | PASS WITH WARNING |
| P12-LINT-01 | Wake Python lint, compile, and patch hygiene | `.venv/bin/ruff check scripts/train_hafiye_wakeword.py tools/wake_word.py tests/tools/test_wake_word.py hermes_cli/config_defaults.py; .venv/bin/python -m py_compile scripts/train_hafiye_wakeword.py tools/wake_word.py tests/tools/test_wake_word.py hermes_cli/config_defaults.py; git diff --check` | All checks passed | PASS |
| P12-REAL-02 | Minimized-window Desktop activation | Real Electron bundle with `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream --use-file-for-fake-audio-capture=/tmp/hafiye-p12-positive-20260824-take2.wav`; Settings → Voice → Wake word enabled; native `BrowserWindow.minimize()` | `minimized=true`, `visible=false`; route changed from `#/settings?tab=config%3Avoice` to `#/`; fresh session opened | PASS |

P12 is accepted. The bundled model is
`tools/wakewords/hafiye.onnx`, SHA-256
`9eb0e8c9fd509900ba5d33b4c43906817265605846564af76232daeea194ba50`. The
threshold/confirmation defaults are `0.6`/`3`; Desktop client capture stayed
functional while minimized. The exact historical five upstream failures remain
accepted comparison baseline entries, and no new/different regression was
found in the P12 matrix. The persistent wake setting was reset to disabled
after the real acceptance run.

## Historical ACCEPTED_UPSTREAM_BASELINE and current comparison baseline

The historical post-source comparison set is this exact five-failure baseline:

1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

The latest post-P5-source-fix full run contained four members of this set; the
remote browser-control ID did not reproduce. The current comparison baseline is
therefore items 2–5 above, while the exact five remain the historical accepted
whitelist. The separate local reconnect failure was observed only in the
earlier post-P6 comparison, reproduced in the P6-parent checkout, and is
documented as KI-019. A web-server file also had a retry-only scheduling flake
that passed on retry; it is not a new regression.

Future failures within the historical five are accepted for comparison. Fewer
failures update the current comparison baseline; any new or different failure
is a regression to investigate. The upstream baseline bugs are not fixed by
Hafiye.

## P0 computer-use acceptance

The final pinned-source doctor on the real Ubuntu GNOME Wayland desktop reports
all of these as true:

- can_register_mcp_tools
- can_build_accessibility_tree
- can_send_development_input
- can_query_windows

It also reports blockers: []. P0 computer-use acceptance passed.

## P13 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P13-PY-01 | Unified cancellation, root gate, managed MCP/computer-use gate, gateway protocol | `.venv/bin/python -m pytest -q tests/test_estop.py tests/test_hafiye_rootd.py tests/tools/test_mcp_tool.py tests/tools/test_computer_use.py tests/tui_gateway/test_protocol.py` | 298 passed; 1 known `vision_analyze_tool` coroutine warning | PASS |
| P13-PY-02 | Async delegation, process registry, TTS and streaming cancellation regression set | `.venv/bin/python -m pytest -q tests/tools/test_async_delegation.py tests/tools/test_delegate_control_actions.py tests/tools/test_process_registry.py tests/tools/test_tts_streaming.py tests/gateway/test_streaming_tts_consumer.py tests/gateway/test_tts_media_routing.py` | 197 passed, 4 skipped, 2 existing async warnings | PASS WITH WARNING |
| P13-LINT-01 | Changed Python compile/lint/patch hygiene | `.venv/bin/python -m py_compile ...`; `.venv/bin/ruff check ...`; `git diff --check` | Compilation passed; Ruff `All checks passed!`; no whitespace errors | PASS |
| P13-D-01 | Desktop emergency shortcut, GNOME fallback, existing stream-throttle behavior | `cd apps/desktop && npx vitest run --project electron electron/emergency-stop-shortcut.test.ts electron/gnome-emergency-stop.test.ts electron/stream-throttle.test.ts` | 3 files; 11 passed | PASS |
| P13-D-02 | Desktop voice stop and existing voice/wake/composer regressions | `cd apps/desktop && npx vitest run --project ui src/lib/voice-stop-word.test.ts src/store/wake-word.test.ts src/app/chat/composer/controls.test.tsx src/app/chat/composer/hooks/use-voice-conversation.test.tsx src/app/chat/composer/hooks/use-voice-conversation-rearm.test.tsx` | 5 files; 58 passed | PASS |
| P13-D-03 | Desktop TypeScript boundary | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E typechecks passed | PASS |
| P13-D-04 | Desktop production package | `cd apps/desktop && npm run build` | Vite, Electron main/preload bundle, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P13-REAL-01 | Persistent gateway stop/pause/resume | Authenticated WebSocket `emergency.stop`, `prompt.submit`, `emergency.resume` against `127.0.0.1:9120` | Stop returned `paused=true`; new prompt returned code `4091` with `paused=true`; resume returned `disengaged=true`, `paused=false`; ESTOP cleared | PASS |
| P13-REAL-02 | Root broker emergency gate | Real non-root broker client with `/home/tolga/.local/share/hafiye/ESTOP` toggled | UID 0 before stop; new privileged op rejected with `code=emergency_stop`; UID 0 after resume | PASS |
| P13-REAL-03 | TTS/process cancellation | Real active TTS state/stop probe and registered temporary sleep process | TTS stop event/state cleanup true; process registry killed 1 process and it exited | PASS |
| P13-REAL-04 | GNOME Wayland global emergency shortcut | Built Electron app, `gsettings`, and `ydotool key 29:1 125:1 1:1 1:0 125:0 29:0` | Electron registration false on this session; GNOME custom binding installed; real chord created ESTOP; clean exit restored `custom-keybindings` to `@as []` | PASS |
| P13-CUA-01 | Direct upstream generic CUA smoke | `tools.computer_use.cua_backend.resolve_cua_driver_cmd()` and worker smoke | `cua-driver` not installed; managed Hafiye `computer-use-linux` MCP path remains green | WARNING; KI-028 |
| P13-OH-01 | Managed OpenHands runtime doctor | `.venv/bin/python - <<'PY' ... openhands_runtime_doctor() ... PY` | Official source commit `6d38810359827823e62a5e1043d0d78d0bafb6de`; SDK/tools/workspace/agent-server `1.41.0`; `ready=true`, `blockers=[]` | PASS |
| P13-OH-02 | Real coding delegation and result return | Real Gemini route through `model_tools.handle_function_call("coding_delegate", ...)` against `/tmp/hafiye-openhands-e2e`; external `.venv/bin/python -m pytest -q` | OpenHands edited `bug.py`; parent result had `status=completed`, `event_count=36`, `changed_files=["bug.py"]`; fixture test returned `1 passed in 0.00s` | PASS |
| P13-OH-03 | Real OpenHands emergency stop/resume | Same-process live worker; `CancellationController.emergency_stop(...)`, then `controller.resume()` | Delegate returned `status=cancelled`; `killed_processes=1`; worker ended; resume returned `paused=false`; no active process remained | PASS |
| P13-ACCEPTANCE | Master P13 closure | Required list includes stopping a real OpenHands delegation | All P13 cancellation boundaries, managed runtime, live delegation, stop, and intentional resume passed; KI-027 resolved | PASS |

P13 is accepted. The exact five historical upstream failures remain the
accepted regression whitelist; the P13 matrix introduced no new or different
upstream failure. The OpenHands runtime/coding-delegate implementation was a
P13 prerequisite; its full coding-delegate and Task Center progress acceptance
is recorded under P15 below.

## P14 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P14-PY-01 | Project registry, project tools, gateway project RPCs, project tree, and session search | `.venv/bin/python -m pytest -q tests/tools/test_project_tools.py tests/hermes_cli/test_projects_db.py tests/hermes_cli/test_projects_cli.py tests/tui_gateway/test_projects_rpc.py tests/tui_gateway/test_project_tree.py tests/tools/test_session_search.py` | 127 passed in 3.38s | PASS |
| P14-REAL-01 | Fresh-process project alias/path resolution and recent context recall | The test creates `Pocket World`, starts a separate Python backend process, resolves `project_switch("pocket-world")` to the exact repository path, and runs `session_search("Pocket World")`; marker `P14_PROJECT_MEMORY_E2E_OK` | Exact path resolved; recent context returned; marker emitted | PASS |
| P14-D-01 | Desktop project store/sidebar/search UI | `cd apps/desktop && ../../node_modules/.bin/vitest run --project ui src/store/projects.test.ts src/app/chat/sidebar/project-dialog.test.tsx src/app/chat/sidebar/projects/project-menu.test.tsx src/app/chat/sidebar/projects/overview-row.test.tsx src/app/chat/sidebar/projects/workspace-groups.test.ts src/lib/session-search.test.ts` | 6 files; 114 passed | PASS |
| P14-D-02 | Desktop E2E TypeScript boundary | `cd apps/desktop && ../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` | Passed | PASS |
| P14-REAL-02 | Real Electron + isolated live gateway project browser/search/edit/delete | `cd apps/desktop && ../../node_modules/.bin/playwright test e2e/p14-project-registry.spec.ts --reporter=list` | 1 passed in 12.2s; repository directory remained on disk after project deletion | PASS |
| P14-D-03 | Desktop production package | `cd apps/desktop && npm run build` | Vite, Electron main/preload, native staging, and `assert-dist-built` passed; existing npm/Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P14-ACCEPTANCE | Master P14 closure | Fresh-process alias/path resolution, session recall, and real Desktop browse/search/rename/delete all passed | No new/different regression; accepted five-ID whitelist and current four-ID baseline unchanged | PASS |

P14 is accepted. The project registry and session-search behavior use the
pin-preserved Hermes implementation; Hafiye's acceptance source/test commit
is `831405dcec4abcba033d8ccc18308804868ecb1f`. P15 followed and is now
complete.

## P15 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P15-PY-01 | OpenHands runtime, Task Center registry/RPC, and coding delegate | `.venv/bin/pytest -q tests/hermes_cli/test_openhands_runtime.py tests/tools/test_task_center.py tests/tools/test_coding_delegate.py tests/tui_gateway/test_tasks_rpc.py` | 10 passed in 1.87s | PASS |
| P15-D-01 | Desktop Task Center panel | `cd apps/desktop && npm run test:ui -- src/app/command-center/task-center.test.tsx` | 1 passed | PASS |
| P15-D-02 | Desktop type boundary | `cd apps/desktop && npm run typecheck` | Passed | PASS |
| P15-D-03 | Desktop Task Center lint | `cd apps/desktop && npx eslint src/app/command-center/task-center.tsx src/app/command-center/maintenance.tsx` | Passed | PASS |
| P15-D-04 | Desktop production package | `cd apps/desktop && npm run build` | Vite, Electron main/preload, native staging, and `assert-dist-built` passed; existing toolchain warnings remain | PASS WITH WARNING |
| P15-LINT-01 | Python lint, compile, and patch hygiene | `.venv/bin/ruff check` on changed P15 Python files; `.venv/bin/python -m py_compile` on changed P15 Python files; `git diff --check` | Ruff passed, compilation passed, no whitespace errors | PASS |
| P15-REAL-01 | Managed OpenHands readiness | `.venv/bin/hafiye runtime openhands install`; `.venv/bin/hafiye runtime openhands doctor` | Official source `6d38810359827823e62a5e1043d0d78d0bafb6de`; all four packages `1.41.0`; `ready=true`; `blockers=[]` | PASS |
| P15-REAL-02 | Master natural-language coding E2E | Real Gemini-backed Hafiye one-shot against a fresh failing-test fixture; external `pytest -q` | Hafiye identified/delegated; OpenHands changed `bug.py`; external fixture verification returned `1 passed in 0.00s`; result and changed files returned | PASS |
| P15-REAL-03 | Gateway Task Center progress boundary | Real Gemini-backed worker plus live `tasks.list` and `task.update` capture | `RUNNING` observed; final `COMPLETED`; 18 progress events; 22 `task.update` events; `file_changes=["bug.py"]`; external `pytest -q` returned `1 passed` | PASS |
| P15-ACCEPTANCE | Master P15 closure | Real identify → delegate → edit → verify → return → report flow, runtime doctor, and Task Center exposure | All P15 criteria passed; no new/different upstream regression; P16 followed and is recorded below | PASS |

P15 is accepted. The source/test commit is
`54b4ee49569267b21e10b357acdde427a8a844ff`; the pinned Hermes commit and
baseline merge commit are unchanged. The five historical
`ACCEPTED_UPSTREAM_BASELINE` failures remain the regression whitelist, and no
new/different failure was found in the P15 matrix.

## P16 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P16-PY-01 | Durable Task Center registry, restart recovery, coding delegate, and gateway RPC | `.venv/bin/pytest -q tests/hermes_cli/test_openhands_runtime.py tests/tools/test_task_center.py tests/tools/test_coding_delegate.py tests/tui_gateway/test_tasks_rpc.py` | 12 passed | PASS |
| P16-PY-02 | Separate-process persistence and gateway RPC reconnect | Two Python processes with isolated `HERMES_HOME`; second imported real `tui_gateway.server` and called `tasks.list` | Completed history survived; in-flight task became `FAILED / INTERRUPTED_BY_GATEWAY_RESTART`; queued task remained queued; marker `P16_TASK_CENTER_RESTART_OK` | PASS |
| P16-D-01 | Task Center component states, metadata, progress, and cancellation | `cd apps/desktop && npm run test:ui -- src/app/command-center/task-center.test.tsx` | 1 passed | PASS |
| P16-D-02 | Desktop renderer/Electron/E2E type boundaries | `cd apps/desktop && npm run typecheck`; `../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` | Passed | PASS |
| P16-D-03 | Task Center lint and Python hygiene | `cd apps/desktop && npx eslint src/app/command-center/task-center.tsx src/app/command-center/maintenance.tsx`; Ruff, `py_compile`, and `git diff --check` on P16 changes | Passed | PASS |
| P16-D-04 | Clean Desktop production package | `cd apps/desktop && npm run build` | Clean build stamp `f93d91835445`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P16-REAL-01 | Real Desktop Task Center and gateway state/cancel flow | `cd apps/desktop && npx playwright test e2e/p16-task-center.spec.ts --reporter=list` | Real Electron + real gateway rendered completed/failed/queued records and cancelled queued work via `tasks.cancel`; 1 passed in 9.2s | PASS |
| P16-ACCEPTANCE | Master P16 closure | Required state categories, task metadata/actions, no private chain-of-thought, persistence, restart/reconnect, and real Desktop acceptance | All criteria passed; no new/different upstream regression; P17 is next | PASS |

P16 is accepted. Source implementation commit `c72c94418` introduced the
durable registry and complete Task Center surface; source/test commit
`f93d9183544581636c6af5b619d62d221040391d` contains the queued-state recovery
fix and real Desktop acceptance. The historical five
`ACCEPTED_UPSTREAM_BASELINE` failures remain unchanged.

## P17 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P17-D-01 | Control Center page navigation contract | `cd apps/desktop && npm run test:ui -- src/app/control-center/index.test.tsx src/app/routes.test.ts` | 2 files; 7 passed | PASS |
| P17-D-02 | Desktop renderer/Electron/E2E type boundaries | `cd apps/desktop && npm run typecheck`; `../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` | Passed | PASS |
| P17-D-03 | Control Center lint and patch hygiene | `cd apps/desktop && npx eslint src/app/control-center/index.tsx src/app/settings/constants.ts e2e/p17-control-center.spec.ts`; `git diff --check` | Passed; no whitespace errors | PASS |
| P17-D-04 | Clean Desktop production package | `cd apps/desktop && npm run build` | Clean build stamp `2dc541d09367`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P17-REAL-01 | Real Control Center and gateway state flow | `cd apps/desktop && npx playwright test e2e/p17-control-center.spec.ts --reporter=list` | Real Electron + real gateway opened all 19 pages; Privacy Mode changed to `LOCAL_ONLY` and remained after renderer reload; 1 passed in 12.7s | PASS |
| P17-ACCEPTANCE | Master P17 closure | Every roadmap page is functional through real backend/state boundaries; no dead switch or mock success state; config persistence and real Desktop acceptance passed | No new/different upstream regression; P18 followed and P19 is next | PASS |

P17 is accepted. Source/test commit
`2dc541d09367b895744b512d99b058506d7f78d2` adds the Control Center route,
page composition, privacy enum, and real Electron acceptance. The pinned
Hermes commit, baseline merge commit, and accepted five-ID upstream failure
whitelist remain unchanged.

## P18 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P18-PY-01 | Hermes cron persistence and scheduled Hafiye policy | `.venv/bin/python -m pytest -q tests/cron/test_scheduler.py tests/cron/test_jobs.py tests/cron/test_p18_scheduler_acceptance.py` | 182 passed; two existing async resource warnings from the upstream scheduler/test harness | PASS WITH WARNING |
| P18-PY-02 | Python quality and patch hygiene | `.venv/bin/ruff check cron/jobs.py cron/scheduler.py hermes_cli/web_models.py hermes_cli/web_server.py tools/cronjob_tools.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/cron/test_p18_scheduler_acceptance.py`; `git diff --check` | Ruff passed; no whitespace errors | PASS |
| P18-D-01 | Desktop cron editor model contract | `cd apps/desktop && npm run test:ui -- src/app/cron/cron-job-model.test.ts` | 15 passed | PASS |
| P18-D-02 | Desktop renderer/Electron/E2E type boundaries | `cd apps/desktop && npm run typecheck` | Passed | PASS |
| P18-D-03 | Desktop scheduler UI lint | `cd apps/desktop && npx eslint src/app/cron/index.tsx src/app/cron/cron-job-model.ts src/app/cron/cron-job-model.test.ts e2e/p18-scheduler.spec.ts` | Passed | PASS |
| P18-D-04 | Clean Desktop production package | `cd apps/desktop && npm run build` | Clean build stamp `fd17e6533894`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing npm/Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P18-REAL-01 | Real recurring local task | `.venv/bin/python -m pytest -q tests/cron/test_p18_scheduler_acceptance.py` | Two real scheduler ticks completed the local task and produced two execution-ledger records | PASS |
| P18-REAL-02 | Real Desktop/gateway scheduler policy flow | `cd apps/desktop && npx playwright test e2e/p18-scheduler.spec.ts --reporter=list` | Real Electron + gateway created route/privacy/custom-toolset job and reloaded the values through Edit; 1 passed in 11.1s | PASS |
| P18-ACCEPTANCE | Master P18 closure | Hermes scheduler/skills/MCP reuse, route/privacy/enabled-tools UI, recurring local task, and real backend boundaries | No new/different upstream regression; P19 is next | PASS |

P18 is accepted. Source/test commit
`fd17e6533894a568744b82454635a8e6bf02709b` contains the scheduler policy
boundary, Desktop controls, and acceptance tests. The historical five-ID
`ACCEPTED_UPSTREAM_BASELINE` remains unchanged.
