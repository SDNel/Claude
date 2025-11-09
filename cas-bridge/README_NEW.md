# CAS Bridge

**Computer Algebra System Bridge** - A production-ready FastAPI service providing symbolic mathematics operations with AI-powered pedagogical step-by-step solutions.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![SymPy](https://img.shields.io/badge/SymPy-1.12+-orange.svg)](https://www.sympy.org/)

## 🎯 Overview

CAS Bridge combines the mathematical power of **SymPy** with **AI-powered explanations** from Claude Sonnet 4.5 to provide:

- **Accurate symbolic computation** (differentiation, integration, solving, matrix operations)
- **Pedagogical step-by-step solutions** with narrative explanations
- **Mathematical validation** of AI-generated steps to prevent hallucinations
- **Stateful session registry** with automatic type inference
- **REST API** using MathJSON for mathematical expressions

### Why CAS Bridge?

- **🎓 Educational**: AI generates clear explanations showing intermediate work
- **🔒 Reliable**: All answers anchored by SymPy's mathematically correct solutions
- **✅ Validated**: Each step is mathematically verified (Phase 2 feature)
- **📊 Stateful**: Session registry maintains variables and functions across requests
- **🚀 Fast**: <100ms for basic operations, 10-20s for AI explanations

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Operations](#operations)
- [AI Step-by-Step](#ai-step-by-step-solutions)
- [Session Registry](#session-registry)
- [Development](#development)
- [Examples](#examples)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) Anthropic API key for AI step-by-step features

### Installation

```bash
# Clone repository
git clone https://github.com/SDNel/Claude.git
cd Claude/cas-bridge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install anthropic  # For AI features

# Configure (optional - only for AI features)
echo 'ANTHROPIC_API_KEY=your-key-here' > .env
```

### Running

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Access:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Test UI: Open `ui/index.html` in browser

### Quick Test

```bash
curl -X POST http://localhost:8000/cas \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "op": "integrate",
    "expr": ["Power", "x", 2],
    "vars": ["x"],
    "want": ["LaTeX"]
  }'
```

Response:
```json
{
  "id": "test-1",
  "ok": true,
  "result": {
    "latex": "\\frac{x^{3}}{3}"
  }
}
```

## ✨ Features

### 1. Symbolic Mathematics (SymPy Core)

| Operation | Description | Example |
|-----------|-------------|---------|
| **simplify** | Algebraic simplification | `(x+1)²-1 → x²+2x` |
| **expand** | Polynomial expansion | `(x+1)³ → x³+3x²+3x+1` |
| **factor** | Factorization | `x²-1 → (x-1)(x+1)` |
| **differentiate** | Symbolic derivatives | `d/dx[sin(x)] → cos(x)` |
| **integrate** | Integration | `∫x² dx → x³/3` |
| **solve** | Equation solving | `x²-4=0 → x=±2` |
| **limit** | Limits | `lim(x→0) sin(x)/x → 1` |
| **series** | Taylor series | `e^x → 1+x+x²/2+...` |
| **linsolve** | Linear systems | Solve Ax=b |
| **rref** | Row reduction | Matrix to RREF |
| **eigen** | Eigenvalues | Matrix eigenvalues |

**Plus:**
- Complex number support (e^(πi) = -1)
- Constant recognition (π, e, i, ∞)
- Matrix operations
- Function evaluation

### 2. AI-Powered Step-by-Step Solutions (Phase 2)

**🎓 Pedagogical Explanations by Claude Sonnet 4.5**

Unlike traditional CAS systems that just show the answer, CAS Bridge provides **narrative, tutorial-style explanations**:

```
Input: ∫x²sin(x) dx

Output:
1. Apply integration by parts with u = x² and dv = sin(x) dx
   • Calculate du: du = 2x dx
   • Calculate v: v = ∫sin(x) dx = -cos(x)
   • Apply formula ∫u dv = uv - ∫v du
   • Result: -x²cos(x) + ∫2x cos(x) dx
   [✓ Verified]

2. For the remaining integral ∫2x cos(x) dx, apply integration by parts again
   • Let u = 2x, dv = cos(x) dx
   • Calculate du = 2 dx, v = sin(x)
   • Result: 2x sin(x) - ∫2 sin(x) dx
   [✓ Verified]

3. Integrate the final term: ∫2 sin(x) dx = -2 cos(x)
   Combine all parts: -x²cos(x) + 2x sin(x) + 2 cos(x)
   [✓ Verified - Matches final solution]
```

**Key Features:**
- **Anchored by SymPy**: Final answer is always mathematically correct
- **Validation**: Each step verified against SymPy (prevents AI hallucinations)
- **Intermediate Work**: Shows du, dv, substitutions explicitly
- **Narrative Flow**: Clear "Now we..." explanations
- **Grouped Steps**: Related work organized together

**Currently Supported:** Integration
**Coming Soon:** Simplification, Factorization, Solving

### 3. Enhanced Session Registry

**Stateful variable storage with automatic type inference:**

```javascript
// Store a variable
POST /cas
{
  "op": "assign",
  "expr": ["Equal", "A", 5]
}

// Store a function
POST /cas
{
  "op": "assign",
  "expr": ["Equal", ["f", "x"], ["Add", ["Power", "x", 2], 1]]
}

// Variables automatically substituted
POST /cas
{
  "op": "simplify",
  "expr": ["Multiply", "A", "x"]
}
// Result: 5x (A replaced with 5)

// Functions automatically evaluated
POST /cas
{
  "op": "simplify",
  "expr": ["f", 2]
}
// Result: 5 (f(2) = 2² + 1 = 5)
```

**Supported Types:**
- `scalar`: Numbers (5, π, e)
- `expression`: Symbolic expressions (x² + 2x)
- `matrix`: 2D matrices ([[1,2],[3,4]])
- `vector`: 1D vectors
- `function`: Lambda functions (f(x) = x² + 1)
- `operator`: Differential operators

**Features:**
- Automatic type inference
- Metadata tracking (creation time, LaTeX, MathJSON)
- Dual storage (SymPy + MathJSON)
- RESTful management (GET, DELETE endpoints)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Application                    │
│              (Browser, Mobile, Python, etc.)            │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (JSON/MathJSON)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    CAS Bridge Server                     │
│                     (FastAPI)                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐    ┌─────────────┐   ┌──────────────┐  │
│  │  Routes    │───▶│ Operations  │──▶│   Registry   │  │
│  │            │    │             │   │              │  │
│  │ /cas       │    │ SymPy Core  │   │ Type Infer   │  │
│  │ /steps     │    │             │   │ Variables    │  │
│  │ /registry  │    │ AI Generate │   │ Functions    │  │
│  └────────────┘    └─────────────┘   └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           AI Step Generator (Phase 2)            │  │
│  │                                                   │  │
│  │  Claude Sonnet 4.5  ────▶  SymPy Validator      │  │
│  │  (Anthropic API)           (Equivalence Check)   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   SymPy     │
              │ (Pure Math) │
              └─────────────┘
```

### Data Flow

1. **Client** sends MathJSON expression
2. **Security** validates against allowlist
3. **Parser** converts MathJSON → SymPy
4. **SymPy** computes mathematically correct result
5. **Registry** looks up/stores variables
6. **(Optional) AI** generates step-by-step explanation
7. **(Optional) Validator** verifies each step
8. **Formatter** converts SymPy → MathJSON/LaTeX/Text
9. **Response** returned to client

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/cas` | POST | Execute operation |
| `/steps` | POST | Execute with AI steps |
| `/registry` | GET | Get all variables |
| `/registry` | DELETE | Clear all variables |
| `/registry/{name}` | DELETE | Delete variable |

### Request Format

```typescript
interface CasRequest {
  id: string;              // Unique request ID
  op: string;              // Operation (integrate, simplify, etc.)
  expr: any;               // MathJSON expression
  vars?: string[];         // Variables for differentiate/integrate
  assumptions?: object;    // Additional parameters
  want?: string[];         // Output formats: MathJSON, LaTeX, Text, Steps
}
```

### Response Format

```typescript
interface CasResponse {
  id: string;
  ok: boolean;
  result?: {
    mathjson?: any;
    latex?: string;
    text?: string;
    steps?: Step[];
  };
  error?: {
    code: string;
    message: string;
  };
  stats?: {
    elapsedMs: number;
    backend: string;
    cached: boolean;
  };
}
```

**Detailed Integration Guide:** See [docs/API_INTEGRATION.md](./docs/API_INTEGRATION.md)

## 🔧 Operations

### Basic Examples

```javascript
// Simplify
{
  "op": "simplify",
  "expr": ["Power", ["Add", "e", "Pi", "ImaginaryI"], 1]
}
// Result: e^(πi) → -1

// Differentiate
{
  "op": "differentiate",
  "expr": ["Power", "x", 3],
  "vars": ["x"]
}
// Result: 3x²

// Integrate
{
  "op": "integrate",
  "expr": ["Sin", "x"],
  "vars": ["x"]
}
// Result: -cos(x)

// Solve
{
  "op": "solve",
  "expr": ["Equal", ["Add", ["Power", "x", 2], ["Negate", 4]], 0],
  "vars": ["x"]
}
// Result: [-2, 2]
```

## 🤖 AI Step-by-Step Solutions

### Phase 1 vs Phase 2

**Phase 1** (Deprecated):
- Used SymPy's `integral_steps`
- Generated rule names only
- No narrative or intermediate work
- **User feedback**: "Mystifying to many students"

**Phase 2** (Current):
- Uses Claude Sonnet 4.5 AI
- Generates narrative explanations
- Shows all intermediate work
- Validates steps mathematically
- **User feedback**: "Good and clear"

### How It Works

1. **SymPy computes correct answer** (anchor point)
2. **AI generates explanations** (Claude Sonnet 4.5)
3. **Validator checks each step** (SymPy equivalence)
4. **Steps returned with validation badges** (✓/⚠)

### Validation Status

- **✓ Verified**: Step is mathematically correct
- **⚠ Unverified**: Couldn't verify (might be hallucination)
- **(no badge)**: First step or unparseable

**Special**: Last step always compared against SymPy's solution.

### Performance

- **Latency**: 10-20 seconds (includes AI + validation)
- **Cost**: ~$0.001-0.01 per request (Anthropic API)
- **Future**: Caching common integrals

## 📊 Session Registry

### Managing Variables

```javascript
// Store variable
POST /cas {"op": "assign", "expr": ["Equal", "a", 5]}

// Get all variables
GET /registry
// Returns: {"objects": {"a": {...}}}

// Delete variable
DELETE /registry/a

// Clear all
DELETE /registry
```

### Type Inference

```javascript
// Scalar
assign("A", 5)  → type: "scalar"

// Expression
assign("B", ["Add", "x", 1])  → type: "expression"

// Matrix
assign("M", [[1,2],[3,4]])  → type: "matrix"

// Function
assign(["f", "x"], ["Power", "x", 2])  → type: "function"
```

### Variable Lookup

Variables are automatically substituted in expressions:

```javascript
// 1. Store
assign("a", 5)

// 2. Use
simplify(["Multiply", "a", "x"])  // Auto-replaces a with 5
// Result: 5x
```

## 🛠️ Development

### Project Structure

```
cas-bridge/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings (loads .env)
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── models.py        # Request/response models
│   ├── core/
│   │   ├── operations.py    # SymPy operations
│   │   ├── mathjson_parser.py  # MathJSON ↔ SymPy
│   │   └── session.py       # Variable registry
│   ├── ai/
│   │   ├── step_generator.py   # Claude AI integration
│   │   └── validator.py     # Step validation
│   └── security/
│       └── allowlist.py     # Security validation
├── ui/
│   └── index.html           # Test interface
├── docs/
│   └── API_INTEGRATION.md   # Integration guide
├── tests/
├── .env                     # Config (git-ignored)
├── requirements.txt
└── README.md
```

### Environment Variables

```.env
# AI Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Security
DEFAULT_TIMEOUT_MS=1000
MAX_TIMEOUT_MS=5000
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=app --cov-report=html
```

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request

## 📚 Examples

### JavaScript Client

```javascript
const cas = new CASBridge('http://localhost:8000');

// Basic integration
const result = await cas.compute('integrate', ['Power', 'x', 2], {vars: ['x']});
console.log(result.latex);  // \frac{x^{3}}{3}

// With step-by-step
const steps = await cas.getSteps('integrate',
  ['Multiply', ['Power', 'x', 2], ['Sin', 'x']],
  {vars: ['x']}
);

steps.steps.forEach(step => {
  const badge = step.validated ? '✓' : '⚠';
  console.log(`${badge} ${step.explanation}`);
  console.log(`   ${step.latex}\n`);
});
```

### Python Client

```python
from cas_bridge import CASBridge

cas = CASBridge("http://localhost:8000")

# Basic operation
result = cas.compute("integrate", ["Power", "x", 2], vars=["x"])
print(result["latex"])  # \frac{x^{3}}{3}

# With steps
steps = cas.get_steps("integrate",
    ["Multiply", ["Power", "x", 2], ["Sin", "x"]],
    vars=["x"]
)

for step in steps["steps"]:
    badge = "✓" if step.get("validated") else "⚠"
    print(f"{badge} {step['explanation']}")
    print(f"   {step['latex']}\n")
```

### React Component

```tsx
import { useState } from 'react';
import { CASBridge } from './cas-bridge';

function Calculator() {
  const [result, setResult] = useState(null);
  const [steps, setSteps] = useState([]);
  const cas = new CASBridge();

  const compute = async () => {
    const mathJSON = ['Power', 'x', 2];
    const result = await cas.compute('integrate', mathJSON, {vars: ['x']});
    setResult(result);

    const stepsData = await cas.getSteps('integrate', mathJSON, {vars: ['x']});
    setSteps(stepsData.steps);
  };

  return (
    <div>
      <button onClick={compute}>Integrate x²</button>
      {result && <div>Result: {result.latex}</div>}
      {steps.map((step, i) => (
        <div key={i}>
          {step.validated ? '✓' : '⚠'} {step.explanation}
        </div>
      ))}
    </div>
  );
}
```

## 🔒 Security

- **Allowlist Validation**: Only permitted MathJSON operations
- **No Code Execution**: Pure symbolic computation
- **Input Validation**: Pydantic models
- **Timeouts**: Prevents infinite loops
- **CORS**: Configurable origins
- **API Key**: Environment-based (.env, not committed)

## 📈 Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| Basic (simplify, expand) | <100ms | Fast |
| Integration (no steps) | <500ms | SymPy only |
| Integration (with AI steps) | 10-20s | AI + validation |
| Variable lookup | <10ms | Registry |

**Optimization opportunities:**
- Cache common integrals
- Stream AI responses
- Redis session storage

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- **SymPy**: Core CAS engine
- **Anthropic**: Claude AI for pedagogical explanations
- **FastAPI**: High-performance web framework
- **MathLive**: Visual math input
- **Compute Engine**: MathJSON standard

## 📞 Support

- **Documentation**: [docs/API_INTEGRATION.md](./docs/API_INTEGRATION.md)
- **API Docs**: http://localhost:8000/docs
- **Issues**: [GitHub Issues](https://github.com/SDNel/Claude/issues)
- **Source**: [GitHub](https://github.com/SDNel/Claude/tree/main/cas-bridge)

---

**Built with ❤️ for mathematics education**
