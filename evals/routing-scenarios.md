# Adaptive Routing Eval Scenarios

Evaluate routing only on tasks where the expected execution shape is clear. The goal is not "more delegation"; it is the smallest sufficient model/effort configuration.

Record:
- main model/effort;
- delegated model/effort or role;
- number of agents;
- whether delegation was necessary;
- task success;
- tool calls/tokens when available;
- wall time;
- duplicate work or conflicting writes.

## Scenarios

1. **One-file local bug**
   - Expected: no subagent, no routing reference needed.
   - Failure: planner/reviewer/test team spawned unnecessarily.

2. **Large unfamiliar repository map**
   - Expected Codex: Terra medium or Luna for mechanical inventory.
   - Expected Claude: scout (Haiku/low).
   - Output should be concise paths/interfaces, not a generic report.

3. **Normal isolated implementation**
   - Expected: current main model directly, or Sol/Sonnet builder only if delegation saves context or enables parallel independent work.

4. **Independent dual investigation**
   - Expected: two bounded read-only investigations may run in parallel.
   - Failure: duplicate agents investigate the same hypothesis.

5. **Targeted test execution**
   - Expected Codex: Luna low/medium.
   - Expected Claude: verifier (Haiku/low).
   - Main thread interprets whether evidence proves completion.

6. **Complex failure after two good attempts**
   - Expected: escalate reasoning/model quality once before increasing loop count.
   - Codex: Sol high or Astra high/xhigh depending severity.
   - Claude: planner (Opus/high) first; escalate to Fable advisor/deep-critic when the problem is cross-system, long-horizon, or still unresolved.

7. **Security/auth/high-impact architecture**
   - Expected Claude: Fable deep-critic on the risky surface only when frontier reasoning is justified; implementation returns to main/Sonnet.

8. **Long-horizon codebase-wide strategy**
   - Expected Claude: Fable advisor at medium effort produces a concise strategy brief; Sonnet/main performs routine execution.
   - Failure: Fable performs boilerplate implementation or receives the full task without a bounded advisory question.

9. **Mechanical repetitive edit**
   - Expected: cheap bounded model only if transformation is precise and independently verifiable.
   - Failure: Astra/Opus used for boilerplate.

10. **Overlapping implementation**
   - Expected: single writer.
   - Failure: two agents edit overlapping files.

11. **Unavailable preferred model**
    - Expected: graceful fallback to nearest available tier/current model without blocking the task.
