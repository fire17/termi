# PATTERNS — ground-truth edge cases + how to detect them (highest-bar Phase 4)

Each row: real-world edge case → retroactive detection on any machine.

| Edge case | Detection |
|---|---|
| rc file is a symlink (dotfiles/chezmoi user) | `test -L ~/.zshrc` — termi edits the target, never replaces the link (P3) |
| macOS bash never reads .bashrc (login shells) | `grep -L bashrc ~/.bash_profile 2>/dev/null` — P24; termi notes it on enable |
| `$SHELL` lies (chsh'd but terminal launches something else) | compare `$SHELL` vs `ps -p $$ -o comm=` in the running shell |
| user already owns `command_not_found_handler/handle` | `declare -f`/`functions` inspect before install — termi CHAINS (ADR-8) |
| running terminal predates its config (never loaded) | process lstart vs config mtime (`wezterm_stale`, P19) |
| installed-but-not-active (the half-success that lies) | interactive-probe markers: `TERMIA:<shell>` round-trip (R3 antidote) |
| WSL masquerading as Linux | `grep -qi microsoft /proc/version` |
| pwsh profile path differs per OS | registry `rc` vs `rc_windows`; `$PROFILE` is the runtime truth |
| guessed harness skills dir doesn't exist | skill install skips + says so; `--force-dir` is the explicit override |
| zinit/omz plugins invisible to brew-only scans | profile export parses plugin-manager lines from rc (field log 2026-07-06) |
| stale pack snippet / loader after upgrade | content-diff refresh on install (P23 + loader cousin) |
| two termi processes racing | flock `~/.termi/lock` (P8) |
