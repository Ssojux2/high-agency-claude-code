# Structural Benchmark — 2026-09-22

This benchmark measures model-facing workflow instruction footprint, not end-to-end coding quality.

## v0.9 impact calibration

High Agency v0.9 adds one model-facing invariant to the ordinary Claude Code path: predict expected change scope before mutation, then compare the actual diff against that immutable estimate.

| Claude Code path | Model-facing workflow words |
|---|---:|
| High Agency core | **815** |
| Core + bounded autonomy | **1,044** |
| Core + adaptive routing reference | **1,893** |
| Bounded + adaptive routing reference | **2,122** |
| Optional role-agent prompt | **~78–110 each, only when spawned** |
| Superpowers measured bug-fix path | 3,987 |
| Superpowers measured feature path | 5,160 |
| Ralph command scaffold | 129 |

Compared with the measured Superpowers paths:

- core: **79.6% / 84.2% smaller**;
- bounded: **73.8% / 79.8% smaller**;
- core + routing: **52.5% / 63.3% smaller**;
- bounded + routing: **46.8% / 58.9% smaller**.

The v0.8 core was 647 words. v0.9 adds about 168 words for impact prediction/calibration. Role prompts, doctor diagnostics, hook implementation, tests, and eval tooling remain optional or outside ordinary model context.

## v0.9 control-flow intent

- one immutable impact estimate before the first code/config mutation;
- actual file/module spread checked against the estimate;
- match keeps the targeted path;
- minor drift expands only to affected verification;
- major drift triggers focused diff review and risk-scoped broader verification;
- unexpected auth/security/schema/dependency/build/deploy paths are major boundary drift;
- semantic public/shared API drift remains a model final-diff check;
- stronger Opus/Fable escalation remains conditional on a real cognitive bottleneck;
- default at most 2 concurrent delegated agents.

## Method

Whitespace-separated words from model-facing files. Hook code, impact parser, tests, and eval files are excluded.

Superpowers/Ralph comparison definitions match the Codex benchmark.

These are process-footprint numbers, not task-success or cost claims.

## End-to-end status

No task-success or cost advantage is claimed until equal-model/equal-budget runs are performed. v0.9 evaluation should additionally measure impact underestimation, overestimation, drift severity, escalation precision, and escalation recall. See evals/impact-calibration.md.
