# High Agency for Claude Code

High Agency is a lightweight coding scaffold designed to use the LLM's own capability first, then spend extra process, stronger models, or deeper effort only where they materially improve correctness.

Current version: **0.13.0**

## Prerequisites

**Claude Code 2.1.163+ is required for the hook output protocol.** CI uses 2.1.290 as the tested integration baseline. Native hook `args` first appeared in 2.1.139; older clients can discard the script arguments and run bare Python. Stop feedback without an error notification requires 2.1.163.

**Python 3.10+ must be available as `python` on the PATH inherited by Claude Code on native Windows, Linux, and macOS.** Hooks use native `command: "python"` with an `args` array on every platform. An installation exposed only as `python3`, or a shell-only alias, does not satisfy that launcher.

An activated virtual environment is acceptable if Claude Code inherits its PATH. The plugin does not install Python, create global aliases, or edit global PATH/configuration. CI runs native Windows, Linux, and macOS regression suites, configuration checks, and real Claude hook execution against a deterministic local model fixture. The fixture verifies event delivery and bounded continuation without paid model calls; authenticated task execution remains a separate acceptance check.

## Install

In Claude Code:

```text
/plugin marketplace add Ssojux2/high-agency-claude-code
/plugin install high-agency@high-agency
```

Start a new session after installation so bundled agents and hooks are loaded.

**0.12.1 hook fixes:** normal Stop continuation now uses Claude's `additionalContext` feedback instead of producing a “Stop hook blocking error.” Impact parsing stays within individual lines, fixing a reproducible hook timeout on whitespace-heavy responses. `/high-agency:doctor` now includes an isolated launcher diagnostic. See [hook troubleshooting](docs/runtime-validation.md#hook-troubleshooting).

> **v0.12.0 routing audit:** catalog query success, freshness, account entitlement, and native dispatch are now separate evidence checks. Read-only routing observations report only the metadata the host exposes. Validation combines regression fixtures with real Claude Code component loading and hook registration on Windows, Linux, and macOS CI. Authenticated end-to-end routing still needs user-run evaluation.

## Core behavior

`high-agency-coding` defaults to **single-agent execution with the current model**.

It does not require planning documents, TDD, worktrees, subagents, full suites, or review stages for every task.

## Coding principles in 0.13.0

The main coding skill now applies four concrete disciplines:

| Principle | Behavior |
|---|---|
| Think before coding | Inspect contracts, state material assumptions, and resolve consequential ambiguity; proceed on reasonable reversible defaults. |
| Simplicity first | Build the smallest complete solution and avoid speculative features, dependencies, configuration, or abstractions. |
| Surgical changes | Keep edits tied to the requested outcome, preserve surrounding style, and clean up only code made unused by this change. |
| Goal-driven execution | Choose observable acceptance criteria and checks that can expose a wrong result; finish with sufficient fresh evidence. |

For bugs, a regression check should distinguish the exact failure. For refactors, compare relevant behavior before and after when feasible. Trivial prose edits can use direct inspection. These are skill and role instructions; they do not add hooks, mandatory TDD, blanket approval questions, or unbounded retries. Runtime routing and the five-line preflight format are unchanged.

The integration adapts the [Karpathy-inspired community guidelines](https://github.com/multica-ai/andrej-karpathy-skills/tree/2c606141936f1eeef17fa3043a72095b4765b9c2) in original wording. See [examples and pinned attribution](plugins/high-agency/skills/high-agency-coding/references/coding-principles.md) and [evaluation scenarios](evals/scenarios.md). This release does not establish comparative quality, token, or cost improvements.

## Adaptive Claude routing

When delegation has real leverage, the plugin can use bundled role agents. Inspect the selected family in the active host's current catalog for the same account and provider. Request an exact model ID only when the currently exposed native `model` input schema explicitly permits it. When that schema accepts only Haiku/Sonnet/Opus/Fable family aliases, use a supported alias; a catalog ID cannot expand the tool's accepted inputs. Bundled aliases are compatibility defaults and do not guarantee freshness. Alias routing leaves latest-version freshness and served identity **UNVERIFIED** unless independent host evidence establishes them.

| Role | Model family / desired effort | Purpose |
|---|---|---|
| `high-agency-scout` | Haiku / low | broad read-only mapping |
| `high-agency-builder` | Sonnet / medium | isolated implementation |
| `high-agency-verifier` | Haiku / low | targeted command/test reporting |
| `high-agency-planner` | Opus / high | high-leverage architecture/root-cause reasoning |
| `high-agency-advisor` | Fable / medium | ambitious codebase-wide strategy and long-horizon coordination |
| `high-agency-deep-critic` | Fable / xhigh | rare security/high-impact/long-horizon hard reasoning escalation |

The main conversation remains the integrator. Small tasks use **zero** subagents. Effort levels are desired policy and must be supported by the chosen model and client; otherwise record a supported substitute or main-model fallback. Fable roles are deliberately tool-free: the main thread/Haiku gathers a compact evidence packet, then Fable reasons over that packet as a one-shot advisor or critic.

Before the first code/config mutation, High Agency now emits one unified preflight from the same read-only inspection:

```text
Preflight: <short task-shape summary>
Complexity: low | medium | high | frontier
Route: DIRECT | CHEAP DELEGATE | BUILDER | STRONG REASONING | FRONTIER ESCALATION
Model: <current main model or exact bundled role with model/effort>
Impact: local | files<=N | modules<=N | boundary=private|shared-api|high-impact
```

The summary, complexity, route, model, and impact estimate are one decision. For a non-DIRECT route, the skill loads `skills/high-agency-coding/references/model-routing.md` and requests the selected native role before delegated work begins, using supported model/effort controls. If the runtime cannot serve the route, record the fallback and continue.

Fable is reserved for ambitious long-horizon strategy or the hardest cognitive bottlenecks; routine execution stays on the main model/Sonnet/Haiku. A routing choice counts as executed only when the matching bundled role is actually dispatched; merely saying that Opus/Fable would be useful does not count.

## What can and cannot self-adjust

High Agency can select among bundled subagent model/effort profiles when Claude Code supports them. This is optional skill guidance for bounded native subtasks; hooks and the observer do not force dispatch or launch agents.

It does **not** silently replace the primary conversation model. Session-level model/effort remains controlled by Claude Code/user settings. The skill adapts by deciding whether to keep work in the main thread or route a bounded subtask to a role with a different model/effort.

If a requested model is unavailable or restricted, High Agency uses explicit fallbacks with current catalog models and supported efforts: **Haiku → Sonnet → current main model** for scout/verifier, **Sonnet → current main model** for builder, **Opus → Fable → current main model** for normal complex planning, and **Fable → Opus → current main model** for long-horizon advice or deep critique. After a rejection, refresh at most once and attempt one supported fallback before continuing on the main model. Preserve explicit user/admin pins and report conflicts instead of rewriting settings.

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
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`
- `ANTHROPIC_DEFAULT_SONNET_MODEL`
- `ANTHROPIC_DEFAULT_OPUS_MODEL`
- `ANTHROPIC_DEFAULT_FABLE_MODEL`

Key warnings:

- `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` can override every per-role model pin.
- experimental agent teams are not required by High Agency; ordinary bounded subagents are the supported routing path.
- catalog query success, freshness, account entitlement/availability, and native dispatch success are separate checks. A role alias, settings allowlist, or successful catalog parse does not prove all four.
- aliases and family environment pins can resolve to older releases. Missing freshness or availability evidence remains **UNVERIFIED**.
- use `/model`, `/effort`, and `/status` for the live session view.

Doctor uses model inventory already exposed by the active host. It does not run paid probes automatically, install an SDK, invent a CLI model-list command, or start nested Claude sessions. A bounded native model probe requires an explicit user request.

## Read-only routing observations

From the plugin root (`plugins/high-agency/` in a checkout), select the current host session explicitly. The same command applies on native Windows, Linux, and macOS; replace the placeholder with the session ID supplied by the host.

```text
python hooks/routing_observer.py --report --session-id "<current-session-id>"
```

`--report` alone shows capabilities with observations **UNVERIFIED**; it does not read a current or latest session automatically. Add `--agent-id "<current-agent-id>"` when inspecting a child agent's scope. A missing session/state record stays **UNVERIFIED** rather than falling back to another session.

The observer can read `PostToolUse` events for `Agent|Task`, retaining a requested model from the native tool input and explicit host-exposed resolved-model or `modelsUsed` metadata when present. The report keeps observer capability and requested, resolved, and `modelsUsed` statuses separate. A dispatched role or a requested alias does not establish the served model; absent explicit metadata, that identity remains **UNVERIFIED**. The observer does not infer model identity from response text.

A forced model setting is configuration evidence, and may explain a mismatch between the requested and resolved route. It is not a substitute for host metadata about what was served. Versionless aliases remain useful compatibility defaults without guaranteeing the latest release.

Observation state is kept per session under the plugin state directory. It retains bounded routing metadata without copying prompts, tool output, or credentials. The observer reports evidence; it does not change the main model, dispatch agents, or enforce a routing choice.

## Impact calibration

The `Impact:` line is now the final line of the unified preflight. The first estimate remains immutable so existing scope-drift hooks can use it as the baseline. The model should not rewrite it later to match what happened.

At completion, the hook compares the actual Git diff against that estimate:

```text
match
→ keep targeted verification

minor drift
→ extend verification only to the newly affected surface

major drift / unexpected high-impact boundary
→ inspect the focused final diff
→ broaden verification only for the expanded risk
→ escalate model/reasoning only if the new scope creates a real cognitive bottleneck
```

The hook objectively checks file count, module spread, truncated change sets, and known high-impact paths such as auth/security/schema/dependency/build/deploy surfaces. Public/shared API drift that cannot be inferred reliably from paths remains a semantic final-diff check for the model.

If no valid estimate was produced, High Agency falls back to its fixed safety heuristics rather than silently assuming the task is local.

## Verification and hooks

Verification follows:

```text
touched → affected → broad only on risk
```

Git-baseline hooks detect native edits plus shell/generator changes, invalidate stale verification, capture the first immutable impact estimate, and compare predicted scope with the actual diff before completion.

Hooks do not automatically run project tests or launch agents.

Stop reminders use `hookSpecificOutput.additionalContext` to keep the turn going without labelling normal feedback as a hook error. Verification, Impact, diff-review and continuation budgets remain bounded. Actual interpreter or process failures still need diagnosis.

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

## High Agency vs Superpowers vs Ralph Loop

The three approaches optimize for different things:

- **Superpowers** — maximize consistency by enforcing a development process.
- **Ralph Loop** — maximize persistence by repeating until a completion condition is reached.
- **High Agency** — maximize model capability per unit of process by staying single-agent first and adding planning, stronger models, broader verification, review, or continuation only when evidence/risk justifies it.

### Summary

| Dimension | High Agency | Superpowers | Ralph Loop |
|---|---|---|---|
| Core philosophy | model judgment + conditional guardrails | process discipline | persistent iteration |
| Default process overhead | low | high | very low |
| Planning | only when uncertainty warrants it | formal brainstorming/spec/plan workflow | no built-in planning discipline |
| TDD | optional | central/mandatory in feature/bug-fix paths | not built in |
| Subagents | only when delegation has leverage | actively used by workflow | not core |
| Model/effort routing | adaptive | not the main design goal | not built in |
| Verification | touched → affected → broad on risk | strong verification/TDD discipline | depends on the prompt/agent |
| Review | focused and conditional | review stages can be part of the normal workflow | not built in |
| Iteration | progress-gated, usually 1–3 extra passes | workflow-dependent | core mechanism |
| Reuse of valid evidence | yes | not a central default rule | no verification model built in |
| False-completion defense | fresh evidence + Stop guard | strong | completion promise / loop condition |
| Token/process efficiency | explicit design goal | secondary to process consistency | highly dependent on iteration count |

### Where High Agency is stronger than Superpowers

High Agency deliberately avoids forcing the full development ceremony onto every task.

A small local fix can remain:

```text
current model
→ inspect
→ edit
→ targeted verification
→ finish
```

There is no mandatory brainstorming, plan document, worktree, TDD cycle, reviewer, or broad test suite unless the task actually benefits from it.

This gives High Agency three main advantages:

1. **Lower process overhead on routine work**  
   Strong models can act directly instead of spending tokens proving that a simple task deserves a simple solution.

2. **Adaptive compute allocation**  
   Cheap/read-heavy/mechanical work can be delegated to lower-cost models, while difficult architecture, security, or root-cause reasoning can escalate to stronger models and higher reasoning effort.

3. **Risk-based verification instead of workflow-wide verification**  
   Verification starts at the changed surface and expands only when propagation risk exists.

The trade-off is that High Agency trusts model judgment more. If the model underestimates task complexity, chooses the wrong verification scope, or fails to escalate when it should, Superpowers' stronger procedural constraints may be more robust.

### Where Superpowers is stronger

Superpowers is intentionally more prescriptive.

That can be valuable when:

- a weaker or less reliable model needs process discipline;
- the project benefits from explicit design approval before implementation;
- a team wants TDD and review to be mandatory rather than discretionary;
- reducing behavioral variance matters more than minimizing token/process overhead.

In short:

```text
Superpowers
= lower behavioral variance
  + stronger process guarantees
  - higher ceremony and context cost
```

### Where High Agency is stronger than Ralph Loop

Ralph's key strength is persistence:

```text
not complete
→ run again
→ run again
→ run again
```

High Agency keeps that useful idea but adds a progress gate.

Another pass is justified only when the previous pass produced something such as:

- a meaningful repository-state change;
- new verification evidence;
- a newly identified or disproven root cause;
- material progress on an acceptance criterion.

So the default rule is closer to:

```text
not complete
+ meaningful progress
+ actionable next step
→ continue
```

rather than simply:

```text
not complete
→ continue
```

High Agency also prefers **reasoning/model escalation before blind iteration** when the same cognitive failure survives multiple evidence-based attempts.

### Where Ralph Loop is stronger

Ralph is much simpler and can be very effective when persistence itself is the main requirement.

It can be a good fit for:

- long-running migrations;
- large repetitive refactors;
- many failing tests that can be fixed incrementally;
- tasks with a very clear completion condition and cheap iterations.

Its simplicity is also its weakness: it does not define which tests to run, when evidence is stale, whether the approach is repeating itself, or when a stronger model would be more effective than another iteration.

### High Agency's design position

High Agency is not intended to be a compromise halfway between Superpowers and Ralph.

It selectively borrows the useful parts of both:

From Superpowers:
- verification discipline;
- root-cause discipline;
- planning when uncertainty is real.

From Ralph:
- continuation;
- persistence.

And adds:
- adaptive model and reasoning routing;
- single-agent-first execution;
- targeted → affected → broad verification;
- evidence reuse;
- Git-state invalidation;
- conditional diff review;
- bounded, progress-gated continuation.

The intended runtime shape is:

```text
                     main model
                         │
              simple task? ── yes ──→ direct implementation
                         │
                         no
                         ↓
                 adaptive escalation
            ┌────────────┼────────────┐
            │            │            │
       cheap/broad    workhorse    frontier
            │            │            │
       lower-cost       normal      strongest
         model          model       reasoning
            └────────────┼────────────┘
                         ↓
                 main integration
                         ↓
              targeted verification
                         ↓
                 risk propagation?
                  │             │
                 no            yes
                  │             ↓
                  │       affected/broad check
                  │             ↓
                  │       conditional review
                  └─────────────┘
                         ↓
                       done
```

### Current trade-off

High Agency's biggest advantage is also its biggest risk: **it relies more on the model making good meta-decisions**.

The important questions are not hard-coded into a fixed workflow:

- Is this task complex enough to plan?
- Is delegation worth its context/handoff cost?
- Is targeted verification enough?
- Should reasoning/model quality escalate?
- Is another continuation likely to produce new evidence?

That is why the current roadmap is evaluation-first. Existing structural measurements describe prescribed process footprint. They do not establish a higher end-to-end task-success rate, token or latency savings, or a benefit caused by the 0.12.0 routing changes. Those outcomes need equal-model/equal-budget end-to-end benchmarks.

### Practical fit

| Task type | Likely fit |
|---|---|
| routine coding / small bug fix | High Agency |
| strong modern model with tight token/time budget | High Agency |
| adaptive multi-model execution | High Agency |
| mandatory TDD / formal development workflow | Superpowers |
| strict design-before-code process | Superpowers |
| very long autonomous repetitive work | Ralph Loop |
| clear completion condition + cheap retries | Ralph Loop |
| long-running work where iteration cost also matters | High Agency bounded autonomy |

## Benchmarks and evals

`benchmarks/` contains structural process-footprint measurements. `evals/` contains task-quality and four-way comparison tooling.

End-to-end success claims are intentionally not published without equal-model/equal-budget runs.

## Development status

**v0.12.0 remains the runtime evaluation baseline; v0.13.0 adds the requested coding-principle guidance.**

The 0.13.0 update changes instructions and evaluation criteria without extending runtime heuristics or claiming a measured performance gain. Comparative model behavior still requires matched end-to-end runs.

The v0.12.0 audit separates catalog lookup from freshness, entitlement, and native dispatch evidence, and adds read-only routing observations. It preserves the main model, bounded role routing, and explicit supported fallbacks.

The 0.12.1 hook patch adds actual Claude event execution against a deterministic loopback model fixture to the Windows, Linux, and macOS CI checks. Account-backed dispatch, served-model identity where exposed, forced-model behavior, and efficiency still require explicit user-run evaluation. See [routing scenarios](evals/routing-scenarios.md) and [runtime validation](docs/runtime-validation.md) for the evidence to capture; these changes do not establish token, latency, or cost savings.

Further runtime features, routing rules, thresholds, or orchestration complexity should not be added based on intuition alone. The next behavioral changes should be driven by real end-to-end Codex/Claude Code runs using the existing `evals/` scenarios and comparable model/budget settings, including impact-estimate calibration.

Before changing the runtime, collect evidence such as:

- task success and false-completion rate;
- impact underestimation / overestimation rate;
- match / minor-drift / major-drift frequency;
- tokens/tool calls/wall time;
- unnecessary delegation or duplicate work;
- targeted vs affected vs full verification frequency;
- no-progress continuation passes;
- routing/fallback failures;
- hook latency or false-positive guards.

Exceptions to the freeze are limited to clear compatibility, security, or correctness bugs.

## License

MIT
