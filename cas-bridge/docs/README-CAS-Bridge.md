# CAS Bridge Package

This folder contains:
- `openapi/cas-openapi.yaml` — OpenAPI 3.0 contract
- `client/cas-types.ts` — TypeScript request/response types
- `goldens/*.json` — sample request/expected fixtures
- `DoD-CAS-Bridge.md` — deliverables & definition of done
- `ui/index.html` — **standalone** test UI (MathLive input + KaTeX output)
  - Set **CAS Service URL** (e.g., `http://localhost:8000/cas`), pick an operation, enter expression in MathLive, and run.

## Quick Start
1. Run your CAS Bridge service locally (e.g., FastAPI on port 8000).
2. Open `ui/index.html` in your browser (double click, or serve via any static server).
3. Set the service URL to `http://localhost:8000/cas` and test.

## Notes
- The UI uses MathLive + Compute Engine to translate LaTeX → MathJSON, and renders results with KaTeX.
- Matrix ops accept a JSON matrix in the **Matrix** textarea (e.g., `[[2,1],[1,3]]` or `{"A":[[2,1],[1,3]],"b":[1,0]}`).
- For definite integrals, set Assumptions: `{"bounds":[a,b]}`. For series: `{"around":0,"order":5}`. For limit: `{"point":0,"direction":"two-sided"}`.
