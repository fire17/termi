# DARWIN — gap rounds (highest-bar Phase 7)

## Round 1 — 2026-07-13 (phase-2 close-out sweep vs VISION Addendum 3)

Closed this phase:
- ✅ all-shells structure + registries (zsh●, bash●, fish●, pwsh●, nushell scaffolded)
- ✅ PowerShell proven on real pwsh 7.6 (block/loader/recover live)
- ✅ cross-platform installer (POSIX sh + ps1, both parse-verified, idempotent)
- ✅ auto-detection + coverage matrix + agent one-liner (`termi env`, 0.075s)
- ✅ bundled agent skill, self-installed into claude-code + codex (skill went LIVE in the
  building session itself); guessed-dir honesty for opencode/pi/openclaw/hermes
- ✅ extensibility = additive TOML (proven by add-a-fake-shell test)
- ✅ control-everything TUI v2 + enable/disable verbs
- ✅ 87/87 tests, 0 skips

Open (honest), with disposition:
- ○ nushell loader — parse-time `source` needs generated-static approach (registry notes it) → next phase
- ○ fish recover variant → next phase (fish block verified; natives cover keys)
- ○ bash keys binds installed but not suite-verified → status "core", not "verified"
- ○ Windows-NATIVE flows (installer PATH write, WT settings) — no Windows box; marked
  NOT live-verified everywhere they appear → verify on first real Windows machine
- ○ TUI item-level probing is zsh-centric (shell rows cover other shells at block level)
- 📌 F18 tmux/herdr out-of-the-box optimizations — user said "remember for later": recorded
  in README F-map + here; NOT built by design this phase

Round-2 recheck came back with no NEW gaps (same list) → per protocol, stop looping and
report. Exit state: open items are all next-phase scoped or hardware-gated, none block ship.
