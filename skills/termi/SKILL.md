---
name: termi
description: Termi — your Terminal Friend. Use when the user wants to set up, diagnose, fix, or level-up their terminal/shell environment on ANY platform — "set up my terminal", "why doesn't my shell do X", "install shell niceties", "fix my keys/prompt", "migrate my setup", "make this machine feel like home", terminal doctor/env checks, typo auto-recovery, editor-style keybindings, or sharing/importing a terminal profile. Wraps the deterministic `termi` CLI — the agent relays consent, never bypasses it.
argument-hint: "[doctor|env|install <pack>|keys|profile ...]"
---

# termi — your Terminal Friend 💛 (agent hands)

Termi is a deterministic CLI that owns the whole terminal experience: diagnosis,
setup, keybindings, typo recovery, profiles, multi-shell support (zsh · bash · fish ·
PowerShell · more via registry). This skill is the agent-side hands; **the CLI is the
only mutation path** and every mutation is snapshot-guarded + `termi undo`-able.

## First move, always

```bash
termi env --json        # full detection: OS, shells, terminal, mux, harnesses, coverage
```

Read the result, then act on what's actually there. Never assume the platform.

## The verbs

| Intent | Command |
|---|---|
| Health check (exit 0 = all green) | `termi doctor` |
| What can be set up | `termi packs` |
| Install a pack/item (asks per item) | `termi install <pack>[/<item>] [--shell bash]` |
| Enable termi for another shell | `termi shells enable <id>` |
| Editor-style keys + terminal config | `termi keys` · `termi keys apply` · `termi keys probe` |
| Export/import a setup profile | `termi export -o me.toml` · `termi import friend.toml` |
| Roll back the last change | `termi undo` |
| Install this skill into more harnesses | `termi skill install` |

## Agent rules (non-negotiable)

1. **Consent is the user's, not yours.** `--yes` only when the user explicitly said
   "yes to everything". Otherwise run interactive commands and relay each question.
2. **Never edit rc files by hand** — termi's managed block + snapshots are the only
   safe mutation path. If termi can't do something, say so; don't improvise around it.
3. **Trust `termi env` over your assumptions** — coverage statuses (verified/core/
   planned) are honest; don't promise a `planned` feature works.
4. **After any install: tell the user to restart their shell** (`exec zsh` etc.), then
   verify with `termi doctor` / `termi env --deep` — never claim success unverified.
5. Something broken? `termi undo` first, then diagnose from the snapshot in
   `~/.termi/snapshots/`.

Repo docs: `README.md` (map) · `ORACLE.md` (playbooks — read before changing termi itself).
