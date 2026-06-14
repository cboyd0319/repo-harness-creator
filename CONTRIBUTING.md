# Contributing

Keep contributions small, reviewed, source-backed, and easy to verify.

## Local Setup

Use Python 3.13+ on macOS 15+, Windows 11+, Ubuntu 22.04+, or another modern
Linux distribution with Python 3.13+.

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests
PYTHONPATH=src:. python3 scripts/check_pins.py --root .
PYTHONPATH=src:. python3 -m repo_harness_creator audit --target . --min-score 85
```

Run `./init.sh` or `.\init.ps1` before submitting larger changes.

## Pull Requests

- Read `AGENTS.md` and the relevant files in `docs/harness/` before editing.
- Keep one feature or fix per pull request.
- Add focused tests for changed behavior when practical.
- Update docs and harness state when behavior, generated files, workflows, or
  durable decisions change.
- Attribute external prior art in the PR description and in docs or comments
  when a design, algorithm, policy, or convention is adapted from another
  project.

## Developer Certificate Of Origin

Commits intended for submission should include a `Signed-off-by` trailer:

```bash
git commit -s -m "fix: validate action score input"
```

The sign-off certifies that you wrote the change or have the right to submit it
under this repository's license.

## AI-Assisted Contributions

AI development tools are allowed, but the contributor owns the result.

- Be able to explain every meaningful change, including the tradeoffs.
- Verify generated code and docs against the current repository state.
- Do not submit autonomous changes without human review of the exact diff.
- Do not use AI tools to launder unattributed derivative work.
- Do not include secrets, credentials, private repository data, or long raw
  logs in prompts, issues, commits, or pull requests.

Disclosure is required when a contribution was produced autonomously or when
AI-produced content is submitted without meaningful human review.

Security-sensitive changes receive heightened review regardless of how they
were produced.
