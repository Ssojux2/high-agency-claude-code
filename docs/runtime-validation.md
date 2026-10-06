# Runtime validation

This separates local fixture checks from checks requiring an authenticated Claude
session. A passing hook test is not evidence that a particular
model was served, or that Claude and Codex have equal task quality or token cost.

## Supported validation targets

| Layer | Target | What it checks |
| --- | --- | --- |
| Python hooks | Python 3.10+ on Windows/Linux/macOS | Process input/output, task state, file snapshots, locking, bounded continuation |
| CI regression matrix | Ubuntu Python 3.10/3.12; macOS Python 3.12; Windows Python 3.12/3.14 | The same regression suite on all three operating systems |
| Claude configuration | Claude Code 2.1.290 on Windows/Linux/macOS | Marketplace, plugin, agents, skill/command loading, hook registration |
| Actual Claude hook execution | Claude Code 2.1.290 with a loopback model fixture on Windows/Linux/macOS | Real event delivery, current verification/diff state, non-error Stop feedback and bounded continuation |
| Authenticated model sessions | Account-dependent; run the scenarios below | Actual dispatch, served-model metadata, background delivery, permissions |

The pinned CLI is the tested integration baseline for 0.12.1. The hook output
protocol requires Claude Code 2.1.163+, which added non-error Stop feedback.
Native `command` plus `args` needs 2.1.139+; a real 2.1.138 host discarded the
script arguments in the compatibility reproduction. Earlier hosts are not
supported by this hook configuration. See the
[official changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md).
The configuration checker uses an empty temporary home, inherits no API
credentials, and makes no model inference requests.

Windows support is native and does not require WSL. Install Git and Python 3.10+
and expose that Python as `python` on the PATH inherited by Claude. An activated
Python virtual environment provides this name on all platforms. On Debian/Ubuntu,
the `python-is-python3` package is another option; on Windows select the Python
installer's PATH option. The doctor checks `python --version`. Hooks use Claude's
exec form (`command` plus `args`), avoiding shell quoting and requiring no Node
bridge. File locks use Windows `msvcrt` or Unix `fcntl` as appropriate. The tool
matcher includes PowerShell as well as Bash.

## Run the automated checks

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_claude_plugin.py
python scripts/validate_claude_hook_execution.py
```

The CLI checker accepts `--claude /absolute/path/to/claude` and optional
`--output /path/to/result.json`. It runs `plugin validate` for the marketplace,
plugin, and agent directory, then `--plugin-dir ... --init-only`. It checks the
debug log for the expected component counts and hook loading. No user task,
background-agent communication, or inference is implied by a successful load.
It also validates a CRLF copy of the Markdown components so Windows Git line
ending conversion cannot silently discard agent frontmatter. Builder and
verifier roles allow the native PowerShell tool as well as Bash.

The execution checker also accepts `--claude` and `--output`. It launches the
official CLI with the checked-in plugin against a deterministic HTTP server bound
to loopback. It uses a dummy test key, an isolated home and disposable Git project.
The fixture requests Read, Write, a real Python unittest command, a Git diff,
one bounded Stop continuation, and a final response. Windows uses the native
PowerShell tool; Linux and macOS use Bash. The checker inspects actual host hook
events and persisted task state, including successful current verification and
the final diff. It requires `Stop hook additional context` and rejects the old
`Stop hook blocking error` feedback. No authenticated model inference, account
entitlement, model routing quality or paid token usage is tested by this fixture.

Hook regressions use genuine subprocesses and temporary Git repositories. Some
events are host-contract fixtures, including delayed/background results. These
fixtures test our event handling; they do not replace observing delivery in the
installed host. Sources for the event contracts:

- [Claude hooks](https://code.claude.com/docs/en/hooks)
- [Plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Subagent model precedence](https://code.claude.com/docs/en/sub-agents)

## Hook troubleshooting

Confirm the loaded plugin version, `claude --version`, and the exact interpreter
name inherited by the Claude process. Release 0.12.1 addresses two distinct cases:

| Symptom | Cause or next check |
| --- | --- |
| `Stop hook blocking error` followed by High Agency continuation/verification text, despite exit code 0 | 0.12.0 sent normal feedback through the blocking-error channel; 0.12.1 uses Stop `additionalContext` |
| Hook timeout while processing an assistant response with many blank lines | The old Impact regex repeatedly crossed line boundaries; 0.12.1 limits it to one line |
| `python` not found, Windows Python alias prompt, or wrong Python version | The configured native executable must be Python 3.10+ named `python`; `python3` alone or a shell alias does not satisfy it |
| Python syntax/name errors involving JSON such as `false` or `null` | Check for a client older than 2.1.139 dropping `args` and launching bare Python |

From the installed plugin directory, run:

```text
python scripts/diagnose_hooks.py
```

If only `python3` or `py -3` is available, use that installed Python 3.10+ to start
the diagnostic. It still tests the configured `python` command instead of silently
substituting the interpreter that ran the diagnostic. Pass `--claude` with a known
native CLI path, or `--claude-version` with the version observed in the affected
host. `/high-agency:doctor` follows the same procedure.

The diagnostic runs synthetic hook inputs in a temporary Git project and reports
interpreter failures, incompatible/unknown client versions and hook output errors.
It does not modify project files, global settings, PATH, or the current session's
state. Its pass result establishes launcher behavior only; current-session event
delivery still needs host evidence. After updating the plugin, start a new Claude
session before retrying. Preserve the exact error, OS, CLI/plugin versions and
failing event if an error remains.

The timeout regression sends 100,000 blank lines, a 2.58 MB mixed-whitespace
response, and a later valid Impact estimate through real hook subprocesses under
a three-second ceiling. CRLF, tabs and Unicode comparison symbols remain covered.

## Authenticated session acceptance

Use a disposable project with a small working test suite and enable the plugin in
a new session. Use the account's normal permissions and available models. Do not
disable permission checks or change global model pins to make a scenario pass.
Record the CLI/plugin version, case, actual hook events, requested model, observed
model metadata, command results, and final outcome. Mark unavailable metadata as
unverified. Avoid retaining prompts, source code, or credentials in shared logs.

| Case | Acceptance evidence |
| --- | --- |
| Small direct fix | One focused change, no unnecessary delegate, a successful current check |
| Automatic skill selection | A normal coding request activates tracking before the first edit |
| Read-only delegate | The intended namespaced role is dispatched; observations are distinct from the requested alias |
| Implementation delegate | Its edits contribute to the parent task and need current verification |
| Model pin/allowlist | User and administrator limits are preserved; fallback is explicit and bounded |
| Failed verification | Failure cannot become a success record; a later repair requires new successful evidence |
| Background verification | Start is pending; only correlated, supported completion evidence can count |
| Two consecutive tasks | The second task gets its own Impact, baseline and continuation budget |
| Bounded continuation | A Stop-generated continuation retains its task/budget and eventually exits |
| Scope expansion | Extra files, modules and high-impact paths trigger the corresponding review |

For background outputs that the installed host does not expose through a supported
completion event, the result remains pending/unverified. Obtain a supported final
result or run a focused foreground check before claiming verification.

The Stop guard uses
[`hookSpecificOutput.additionalContext`](https://code.claude.com/docs/en/hooks#stop-decision-control)
to continue without an error notification. It is advisory and bounded: after its warning budget is exhausted it
allows a truthful final report of failed/pending/unverified checks. It does not
certify correctness or block forever until every test passes.

## Release evidence

The 0.12.1 release adds the real-host, local-model-fixture execution check to the
0.12.0 configuration/loading checks. CI runs both on each native platform.
Authenticated task-quality, model-entitlement and token-efficiency results must
be recorded separately; they are not produced by the automated checks above.

Main-request model switching via Claude Mods is an optional future feature. This
release preserves the existing main-model policy and improves delegation evidence.
