# Structural Benchmark — 2026-09-22

This benchmark measures model-facing workflow instruction footprint, not end-to-end coding quality.

## v0.7 progressive disclosure

High Agency v0.7 moved routing detail out of the core skill and added small role agents that are loaded only when spawned.

| Claude Code path | Model-facing workflow words |
|---|---:|
| High Agency core | **647** |
| High Agency core + bounded autonomy | **876** |
| High Agency core + routing reference | **1,132** |
| High Agency bounded + routing reference | **1,361** |
| Optional role-agent prompt | **78–88 each, only when spawned** |
| Superpowers measured bug-fix path | 3,987 |
| Superpowers measured feature path | 5,160 |
| Ralph command scaffold | 129 |

The v0.6 ordinary core was 1,163 words. v0.7's ordinary core is about **44% smaller**. The optional routing reference and subagent body are paid only when delegation is justified.

Superpowers/Ralph figures are included as structural reference points, not quality rankings.

## Method

Whitespace-separated word counts from model-facing files. Hook code is excluded because it executes outside model context.

High Agency:
- core skill;
- optional bounded skill;
- optional routing reference;
- optional role-agent system prompt when that role is spawned.

Superpowers and Ralph path definitions match the Codex repository benchmark.

These are word counts, not tokenizer counts.

## Runtime shape

Small task:

```text
main model → edit → targeted check → finish
```

Higher-leverage task:

```text
Haiku scout / Opus planner (only if justified)
            ↓
     main integration / Sonnet builder
            ↓
       Haiku verifier
            ↓
    risk-triggered review only
```

## End-to-end status

No task-success or cost advantage is claimed until equal-model/equal-budget task runs are performed. Use `evals/` for reproducible comparisons.
