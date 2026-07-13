# SWARM — orchestration decision log (highest-bar Phase 6, 2026-07-13)

**Decision: single-writer main-agent build. Logged per the protocol's failure table —
never quietly under-strength.**

Why: the core is ONE tightly-coupled file (`bin/termi`) plus registries the core parses —
per ep-pro F2, shared-mutable-state lanes serialize; 12 agents on one file = collisions,
not speed. The genuinely parallel work (5 shells × live verification) ran as parallel
*processes* (ThreadPoolExecutor probes + per-shell test lanes), not parallel agents.

Fable never spawned subagents (rule 4 holds — no spawns at all this phase).
zenith available but not engaged: mission fit inside one focused session with the task
board + ORACLE as the durable plan. `/workflow-model-guard` unneeded (no workflows authored).

If phase 3 grows independent lanes (showcase site, Windows-native verification, nushell
port), THOSE are the fan-out candidates: Opus 4.8 @ high builders under /ponytail,
disjoint dirs, verify lanes separate from build lanes.
