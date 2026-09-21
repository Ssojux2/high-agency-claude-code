# Adaptive Model and Effort Routing — Claude Code

Load this reference only when delegation is justified by the parent skill.

## Principle

Keep the current main model as integrator. Use plugin subagents only when a different capability/cost tier or isolated context materially helps.

Do not spawn agents merely to imitate a team. Handoff and duplicate context are costs.

This plugin provides role agents with model/effort pinned in frontmatter. If a model is blocked or unavailable, accept Claude Code's supported fallback/substitution and continue.

## Available roles

| Role | Model / effort | Use |
|---|---|---|
| `high-agency-scout` | Haiku / low | broad read-only mapping, grep, file inventory, simple API/doc location |
| `high-agency-verifier` | Haiku / low | targeted test execution, command results, deterministic verification reporting |
| `high-agency-builder` | Sonnet / medium | isolated implementation when delegation saves context or enables parallel work |
| `high-agency-planner` | Opus / high | everyday complex architecture, ambiguous cross-system decisions, difficult root-cause reasoning |
| `high-agency-advisor` | Fable / medium | ambitious codebase-wide strategy, long-horizon planning, cross-system coordination, difficult review |
| `high-agency-deep-critic` | Fable / xhigh | rare final escalation for security/high-impact/long-horizon hard reasoning |

## Routing principle

Prefer the smallest sufficient role.

- **Haiku** for speed/scale and deterministic read-heavy work.
- **Sonnet** as the workhorse delegated implementer.
- **Opus** for normal complex reasoning where a strong independent view helps.
- **Fable** for frontier long-horizon strategy or the hardest unresolved reasoning.

Fable is not the default planner. Use it when the problem spans a large codebase, long horizon, many interacting systems, or when cheaper/standard strong reasoning has already failed.

Fable roles are deliberately **tool-free one-shot advisors**. The main thread or Haiku scout gathers the minimum relevant evidence first and passes a compact problem packet to Fable. This keeps frontier reasoning focused on the cognitive bottleneck instead of spending it on repository exploration, reduces duplicate context/tool traffic, and avoids depending on multi-turn child-agent tool behavior.

The advisor pattern is preferred over handing the entire task to Fable: Fable sets the strategy or resolves the hard cognitive bottleneck; the main thread/Sonnet/Haiku perform routine execution and verification.

## Stage guidance

### Planning

- Local/obvious: main thread; no planner.
- Normal multi-step: current main model with a short plan.
- Large unfamiliar repo: scout first, then main thread.
- Everyday complex architecture: planner (Opus/high).
- Ambitious codebase-wide or long-horizon architecture: gather evidence with main/scout, then advisor (Fable/medium) on a bounded packet.
- Capability-critical strategy where medium is insufficient: deep-critic (Fable/xhigh) on a bounded packet, rarely.

Do not send routine planning to Opus or Fable.

### Implementation

- Small/local: main thread directly.
- Isolated work package or parallel independent component: builder.
- Avoid two writing agents in overlapping files.
- Keep integration and final acceptance in the main thread.
- Do not use Fable for routine implementation boilerplate. Use it to guide or unblock the hard part, then return execution to main/Sonnet.

### Testing

- Running targeted tests and reporting exact output: verifier.
- Failure requires interpretation: main thread.
- Complex failure after two evidence-based attempts: planner (Opus/high).
- Persistent long-horizon or cross-system failure after that: main/scout packages the evidence, then advisor (Fable/medium) or deep-critic (Fable/xhigh).

### Review

- Small local diff: main thread only.
- Conditional normal review: main thread or planner when a second strong view matters.
- Broad cross-codebase review: advisor.
- Security/auth/schema/high-impact or subtle long-horizon failure: deep-critic on the risky surface only.

## Effort policy

The role definitions encode common effort levels so the main session does not need maximum effort for every subtask.

- **low** — deterministic search/test/reporting.
- **medium** — normal implementation and economical Fable advisor work.
- **high** — complex Opus reasoning.
- **xhigh** — rare Fable escalation when maximum depth matters.

Fable thinking is always adaptive; effort controls how much reasoning it spends. Prefer Fable/medium for advisor work and reserve xhigh for capability-sensitive cases.

## Parallelism

Good:
- scout maps code while verifier checks an independent current behavior;
- two scouts investigate independent subsystems;
- builder implements an isolated component while main thread handles another non-overlapping one;
- advisor reasons about strategy while a read-only scout gathers a separate factual dependency map.

Bad:
- planner + advisor + builder + verifier for a one-file fix;
- multiple writers on the same files;
- Opus and Fable both solving the same question without a specific reason;
- agents that all receive the whole task and duplicate reasoning.

Ask each subagent for concise findings, file paths, commands, evidence, a strategy brief, or a bounded patch—not a full restatement of context.
