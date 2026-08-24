# Hafiye Release Record

## P20 packaging validation — 2026-08-24

The first Ubuntu/Debian package assembly is implemented by
`scripts/build_deb.py`. It wraps the real Electron `linux-unpacked` build with
the Hafiye backend, the user-scoped `hafiye-gateway.service`, the explicit
per-user root-broker activation path, XDG application/autostart entries,
icons, dependency doctor/installer, and license/notices.

Build the Desktop first, then assemble the package:

```bash
cd apps/desktop && npm run pack
cd ../..
.venv/bin/python scripts/build_deb.py --output dist/hafiye_0.20.5_amd64.deb --desktop-dir apps/desktop/release/linux-unpacked
```

The generated artifact is intentionally ignored by Git under `dist/`. Its
`/usr/lib/hafiye/package-manifest.json` records the pinned Hermes commit, the
history-preserving baseline merge, and the source commit used for the build.
Managed llama.cpp, whisper.cpp, Piper, and computer-use runtimes remain
first-run/user-data installs as required by the master roadmap. `hafiye package
doctor` diagnoses the package and `hafiye package install` installs the locked
Python extras into the user-scoped Hafiye venv.

The package was built with `dpkg-deb`; a fixture package test and an extract of
the real 119 MB artifact passed. Rootless `fakeroot dpkg --unpack` and
`fakeroot dpkg --configure` passed with `--force-not-root
--force-script-chrootless --force-depends`; the dependency warnings are
expected because the temporary dpkg database intentionally contains no host
packages. A privileged install on a real Ubuntu/Debian host remains the final
release-signing validation.
