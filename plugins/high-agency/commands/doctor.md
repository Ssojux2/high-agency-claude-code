---
description: Diagnose High Agency routing, hooks, model/effort overrides, and environment without modifying project files
argument-hint: [--probe-models]
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Agent
model: haiku
effort: low
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/high-agency-doctor/SKILL.md` and follow that single diagnostic procedure with `$ARGUMENTS`.

Do not modify project files or settings. Run optional model probes only when the user explicitly supplied `--probe-models`; otherwise remain read-only and use existing observations.
