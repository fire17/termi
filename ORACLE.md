# Termi ORACLE — the pseudo-oracle (wartable 2026-07-06)

Forged by Fable 5 at maximum context, per `/wargame`. **Read this before touching Termi.**
If reality diverges from what this oracle predicts: **STOP, append the divergence to §8
(field log), and escalate** — do not improvise past a broken map.

---

## 1 · Context capsule

**Termi is your Terminal Friend** — one product that owns the terminal experience end to
end: diagnose (`doctor`), set up (`setup`/packs), migrate/share (profiles), teach
(psst + onboarding), and eventually sync (SSO). Vision verbatim: `VISION.md` (SACRED).
Feature map F1–F15: `README.md`.

The *why behind the why*: terminal mastery is fragmented tribal knowledge. fire17 already
shipped two fragments — **psst** (hints/warnings, pure zsh, brew `fire17/tap/psst`) and
**bettercd** (zoxide-fuzzy cd, pure zsh, brew `fire17/tap/bettercd`). Termi is the umbrella
that makes the whole loved setup a portable, reproducible, shareable artifact. The metaphor
that governs design taste: *"docker from the future, tailored to dev-envs"* — declarative
manifest in, identical terminal out, additive and reversible always.

Two audiences, one bar: a junior must never be stranded; a 20-year expert must still feel
a level-up. Every feature must serve both or stay out.

## 2 · Decision records

**ADR-1 · Core language: Python 3 stdlib-only, zsh shim for shell-side.** `bin/termi` is
python3 (argparse, no pip deps ever in core); `termi.zsh` is the sourced shell half.
Rejected: pure zsh (doctor/profile logic + TOML handling too complex; psst/bettercd stay
zsh because they live *inside* the prompt loop — Termi is a tool you *run*), Go+Charm
(single-binary is attractive — revisit at the v0.3 TUI milestone if the ANSI TUI feels
weak). Consequence: python3 is a hard dep — install.sh must guarantee it (§4 P1).
**ADR-2 · Profile format: TOML** (`~/.termi/profile.toml`). Read via stdlib `tomllib`
(needs python ≥3.11); written by our own tiny emitter (our schema is flat — trivial).
Rejected: YAML (needs a pip dep — breaks ADR-1), JSON (hostile to hand-editing).
Revisit if: python <3.11 shows up in the field (then vendor a 200-line TOML reader).
**ADR-3 · Mutation law: managed-block + snapshot + undo.** Termi touches `~/.zshrc` ONLY
inside one marker pair `# >>> termi >>>` / `# <<< termi <<<` containing a single
`source ~/.termi/termi.zsh` line. Everything else Termi controls lives under `~/.termi/`.
Every mutating command snapshots prior state to `~/.termi/snapshots/<UTC-ts>/` first.
`termi undo` restores the latest snapshot. Non-negotiable — this is the SACRED rule's
code-shaped twin.
**ADR-4 · Packs are declarative TOML data**, not code: name, why-line, per-OS install
(brew formula / apt pkg), `check` command, optional zshrc snippet + psst hints. Consent
per item, always, with the why shown. Rejected: shell-script packs (arbitrary code =
untrustable for F7 sharing; see §5 R1).
**ADR-5 · Distribution: house pattern.** GitHub `fire17/termi` + `fire17/homebrew-tap`
formula + curl-able `install.sh`. NOTHING leaves the machine without fire17's explicit
confirmation (registry hard rule 2) — build publish-ready, then ask.
**ADR-6 · Sync (F10) is offline-first.** v1 sync = the profile in a private git repo
(or any file channel); SSO/OAuth is a later convenience layer over the same format.
Rejected for now: building an auth server (premature; atuin proves E2E-encrypted sync
can come later without format changes).
**ADR-12 · Shells, terminals, and harnesses are DATA (support/*.toml).** Adding one is an
additive registry entry — zero python edits for detection/listing/enabling (proven by the
add-a-fake-shell test). Every entry carries honest per-feature statuses (verified/native/
core/planned/untested) and the coverage matrix renders straight from those words — a
`verified` cell without a backing test is a lie and a build failure. Activation truth is
the `TERMI_ACTIVE` marker each loader exports, round-tripped through a real interactive
shell (`probe` + `probe_echo`) — the uniform R3 antidote across shells.
**ADR-13 · The TUI owns raw mode for its whole lifetime.** Per-key raw/cooked toggling
leaves cooked gaps (echo + line-buffered swallows); shell-outs get cooked()/raw() wraps.
Key reads are CSI-aware (`_tui_key`): a fixed burst window is a scheduling race — under
load an arrow's bytes split past it and the stream desyncs (P21's failure mode). Raw
rendering needs `\r\n`; repaint via `\033[H\033[J` write, never clear-scroll (no flicker).
**ADR-11 · jumpto (F17) is EXPERIMENTAL, opt-in, and instantly killable.** Its own pack
(`termi install jumpto`), and `TERMI_JUMPTO=0` makes the widget decline at runtime with
the bindings still in place — never a shell you have to repair. Search runs **fork-free
pure zsh** (`_termi_jump_matches` fills a global array): it executes on every keystroke,
so a subshell per char would be felt. Exact case-insensitive substring matches win
outright; the fuzzy subsequence fallback runs ONLY when there are no exact hits —
otherwise `ab` "fuzzy-matches" half the line and the feature feels random. Wire ⌘⌥←/→ to
**CSI modifier 7** (`\e[1;7D/C`) — the same bytes ⌃⌥ produces on Linux/Windows, so one
binding serves every platform.
**ADR-10 · Termi MAY write the emulator's config — under the same law as `.zshrc`.**
(2026-07-13, amending ADR-9's "detect and instruct" for text-config terminals.) ⌘←/⌘→
send *nothing* by default, so no shell binding can ever catch them — instructing the user
was leaving the feature broken. `termi keys apply` writes a **managed block** (`>>> termi >>>`
markers) into the emulator config, snapshot-guarded and reverted by `termi undo` — never
touching a byte outside its markers. Text configs only (wezterm/kitty/ghostty); a fresh
wezterm file is created whole, an existing one is injected **before its `return <var>`**
line (retargeted to their variable name) or termi refuses and prints the block. GUI/plist
terminals (iTerm2, Terminal.app) are still instructions-only — never poke a plist.
**ADR-9 · Keys: bind the SHELL, configure the EMULATOR, never fake the difference.**
Word-jumps/selection/delete-word are ZLE bindings Termi installs (bind every sequence
the common emulators send — inert ones are harmless). But **⌥-as-Esc+ and
click-to-move-cursor are emulator settings Termi cannot set** — it detects the emulator
and prints the exact toggle. Never claim a capability the emulator lacks (wezterm has no
click-to-move-cursor; say so). `termi keys probe` closes the loop by learning the
terminal's REAL byte sequences. Rejected: enabling SGR mouse reporting from zsh to get
click-to-move — it hijacks selection/scrollback and breaks every other TUI (§3).
**ADR-8 · Auto-recover suggests + preloads, NEVER executes.** The typo fix goes into the
composer via `print -z` (press ↵ to run); auto-running a guessed command is how you run
the wrong `rm`. On an existing `command_not_found_handler` (brew/ubuntu/the user's own):
**CHAIN, don't refuse** — copy it aside with `functions -c` and call it when termi has no
close match. (Amended 2026-07-13: "define ours only if absent" meant termi was silently
shut out on any machine that already had a handler — fire17's did. Refusing is not safety,
it's a dead feature.) Non-negotiable, like ADR-3.
**ADR-7 · Termi orchestrates siblings, never absorbs them.** psst and bettercd are
installed/configured/health-checked by Termi via brew + their own CLIs. Never vendor,
fork, or reimplement them. Revisit if: a sibling's CLI breaks Termi twice (then pin
versions in the pack).

## 3 · Dead ends (do not rediscover)

- **chezmoi/stow as the profile engine** — evaluated 2026-07-06: powerful but wrong
  center of gravity; they manage *files*, Termi manages *capabilities* (tools+config+
  hints). We may still *recommend* chezmoi for raw dotfiles. Don't rebuild Termi on it.
- **Auto-editing arbitrary lines of the user's `.zshrc`** (e.g. sed-ing their aliases) —
  forbidden forever; it's how every dotfile tool earns hatred. Managed block only (ADR-3).
- **`curl | sh` snippets inside packs/profiles** — never; see §5 R1.
- **Detecting the terminal font programmatically** — unreliable across emulators;
  use the render-and-ask probe instead (§4 P6).
- **Enabling mouse reporting (`\e[?1000h`/SGR) from zsh to implement click-to-move-cursor**
  — evaluated 2026-07-13 and rejected: it steals the mouse from the emulator (no
  text selection, no scrollback) and fights every TUI you launch. Click-to-move is an
  emulator feature (Terminal.app/iTerm2 natively; kitty/ghostty via shell integration);
  Termi's job is to detect and instruct, not to hijack (ADR-9).
- **`chsh` automation** — needs the user's password interactively; print the command,
  don't run it (§4 P5).

## 4 · Playbooks (symptom-keyed — what you SEE → what you DO)

- **P1 · `python3: command not found` / `No module named tomllib`** — macOS: run
  `xcode-select --install` then retry; or `brew install python3`. Debian/WSL:
  `sudo apt-get update && sudo apt-get install -y python3`. tomllib missing = python
  <3.11 → same fix (brew/apt give ≥3.11). install.sh must check BEFORE invoking termi:
  `python3 -c 'import tomllib' 2>/dev/null || <the above>`.
- **P2 · `brew: command not found`** — macOS: offer the official installer (prints, asks
  consent — it's `curl|bash`, the ONE sanctioned exception, upstream official only, URL
  hardcoded: `https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh`).
  Linux/WSL: skip brew entirely; packs use their `apt` field. A pack with no apt field
  reports "unavailable on this OS" honestly — never guess a package name.
- **P3 · `.zshrc` is a symlink** (dotfiles repo / chezmoi user) — do NOT replace the
  symlink with a file (silently orphans their repo). Resolve with `os.path.realpath`,
  edit the target in place, and WARN: "your .zshrc is a symlink → edited <target>;
  commit it in your dotfiles repo."
- **P4 · No `.zshrc` at all** (fresh machine/junior) — create it containing only the
  managed block + a friendly comment header. Snapshot the nothing-state first so undo
  returns to no-file.
- **P5 · `$SHELL` is not zsh** — macOS default IS zsh since Catalina; bash means the
  user chose it or it's old Linux. Print (never run): `chsh -s $(which zsh)` + why,
  offer to continue anyway with degraded checks. Detect via `$SHELL` basename, not `ps`.
- **P6 · Glyphs look broken after starship install** (user reports `?`/boxes) — Nerd
  Font missing, the #1 silent junior failure. Doctor's font probe: print `` and
  ask "does this look like a branch symbol? [y/n]" — on n: macOS
  `brew install --cask font-jetbrains-mono-nerd-font` + "select it in your terminal's
  settings" (per-emulator steps in the pack's why-file). NEVER skip the probe after
  installing starship.
- **P7 · Pack `check` passes but the tool doesn't work in the user's shell** (installed
  ≠ active — the half-success that lies). Verify activation separately:
  `zsh -ic '<activation probe>'` (e.g. `type __zoxide_z`, `[[ -n $ZSH_AUTOSUGGEST_STRATEGY ]]`).
  Report three states honestly: `missing` / `installed-not-active (reload or re-source)` /
  `active`. Doctor exit code only greens on active.
- **P8 · Two termi processes racing** (both mutating) — `~/.termi/lock` via
  `fcntl.flock` non-blocking; loser prints "another termi is running (pid N)" and exits
  3. Never queue silently.
- **P9 · `termi apply` re-run** — must be a no-op (idempotent): managed block replaced
  in place (regex spans the markers), pack installs skipped when check+activation pass,
  snapshot still taken (cheap) so undo history stays linear.
- **P10 · brew install fails mid-pack** (network/sudo/keg conflict) — report per-item
  results table (ok/failed/skipped + stderr tail), continue remaining items, exit 1.
  Never abort the whole pack on one failure; never retry-loop brew.
- **P11 · Imported profile wants something suspicious** — see §5 R1: raw `zshrc_extra`
  content from a non-builtin source renders as a full diff with a red UNTRUSTED banner,
  requires typing `yes` (not y). No API keys/secrets ever go INTO a profile export —
  the exporter regex-screens for `KEY|TOKEN|SECRET|PASSWORD|BEGIN.*PRIVATE` and refuses
  those lines with a notice (they stay local; sync of secrets is explicitly out of scope
  until F10's encrypted layer).
- **P12 · Windows PowerShell user** (F5) — Termi core cannot run there; the flow is
  `install.ps1`: kindly explain (never mock) why serious dev happens on Linux/WSL,
  then offer to run `wsl --install` (needs admin + reboot), then re-run install.sh
  inside WSL. WSL detection from inside Linux: `grep -qi microsoft /proc/version`.
- **P14 · "⌥← does nothing / prints `[D` / inserts a weird char"** — the emulator is
  eating or mis-sending the ⌥ key; NO shell binding can fix that. Run `termi keys` and
  apply the printed emulator setting (iTerm2: Left Option = Esc+ · Terminal.app: Use
  Option as Meta · ghostty: `macos-option-as-alt = true` · kitty: `macos_option_as_alt yes`
  · wezterm: `send_composed_key_when_left_alt_is_pressed = false` · VS Code:
  `terminal.integrated.macOptionIsMeta: true`). Inside tmux also needs
  `set -g xterm-keys on`. Then `termi keys probe` to confirm what actually arrives.
- **P15 · `termi keys probe` says "that's a PLAIN key"** — the terminal sent e.g. `\e[D`
  (plain ←) for ⌥←, meaning the modifier never reached it. Termi REFUSES to bind it
  (binding it would break the plain arrow). This is P14 — fix the emulator, re-probe.
  Same rule if two combos report the same sequence: both are skipped, not guessed.
- **P16 · Shift-select highlights nothing / typing doesn't replace the selection** —
  needs zsh ≥ 5.0.8 (`REGION_ACTIVE`). Check `zsh --version`. If autosuggestions is
  installed, confirm it WRAPPED our widget rather than replacing it:
  `zle -l | grep autosuggest-orig.*self-insert` must show `(_termi_self_insert)`.
  If it shows something else, the keys snippet loaded AFTER autosuggest's bind pass —
  verify `~/.termi/zsh.d` ordering (keys = 50, autosuggestions = 30). Escape hatch:
  `TERMI_KEYS_TYPE_OVER=0` disables only the typing-replaces-selection half.
- **P24 · "termi works in zsh but bash acts like it's not installed" (macOS)** — macOS
  Terminal/WezTerm open bash as a LOGIN shell, which reads `~/.bash_profile`, NOT
  `~/.bashrc`. Termi's block lives in .bashrc (the cross-platform convention). Fix:
  ensure `~/.bash_profile` contains `[ -r ~/.bashrc ] && . ~/.bashrc`. `termi shells
  enable bash` prints this note; interactive NON-login (`bash -ic`, subshells) work
  regardless — which is why probes pass while a login terminal misses termi.
- **P25 · pwsh one-liners: `$?` inside an expression is a PARSE error** — pwsh can't do
  `(cmd; $?)` inline; split into statements ($pyOk pattern in install.ps1). Validate any
  .ps1 with pwsh's own parser before shipping:
  `[System.Management.Automation.Language.Parser]::ParseFile(...)` — the ADR-10 lesson
  (verify with the tool's own parser) applies to every config/script format.
- **P23 · "I edited a pack but nothing changed in my shell"** — snippet updates propagate
  on the next `termi install <pack>` run: an active item whose INSTALLED snippet file
  differs from the pack is rewritten ("snippet refreshed"). Guard: an item active with NO
  termi snippet file (e.g. provided by zinit) is never touched — refresh only maintains
  what termi itself installed. Then `exec zsh`.
- **P21 · A ZLE widget that reads keys eats arrow keys as "Escape"** — an arrow arrives as
  `ESC [ D`, and a naive `read -k` loop sees the bare ESC and cancels. After ESC, do a
  timed read (`read -k 1 -t 0.06`): if bytes follow, drain the CSI to its final letter and
  act on that (D/A = prev, C/B = next); if nothing follows, THAT is a real Escape keypress.
  `_termi_jump_csi` is the reference implementation.
- **P22 · Testing an interactive ZLE mode: never press Enter to inspect it** — Enter
  EXECUTES the line. Bind a spare key (⌃T/⌃G) to a widget that dumps `$BUFFER`/`$CURSOR`
  to a file, and press that. (A test that pressed Enter silently ran `git commit`.)
- **P19 · "⌘← does nothing"** — the emulator sends no bytes at all for ⌘-arrows (unlike ⌥,
  which sends a real CSI). The shell is already listening for `\e[H`/`\e[F`/`\x15`. Run
  `termi keys apply` (wezterm/kitty/ghostty: writes a managed block) or apply the printed
  GUI step (iTerm2/Terminal.app). Verify without guessing: `wezterm --config-file
  ~/.wezterm.lua show-keys | grep SUPER` — wezterm names ⌘ **SUPER**, and must list
  `SendString("\u{1b}[H")`. (The wezterm binary may not be on PATH; it lives at
  `/Applications/WezTerm.app/Contents/MacOS/wezterm`.)
  **The parser passing does NOT mean the running instance has it** (bitten live
  2026-07-13): a WezTerm launched when NO config file existed is not watching the path
  and will never hot-reload it — only a full quit+reopen loads it (a new tab/window is
  not enough; herdr keeps sessions alive through it). `termi keys` / `termi keys apply`
  now detect this exact state (`wezterm_stale`: newest wezterm-gui start time vs config
  mtime, via `ps -axo lstart=,comm=` — pgrep is BLIND in sandboxed shells where ps still
  works). After the restart, `termi keys probe` + ⌘← must show `$'\e[H'`.
- **P20 · `re.error: bad escape \x` when re-applying a managed block** — the replacement
  text contains `\x1b`, and `re.sub(replacement_string, …)` parses escapes in the
  REPLACEMENT. Always `rx.sub(lambda _m: block, text)`. Caught only by the idempotency
  test; a first apply works fine and the second crashes.
- **P17 · A feature "exists" but does nothing in the user's shell** — first question is
  always *was it ever installed?* `termi doctor` and `termi keys` both say so plainly.
  Building a pack is NOT installing it; nothing reaches the shell until
  `termi install <pack>` writes `~/.termi/zsh.d/*.zsh` and the managed block sources it.
  (Live miss 2026-07-13: F16 was built, tested, and demoed — but never installed, so ⌥←
  printed `;3D`. Ship = build + install + a real keypress.)
- **P18 · A zsh probe that greps `${functions[name]}` for a marker always fails** —
  **zsh strips comments from stored function text.** The marker must be real code
  (a function call, a variable), never `# a comment`. This silently broke both
  recover's recursion guard and its active-probe until caught by test.
- **P13 · Doctor feels slow (>2s)** — checks run in a thread pool (they're subprocess-
  bound); if a single check hangs, it gets a 5s timeout and reports `timeout` state,
  never wedges the whole doctor.

## 5 · Risk register

| Risk | Likely | Blast | Detection | Pre-approved response |
|---|---|---|---|---|
| R1 **Shared-profile code execution** — a "friend's setup" carries a malicious zshrc snippet | med | machine compromise | any non-builtin `zshrc_extra`/unknown pack in an import | Packs = data not code (ADR-4); untrusted diff + typed `yes` (P11); no curl\|sh ever (§3) |
| R2 Clobbering a user's config → trust permanently lost | med | product-fatal | any write outside markers/`~/.termi` | ADR-3 invariant + I2's checksum test in CI; undo always |
| R3 Half-configured shell (installed-not-active) reported as healthy | high | silent — worst kind | user says "it doesn't work" while doctor is green | three-state activation probes (P7); doctor greens on ACTIVE only |
| R4 Scope drown — F1–F15 at once, nothing ships | high | project rots (premortem's #1 history) | WIP >1 milestone | Roadmap is serial: v0.1 doctor+packs ships alone first |
| R5 macOS-only rot — every pack assumes brew | med | WSL story (F5!) dies | pack missing `apt` field | dual install fields required at pack-review; CI lints packs |
| R6 Sibling drift — psst/bettercd CLI change breaks orchestration | low | doctor lies | pack check fails after sibling update | ADR-7 revisit-clause; field-log it, pin version |
| R7 Secrets leak via profile share | med | credential leak | regex screen hits at export | P11 screen; refuse + notice |
| R8 Oracle staleness — this file diverges from code | certain, eventually | workers trust a wrong map | any P-entry contradicts observed behavior | divergence rule (header); re-wargame triggers: milestone ships, 3+ field-log entries, python/brew/OS shift |

## 6 · Invariants & verification recipes

- **I1** Registry stays healthy: `python3 ~/Creations/.deify/reconcile.py` → exit 0.
- **I2** Termi never alters user content outside its markers. Proof (also the CI test):
  checksum `.zshrc` minus the managed block before/after any command — identical.
  `sed '/# >>> termi >>>/,/# <<< termi <<</d' ~/.zshrc | shasum`
- **I3** Every mutating command leaves a snapshot: after it, newest dir in
  `~/.termi/snapshots/` is ≤ its start time; `termi undo` restores it.
- **I4** `termi doctor` exits 0 only when every enabled check is ACTIVE (not merely
  installed); runs <2s on this machine.
- **I5** Core imports nothing outside stdlib: `python3 -c "import ast,sys;
  [print(n.names[0].name) for n in ast.walk(ast.parse(open('bin/termi').read()))
  if isinstance(n,(ast.Import,))]"` — eyeball: stdlib only.
- **I6** `install.sh` is idempotent: second run changes nothing, exits 0.
- **Done-means per milestone:** v0.1 = fresh-macOS-sim (temp $HOME) install → doctor →
  pack install → doctor green → undo → original state byte-identical. v0.2 = export on
  machine A(sim), cherry-pick import on B(sim), both doctors green, R1 path exercised.
  v0.3 = TUI drives every CLI verb. v0.4 = install.ps1 flow walked on paper + WSL detect
  tested. v1.0 = profile round-trips through a private git repo.

## 7 · Escalation contract

STOP and say "I'm struggling" — including symptom, what you tried, which oracle entries
you consulted — when ANY of: (a) an invariant I1–I6 fails and the fix isn't a P-entry;
(b) you're about to write outside `~/.termi/` + managed block + repo dir; (c) a step
needs credentials/sudo/network you don't have; (d) the same error survives 2 distinct
fix attempts; (e) anything must leave the machine (push/publish/post — hard rule 2:
prepare, then ask fire17); (f) you meet a fork this oracle doesn't cover — log it in §8
first. Escalating early is cheap; wrong guesses compound. Never grind silently.

## 8 · Field log (append-only — symptom → what worked)

- 2026-07-06 · (wartable) `rg` exists only inside Codex.app on this machine — PATH
  visibility of a tool ≠ usable install; activation probes must use the user's real
  interactive shell (`zsh -ic`), not this process's PATH.
- 2026-07-06 · (wartable) fire17's real `.zshrc` is zinit-managed with fzf-tab +
  autosuggestions + syntax-highlighting; zoxide lines commented out in favor of
  bettercd. Export must capture plugin-manager plugins (zinit/omz/antidote), not just
  brew formulas — a profile that misses zinit lines misses half the setup.
- 2026-07-06 · (v0.1 build) all activation probes matched predictions on first live run
  (p10k, psst `_psst_preexec`, bettercd fn, zinit-provided plugins). Doctor found a real
  ◐ on its first outing: mise installed but never activated. 12/12 tests green; doctor
  1.09s (I4 budget holds). Fixture lesson: an item whose `active` probe doesn't depend
  on its snippet can't test install mechanics — probe must ride the real chain.
- 2026-07-06 · (v0.1 build) `install.ps1` written per P12 but NOT live-verified — no
  Windows box here. First Windows user is the verification; treat it as untested.
- 2026-07-06 · (F2 build) difflib misses transpositions (`gti`→`git` ratio 0.67 < any
  sane cutoff) — OSA/Damerau distance is required for typo matching. And rank same-length
  matches above deletions: live bug — a real command named `ti` beat `git` for `gti`
  until the tie-break became (distance, |len-diff|). Suggest-quality bugs only show up
  against a REAL crowded PATH — always live-test suggestions, not just unit-test them.
- 2026-07-06 · (F2 build) a pack item whose `check` keys off the termi binary itself
  reads ◐ forever for users who never opted in — self-referential items must key
  `check` off their own installed snippet file instead.
- 2026-07-13 · (F16 build) `select-word-style bash` does NOT empty `$WORDCHARS` — it
  sets `zstyle ':zle:*' word-chars ''` and rebinds the word widgets to their `-match`
  variants (`backward-word (backward-word-match)`). Assert on THAT, not on WORDCHARS;
  a test that checked WORDCHARS failed against correct code.
- 2026-07-13 · (F16 build) zsh-autosuggestions binds widgets at first precmd, so it
  WRAPS whatever `self-insert` exists then. Verified live against fire17's real zshrc:
  `autosuggest-orig-1-self-insert (_termi_self_insert)` — ghost-text and
  typing-replaces-selection coexist. If a future zsh plugin binds EARLIER than precmd,
  re-check this; it is the one fragile coupling in the keys pack.
- 2026-07-13 · (F16 build) fire17's terminal is **wezterm** (detected live). wezterm has
  no click-to-move-cursor action — don't promise it. Terminal.app/iTerm2 do it natively;
  kitty/ghostty via shell integration.
- 2026-07-13 · **THE INSTALLER BUG** — `cmd_install` rejected any item with a snippet but
  no `brew`/`apt` as "unavailable on this OS". That silently killed BOTH shell-native
  packs (keys, recover): they could never be installed, on any machine. Not caught by 22
  passing tests because every test installed a fixture item that had… the same shape as
  the broken path. Lesson: a test suite that never installs the REAL packs proves nothing
  about them. `test_real_packs_shell_native_items_are_installable` now guards it.
- 2026-07-13 · **Screen-scraping a shell lies.** Verifying a keybinding by reading the
  pty output fails: zsh's redraw emits backspaces, so `hello Xworld` never appears
  contiguously even when the edit is correct. Ask ZLE for `$BUFFER`/`$CURSOR` via a
  widget bound to a spare key — that is ground truth. `tests/test_keys_pty.py` does this
  and is the model for verifying ANY future shell-side feature.
- 2026-07-13 · (⌘-keys) wezterm had NO config file at all on fire17's machine, so ⌘←/⌘→
  emitted nothing. Created one (termi block only, everything else default) and verified
  with wezterm's OWN parser — `show-keys` lists all five bindings and calls ⌘ **SUPER**.
  Emulator config is now writable by termi (ADR-10). Always verify with the emulator's own
  tooling rather than trusting the file you just wrote.
- 2026-07-13 · (phase 2) naive plural bit for real: `load_support` built `f"{kind}s.toml"`
  → `harnesss.toml` (harness+s) — every harness silently vanished. English plurals are a
  lookup table, never string concat. Same class as "half-succeeds and lies": env printed
  fine, just with an empty harness section.
- 2026-07-13 · (phase 2) fish 4.8 + PowerShell 7.6 brew-installed to make cross-shell
  claims PROVABLE on this machine. pwsh `-Command` DOES load the profile (that's why
  `-NoProfile` exists) — which makes `pwsh -Command` a valid activation probe.
  `TERMIA:<shell>` marker round-trip through real interactive shells = the uniform
  activation proof; blank `TERMI_ACTIVE` in the probe env or the parent shell's value
  leaks in and false-positives.
- 2026-07-13 · (phase 2) the bundled termi skill, installed via `termi skill install`,
  went LIVE in the building Claude Code session itself mid-build — harness skill dirs are
  hot-loaded. Real proof the harness-detection + install path works end-to-end.
- 2026-07-13 · (⌘-keys ENABLED, zero-restart) the stale running WezTerm was fixed WITHOUT
  restart: stock WezTerm binds **⌃⇧R → ReloadConfiguration**, and ReloadConfiguration
  re-runs config discovery — it picks up a file that did NOT exist at launch. Automated
  end-to-end: osascript synthesized ⌃⇧R (app-level binding — consumed by wezterm, never
  reaches the pane/composer), then PROOF by spawning a capture pane (`wezterm cli spawn --
  sh -c 'cat > file'`, ~1.5s focus theft), synthesizing a real ⌘← (`key code 123 using
  command down`), and reading the captured bytes: `1b 5b 48` = `\e[H`. This is the
  reference method for verifying emulator-side keys with zero user action. Caveats:
  osascript needs Accessibility (was granted here); frontmost must be wezterm (checked
  first); `wezterm_stale` CANNOT see reloads (compares process start vs config mtime), so
  after a ⌃⇧R it false-positives — its message says so and points to `keys probe`.
- 2026-07-13 · (ponytail pass) measured optimizations landed: `item_states` runs the
  `zsh -ic` probe CONCURRENTLY with thread-pooled per-item checks (doctor 0.43s → 0.32s);
  `cmd_install` probes only the requested items (single-pack install ~1s → 0.30s);
  `prepare_zshd()` is now the ONE gate for block+dir+loader (was triplicated);
  `BLOCK_RE = block_re("#")` (was two hand-kept regexes). Rejected as churn: TUI dict
  dispatch, doctor-state caching (staleness > win), matcher micro-opt (already fork-free).
  cmd_doctor/cmd_export still probe everything — correct, they report everything.
- 2026-07-13 · (highest-bar sweep) four defects caught in the last-chance review:
  (1) pack upgrades never propagated ("already active" skipped snippet rewrite forever —
  now refreshes when the installed file differs, P23); (2) wezterm block injection used
  the FIRST `return <var>` — an early return inside a helper function would have
  corrupted the lua (now LAST match, test-guarded); (3) duplicate `\e[3~` bind in keys
  pack (plain delete-char shadowed by _termi_delete — trimmed, propagated live via the
  new refresh path); (4) `termi keys` didn't report jumpto state. VISION.md got its
  integrity footer (sha256 verified byte-exact after append).
- 2026-07-13 · (jumpto) POSTDISPLAY is SHARED with zsh-autosuggestions' ghost text —
  jumpto overwrites it during the mode and clears it on exit; the ghost text reappears
  on the next keystroke. Cosmetic overlap only, NOT live-verified with autosuggestions
  mid-mode — if a user reports ghost-text weirdness in jumpto, this is where to look.
- 2026-07-13 · `TERMI_DIR`/`TERMI_ZSHRC`/`TERMI_PACKS_DIR` env overrides are for TESTS —
  real packs' `check` fields hardcode `$HOME/.termi`, so a user pointing TERMI_DIR
  elsewhere would break check/state coherence. Don't document them as user knobs.
- 2026-07-13 · fire17's zshrc already defines a `command_not_found_handler` (an
  experimental one that echoes "AAAAA" and contains invalid syntax
  `${history | tail -n 1}`). Termi now chains onto it. It is HIS file, outside the
  managed block — Termi must never edit it (ADR-3); mention it, let him decide.

---

## Final chaser — from the planner, before handing over the keys

I planned this with the whole board in view, so here is what the sections couldn't hold.

The feature list glitters — AI in the terminal, SSO sync, community — but Termi lives or
dies on something boring: **whether people trust it to touch their `.zshrc`.** That trust
is ADR-3, and it is the one place I'd tell you to be paranoid beyond reason. If you ever
feel a shortcut coming on — "I'll just append this one line outside the markers" — that's
the moment the product dies. Run the I2 checksum like a ritual.

The danger I couldn't fully pin down sleeps in **F7 sharing**. The moment setups travel
between people, Termi becomes a code-distribution channel wearing a friendly face. I wrote
R1 and P11, and packs-as-data kills most of it, but social pressure ("my friend sent me
this, just apply it") will erode any consent dialog that's merely annoying. If you get to
v0.2, spend your best hours making the untrusted-diff moment *genuinely informative*, not
a click-through.

What surprised me while grounding: how much already exists. psst is not a feature to
build — it's a dependency with a rich CLI. bettercd too. The v0.1 doctor is mostly
*orchestration and honesty* (the three-state probe is the soul of it). Resist rewriting
anything that ships; Termi's job is to be the friend who introduces you to the band, not
to replay their instruments.

If things get weird mid-build, the first thing I'd reach for is the temp-$HOME simulation
(done-means, §6) — nearly every bug this product can have is visible in a fake home
directory, and it costs nothing. And keep the voice warm. "Scolds the user" in the vision
means the way a friend scolds — Termi is charming or it is nothing.

— Fable 5, 2026-07-06, at the founding wartable. The map is honest as of today; trust it,
but when the ground disagrees, believe the ground and write it down.
