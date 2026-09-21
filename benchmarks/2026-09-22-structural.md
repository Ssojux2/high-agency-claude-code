# Structural Benchmark — 2026-09-22

This benchmark measures model-facing workflow instruction footprint, not end-to-end coding quality.

## v0.8 progressive disclosure

High Agency keeps normal Claude Code work single-agent and loads routing/diagnostics only when needed.

| Claude Code path | Model-facing workflow words |
|---|---:|
| High Agency core | **647** |
| Core + bounded autonomy | **876** |
| Core + adaptive routing reference | **1,725** |
| Bounded + adaptive routing reference | **1,954** |
| Doctor skill, natural invocation | **432** |
| /high-agency:doctor command | **232** |
| Optional role-agent prompt | **~78–110 each, only when spawned** |
| Superpowers measured bug-fix path | 3,987 |
| Superpowers measured feature path | 5,160 |
| Ralph command scaffold | 129 |

Compared with the measured Superpowers paths:

- core remains about **83.8% / 87.5% smaller**;
- core + routing is about **56.7% / 66.6% smaller**;
- bounded + routing is about **51.0% / 62.1% smaller**.

The doctor is fully optional. The slash doctor is self-contained and runs on Haiku/low; it does not need to load the full routing skill just to inspect environment overrides.

## v0.8 routing shape

| Role | Default model / effort |
|---|---|
| scout | Haiku / low |
| verifier | Haiku / low |
| builder | Sonnet / medium |
| planner | Opus / high |
| advisor | Fable / medium |
| deep critic | Fable / xhigh |

Fable roles are tool-free one-shot reasoning roles. Ordinary work pays none of this role prompt cost unless a role is spawned.

## Control-flow intent

- default at most 2 concurrent delegated agents;
- no recursive agent tree from bundled Claude roles;
- compact handoff packets instead of full-task duplication;
- explicit fallbacks when a preferred model is unavailable;
- CLAUDE_CODE_SUBAGENT_MODEL_FORCE and experimental agent-team settings are surfaced by doctor;
- targeted verification and Git-baseline invalidation remain unchanged.

## Method

Whitespace-separated words from model-facing files. Hook code, tests, and eval files are excluded.

Superpowers/Ralph comparison definitions match the Codex benchmark.

These are process-footprint numbers, not task-success or cost claims.

## End-to-end status

No task-success or cost advantage is claimed until equal-model/equal-budget runs are performed. Use evals/ for reproducible comparisons.
