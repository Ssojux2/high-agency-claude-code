---
description: Diagnose High Agency routing, hooks, model/effort overrides, and environment without modifying project files
argument-hint: [--probe-models]
allowed-tools: Bash, Read, Grep, Glob, Task
model: haiku
effort: low
---

Run a read-only High Agency diagnostic. Do not modify project files or settings.

Check:
1. `claude --version`, `python3 --version`, and `git --version`.
2. Only these environment variables:
   - `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`
   - `CLAUDE_CODE_SUBAGENT_MODEL`
   - `CLAUDE_CODE_EFFORT_LEVEL`
   - `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
3. User/project Claude settings only for safe routing-related keys: `effortLevel`, `teammateMode`, and those four env keys when present under `env`. Do not print full settings or unrelated environment values.
4. High Agency routing expectations:
   - Haiku low scout/verifier
   - Sonnet medium builder
   - Opus high planner
   - Fable medium advisor
   - Fable xhigh deep critic
5. Warnings:
   - `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` overrides per-role model routing.
   - experimental agent teams are not required or preferred for High Agency.
   - model availability remains UNVERIFIED unless runtime evidence proves the effective served model.

Fallbacks:
- scout/verifier: Haiku → Sonnet → current main
- builder: Sonnet → current main
- planner: Opus → Fable → current main
- advisor/deep critic: Fable → Opus → current main

If `$ARGUMENTS` contains `--probe-models`, attempt only minimal one-turn bounded probes for roles relevant to the user's problem. Do not fan out across every model automatically, and do not claim an effective model identity without runtime proof.

Return a compact `Check | Status | Detail` table followed by actionable warnings only.