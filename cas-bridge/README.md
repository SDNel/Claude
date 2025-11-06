# CAS Bridge - Computer Algebra System API

A production-ready service that provides symbolic mathematics operations via a REST API. Accepts **MathJSON** expressions and returns results in MathJSON, LaTeX, and text formats.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Build the image
docker build -t cas-bridge:1.0 .

# Run the service
docker run -p 8000:8000 cas-bridge:1.0
```

Or use docker-compose:

```bash
docker-compose up
```

The service will be available at `http://localhost:8000`

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Run the service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the UI

Open `ui/index.html` in your browser (or serve it via a static server). Set the service URL to `http://localhost:8000/cas` and start testing operations!

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: `openapi/cas-openapi.yaml`

### Endpoints

#### `GET /healthz`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

#### `POST /cas`
Execute a symbolic math operation.

**Request:**
```json
{
  "id": "req-001",
  "op": "differentiate",
  "expr": ["Sin", "x"],
  "vars": ["x"],
  "want": ["MathJSON", "LaTeX", "Text"]
}
```

**Response:**
```json
{
  "id": "req-001",
  "ok": true,
  "result": {
    "latex": "\\cos\\left(x\\right)",
    "mathjson": ["Cos", "x"],
    "text": "cos(x)"
  },
  "stats": {
    "elapsedMs": 45.2,
    "backend": "remote-sympy",
    "cached": false
  }
}
```

#### `POST /steps`
Same as `/cas` but includes step-by-step explanation in `result.steps`.

## 🔧 Supported Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `simplify` | Simplify expression | `(x+1)²-1` → `x²+2x` |
| `expand` | Expand expression | `(x+1)³` → `x³+3x²+3x+1` |
| `factor` | Factor expression | `x²-1` → `(x-1)(x+1)` |
| `differentiate` | Differentiate | `d/dx[sin(x)]` → `cos(x)` |
| `integrate` | Integrate | `∫x²dx` → `x³/3` |
| `limit` | Compute limit | `lim(x→0) sin(x)/x` → `1` |
| `series` | Taylor series | `e^x` at x=0 → `1+x+x²/2+...` |
| `solve` | Solve equation | `x²-4=0` → `x=±2` |
| `linsolve` | Linear system | Solve Ax=b |
| `rref` | Row echelon form | Reduce matrix |
| `eigen` | Eigenvalues | Find eigenvalues of matrix |

## 📝 MathJSON Format

MathJSON is a JSON-based representation of mathematical expressions. Examples:

```javascript
// Addition: x + 1
["Add", "x", 1]

// Power: x²
["Power", "x", 2]

// Trigonometric: sin(x)
["Sin", "x"]

// Complex: (x+1)³
["Power", ["Add", "x", 1], 3]

// Matrix
[[2, 1], [1, 3]]

// Linear system
{"A": [[2,1],[1,3]], "b": [1,0]}
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Integration Tests (Golden Fixtures)
```bash
pytest tests/integration/test_goldens.py -v
```

### Run All Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Golden Fixtures
The `goldens/` directory contains test fixtures with expected outputs. All fixtures must pass for the service to be production-ready.

## 🔒 Security

### Key Security Features

1. **Allow-list Based Validation**: Only permitted MathJSON operations are allowed. No arbitrary code execution.
2. **No `eval()`**: All expression parsing uses strict allow-list mapping to SymPy functions.
3. **Timeouts**: Per-request timeouts prevent infinite loops and DoS attacks.
4. **Resource Limits**: Maximum expression depth, matrix sizes, and string lengths.
5. **PII Redaction**: Expressions are hashed or truncated in logs to prevent data leakage.

### Security Configuration

```bash
# Environment variables
DEFAULT_TIMEOUT_MS=1000       # Default operation timeout
MAX_TIMEOUT_MS=5000          # Maximum allowed timeout
MAX_EXPRESSION_LENGTH=10000  # Max string length
REDACT_EXPRESSIONS=true      # Hash expressions in logs
```

### Security Notes

- ⚠️ **Never disable the allow-list validation**
- ⚠️ **Always run with resource limits in production**
- ⚠️ **Keep SymPy updated for security patches**
- ⚠️ **Monitor for unusual request patterns**

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true

# Security
DEFAULT_TIMEOUT_MS=1000
MAX_TIMEOUT_MS=5000
MAX_EXPRESSION_LENGTH=10000

# Performance
MAX_WORKERS=4
BACKEND_NAME=remote-sympy

# Logging
LOG_FORMAT=json
REDACT_EXPRESSIONS=true
```

## 📊 Performance

### Latency Targets (P95)

| Operation | Target | Notes |
|-----------|--------|-------|
| simplify, expand, factor, differentiate | ≤ 250ms | Basic operations |
| integrate, solve, series, eigen, rref | ≤ 350ms | Complex operations |

### Performance Testing

```bash
# Run benchmark tests
pytest tests/performance/ --benchmark-only
```

## 🏗️ Project Structure

```
cas-bridge/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── models.py        # Pydantic models
│   ├── core/
│   │   ├── operations.py    # Mathematical operations
│   │   └── mathjson_parser.py  # MathJSON↔SymPy conversion
│   ├── security/
│   │   └── allowlist.py     # Security validation
│   └── utils/
│       └── logging.py       # Logging utilities
├── tests/
│   ├── conftest.py
│   ├── unit/                # Unit tests
│   ├── integration/         # Golden fixture tests
│   └── performance/         # Benchmark tests
├── ui/
│   └── index.html           # Test UI
├── openapi/
│   ├── cas-openapi.yaml     # OpenAPI 3.0 spec
│   └── cas-types.ts         # TypeScript types
├── goldens/                 # Test fixtures
├── docs/                    # Documentation
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in docker run
docker run -p 8001:8000 cas-bridge:1.0

# Or update .env file
PORT=8001
```

**CORS errors in browser:**
```bash
# Add your origin to CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,http://yourdomain.com
```

**Timeout errors:**
```bash
# Increase timeout limit
DEFAULT_TIMEOUT_MS=2000
MAX_TIMEOUT_MS=10000
```

## 📖 Additional Documentation

- `docs/DoD-CAS-Bridge.md` - Definition of Done & deliverables
- `docs/Prompt-CAS-Bridge.md` - Contractor prompt & requirements
- `docs/README-CAS-Bridge.md` - Package overview
- `docs/Golden Tests.md` - Golden fixture documentation

## 🔄 Development Status

### ✅ Completed
- [x] Project structure
- [x] Configuration management
- [x] API endpoints (skeleton)
- [x] Pydantic models
- [x] Security allow-list
- [x] Docker configuration
- [x] Test infrastructure
- [x] Documentation

### 🚧 In Progress
- [ ] MathJSON↔SymPy parser implementation
- [ ] Mathematical operations implementation
- [ ] Step-by-step explanations
- [ ] Golden fixture tests

### 📅 TODO
- [ ] Complete all 11 operation implementations
- [ ] Implement timeout mechanism
- [ ] Add comprehensive error handling
- [ ] Performance optimization
- [ ] Load testing
- [ ] Security audit

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Email: your.email@example.com

---

**Built with ❤️ using FastAPI and SymPy**
