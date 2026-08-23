# Upstream Hermes State

## Remotes

`origin   https://github.com/tolgaakcaoglu/hafiye.git`
`upstream https://github.com/NousResearch/hermes-agent.git`

## Separate commit identities

- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`
- Current Hafiye HEAD at the last state capture: `0b2febafcead545b208f1e91c237c9f40bab40f9`

The pinned commit is the Hermes code baseline. The baseline merge commit is the Hafiye history-preserving merge. The current Hafiye HEAD is a separate repository commit and must not be confused with either upstream SHA.

## Pinned Hermes base

- Upstream ref: `upstream/main`
- Pinned commit subject: `fix(dashboard): detect stale code after hermes update and refuse model picker with clear 503 (#86207)`
- Last fetch: `2026-08-23`
- Hafiye development branch: `hafiye/p0`

The branch was created from `upstream/main` and merged with the original Hafiye documentation history using `--allow-unrelated-histories`. Both histories remain reachable; Hermes history is not rewritten.

## Sync and conflicts

- The initial merge had one add/add conflict in `AGENTS.md`. The current file carries the Hafiye binding instructions first and preserves the upstream Hermes development guide below them.
- No Hermes runtime/Desktop source patch has been applied during P0.
- Hafiye repository-instruction and evidence-document changes are kept separate from the upstream-derived history.
- The working branch intentionally tracks `upstream/main` for upstream visibility; `origin` remains the Hafiye repository.

## Hafiye patch groups

No product patch groups exist yet. Future changes should remain separable under the roadmap's groups:

`
branding
xdg-paths
persistent-gateway
local-model-runtime
routing
linux-computer-use
root-broker
voice-local-stack
hafiye-wakeword
project-registry
openhands
control-center
packaging
`

## Accepted upstream test baseline

Before Hafiye source changes, the canonical backend suite with relevant optional SDKs completed with 36,903 passed, 5 failed, and 320 skipped. The exact five test IDs are recorded in `KNOWN_ISSUES.md` and `TEST_MATRIX.md` as `ACCEPTED_UPSTREAM_BASELINE`.

After Hafiye source changes, the same five failures are not regressions. A smaller failure set updates the baseline; any new or different failure requires investigation. Hafiye P0 does not fix these upstream bugs.

## Computer-use-linux pinned source

- Repository: `https://github.com/agent-sh/computer-use-linux`
- Pinned source commit: `94736dc3e0dca56acfc89752c26869fb9ed01202`
- Source checkout used for setup: `/tmp/hafiye-computer-use-linux.djXfCX/repo`
- Source package version: `0.4.10`
- Official final P0 setup path: run the pinned checkout's `./install.sh`, allowing its official system-dependency, Rust, build, AT-SPI, ydotoold, and GNOME extension steps. Then run the source-installed `computer-use-linux doctor`.
- Official setup commands available from this checkout include `computer-use-linux setup` and `computer-use-linux setup-window-targeting` where the installer or doctor requires them.
- The source's expected `0.4.10` GitHub release asset returned HTTP 404. Released npm `0.4.9` was used only for the historical diagnostic and is not the final setup path.
- Historical normalized doctor output is saved at `docs/p0/computer-use-linux-doctor-report.json`.

P0 computer-use acceptance requires:

- `can_register_mcp_tools = true`
- `can_build_accessibility_tree = true`
- `can_send_development_input = true`
- `can_query_windows = true`
- `blockers = []`

## Baseline divergence

The upstream Hermes baseline contains its own `cua-driver` computer-use integration. Hafiye has not changed or replaced it in P0; the roadmap-prescribed `agent-sh/computer-use-linux` integration remains a later Hafiye phase.
