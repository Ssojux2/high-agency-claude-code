---
description: Diagnose High Agency routing, hooks, model/effort overrides, and environment without modifying project files
argument-hint: [--probe-models]
allowed-tools: Bash, Read, Grep, Glob
model: haiku
effort: low
---

Run the installed `high-agency-doctor` skill.

Stay read-only. Do not modify project files or settings.

If `$ARGUMENTS` includes `--probe-models`, perform only the optional bounded model probes described by the doctor skill. Otherwise perform static diagnostics only.

Return the doctor's compact status table, actionable warnings, and effective fallback behavior.