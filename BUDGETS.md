# BUDGETS — vision adjectives as enforced numbers (highest-bar Phase 2)

Derived 2026-07-13 from VISION.md Addendum 3. A regression here is a build failure.

| Vision adjective | Metric | Threshold | Test |
|---|---|---|---|
| "best cli the world has ever seen" — instant | `termi env` wall time | ≤ 0.35s | `time termi env` |
| same — doctor snappy at full breadth | `termi doctor` wall time | ≤ 2s (I4) | `time termi doctor` |
| TUI feels like your hand (B.3 latency-is-emotion) | keypress → redraw | ≤ 50ms perceived; no flicker (repaint via ANSI, no clear-scroll) | manual feel-test + no `clear` in TUI loop |
| "good install script" | fresh install to working `termi` | ≤ 5s excl. downloads; idempotent (I6) | double-run `install.sh` |
| "auto recognizes" | detection with zero flags | shells+OS+terminal+mux+harnesses all detected with no args | `termi env` output inspection |
| "tested verified coverage" | every matrix cell backed | each `verified` claim has a passing test on this machine; everything else says `core`/`planned`/`untested` — never overstated | test suite + matrix source audit |
| "easily extend" | new shell/terminal/harness | additive TOML entry only — zero python edits for detection+listing | add-a-fake-entry test |
| "windows powershell" | pwsh mechanics | block/loader/recover proven on real pwsh (macOS pwsh); Windows-native marked NOT live-verified | pwsh tests (skip-if-absent) |
| "control everything" | every pack item | enable/disable/status via CLI verb AND TUI | disable→doctor→enable round-trip test |
| zero overhead | idle cost | no daemons, no login-time slowdown > 5ms added per shell (loader is a glob+source) | `time zsh -ic exit` delta |
