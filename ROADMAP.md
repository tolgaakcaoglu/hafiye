# Roadmap

The authoritative phase definitions are in `HAFIYE_MASTER_ROADMAP.md`. This file records execution status only.

- [x] P0 Fork + environment
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
- [x] Run and record the historical real `computer-use-linux doctor` diagnostic.
- [x] Complete the pinned-source official setup and pass the final doctor readiness acceptance.
- [x] P0 acceptance: the five Hermes failures are recorded as `ACCEPTED_UPSTREAM_BASELINE`, no new/different Hafiye regression exists, and the pinned-source computer-use-linux doctor reports all required capabilities true with `blockers=[]`.

P0 is complete. The accepted Hermes baseline failures, missing `pactl`, and missing `vulkaninfo` are not blockers. P1 is the next phase.
