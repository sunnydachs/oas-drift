# Working agreement for this repository

Short rules for anyone — human or agent — changing `oas-drift`.

## What this tool is

`oas-drift` detects drift between an OpenAPI spec and the implementation. It is
**read-only, deterministic, stdlib-only** and makes no LLM or network call.

## Ground rules

- **Read-only.** The tool reports drift; it never edits the spec or the code.
- **No dependencies, no network.** It must run from a clean checkout.
- **Deterministic output.** Same inputs in, same report out.
- **Tests come with the change.** `pytest -q` must pass, and a new drift category
  needs a fixture that triggers it.
- **No secrets in Git**, and no absolute paths in code, tests or docs — a clone
  must run anywhere.
- **Do not bypass the secret scan.** `git commit --no-verify` is never a fix for a
  gitleaks hit; rotate the credential and rewrite the commit.
- **The README is a promise.** Every documented command must work on a fresh
  clone.

## Checks that must pass

```
pip install -e ".[dev]"
python -m pytest -q
```
