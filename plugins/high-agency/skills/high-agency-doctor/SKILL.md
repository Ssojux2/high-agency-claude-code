---
name: high-agency-doctor
description: Use when diagnosing High Agency installation, routing, hooks, Fable/Opus/Sonnet/Haiku profiles, effort configuration, or unexpected delegation behavior in Claude Code. Performs read-only checks and never modifies project files.
---

# High Agency Doctor — Claude Code

Diagnose configuration without spawning an agent team or modifying project files.

Do not run model probes unless the user explicitly asks for them.

## Checks

Run these cheap read-only checks:

1. `claude --version`
2. `python3 --version`
3. `git --version`
4. Inspect only these environment variables:
   - `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`
   - `CLAUDE_CODE_SUBAGENT_MODEL`
   - `CLAUDE_CODE_EFFORT_LEVEL`
   - `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
5. Inspect user/project Claude settings only for safe routing-related fields such as:
   - `effortLevel`
   - `teammateMode`
   - the four environment keys above when stored under `env`

Use JSON parsing. Do **not** print full settings or unrelated environment variables.

## Interpret

Flag these conditions:

- **WARN** `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is set: it can force one model onto every subagent and override High Agency's per-role model routing.
- **INFO** `CLAUDE_CODE_SUBAGENT_MODEL` is set without FORCE: report it as a global/default influence, but do not assume it overrides every explicit role.
- **WARN** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`: High Agency is designed around ordinary bounded subagents, not experimental agent teams. Keep High Agency routing on normal subagents unless the user deliberately chooses teams.
- **INFO** session effort/model may override or differ from settings; `/model`, `/effort`, and `/status` are the interactive sources of truth.
- **UNVERIFIED** model availability: a `model: fable|opus|sonnet|haiku` profile does not prove the account will serve that exact model.

The Fable advisor/deep-critic are intentionally tool-free one-shot roles. Treat that as healthy, not a missing-tool error.

## Routing contract

Expected fallback chains:

- scout/verifier: **Haiku → Sonnet low/medium → current main model**
- builder: **Sonnet medium → current main model**
- normal complex planner/root cause: **Opus high → Fable medium → current main model**
- long-horizon advisor: **Fable medium → Opus high → current main model**
- deep critic: **Fable xhigh → Opus xhigh/high → current main model**

If `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is active, report that the configured chain is logically present but runtime routing is overridden.

## Optional model probe

Only if the user explicitly asks to probe models:

- use one-turn bounded probes;
- prefer tool-free roles for Fable;
- probe only roles relevant to the user's task;
- report dispatch success/failure and any effective model metadata the runtime actually exposes;
- do not claim model identity is verified when the runtime gives no proof;
- do not use experimental agent teams for the probe.

## Output

Return a compact table:

| Check | Status | Detail |
|---|---|---|

Then list only actionable warnings and the effective fallback chain.