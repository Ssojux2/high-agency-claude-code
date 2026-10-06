# high-agency

Version: **0.12.0**

## Prerequisites

**Python 3.10+ must be available as `python` on the PATH inherited by Claude Code on native Windows, Linux, and macOS.** Hooks use native `command: "python"` with an `args` array on every platform. An installation exposed only as `python3`, or a shell-only alias, does not satisfy that launcher.

An activated virtual environment is acceptable if Claude Code inherits its PATH. The plugin does not install Python, create global aliases, or edit global PATH/configuration. CI runs native Windows, Linux, and macOS regression suites and real Claude Code configuration checks. These verify component loading and hook registration without model inference; authenticated task execution remains a separate acceptance check.

## Contents

Lightweight Claude Code plugin containing:

- `high-agency-coding`: direct autonomous coding with fresh verification.
- `bounded-autonomy`: opt-in bounded continuation via the bundled Stop hook.
- `high-agency-doctor`: read-only configuration and routing diagnostics.
- bounded native scout, builder, verifier, planner, advisor, and deep-critic roles.
- `hooks/routing_observer.py`: read-only reporting of routing evidence.

## Routing and evidence

The current main model stays the integrator. Native subtask delegation is optional skill guidance; plugin code does not force dispatch or launch agents. Inspect the selected Haiku/Sonnet/Opus/Fable family in the active host's current catalog and use only supported effort controls. An exact model ID is valid only when the exposed native input schema accepts it; an alias-only schema requires a supported family alias. Versionless role aliases are compatibility defaults and do not guarantee freshness or served identity. Preserve explicit user/admin pins and record supported fallbacks.

Catalog query success, freshness, account entitlement/availability, native dispatch, and served-model evidence are separate checks. An alias, allowlist, or successful catalog parse does not establish all of them.

From this plugin directory, run `python hooks/routing_observer.py --report --session-id "<current-session-id>"` on native Windows, Linux, or macOS, using the current session ID supplied by the host. `--report` alone returns capabilities and **UNVERIFIED** observations; it never chooses a current/latest session automatically. Add `--agent-id "<current-agent-id>"` for child scope. A missing session/state record stays **UNVERIFIED** rather than selecting another session.

The scoped report separates observer capability and requested-model, resolved-model, and `modelsUsed` statuses. `PostToolUse` observations for `Agent|Task` can capture the requested model and explicit host model metadata when exposed. A role name, alias, forced-model setting, or response text does not prove served identity; absent explicit host metadata, it remains **UNVERIFIED**.

State is kept per session under the plugin state directory, without copying prompts, tool output, or credentials. Diagnostics do not run paid probes automatically, install SDKs, or start nested Claude sessions.

The 0.12.0 audit changes are checked with regression fixtures and real Claude Code component loading and hook registration on Windows, Linux, and macOS CI. Authenticated end-to-end evaluation is still needed; token, latency, and cost savings are not established by this patch.

See the [repository README](../../README.md), [routing scenarios](../../evals/routing-scenarios.md), and [runtime validation](../../docs/runtime-validation.md) for installation, usage, and evaluation evidence.
