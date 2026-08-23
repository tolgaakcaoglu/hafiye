# Upstream Hermes State

## Remotes

```text
origin   https://github.com/tolgaakcaoglu/hafiye.git
upstream https://github.com/NousResearch/hermes-agent.git
```

## Pinned Hermes base

- Upstream ref: `upstream/main`
- Pinned commit: `f293e7206b4ddd66042329442c6afebc19a8808d`
- Upstream commit subject: `fix(dashboard): detect stale code after hermes update and refuse model picker with clear 503 (#86207)`
- Last fetch: `2026-08-23`
- Hafiye development branch: `hafiye/p0`
- Hafiye baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`

The current branch was created from `upstream/main` and merged with the original Hafiye documentation commit using `--allow-unrelated-histories`. This keeps both histories reachable and avoids rewriting Hermes commits.

## Sync and conflicts

- Initial upstream fetch completed successfully.
- The merge had one add/add conflict in `AGENTS.md`. The Hafiye repository instruction file was retained because it is the binding repository instruction supplied for this project. No upstream Hermes source conflict was resolved or changed.
- No Hafiye source patch has been applied during P0.
- The working branch intentionally tracks `upstream/main` for upstream visibility; `origin` remains the Hafiye repository.

## Hafiye patch groups

No patch groups exist yet. Future changes should remain separable under the roadmap's groups:

```text
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
```

## Computer-use-linux research snapshot

- Repository: `https://github.com/agent-sh/computer-use-linux`
- Current source commit inspected: `94736dc3e0dca56acfc89752c26869fb9ed01202`
- Current source package version: `0.4.10`
- The current source's npm installer requested release assets under `v0.4.10`; GitHub returned HTTP 404 for the Linux x86_64 asset.
- The released npm package `@agent-sh/computer-use-linux@0.4.9` was installed temporarily under `/tmp` with its SHA-256-verified release binaries and used for the real `doctor` run.
- The exact normalized diagnostic is saved in `docs/p0/computer-use-linux-doctor-report.json`.

## Baseline divergence

The upstream Hermes baseline currently contains its own `cua-driver` computer-use integration. Hafiye has not changed or replaced it in P0; the roadmap-prescribed `agent-sh/computer-use-linux` integration remains a later Hafiye phase.
