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
   - `ANTHROPIC_DEFAULT_HAIKU_MODEL`
   - `ANTHROPIC_DEFAULT_SONNET_MODEL`
   - `ANTHROPIC_DEFAULT_OPUS_MODEL`
   - `ANTHROPIC_DEFAULT_FABLE_MODEL`
5. Inspect user/project Claude settings only for safe routing-related fields such as:
   - `model`
   - `availableModels`
   - `effortLevel`
   - `teammateMode`
   - the environment keys above when stored under `env`

Use JSON parsing. Do **not** print full settings or unrelated environment variables.

## Current model catalog

Read `../high-agency-coding/references/model-routing.md`. Inspect any current account/provider model inventory exposed by the host. Do not invent a CLI model-list command, install an SDK, start a nested Claude session, or run inference solely to discover models.

Compare the selected family against the latest available stable version in that inventory. Versionless aliases are healthy compatibility defaults, but not proof of freshness: the alias can inherit an older same-family main model, and provider/gateway defaults can lag newer releases. Prefer the exact available model ID via the role's supported per-invocation `model` parameter. Preserve the role's tool restrictions.

Flag explicit family environment pins, older same-family session models, provider differences, outdated clients, unsupported effort, and forced routing. Do not silently remove pins or rewrite user settings. Public documentation identifies new releases but does not prove account-specific access. `availableModels` is an allowlist, not a live availability API. If no current inventory is exposed, report latest availability **UNVERIFIED** and retain the supported native alias/fallback.

## Interpret

Flag these conditions:

- **WARN** `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is enabled: it can force one model onto every subagent and override both per-invocation and frontmatter model routing. If FORCE is enabled without a subagent model, the main model is the forced source.
- **INFO** `CLAUDE_CODE_SUBAGENT_MODEL` is set without FORCE: report it as a global/default influence, but do not assume it overrides every explicit role.
- **WARN** `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, or `ANTHROPIC_DEFAULT_FABLE_MODEL` pins an older release: report the latest-version conflict without changing the pin.
- **WARN** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`: High Agency is designed around ordinary bounded subagents, not experimental agent teams. Keep High Agency routing on normal subagents unless the user deliberately chooses teams.
- **INFO** session effort/model may override or differ from settings; `/model`, `/effort`, and `/status` are the interactive sources of truth. `/tasks` can expose the actual model of a running subagent on supported clients.
- **UNVERIFIED** model availability: a `model: fable|opus|sonnet|haiku` profile does not prove the account will serve the latest release or that a subagent has actually run.

The Fable advisor/deep-critic are intentionally tool-free one-shot roles. Treat that as healthy, not a missing-tool error.

## Routing contract

Expected fallback chains, with current available versions and supported efforts:

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
