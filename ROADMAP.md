# Roadmap

The authoritative phase definitions are in `HAFIYE_MASTER_ROADMAP.md`. This file records execution status only.

- [ ] P0 Fork + environment
- [ ] P1 Hafiye external identity and data root
- [ ] P2 Persistent gateway + Desktop connection
- [ ] P3 Hafiye Composer + tray + autostart
- [ ] P4 llama.cpp managed local runtime
- [ ] P5 Providers + Gemini + remote OpenAI-compatible
- [ ] P6 Model router + privacy modes
- [ ] P7 Full host tools + execution policy
- [ ] P8 Hafiye root broker
- [ ] P9 Linux computer use
- [ ] P10 Browser
- [ ] P11 Local Turkish voice stack
- [ ] P12 Custom Hafiye wake word
- [ ] P13 Barge-in + emergency stop
- [ ] P14 Memory + project registry
- [ ] P15 OpenHands coding delegate
- [ ] P16 Task Center
- [ ] P17 Control Center
- [ ] P18 Scheduler / skills / MCP
- [ ] P19 Hardening
- [ ] P20 Packaging
- [ ] P21 First-run onboarding
- [ ] P22 CLI
- [ ] P23 Final E2E suite

## P0 execution status

- [x] Preserve upstream Git history and establish `hafiye/p0`.
- [x] Configure `origin` and `upstream`.
- [x] Record the pinned Hermes commit in `UPSTREAM.md`.
- [x] Inspect and record the real Ubuntu/Linux environment.
- [x] Install the user-space Python toolchain needed by the upstream constraints.
- [x] Run the unmodified upstream backend test suite.
- [x] Re-run the unmodified backend suite after installing relevant optional test SDKs.
- [x] Build and test the unmodified Hermes Desktop baseline.
- [x] Run and record the real `computer-use-linux doctor` diagnostic.
- [ ] P0 acceptance: baseline and readiness blockers resolved or accepted with no remaining blocker.

P0 remains open. No P1 work has started.
