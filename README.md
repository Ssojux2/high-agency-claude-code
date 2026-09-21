# High Agency for Claude Code

High Agency is a lightweight coding scaffold designed to use the LLM's own capability first, then spend extra process, stronger models, or deeper effort only where they materially improve correctness.

Current version: **0.8.0**

## Install

In Claude Code:

```text
/plugin marketplace add Ssojux2/high-agency-claude-code
/plugin install high-agency@high-agency
```

Start a new session after installation so bundled agents and hooks are loaded.

## Core behavior

`high-agency-coding` defaults to **single-agent execution with the current model**.

It does not require planning documents, TDD, worktrees, subagents, full suites, or review stages for every task.

## Adaptive Claude routing

When delegation has real leverage, the plugin can use bundled role agents:

| Role | Model / effort | Purpose |
|---|---|---|
| `high-agency-scout` | Haiku / low | broad read-only mapping |
| `high-agency-builder` | Sonnet / medium | isolated implementation |
| `high-agency-verifier` | Haiku / low | targeted command/test reporting |
| `high-agency-planner` | Opus / high | high-leverage architecture/root-cause reasoning |
| `high-agency-advisor` | Fable / medium | ambitious codebase-wide strategy and long-horizon coordination |
| `high-agency-deep-critic` | Fable / xhigh | rare security/high-impact/long-horizon hard reasoning escalation |

The main conversation remains the integrator. Small tasks use **zero** subagents. Fable roles are deliberately tool-free: the main thread/Haiku gathers a compact evidence packet, then Fable reasons over that packet as a one-shot advisor or critic.

The detailed policy is in `skills/high-agency-coding/references/model-routing.md` and is read only when delegation is justified. Fable is reserved for ambitious long-horizon strategy or the hardest cognitive bottlenecks; routine execution stays on the main model/Sonnet/Haiku.

## What can and cannot self-adjust

High Agency can select among bundled subagent model/effort profiles when Claude Code supports them.

It does **not** silently replace the primary conversation model. Session-level model/effort remains controlled by Claude Code/user settings. The skill adapts by deciding whether to keep work in the main thread or route a bounded subtask to a role with a different model/effort.

If a requested model is unavailable or restricted, High Agency uses explicit fallbacks: Haiku→Sonnet→main for scout/verifier, Sonnet→main for builder, Opus→Fable→main for normal complex planning, Fable→Opus→main for long-horizon advice, and Fable→Opus→main for deep critique.

## Doctor

Run:

```text
/high-agency:doctor
```

or invoke the `high-agency-doctor` skill directly.

The doctor is read-only and defaults to static diagnostics. It checks Claude/Python/Git versions, safe routing-related settings, and these environment overrides without printing unrelated settings or secrets:

- `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`
- `CLAUDE_CODE_SUBAGENT_MODEL`
- `CLAUDE_CODE_EFFORT_LEVEL`
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`

Key warnings:

- `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` can override every per-role model pin.
- experimental agent teams are not required by High Agency; ordinary bounded subagents are the supported routing path.
- Fable/Opus/Sonnet/Haiku availability is **UNVERIFIED** unless the user explicitly requests model probes.
- use `/model`, `/effort`, and `/status` for the live session view.

Optional model probes are one-turn and opt-in; doctor never fan-outs across all models by default.

## Verification and hooks

Verification follows:

```text
touched → affected → broad only on risk
```

Git-baseline hooks detect native edits plus shell/generator changes, invalidate stale verification, and trigger focused final diff review only on meaningful risk signals.

Hooks do not automatically run project tests or launch agents.

## Bounded autonomy

`bounded-autonomy` uses the smallest useful pass budget:

- local/narrow: `max=1`;
- normal multi-step: `max=3`;
- more only when justified/requested;
- hard cap: 12.

If two good attempts fail for the same cognitive reason, High Agency escalates model/effort before adding blind iterations.

## Why this stays lightweight

Normal path:

```text
main model → edit → targeted verification → finish
```

Only higher-leverage tasks fan out:

```text
Haiku scout ─────┐
Opus planner ─────┼→ main / Sonnet builder
Fable advisor ───┘
                    ↓
             Haiku verifier
                    ↓
         risk-triggered review only
```

## Benchmarks and evals

`benchmarks/` contains structural process-footprint measurements. `evals/` contains task-quality and four-way comparison tooling.

End-to-end success claims are intentionally not published without equal-model/equal-budget runs.

## Development status

**v0.8.0 is the current feature-freeze baseline.**

Further runtime features, routing rules, thresholds, or orchestration complexity will not be added based on intuition alone. The next behavioral changes should be driven by real end-to-end Codex/Claude Code runs using the existing `evals/` scenarios and comparable model/budget settings.

Before changing the runtime, collect evidence such as:

- task success and false-completion rate;
- tokens/tool calls/wall time;
- unnecessary delegation or duplicate work;
- targeted vs affected vs full verification frequency;
- no-progress continuation passes;
- routing/fallback failures;
- hook latency or false-positive guards.

Exceptions to the freeze are limited to clear compatibility, security, or correctness bugs.

## License

MIT
