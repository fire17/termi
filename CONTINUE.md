# CONTINUE — Termi, for a fresh session with zero context

**What this is:** Termi 💛 — your Terminal Friend. A stdlib-only python3 CLI
(`bin/termi`) + zsh/bash/fish/pwsh shell halves that own the whole terminal experience:
doctor, packs, editor keys, typo-recovery, jumpto, profiles, universal multi-shell
support, agent skill, TUI control center. fire17's founding vision is VERBATIM in
`VISION.md` (SACRED, sha-footer) — 3 addenda, all law.

**Read in this order:** `ORACLE.md` (the wartable pseudo-oracle — 13 ADRs, 25 playbooks,
field log; carries the divergence rule: reality ≠ oracle → stop, log, escalate) →
`README.md` (feature map F1–F22 + usage) → `BUDGETS/IA/PATTERNS/SWARM/DARWIN.md`.

**State (2026-07-13, honest):**
- 87/87 tests, 0 skips: `python3 -m unittest discover -s tests`
- Live-verified on fire17's mac: zsh full stack; bash+fish+pwsh blocks "on"
  (`termi env --deep`); recover working in real bash + real PowerShell 7.6;
  keys/jumpto in zsh incl. wezterm ⌘/⌘⌥ config; skill installed into claude-code+codex.
- NOT verified: Windows-native (no box), nushell loader, fish recover, bash keybinds
  (status "core"). F18 tmux/herdr optimizations: deferred by fire17's explicit word.
- Never published — no repo yet (shipit staged by /sas).

**Everything lives HERE** (~/Creations/Termi is both project home and snapshot — no
files/ copies needed). Installed surfaces on this machine: `~/.local/bin/termi`
(symlink → bin/termi), `~/.termi/` (zsh.d/bash.d/fish.d/ps.d + loaders + snapshots),
managed blocks in `~/.zshrc`, `~/.bashrc`, `~/.config/fish/config.fish`,
`~/.config/powershell/Microsoft.PowerShell_profile.ps1`, `~/.wezterm.lua`.
Registry entry: `~/Creations/termi.md` (changelog = the project's true history).

**Resume:** `claude --resume 90830f22-53fa-4945-b17c-93dff32793a3` from
`~/Creations/Termi`, or read `conversation/*.jsonl` (verbatim, point-in-time).

**Next steps:** ship via /shipit (staged) · nushell loader (generated static file) ·
fish recover variant · bash keybind suite-verification · Windows box verification ·
F18 tmux/herdr pack · F15 "jjk upnext" still awaits fire17's definition.
