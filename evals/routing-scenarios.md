# Adaptive Routing Eval Scenarios

Evaluate routing on tasks with a clear expected execution shape. The goal is the smallest sufficient supported model/effort configuration. Keep the current main model as integrator; routing is optional native subtask guidance, and hooks do not force agent dispatch.

Role families and efforts below are desired policy targets. The currently exposed native input schema controls what can be requested; an alias-only interface cannot pin a catalog's exact release. Verify latest-version freshness and served identity separately when host evidence permits.

## Evidence to record

Keep these evidence categories separate. A successful catalog query is not proof of freshness, entitlement, dispatch, or served identity.

| Category | Required record |
|---|---|
| Preflight | Exact five-line unified preflight before the first mutation; expected task shape and why delegation helps, if used. |
| Host context | Client/runtime version, provider, non-secret account/profile context, main model/effort, relevant native controls, and explicit user/admin pins. |
| Platform / interpreter | Native operating system, Python version and executable visible to the host, launcher used, and whether the evidence is a native CLI run, WSL/POSIX run, or offline fixture. |
| Observation scope | Explicit current host session ID, optional child agent ID, known routing-state directory where required, and state-access/observation status. Never select a latest session automatically. |
| Catalog query | Query success/failure, source, lookup time, source-data time when exposed, pagination/completeness, and whether the catalog matches the active host context. |
| Freshness | Whether the inventory and latest stable release within the chosen family can be established; record the supporting host metadata or **UNVERIFIED**. A saved catalog, successful parse, or alias alone does not prove freshness. |
| Entitlement / availability | Explicit host visibility/restriction flags and any native rejection or successful dispatch evidence. Distinguish advertised models from proven request outcomes; a failed lookup does not prove lack of access. |
| Native dispatch | Whether a native subagent was actually dispatched, role where applicable, agent count, dispatch outcome, and the host evidence source. A prose routing recommendation is only policy selection. |
| Model identity | Separate requested ID/alias, host-resolved model, and host-reported `modelsUsed`, each with its evidence source and status. Leave missing fields **UNVERIFIED** and preserve multiple reported models without reducing them to a guessed single identity. |
| Effort | Desired, supported, requested, and host-reported effective effort as separate values; source of supported-effort evidence and any downgrade or omitted override. An accepted request alone does not prove effective effort. |
| Fallback | Rejection/override reason, supported replacement or current-main route, whether pins were preserved, and evidence for at most one catalog refresh and one supported fallback attempt after rejection. |
| Outcome / efficiency | Task success, acceptance evidence, necessary vs unnecessary delegation, duplicate work/conflicting writes, tool calls/tokens, wall time, and cost only when exposed. Record missing metrics as unavailable. |

Never store credentials, prompts, or tool output in routing-observer state. Evaluate the bounded routing metadata in the per-session report; keep task acceptance evidence in the normal evaluation record.

## Platform prerequisites

Python **3.10+** must be available as `python` on the PATH inherited by Claude Code on native Windows, Linux, and macOS. Hooks use native `command: "python"` plus `args`. An activated virtual environment is acceptable; a `python3`-only installation or shell-only alias does not satisfy the launcher. Record a missing interpreter without installing Python or editing global aliases/PATH/configuration automatically.

## Validation modes

- **Offline fixtures/mocks:** exercise catalog statuses, selection/fallback logic, and hook-payload/report handling. Label these results offline; they do not establish real account entitlement or CLI dispatch.
- **Native CLI configuration checks:** CI uses real Claude Code configuration and component registration on Windows, Linux and macOS in an isolated home without API credentials or model inference. These checks complement the regression suite; they do not establish authenticated dispatch or task quality.
- **Explicit user-run CLI end-to-end evaluation:** use a real relevant task or an explicitly requested bounded native probe, then capture the evidence above. Do not automatically spend on probes, install SDKs, start nested CLI sessions, or change model pins to make a scenario pass.

The 0.12.0 audit combines regression fixtures with native CLI configuration checks. Actual CLI end-to-end routing remains to be evaluated explicitly on each target platform. Windows-style argv or payload tests on Linux are not native Windows evidence; WSL results must be labeled separately. Neither fixture success nor routing observations establish token, latency, cost, or task-success improvements; those require comparable real task runs with equal model/budget conditions.

## Scenarios

1. **One-file local bug**
   - Expected: current main model, zero subagents; no routing reference needed.
   - Failure: unnecessary planner/reviewer/test team or a changed main model.

2. **Large unfamiliar repository map**
   - Expected: scout with the latest available Haiku and supported low effort when delegation helps; fallback to Sonnet with supported effort, then the current main model.
   - Return concise paths/interfaces and unknowns.

3. **Normal isolated implementation**
   - Expected: current main model directly, or builder with latest available Sonnet and supported medium effort when independent work or context savings justify it; fallback to the current main model.

4. **Independent dual investigation**
   - Expected: two bounded read-only investigations may run in parallel when both are necessary.
   - Failure: duplicate agents investigate the same hypothesis or copy unnecessary context.

5. **Targeted test execution**
   - Expected: current model for a cheap local command, or verifier with latest available Haiku and supported low effort when delegation helps; fallback to Sonnet, then the current main model.
   - Main thread interprets whether the evidence proves completion.

6. **Complex failure after two good attempts**
   - Expected: escalate model/effort once at the cognitive bottleneck before increasing loop count; planner with latest available Opus/high when supported, then Fable/medium if a supported fallback is needed, then the current main model.
   - Cross-system, long-horizon, or unresolved reasoning may justify an advisor/deep-critic packet.

7. **Security/auth/high-impact architecture**
   - Expected: deep-critic with latest available Fable/xhigh only when supported and frontier reasoning is justified; otherwise a supported Opus effort or current main model. Implementation returns to main/Sonnet.

8. **Long-horizon codebase-wide strategy**
   - Expected: tool-free advisor with latest available Fable and supported medium effort receives a bounded evidence packet and returns a concise strategy brief; fallback to Opus/high when supported, then current main model.
   - Failure: Fable performs boilerplate implementation or receives the full task without a bounded advisory question.

9. **Mechanical repetitive edit**
   - Expected: a cheap bounded model only if the transformation is precise and independently verifiable.
   - Failure: Opus/Fable handles boilerplate without a cognitive reason.

10. **Overlapping implementation**
    - Expected: one writer owns each affected surface.
    - Failure: two agents edit overlapping files.

11. **Unavailable preferred model**
    - Expected: record whether the host marked the model unavailable or rejected a request, refresh at most once, and attempt one supported fallback before using the current main model.
    - Failure: fabricated model IDs, repeated rejected requests, automatic paid probes, nested sessions, or blocking a task that the main model can complete.

12. **Alias-only native schema/inventory or stale catalog**
    - Expected: a successful query/parse remains separate from freshness. If the exposed native `model` schema accepts only family aliases, use a supported alias even when the catalog lists exact IDs. Request an exact ID only when that input schema explicitly accepts it.
    - Report alias freshness and served identity **UNVERIFIED** without independent host evidence. Include an older same-family main model, provider alias mapping, and stale catalog as cases. Neither an alias nor a public release announcement proves what the account can serve.

13. **Forced model or explicit family pin**
    - Expected: preserve `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, the applicable subagent model/default, and explicit family pins. Record the configured forced route and any conflict with preferred routing.
    - Include FORCE with a subagent model and FORCE without one. A setting explains expected override behavior but does not prove served identity; retain requested and host-resolved values separately.
    - Failure: silently clearing pins or declaring the role's preferred model served because that role was dispatched.

14. **Unsupported or unexposed effort control**
    - Expected: use supported effort only. If the desired role effort cannot be adjusted through a supported native control, use a compatible role or the current main model and record the fallback.
    - Failure: assuming every model/client supports low/medium/high/xhigh or editing installed role definitions to force a retry.

15. **Agent/Task event without model metadata**
    - Expected: `PostToolUse` for `Agent|Task` records the requested model when present, while missing resolved-model and `modelsUsed` fields remain **UNVERIFIED**.
    - A role name, family alias, request field, forced-model setting, or response text is not proof of the served model. Record observer capability separately from metadata completeness.

16. **Explicit host model metadata or substitution**
    - Expected: retain requested ID/alias, explicit host-resolved model, and host-reported `modelsUsed` separately, including mismatches and multiple models.
    - A successful alias dispatch does not prove the latest family release; a resolved ID does not itself establish catalog freshness. Record each conclusion from its own evidence.

17. **Native Windows and Linux launcher prerequisites**
    - Expected: native `command: "python"` plus `args` resolves Python 3.10+ on the host's PATH on native Windows, Linux, and macOS. Include plugin/state paths with spaces and non-ASCII characters.
    - Include a `python3`-only environment as an unmet prerequisite and an activated virtual environment with `python` as a supported setup. Native target-platform runs, offline argv/payload checks, and WSL results are separate evidence.

18. **Explicit session and child scope in reports**
    - Expected: `--report` alone exposes capabilities and **UNVERIFIED** observations. `--report --session-id "<current-session-id>"` reads only that explicit session; optional `--agent-id "<current-agent-id>"` selects its child scope.
    - Missing state/records remain **UNVERIFIED**. Never scan for or auto-select a latest session, and never substitute another session's observations.

## Runtime routing evidence

For each non-DIRECT preflight, compare the selected role and model/effort with the actual native dispatch when the host supports it. A role dispatch establishes delegation; it does not establish served identity. When the runtime cannot provide the requested control, record the supported fallback and its evidence.

From the plugin root on native Windows, Linux, or macOS, run `python hooks/routing_observer.py --report --session-id "<current-session-id>"`, adding `--agent-id "<current-agent-id>"` for child scope when needed. Supply identifiers from the current host. The scoped report exposes capability and requested/resolved/`modelsUsed` statuses for only that session/scope. `--report` alone returns capabilities with observations **UNVERIFIED**, and no latest session is selected automatically. `PostToolUse` observations for `Agent|Task` may provide request and explicit host model metadata. Missing fields remain **UNVERIFIED**, and an unavailable event/report capability must be recorded as a limitation. The observer does not launch agents, enforce the route, or verify task quality.

Score task completion, routing policy, dispatch, identity evidence, and fallback handling separately. A documented supported fallback can satisfy the task without establishing that the preferred model ran. No latency, token, or cost saving should be claimed from these observations alone.
