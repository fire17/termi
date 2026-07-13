# IA — information architecture (highest-bar Phase 3, 2026-07-13)

Ladder-aware: every surface answers at its altitude and lets you act from there.

| Entity | Big picture | Mid | Granular | Act from here |
|---|---|---|---|---|
| Environment | `termi env` matrix (one screen: OS·terminal·mux·shells·harnesses·coverage) | `termi env --deep` (live activation per shell) | `termi env --json` (every field) | `termi shells enable <id>` · agent one-liner |
| Health | `termi doctor` exit code | per-pack sections | per-item 3-state + why | `termi install <pack/item>` |
| Features | TUI control center (see everything) | pack rows | item state + snippet file | ↵ toggles install/disable |
| Keys | `termi keys` summary | emulator tips per terminal | `termi keys probe` raw bytes | `termi keys apply` |
| Profile | `termi export` (whole setup as one artifact) | tool/plugin lists | zshrc_extra diff | `termi import` cherry-pick |
| History | snapshot list (`~/.termi/snapshots/`) | manifest.json per snapshot | file-level diffs | `termi undo` |

Data sources: support/*.toml registries (extensible, additive) · live probes (never cached
truth) · packs/*.toml. KPIs per view: coverage counts (n verified / n total), doctor
active-count, budget timings. The agent one-liner is the bridge rung: it hands the whole
ladder to any AI harness via the bundled skill.
