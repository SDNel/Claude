# Contractor Prompt — CAS Bridge (Backend + Test UI not imported)

You are building a **standalone CAS Bridge** service and a **tiny test UI** (not imported by our app). No access to our repo.

## Objective
Create a production-ready service that accepts **MathJSON** expressions and returns **MathJSON/LaTeX/Text/Steps** for symbolic ops (simplify, expand, factor, differentiate, integrate, limit, series, solve, linsolve, rref, eigen, steps). Provide a **Dockerized** server, **OpenAPI** spec, **allow-list** mapping, **timeouts**, and **unit tests** with golden fixtures.

## Hard Requirements
- **Security**: Strict **allow-list** MathJSON→SymPy (or equivalent) mapping; **no eval** of raw strings. Per-request **timeouts**; CPU/mem/resource caps.
- **Correctness**: Golden fixtures pass; LaTeX must be valid; steps for integration via `integral_steps()` or equivalent.
- **Performance**: P95 latency ≤ 350 ms for typical ops.
- **Packaging**: Dockerfile; OpenAPI 3.0; README with env vars.
- **No repo access**: deliver self-contained tar/zip or git project.

## API
Use the OpenAPI in `openapi/cas-openapi.yaml` (attached). Two endpoints:
- `POST /cas` → `CasRequest` → `CasResponse`
- `POST /steps` → same request/response; result.steps populated

`CasRequest` fields: `id`, `op`, `expr (MathJSON)`, optional `vars`, `assumptions`, `options`, `want`.

## Golden Tests
Use the JSON fixtures provided in `/goldens`. Implement a test runner that POSTs each `request` and validates the response matches the `expected` fields (allow minor LaTeX variations if mathematically equivalent — suggest normalizing unicode, whitespace, and parentheses).

## Non-Functional
- Logging: redact expressions or hash in logs.
- Observability: collect operation timing (elapsedMs) and operation name.

## Test UI
Provide a single-file `index.html` (no bundler) that:
- Loads **MathLive** + **Compute Engine** (CDN) for LaTeX → MathJSON.
- Lets user pick `op`, enter expression and optional matrix/bounds.
- Posts to `/cas` and renders back **LaTeX** via **KaTeX**; show raw JSON too.
- Configurable **CAS Service URL** textbox (defaults `http://localhost:8000/cas`).

## Acceptance (Definition of Done)
- All deliverables present (OpenAPI, Dockerfile, service, tests, UI, README).
- `/goldens` pass; latency budget met on a laptop; steps returned for the `steps` endpoint.
- Code is linted; no high-sev security issues.
