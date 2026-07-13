# Termi 🖥️💛 — your Terminal Friend

**One command and you're home.** Termi is the holistic terminal experience — it sets up,
heals, teaches, upgrades, migrates, shares, and syncs your entire dev-env. A friend for
newcomers opening a terminal for the first time, and a level-up even for engineers with
decades of muscle memory. *"Docker from the future, tailored to dev-envs and the terminal
holistic end-to-end experience."*

The founding vision is preserved verbatim in [VISION.md](VISION.md) (SACRED — never edit).
This file is the derived, living map. **Before working on Termi, read [ORACLE.md](ORACLE.md)**
— the wartable pseudo-oracle (2026-07-06): ADRs, playbooks, risk register, invariants,
escalation contract. The moment reality diverges from it, stop and log the divergence.

## v0.2 — universal environments (2026-07-13)

```
termi env             # OS · terminal · mux · shells · harnesses + honest coverage matrix (0.075s)
termi env --deep      # + live activation probe per shell (TERMI_ACTIVE round-trip)
termi shells enable bash|fish|powershell|…   # managed block + loader, any registered shell
termi install recover --shell bash           # per-shell pack variants
termi skill install   # the bundled agent skill → every detected harness (6 known)
termi enable/disable <pack>/<item>           # feature control, snapshot-guarded
termi                 # TUI v2: the control center — see everything, toggle anything
```

Registries in `support/*.toml` — a new shell/terminal/harness is an additive TOML entry
(test-enforced). Live-verified here: zsh+bash+fish+pwsh blocks all "on", typo-recovery
working in real bash AND real PowerShell 7.6. 87/87 tests, 0 skips.
Protocol docs: `BUDGETS.md · IA.md · PATTERNS.md · SWARM.md · DARWIN.md`.

## v0.1 is real (2026-07-06)

```
./install.sh          # symlinks ~/.local/bin/termi (idempotent)
termi doctor          # 3-state honesty: missing / installed-not-active / active
termi packs           # 8 packs, 22 items (shell-qol, navigation, hints, recover, keys, jumpto, modern-unix, dev)
termi keys            # editor-style keys: what's bound + YOUR emulator's exact settings
termi keys apply      # writes ⌘←/⌘→/⌘⌫/⇧⌘← into your emulator's config (managed block, undoable)
termi keys probe      # learns the real byte sequences your terminal sends (F16)
termi install <pack>  # consent per item, snapshot first, managed-block only
termi export -o me.toml && termi import friend.toml   # profiles, secret-screened, R1-guarded
termi undo            # byte-exact restore of the pre-change state
termi                 # the TUI menu
```

**37/37 tests** (`python3 -m unittest discover -s tests`). The strongest ones drive a REAL
interactive zsh through a pty and ask ZLE for its own `$BUFFER`/`$CURSOR` — screen-scraping
lies, because zsh's redraw uses backspaces (`tests/test_keys_pty.py`; the model for verifying
any shell-side feature). Live on this machine: ⌥←/⌥→/⌃← jump words, ⌥⌫ deletes a word,
⇧⌥← selects and typing replaces it, words break on `/` in paths, plain arrows untouched;
typo recovery chains onto a pre-existing `command_not_found_handler` instead of being shut
out by it. `install.ps1` (WSL on-ramp) is still NOT Windows-verified.

> **Ship = build + install + a real keypress.** F16 was built, tested and demoed while
> never actually installed — so ⌥← printed `;3D` in fire17's shell. Two bugs hid behind
> green tests: the installer rejected every snippet-only pack (keys *and* recover could
> never install, on any machine), and doctor reported `✓ active` for recover while another
> handler owned the hook. Both fixed, both now guarded by tests. See ORACLE §4 P17/P18.

---

## Feature map (from the vision)

| # | Feature | Status |
|---|---------|--------|
| F1 | **psst** — tips & warnings before commands run | ✅ EXISTS — shipped v0.4.0, [github.com/fire17/psst](https://github.com/fire17/psst), incl. THE GUARD countdown |
| F2 | **Auto-recovered commands** — auto-fixes typos | ✅ MVP — `recover` pack: OSA-distance matcher, suggests + preloads, never auto-runs (ADR-8) |
| F3 | **Native AI in the terminal** — questions & actions; deep mode when combined with any harness (herdr++) | idea |
| F4 | **Junior onboarding** — help a first-timer set up their terminal end-to-end | 🔨 partial — `termi install` consent-per-item walk + P4 fresh-file birth |
| F5 | **WSL advocacy** — detect Windows PowerShell, kindly scold, explain why serious engineering happens on Linux/WSL, then *walk them through it* (harness-assisted if available) | 🔨 `install.ps1` written, NOT Windows-verified |
| F6 | **Env checks & upgrades** — zsh, battle-tested beautiful statusline, fish-like autosuggestions, zoxide-fuzzy native `cd` via **bettercd** | ✅ `termi doctor` live (3-state honesty); bettercd shipped |
| F7 | **Migrate / cherry-pick** — restore from your backups OR adopt pieces of setups shared by friends/online; choose how much (or all) to take | ✅ MVP — `termi import` (typed-yes untrusted gate) |
| F8 | **Share your own setup** — export what you love, others cherry-pick from it | ✅ MVP — `termi export` (tools + zinit plugins, secret-screened) |
| F9 | **Community features** — (later, once F7/F8 prove out) | future |
| F10 | **SSO/OAuth sign-in → cross-device sync** — never set up from scratch again; 1-command return to the terminal you love | future (profile format is sync-ready, ADR-6) |
| F11 | **Adopt anything already on your system** into your Termi profile | 🔨 partial — export captures active tools + plugin lines |
| F12 | **Hooks, events, triggers** + more interactions/interfaces/user-stories | idea |
| F13 | **Programmatic reproduction** — declarative, deterministic dev-env ("docker from the future") | 🔨 partial — `profile.toml` declarative; lockfile pending |
| F14 | **Own CLI + CLI TUI + agent skills** | 🔨 CLI ✅ + minimal TUI ✅; agent skills pending |
| F15 | **jjk upnext** (board `T67` / seed S25) — awaiting definition from fire17 | queued |
| F18 | **tmux + herdr optimizations out of the box** (Addendum 3) — 📌 "remember that for later", by fire17's word | planned — deliberately deferred |
| F19 | **Universal shell support** (Addendum 3) — zsh · bash · fish · PowerShell · nushell, extensible by TOML entry alone | ✅ registry + engine live; matrix: zsh ●●●●● · bash ●●◐ · fish ●/native · pwsh ●●/native · nu scaffolded |
| F20 | **Cross-platform installer** (Addendum 3) — POSIX sh + PowerShell, auto-detect, coverage matrix + agent one-liner as the post-install screen | ✅ both parse-verified & idempotent; Windows-native flow NOT live-verified |
| F21 | **Bundled agent skill + harness detection** (Addendum 3) — `termi skill install` into claude-code/codex/opencode/pi/openclaw/hermes | ✅ live-installed into claude-code + codex (skill hot-loaded mid-build); guessed dirs skipped honestly |
| F22 | **Control-everything TUI** (Addendum 3) — see + toggle every feature/pack/shell from one raw-mode control center | ✅ TUI v2 + `termi enable/disable/shells` verbs |
| F17 | **jumpto** (2026-07-13, EXPERIMENTAL) — ⌘⌥←/→ enters a jump-to-text mode: type, and the cursor flies to the match inside your line — fuzzy + case-insensitive; ⌃N/↓/Tab next · ⌃P/↑ prev · ↵ accept · Esc cancel | ✅ opt-in pack (`termi install jumpto`); `TERMI_JUMPTO=0` disables |
| F16 | **Great keyboard & mouse in every terminal** (2026-07-13) — ⌥/⌃/⌘ word+line jumps, ⌥⌫ delete-word, ⇧⌥←/→ select like a normal app, click-to-move-caret | ✅ — `keys` pack (ZLE half) · `termi keys apply` (writes the emulator's config for ⌘←/⌘→/⌘⌫/⇧⌘←, managed-block + undo) · `termi keys probe` (learns your terminal's real byte sequences) |

## Recommendations (Claude 💭 — the "what am I missing" list)

**Shell layer** — fzf (fuzzy history/files everywhere — foundational, pairs with bettercd),
zsh-syntax-highlighting (red-before-you-run), atuin (SQLite shell history with encrypted
sync — *this is the F10 sync story for history, already solved*), completions everywhere.

**Modern replacements pack** — eza (ls), bat (cat), fd (find), ripgrep (grep), delta (git
diff), dust/duf (du/df), btop (top), tealdeer (tldr — example-first man pages; natural psst
sibling). Ship as an opt-in "modern-unix" pack — psst already nudges toward these, so Termi
installs what psst preaches.

**Statusline** — starship as the battle-tested default (cross-shell, TOML, fast), powerlevel10k
as the zsh-native alternative; Nerd Font install is the hidden prerequisite Termi must handle
(the #1 silent failure for juniors — broken glyphs).

**Env & runtime** — mise (asdf successor: per-project runtimes + env), direnv, gh CLI.
**Terminal emulator counsel** — ghostty/kitty/wezterm recommendations per-OS + font setup.

**Substrate for F7/F8/F13 (the big one)** — a declarative **Termi profile**: a single
manifest (`termi.yaml` + lockfile) listing shell, plugins, packs, tools, dotfiles, secrets
policy. `termi apply` is idempotent; every apply snapshots prior state → `termi undo`.
chezmoi (templates + age-encrypted secrets) is the strongest existing engine to build on or
learn from. Cherry-picking = selecting entries from someone else's manifest — never raw
file copies. **Never clobber** the user's existing config: additive, reversible, diff-first.

**Safety rails** — trash-put over rm, `--force-with-lease` habits — psst's GUARD already
covers the warn-and-hold half; Termi installs the safer defaults half.

**The doctor** — `termi doctor`: one command that checks every layer (shell, PATH health,
font/glyphs, git identity, ssh keys, plugin conflicts, startup-time budget with per-plugin
blame) and offers fixes. This is the recurring re-entry point and the junior's lifeline.

**Sync (F10) staging** — offline-first: profile in a private git repo or E2E-encrypted blob
first (works TODAY, no auth server); SSO/OAuth becomes a convenience layer over the same
format later. Atuin proves the encrypted-sync pattern.

## Architecture sketch 💭

```
termi CLI ─┬─ doctor      # detect & heal (F5, F6)
           ├─ setup       # guided onboarding, packs (F4)
           ├─ profile     # export / import / cherry-pick / apply / undo (F7, F8, F11, F13)
           ├─ ai          # native ai + harness bridge (F3, herdr++)
           ├─ hooks       # events & triggers (F12)
           └─ tui         # the friendly face (F14)
agent skills: termi-setup / termi-doctor / termi-migrate  (F14)
```

## Ecosystem ties

- **psst** and **bettercd** are shipped, published Termi ingredients — Termi orchestrates them.
- **herdr** is the harness layer F3 refers to ("herdr++").
- Registry entry: `~/Creations/termi.md` · Seed **S25** ⇄ board **T67** (`~/General/todos/TODOS.md`, P11 Products & Apps).

## Roadmap sketch 💭

1. **v0.1 — doctor + packs**: `termi doctor` + zsh/starship/autosuggestions/fzf/bettercd/psst
   install with consent-per-item. Immediately valuable, no accounts, no sync.
2. **v0.2 — profiles**: manifest + apply/undo/export; migrate-from-backup; cherry-pick from a shared file.
3. **v0.3 — TUI + AI**: the friendly face; native ai + harness detection.
4. **v0.4 — WSL flow** + Windows detection story.
5. **v1.0 — sync**: git/E2E first, SSO layer after. Community features once sharing proves out.
