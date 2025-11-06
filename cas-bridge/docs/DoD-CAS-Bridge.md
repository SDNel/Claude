# CAS Bridge — Deliverables & Definition of Done

## Deliverables
- [ ] OpenAPI 3.0 spec (`openapi/cas-openapi.yaml`)
- [ ] Dockerized service (Python FastAPI recommended) with allow-listed MathJSON→SymPy mapping (no eval)
- [ ] Unit tests that consume `/goldens/*.json` and validate expected fields (Text/LaTeX/MathJSON/Steps)
- [ ] Latency report (P50/P95 per op) under nominal load
- [ ] README with run instructions and security notes

## Non-Functional Targets
- P95: simplify/expand/factor/diff ≤ 250 ms; integrate/solve/series/eigen/rref ≤ 350 ms
- 504 on timeout; no partial responses unless WS is explicitly enabled
- No PII in logs; hash or truncate expressions in error logs

## Acceptance
- Golden fixtures all pass
- Axe-clean test UI (no criticals) when scanned against a live preview
- One-click `docker run -p 8000:8000 cas-bridge:1.0` works
