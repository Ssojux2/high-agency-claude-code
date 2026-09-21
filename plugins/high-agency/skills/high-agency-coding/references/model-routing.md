# Adaptive Model and Effort Routing — Claude Code

Load this reference only when delegation is justified by the parent skill.

## Principle

Keep the current main model as integrator. Use plugin subagents only when a different capability/cost tier or isolated context materially helps.

Do not spawn agents merely to imitate a team. Handoff and duplicate context are costs.

This plugin provides role agents with model/effort already pinned in frontmatter. If a model is blocked or unavailable, accept Claude Code's supported fallback/substitution and continue.

## Available roles

| Role | Model / effort | Use |
|---|---|---|
| `high-agency-scout` | Haiku / low | broad read-only mapping, grep, file inventory, simple API/doc location |
| `high-agency-planner` | Opus / high | high-leverage architecture, ambiguous cross-system decisions, difficult plan/critique |
| `high-agency-builder` | Sonnet / medium | isolated implementation when delegation saves context or enables parallel work |
| `high-agency-verifier` | Haiku / low | targeted test execution, command results, deterministic verification reporting |
| `high-agency-deep-critic` | Opus / xhigh | rare escalation for security-critical review or hard reasoning after strong attempts fail |

## Stage guidance

### Planning

- Local/obvious: main thread; no planner.
- Normal multi-step: current main model with a short plan.
- Large unfamiliar repo: scout first, then main thread.
- High-impact/ambiguous architecture: planner returns a concise decision, interfaces, risks, and acceptance evidence.

Do not send routine planning to Opus.

### Implementation

- Small/local: main thread directly.
- Isolated work package or parallel independent component: builder.
- Avoid two writing agents in overlapping files.
- Keep integration and final acceptance in the main thread.

### Testing

- Running targeted tests and reporting exact output: verifier.
- Failure requires interpretation: main thread.
- Complex failure after two evidence-based attempts: planner or deep-critic for root-cause reasoning, then return execution to main/builder.

### Review

- Small local diff: main thread only.
- Conditional normal review: main thread or a bounded builder/second pass if independence matters.
- Security/auth/schema/high-impact architecture: planner or deep-critic on the risky surface only.

## Effort policy

The role definitions encode the common effort levels so the main session does not need to run at maximum effort for every subtask.

- **low** — deterministic search/test/reporting.
- **medium** — normal implementation.
- **high** — architecture and complex reasoning.
- **xhigh** — rare deep critique when consequences or uncertainty are high.

Use the deepest role only when its expected accuracy gain exceeds handoff cost.

## Parallelism

Good:
- scout maps code while verifier checks an independent current behavior;
- two scouts investigate independent subsystems;
- builder implements an isolated component while main thread handles another non-overlapping one.

Bad:
- planner + builder + verifier for a one-file fix;
- multiple writers on the same files;
- agents that all receive the whole task and duplicate reasoning.

Ask each subagent for concise findings, file paths, commands, evidence, or a bounded patch—not a full restatement of context.