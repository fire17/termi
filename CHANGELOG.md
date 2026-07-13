# Changelog

## 0.2.0 — 2026-07-13 · universal environments
- support registries (`support/*.toml`): shells · terminals · harnesses — additive TOML
  extension, honest per-feature statuses (test-enforced vocabulary)
- multi-shell engine: managed block + loader + snapshot/undo for zsh · bash · fish ·
  PowerShell (nushell scaffolded); `termi shells enable/disable <id>`
- `termi env [--deep|--json]`: OS/terminal/mux/shell/harness detection, coverage matrix,
  agent one-liner (0.075s)
- recover ported: bash (`command_not_found_handle`, chains existing) + PowerShell
  (`CommandNotFoundAction`) — both live-verified; per-shell pack variants
  (`termi install <pack> --shell <id>`)
- cross-platform installers: `install.sh` (POSIX) + `install.ps1` (Windows-native flow
  not yet live-verified); both parser-validated, idempotent
- bundled agent skill (`skills/termi`) + `termi skill install` into detected harnesses
  (claude-code/codex verified live; guessed dirs skipped honestly)
- `termi enable/disable <pack>/<item>` + TUI v2 control center (raw-mode, CSI-aware keys)
- 87 tests, 0 skips

## 0.1.x — 2026-07-06 → 2026-07-13 · the foundation
- doctor (3-state honesty) · 8 packs / 22 items · managed-block + snapshot + undo law
- keys (F16): ⌥/⌃/⌘ motions, ⇧-select, ⌘⌥ jumpto (F17, experimental) · wezterm config
  writer + `keys probe` · typo auto-recovery (OSA distance, suggest-never-run)
- profiles: export/import, secret-screened, typed-yes untrusted gate
