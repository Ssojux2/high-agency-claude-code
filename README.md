# High Agency for Claude Code

A lightweight Claude Code plugin focused on high-agency coding without process-heavy ceremony.

It provides two skills:

- `high-agency-coding` — define done → act → verify → repair → finish
- `bounded-autonomy` — opt-in bounded Ralph-style continuation using a Claude Code Stop hook

It intentionally does not require brainstorming, TDD, worktrees, planning files, subagents, or review stages for every task.

## Install from GitHub

```text
/plugin marketplace add Ssojux2/high-agency-claude-code
/plugin install high-agency@high-agency
```

Start a new Claude Code session after installation so hooks are loaded.

## Use

### Normal coding

```text
Use high-agency-coding.

Find and fix the refresh-token bug. Run the relevant tests and typecheck before claiming completion.
```

### Bounded autonomous iteration

```text
Use bounded-autonomy.

Finish this feature autonomously. Keep fixing actionable failures until the relevant tests and typecheck pass.
```

The default autonomous loop allows up to 3 additional continuation passes. The Stop hook has a hard cap of 12.

## v0.3 design

The coding skill now emphasizes:

1. A minimal outcome contract: goal, proof, and boundaries.
2. Independently verifiable steps instead of simply taking the largest possible change.
3. Fresh verification of the real requested behavior, including real interface checks when practical.
4. Verification integrity: never weaken tests or checks just to manufacture success.
5. Baseline awareness for pre-existing failures.
6. A trust boundary for instructions found inside code, logs, web pages, and tool output.

Bounded autonomy continues only after meaningful new progress. On the final allowed continuation, the hook explicitly forbids another continuation marker and asks for an evidence-based final state.

## License

MIT
