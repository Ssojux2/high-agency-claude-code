# Adaptive Model and Effort Routing — Claude Code

Load this reference only when delegation is justified by the parent skill.

## Contents

- [Catalog and input capabilities](#current-model-catalog--resolve-before-routing)
- [Runtime evidence](#runtime-evidence)
- [Roles](#available-roles)
- [Stage guidance](#stage-guidance)
- [Fallbacks](#explicit-fallback-chains)
- [Delegation budget](#delegation-budget)

## Principle

Keep the current main model as integrator. Use plugin subagents only when a different capability/cost tier or isolated context materially helps.

Do not spawn agents merely to imitate a team. Handoff and duplicate context are costs.

This plugin provides role agents with **versionless family aliases** and desired effort levels in frontmatter. Those are compatibility defaults, not immutable model-version pins. If a model is blocked or unavailable, accept Claude Code's supported fallback/substitution and continue.

## Current model catalog — resolve before routing

1. Before the first delegation in each task, inspect the model inventory/capabilities exposed by the current runtime for the active account, provider and client. Use an existing host/SDK model-list capability when exposed; do not invent a Claude CLI `models list` command. Reuse the result within that task and refresh after an account/provider/client change or a rejected model.
2. Resolve the newest available stable release within the chosen Haiku/Sonnet/Opus/Fable family. Use explicit runtime release/upgrade metadata where available, otherwise compare numeric versions within that family. Do not compare model families by version alone. Ignore unavailable, hidden, disabled, preview-only or disallowed entries unless the user explicitly opts into a preview. Public release docs identify releases but do not prove access by this account/provider.
3. Inspect the live input schema before using the bundled role's per-invocation `model` parameter. Current alias-only `Agent` schemas accept `haiku`, `sonnet`, `opus`, and `fable`, not arbitrary release IDs. Pass an **exact model ID only when the schema allows it**; otherwise retain a supported alias. Keep the role's tool restrictions and bounded task intact. Supported per-invocation overrides take precedence over frontmatter except where the host documents an inherited/forced route. Do not write a discovered version back into the installed plugin or global settings.
4. Do not assume a versionless alias guarantees the latest model: a same-family alias can inherit the main conversation's older exact model, and provider/gateway alias mappings can lag newer releases. Prefer the exact current catalog ID only when the input schema permits it to avoid this same-family inheritance. If the host exposes only aliases, retain a supported alias and report latest availability unverified; never fabricate a full ID from memory.
5. Respect explicit user/admin pins and `availableModels` restrictions. Inspect only the safe routing keys: `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_FABLE_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`, and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`. A setting/allowlist is not itself proof of availability. Report a pin/latest-version conflict; do not silently unset or override an intentional pin. Do not print credentials or full settings files.
6. When `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is enabled, the runtime can ignore both the per-invocation model and frontmatter. Report the forced route, not a fictitious latest-model dispatch. If FORCE is enabled without a subagent model, the main model is the effective forced source.
7. Choose only effort levels supported by the resolved model and installed client. Bundled low/medium/high/xhigh levels are desired policy, not a universal capability declaration. If a role's fixed effort cannot be served and the runtime offers no supported per-invocation adjustment, choose a compatible role or stay on the main model. Do not mutate the installed role just to retry.
8. If the catalog or per-invocation control is unavailable, use the native family alias/substitution or current main model. Report catalog source, requested ID or alias, fallback, and the effective served model only when runtime metadata proves it. Latest availability and served-model identity are separate checks. Use at most one catalog refresh and one supported fallback attempt after rejection, then continue on the main model.

No API key, new SDK installation, paid model probe, nested Claude session, or global config rewrite is required by this policy. In hosts without model-list access, alias routing remains supported but cannot guarantee the globally newest release. Keep the CLI current so its native alias/catalog mappings can update; report an outdated client instead of auto-updating it during a coding task.

## Runtime evidence

Separate successful inventory lookup, catalog freshness, account entitlement, and executed dispatch. The bundled `hooks/routing_observer.py` records native `Agent`/`Task` PostToolUse metadata: `requested` with its source, `resolvedModel`, and `modelsUsed` when exposed. It also records supported failure events without copying error text. Read a session explicitly with `--report --session-id <current-session-id>`; `--report` alone reports capabilities and leaves current-session evidence unverified.

`resolvedModel` is a host resolution field. `modelsUsed` is host-reported serving history; neither is reconstructed from answer text or the common parent hook `model`. Missing fields stay unverified. `async_launched` is the backgrounding snapshot and does not prove eventual completion. Desired role effort remains distinct from actual served effort, which this adapter cannot observe. An observed model difference or multiple models does not establish the reason for fallback. Preserve that uncertainty in the preflight/final report.

The observer never dispatches agents, queries an API, reads credentials, or copies prompts/answers. Consult `high-agency-doctor` for its read-only report and capability limits.

## Available roles

Every family below means the latest available version resolved above, not a remembered release number.

| Role | Family / desired effort | Use |
|---|---|---|
| `high-agency-scout` | Haiku / low | broad read-only mapping, grep, file inventory, simple API/doc location |
| `high-agency-verifier` | Haiku / low | targeted test execution, command results, deterministic verification reporting |
| `high-agency-builder` | Sonnet / medium | isolated implementation when delegation saves context or enables parallel work |
| `high-agency-planner` | Opus / high | everyday complex architecture, ambiguous cross-system decisions, difficult root-cause reasoning |
| `high-agency-advisor` | Fable / medium | ambitious codebase-wide strategy, long-horizon planning, cross-system coordination, difficult review |
| `high-agency-deep-critic` | Fable / xhigh | rare final escalation for security/high-impact/long-horizon hard reasoning |

## Unified-preflight routing principle

The parent skill emits one unified preflight before the first mutation. Its `Route` and `Model` lines are the execution decision, not commentary. For a non-DIRECT route, dispatch the matching bundled role named in `Model` with the resolved model, instead of merely mentioning that a stronger/cheaper model would be useful.

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
- Everyday complex architecture: planner (latest available Opus/high).
- Ambitious codebase-wide or long-horizon architecture: gather evidence with main/scout, then advisor (latest available Fable/medium) on a bounded packet.
- Capability-critical strategy where medium is insufficient: deep-critic (Fable/xhigh) on a bounded packet, rarely and only when supported.

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
- Persistent long-horizon or cross-system failure after that: main/scout packages the evidence, then advisor (Fable/medium) or deep-critic (Fable/xhigh), with supported effort.

### Review

- Small local diff: main thread only.
- Conditional normal review: main thread or planner when a second strong view matters.
- Broad cross-codebase review: advisor.
- Security/auth/schema/high-impact or subtle long-horizon failure: deep-critic on the risky surface only.

## Effort policy

The role definitions encode desired effort levels so the main session does not need maximum effort for every subtask. Validate these against the selected model/client rather than assuming identical support across versions.

- **low** — deterministic search/test/reporting.
- **medium** — normal implementation and economical Fable advisor work.
- **high** — complex Opus reasoning.
- **xhigh** — rare Fable escalation when supported and maximum depth matters.

Prefer supported medium effort for advisor work and reserve supported xhigh for capability-sensitive cases.

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

## Explicit fallback chains

Do not block the task because a preferred delegated role/model is unavailable. Resolve every candidate family from the same current catalog and use supported efforts only.

- **scout / verifier:** Haiku low → Sonnet low/medium → current main model
- **builder:** Sonnet medium → current main model
- **normal complex planner / root cause:** Opus high → Fable medium → current main model
- **long-horizon advisor:** Fable medium → Opus high → current main model
- **deep critic:** Fable xhigh → Opus xhigh/high → current main model

If `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is active, treat per-role model pins as overridden and use the effective forced model rather than pretending the routing policy executed.

Do not use experimental agent teams as a fallback mechanism. Use ordinary bounded subagents or stay in the main thread.

Do not silently claim a Fable/Opus role ran when the runtime provides no proof of the served model. A routing decision is only considered executed when the matching bundled role was actually dispatched; otherwise report that execution stayed on the current model. The doctor skill can report configuration and override risks separately.

## Delegation budget

Keep orchestration shallow.

- Default to **at most 2 concurrent delegated agents**.
- Use 3 only for 3 clearly independent workstreams with non-overlapping writes.
- Do not use experimental agent teams to increase fanout.
- Bundled High Agency agents intentionally do not receive the Agent tool, so they cannot recursively create an agent tree.
- Do not spend both Opus and Fable on the same question unless one is explicitly critiquing materially new evidence from the other.

## Handoff packet

Give each role the smallest self-contained packet that preserves correctness:

1. **Goal** — one bounded question or deliverable.
2. **Evidence** — exact file excerpts, symbols, errors, or observations needed for that role.
3. **Constraints** — scope, write boundary, safety/permission limits.
4. **Expected return** — concise findings, strategy brief, bounded patch, or verification evidence.
5. **Stop condition** — return instead of exploring beyond the delegated surface.

Especially for Fable, gather evidence first with main/Haiku and pass a compact packet rather than duplicating a large repository context.

## Sources

Contracts reviewed 2026-10-06. Documentation and offline fixture tests are not proof of account-specific access or a completed native session:
- https://code.claude.com/docs/en/model-config#model-aliases
- https://code.claude.com/docs/en/sub-agents#choose-a-model
- https://code.claude.com/docs/en/hooks#posttooluse

The installed CLI's `sdk-tools.d.ts` defines the concrete `AgentInput` and `AgentOutput` contract; inspect the current exposed schema instead of assuming a remembered schema version.
