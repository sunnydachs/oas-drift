# oas-drift

Detect drift between your OpenAPI spec and your actual API implementation. Read-only, deterministic, zero dependencies, no LLM.

Point it at an `openapi.json` and a Python codebase, and it reports three classes of drift:

| Finding | Meaning |
|---|---|
| `SPEC ONLY` | defined in the spec but no matching route in code |
| `CODE ONLY` | route exists in code but is not in the spec |
| `METHOD MISMATCH` | path matches but the HTTP method differs |

Supports FastAPI-style (`@app.get(...)`, `@router.post(...)`), variable receivers (`@api_v1.get(...)`), and Flask-style (`@app.route(..., methods=[...])`) decorators, extracted via `ast` — no imports, no execution.

## Install

```bash
pip install .
```

Or run from source with no install (stdlib only):

```bash
python -m oas_drift.cli --spec openapi.json .
```

## Usage

```bash
# scan the current directory against a spec
oas-drift --spec openapi.json

# scan a specific root, machine-readable output
oas-drift --spec openapi.json ./src --json
```

Example output:

```
oas-drift — scanned .
  spec: 12 endpoint(s) | code: 11 route(s)

/items/{id}  ⚠️ METHOD MISMATCH
    spec: delete | code: post
/health  ➕ CODE ONLY
    route in code but not defined in spec

summary: {"code_only": 1, "method_mismatch": 1} | ok: 10
```

Exit code is `0` either way — oas-drift is a *detector*, not a gate. Wire it into CI with `--json` and `jq` if you want to fail on specific statuses.

## Design notes

- **Read-only, deterministic.** Parses sources with the `ast` module. Never imports, never executes, never writes. Same input → same output, always.
- **No dependencies.** Python ≥ 3.11 standard library only.
- **JSON only (for now).** OpenAPI 3.x JSON specs are supported; YAML support is a future item.
- **Path params must match literally.** `/users/{id}` in the spec must appear as `/users/{id}` in code (normalize prefixes if you use router-mounted paths).

## Development

```bash
pip install -e .[dev]
pytest -q
```

15 tests, all pure-function (no network, no fixtures on disk).

## License

MIT
