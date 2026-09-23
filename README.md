# High Agency for Claude Code

High Agency is a lightweight coding scaffold designed to use the LLM's own capability first, then spend extra process, stronger models, or deeper effort only where they materially improve correctness.

Current version: **0.9.0**

## Install

In Claude Code:

```text
/plugin marketplace add Ssojux2/high-agency-claude-code
/plugin install high-agency@high-agency
```

Start a new session after installation so bundled agents and hooks are loaded.

> **v0.8.2 manifest compatibility:** `agents/` and `commands/` use Claude Code's standard automatic discovery. They are intentionally not declared in `.claude-plugin/plugin.json`, because current Claude Code builds can reject those manifest fields even though older plugin-development references document them.

> **v0.8.3 hook reliability:** fixes repeated `PostToolUse:Bash hook error` messages caused by a missing Python `tempfile` import in the verification-state hook. The tracking hook now also fails open by default so an unexpected diagnostic/state error does not interrupt Claude Code. Set `HIGH_AGENCY_HOOK_DEBUG=1` only when debugging a hook failure.

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

## Impact calibration

Before the first code/config mutation, High Agency now asks the model to commit to one compact scope estimate:

```text
Impact: local | files<=2 | modules<=1 | boundary=private
```

The first estimate is immutable. The model should not rewrite it later to match what happened.

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

That is why the current roadmap is evaluation-first. Structural overhead is already lower than the measured Superpowers paths, but no claim is made that High Agency has a higher task-success rate until equal-model/equal-budget end-to-end benchmarks are run.

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

**v0.9.0 is the current evaluation baseline.**

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
