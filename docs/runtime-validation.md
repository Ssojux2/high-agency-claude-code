# Runtime validation

This separates checks that run without model inference from checks requiring an
authenticated Claude session. A passing hook test is not evidence that a particular
model was served, or that Claude and Codex have equal task quality or token cost.

## Supported validation targets

| Layer | Target | What it checks |
| --- | --- | --- |
| Python hooks | Python 3.10+ on Windows/Linux/macOS | Process input/output, task state, file snapshots, locking, bounded continuation |
| CI regression matrix | Ubuntu Python 3.10/3.12; macOS Python 3.12; Windows Python 3.12/3.14 | The same regression suite on all three operating systems |
| Claude configuration | Claude Code 2.1.290 on Windows/Linux/macOS | Marketplace, plugin, agents, skill/command loading, hook registration |
| Authenticated model sessions | Account-dependent; run the scenarios below | Actual dispatch, served-model metadata, background delivery, permissions |

The pinned CLI is the integration baseline for 0.12.0. Older hosts may lack events
used by this release; they are not covered by the CLI gate. The native CLI check uses an empty temporary
home, inherits no API credentials, and makes no model inference requests.

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
```

The CLI checker accepts `--claude /absolute/path/to/claude` and optional
`--output /path/to/result.json`. It runs `plugin validate` for the marketplace,
plugin, and agent directory, then `--plugin-dir ... --init-only`. It checks the
debug log for the expected component counts and hook loading. No user task,
background-agent communication, or inference is implied by a successful load.
It also validates a CRLF copy of the Markdown components so Windows Git line
ending conversion cannot silently discard agent frontmatter. Builder and
verifier roles allow the native PowerShell tool as well as Bash.

Hook regressions use genuine subprocesses and temporary Git repositories. Some
events are host-contract fixtures, including delayed/background results. These
fixtures test our event handling; they do not replace observing delivery in the
installed host. Sources for the event contracts:

- [Claude hooks](https://code.claude.com/docs/en/hooks)
- [Plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Subagent model precedence](https://code.claude.com/docs/en/sub-agents)

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

The Stop guard is advisory and bounded: after its warning budget is exhausted it
allows a truthful final report of failed/pending/unverified checks. It does not
certify correctness or block forever until every test passes.

## Release evidence

The 0.12.0 release fixes were checked with local hook regression tests and the
official CLI's configuration/loading path. CI provides its own platform results.
Authenticated task-quality, model-entitlement and token-efficiency results must
be recorded separately; they are not produced by the automated checks above.

Main-request model switching via Claude Mods is an optional future feature. This
release preserves the existing main-model policy and improves delegation evidence.
