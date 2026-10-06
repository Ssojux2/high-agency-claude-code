---
name: high-agency-doctor
description: Diagnose High Agency installation, hook activation, native subagent routing, model/effort overrides, and missing runtime evidence in Claude Code without changing project files or settings.
---

# High Agency Doctor — Claude Code

Use this procedure for both the skill and `/high-agency:doctor`. Do not run model probes unless the user explicitly asks for them.

## Prerequisites and safe settings

1. Run `claude --version`, `python --version`, and `git --version`. The native hook launcher requires **Python 3.10+ available as `python`** on Windows, Linux, and macOS. An activated virtual environment can supply it. Report a missing/wrong interpreter; do not install Python, add aliases, or rewrite global configuration automatically.
2. Inspect only these environment variables and the same keys under settings `env`:
   - `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`
   - `CLAUDE_CODE_SUBAGENT_MODEL`
   - `CLAUDE_CODE_EFFORT_LEVEL`
   - `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
   - `ANTHROPIC_DEFAULT_HAIKU_MODEL`
   - `ANTHROPIC_DEFAULT_SONNET_MODEL`
   - `ANTHROPIC_DEFAULT_OPUS_MODEL`
   - `ANTHROPIC_DEFAULT_FABLE_MODEL`
3. Inspect only `model`, `availableModels`, `effortLevel`, and `teammateMode` in relevant user/project settings. Use JSON parsing. Do **not** print full settings or unrelated environment values.
4. Check plugin discovery and hook errors using the installed client's supported diagnostics. A configuration file alone does not prove that hooks executed. Treat missing recorded events as **UNVERIFIED**.

## Inventory and input capabilities

Read `../high-agency-coding/references/model-routing.md`. Use only an existing, authorized host/SDK inventory capability. Do not invent a CLI model-list command, install an SDK, start a nested Claude session, or run inference to discover models.

Inspect the exposed `Agent` input schema before selecting an override. Current alias-only schemas accept `haiku`, `sonnet`, `opus`, and `fable`; do not put a versioned ID into an enum that rejects it. Use an exact catalog ID only when the live input schema permits it. Preserve the selected role's tools and task boundaries.

Separate catalog query success, freshness, account entitlement, and actual dispatch. A catalog, `availableModels` allowlist, versionless alias, or public release note does not prove all four. Same-family inheritance and provider mappings can lag a release. Without a current inventory, report latest availability **UNVERIFIED** and retain the supported native alias/fallback. Do not remove an intentional pin.

## Recorded routing evidence

Read the current session's observer report:

```sh
python "${CLAUDE_PLUGIN_ROOT}/hooks/routing_observer.py" --report --session-id "${CLAUDE_SESSION_ID}"
```

`${CLAUDE_SESSION_ID}` is a supported skill string substitution, not an assumed shell environment variable. If the client leaves it unresolved, run `--report` without a session ID and report current-session observations as UNVERIFIED. Never pick another recent session automatically.

Interpret fields separately:

| Evidence | Meaning |
|---|---|
| `requested` and its source | Explicit invocation model or desired bundled role default; effort is requested policy |
| `resolvedModel` | Native host resolution metadata, when exposed |
| `modelsUsed` | Native host-reported model history; do not derive it from answer text or the parent hook `model` |
| `dispatch_status` | Completed, launched, failed, or only an observed response; an async launch does not prove eventual completion |
| `fallback_status` | Observed model difference/swap or unknown; a difference does not prove why it happened |
| `effort_status` | UNVERIFIED unless a future supported adapter exposes actual served effort |
| `capabilities` | Documented adapter support, not proof of the installed client's behavior |

The observer stores bounded model/identity metadata only. It does not query models, dispatch agents, read credentials, or copy prompts and answers. Missing metadata remains UNVERIFIED.

## Interpret configuration

- Warn when `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` forces a global route. With FORCE but no subagent model, the main model is the forced source. Compare observations; do not claim per-role routing succeeded from settings alone.
- Treat `CLAUDE_CODE_SUBAGENT_MODEL` without FORCE as a default influence. Report user/admin family pins and unsupported effort without changing them.
- Report `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; High Agency uses ordinary bounded subagents. Do not enable teams as a fallback.
- Use `/model`, `/effort`, `/status`, and `/tasks` only when supported to inspect the current session. Static settings can differ from session overrides.
- Treat tool-free Fable advisor/deep-critic roles as intentional. The main model remains the integrator.

## Optional model probe

Only if the user explicitly asks to probe models, or supplies `--probe-models`, make the smallest bounded native subagent request for a route relevant to the problem. Use only supported input fields; do not probe every model. Prefer tool-free Fable roles. Report native dispatch and metadata honestly, including failures or absent identity evidence. No SDK installation, credentials discovery, nested CLI session, or global setting rewrite is part of this procedure.

## Output

Return `Check | Status | Detail` for interpreter/hook activation, inventory query/freshness, entitlement, input capabilities, requested/resolved/modelsUsed, effort, and fallback. Then list actionable warnings only. Use the fallback chains in the routing reference rather than maintaining a second copy here.
