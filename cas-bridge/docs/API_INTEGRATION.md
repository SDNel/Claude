# CAS Bridge API Integration Guide

Complete guide for integrating CAS Bridge into your application.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Request Format](#request-format)
- [Response Format](#response-format)
- [Endpoints](#endpoints)
- [Operations](#operations)
- [Session Registry](#session-registry)
- [AI Step-by-Step Solutions](#ai-step-by-step-solutions)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)
- [Best Practices](#best-practices)

## Overview

CAS Bridge provides a REST API for symbolic mathematics operations. All requests and responses use JSON format with **MathJSON** for mathematical expressions.

### Key Concepts

- **MathJSON**: JSON-based mathematical notation (Compute Engine standard)
- **Session**: Stateful context that stores variables and functions
- **Operations**: Mathematical transformations (simplify, integrate, solve, etc.)
- **Validation**: All steps are mathematically verified against SymPy

## Authentication

Currently, CAS Bridge does not require authentication. If deploying in production, add authentication middleware (JWT, API keys, etc.).

For AI step-by-step features, the server requires an `ANTHROPIC_API_KEY` environment variable.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

## Request Format

All POST requests use JSON with the following structure:

```typescript
interface CasRequest {
  id: string;                    // Unique request ID
  op: string;                    // Operation type
  expr: any;                     // MathJSON expression
  vars?: string[];               // Variables (for differentiate, integrate, etc.)
  assumptions?: {[key: string]: any};  // Additional parameters
  want?: string[];               // Desired output formats
}
```

### Output Formats

Specify desired output formats in the `want` array:

- `"MathJSON"` - JSON representation
- `"LaTeX"` - LaTeX string
- `"Text"` - Plain text (Python syntax)
- `"Steps"` - Step-by-step solution (only for `/steps` endpoint)

**Default**: `["MathJSON", "LaTeX", "Text"]`

## Response Format

```typescript
interface CasResponse {
  id: string;                    // Matches request ID
  ok: boolean;                   // Success flag
  result?: {
    mathjson?: any;              // MathJSON result
    latex?: string;              // LaTeX result
    text?: string;               // Text result
    steps?: Step[];              // Step-by-step (if requested)
  };
  error?: {
    code: string;                // Error code
    message: string;             // Error message
    details?: any;               // Additional error details
  };
  stats?: {
    elapsedMs: number;           // Execution time
    backend: string;             // Backend engine
    cached: boolean;             // Whether result was cached
  };
}
```

### Step Format

```typescript
interface Step {
  expression: string;            // Text representation
  latex: string;                 // LaTeX representation
  explanation: string;           // Human-readable explanation
  depth: number;                 // Indentation level (0, 1, 2)
  validated?: boolean | null;    // Mathematical verification status
  validation_note?: string;      // Validation details
}
```

## Endpoints

### GET /healthz

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### POST /cas

Execute a mathematical operation.

**Request Example:**
```json
{
  "id": "req-001",
  "op": "integrate",
  "expr": ["Power", "x", 2],
  "vars": ["x"],
  "want": ["LaTeX", "MathJSON"]
}
```

**Response Example:**
```json
{
  "id": "req-001",
  "ok": true,
  "result": {
    "mathjson": ["Multiply", ["Divide", 1, 3], ["Power", "x", 3]],
    "latex": "\\frac{x^{3}}{3}"
  },
  "stats": {
    "elapsedMs": 45.2,
    "backend": "remote-sympy",
    "cached": false
  }
}
```

### POST /steps

Same as `/cas` but includes AI-powered step-by-step explanations.

**Request Example:**
```json
{
  "id": "req-002",
  "op": "integrate",
  "expr": ["Multiply", ["Power", "x", 2], ["Sin", "x"]],
  "vars": ["x"],
  "want": ["Steps", "LaTeX"]
}
```

**Response Example:**
```json
{
  "id": "req-002",
  "ok": true,
  "result": {
    "latex": "-x^{2}\\cos(x) + 2x\\sin(x) + 2\\cos(x)",
    "steps": [
      {
        "expression": "-x^2*cos(x) + integral(2*x*cos(x), x)",
        "latex": "-x^2\\cos(x) + \\int 2x\\cos(x)\\,dx",
        "explanation": "Apply integration by parts with u = x² and dv = sin(x) dx. We get du = 2x dx and v = -cos(x). Using ∫u dv = uv - ∫v du: -x²cos(x) + ∫2x cos(x) dx",
        "depth": 0,
        "validated": null,
        "validation_note": "First step (no previous step to compare)"
      },
      {
        "expression": "2*x*sin(x) - integral(2*sin(x), x)",
        "latex": "2x\\sin(x) - \\int 2\\sin(x)\\,dx",
        "explanation": "For ∫2x cos(x) dx, apply integration by parts with u = 2x, dv = cos(x) dx. We get du = 2 dx, v = sin(x): 2x sin(x) - ∫2 sin(x) dx",
        "depth": 1,
        "validated": null,
        "validation_note": "Could not parse expression"
      },
      {
        "expression": "-x^2*cos(x) + 2*x*sin(x) + 2*cos(x)",
        "latex": "-x^2\\cos(x) + 2x\\sin(x) + 2\\cos(x)",
        "explanation": "Integrate the remaining term: ∫2 sin(x) dx = -2 cos(x). Combine all parts",
        "depth": 0,
        "validated": true,
        "validation_note": "Matches final solution ✓"
      }
    ]
  },
  "stats": {
    "elapsedMs": 15234.5,
    "backend": "remote-sympy",
    "cached": false
  }
}
```

### GET /registry

Get all variables stored in the current session.

**Response Example:**
```json
{
  "objects": {
    "A": {
      "name": "A",
      "type": "scalar",
      "value_text": "5",
      "latex": "5",
      "mathjson": 5,
      "metadata": {},
      "created_at": "2025-11-08T12:34:56",
      "updated_at": "2025-11-08T12:34:56"
    },
    "f": {
      "name": "f",
      "type": "function",
      "value_text": "Lambda(x, x**2 + 1)",
      "latex": "x \\mapsto x^{2} + 1",
      "mathjson": ["Function", ["Block", ["Add", ["Power", "x", 2], 1]], "x"],
      "metadata": {
        "arity": 1,
        "arguments": ["x"]
      },
      "created_at": "2025-11-08T12:35:10",
      "updated_at": "2025-11-08T12:35:10"
    }
  }
}
```

### DELETE /registry

Clear all variables from the session.

**Response:**
```json
{
  "status": "cleared"
}
```

### DELETE /registry/{variable_name}

Delete a specific variable from the session.

**Response:**
```json
{
  "status": "deleted",
  "variable": "A"
}
```

## Operations

### simplify

Algebraic simplification.

```json
{
  "op": "simplify",
  "expr": ["Add", ["Power", ["Add", "x", 1], 2], ["Negate", 1]]
}
// Result: ["Add", ["Power", "x", 2], ["Multiply", 2, "x"]]
// (x+1)² - 1 → x² + 2x
```

### expand

Polynomial expansion.

```json
{
  "op": "expand",
  "expr": ["Power", ["Add", "x", 1], 3]
}
// Result: x³ + 3x² + 3x + 1
```

### factor

Polynomial factorization.

```json
{
  "op": "factor",
  "expr": ["Add", ["Power", "x", 2], ["Negate", 1]]
}
// Result: (x-1)(x+1)
```

### differentiate

Symbolic differentiation.

```json
{
  "op": "differentiate",
  "expr": ["Sin", "x"],
  "vars": ["x"]
}
// Result: cos(x)
```

### integrate

Symbolic integration (indefinite or definite).

**Indefinite:**
```json
{
  "op": "integrate",
  "expr": ["Power", "x", 2],
  "vars": ["x"]
}
// Result: x³/3
```

**Definite:**
```json
{
  "op": "integrate",
  "expr": ["Power", "x", 2],
  "vars": ["x"],
  "assumptions": {
    "lower": 0,
    "upper": 1
  }
}
// Result: 1/3
```

### solve

Solve equations or systems.

```json
{
  "op": "solve",
  "expr": ["Equal", ["Add", ["Power", "x", 2], ["Negate", 4]], 0],
  "vars": ["x"]
}
// Result: [-2, 2]
```

### assign

Store variables or define functions.

**Variable Assignment:**
```json
{
  "op": "assign",
  "expr": ["Equal", "A", 5]
}
// Stores A = 5 in session registry
```

**Function Definition:**
```json
{
  "op": "assign",
  "expr": ["Equal", ["f", "x"], ["Add", ["Power", "x", 2], 1]]
}
// Stores f(x) = x² + 1
```

### evaluate

Self-contained calculus expressions (auto-detected).

```json
{
  "op": "evaluate",
  "expr": ["Integrate", ["Function", ["Block", ["Sin", "x"]], "x"], ["Limits", "x", "Nothing", "Nothing"]]
}
// Automatically processes ∫sin(x) dx
```

## Session Registry

The session registry provides **stateful variable storage** across requests.

### Type System

Variables are automatically classified:

| Type | Description | Example |
|------|-------------|---------|
| `scalar` | Numbers with no variables | `5`, `3.14`, `π` |
| `expression` | Expressions with variables | `x² + 2x`, `sin(x)` |
| `matrix` | 2D matrices | `[[1,2],[3,4]]` |
| `vector` | 1D vectors | Column or row vectors |
| `function` | Lambda functions | `f(x) = x² + 1` |
| `operator` | Differential operators | `D_x` |

### Variable Lookup

Stored variables are automatically substituted:

```javascript
// 1. Store a variable
await fetch('/cas', {
  method: 'POST',
  body: JSON.stringify({
    id: 'req-1',
    op: 'assign',
    expr: ['Equal', 'a', 5]
  })
});

// 2. Use it in an expression
await fetch('/cas', {
  method: 'POST',
  body: JSON.stringify({
    id: 'req-2',
    op: 'simplify',
    expr: ['Multiply', 'a', 'x']  // a is automatically replaced with 5
  })
});
// Result: 5x
```

### Function Evaluation

Stored functions can be called:

```javascript
// 1. Define function
await fetch('/cas', {
  method: 'POST',
  body: JSON.stringify({
    id: 'req-1',
    op: 'assign',
    expr: ['Equal', ['f', 'x'], ['Add', ['Power', 'x', 2], 1]]
  })
});

// 2. Call it
await fetch('/cas', {
  method: 'POST',
  body: JSON.stringify({
    id: 'req-2',
    op: 'simplify',
    expr: ['f', 2]  // Calls f(2)
  })
});
// Result: 5 (because f(2) = 2² + 1 = 5)
```

## AI Step-by-Step Solutions

AI-powered explanations use **Claude Sonnet 4.5** to generate pedagogical step-by-step solutions.

### Features

- **Anchored by SymPy**: Final answer is always mathematically correct
- **Narrative Flow**: Clear explanations with "Now we..." style
- **Intermediate Work**: Shows du, dv, substitutions explicitly
- **Validation**: Each step is mathematically verified
- **Grouped Substeps**: Related work (e.g., integration by parts) grouped together

### Currently Supported

- **Integration** (indefinite and definite)

### Coming Soon

- Simplification
- Expansion
- Factorization
- Equation solving

### Validation Status

Each step includes a `validated` field:

- `true` ✓: Step is mathematically verified
- `false` ⚠: Step could not be verified (possible hallucination)
- `null`: Step couldn't be parsed or is first/last step

**Last Step**: Always compared against SymPy's solution for final verification.

### Performance

- **Typical latency**: 10-20 seconds
- **Includes**: AI generation + mathematical validation
- **Optimization**: Future caching for common integrals

## Error Handling

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Malformed request JSON |
| `INVALID_MATHJSON` | MathJSON structure invalid |
| `OPERATION_NOT_SUPPORTED` | Unknown operation |
| `SECURITY_VIOLATION` | Expression contains disallowed operations |
| `TIMEOUT` | Operation exceeded time limit |
| `INTERNAL_ERROR` | Server error |

### Error Response

```json
{
  "id": "req-123",
  "ok": false,
  "error": {
    "code": "INVALID_MATHJSON",
    "message": "Unsupported MathJSON operation: Eval",
    "details": {
      "operation": "Eval",
      "allowed_operations": ["Add", "Multiply", ...]
    }
  }
}
```

### Client-Side Error Handling

```javascript
try {
  const response = await fetch('http://localhost:8000/cas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  const data = await response.json();

  if (!data.ok) {
    console.error(`Error ${data.error.code}: ${data.error.message}`);
    return;
  }

  // Process result
  console.log(data.result.latex);

} catch (error) {
  console.error('Network error:', error);
}
```

## Code Examples

### JavaScript/TypeScript

```typescript
class CASBridge {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async compute(operation: string, expression: any, options: any = {}): Promise<any> {
    const request = {
      id: `req-${Date.now()}`,
      op: operation,
      expr: expression,
      ...options,
      want: options.want || ['LaTeX', 'MathJSON', 'Text']
    };

    const response = await fetch(`${this.baseUrl}/cas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    const data = await response.json();

    if (!data.ok) {
      throw new Error(`CAS Error: ${data.error.message}`);
    }

    return data.result;
  }

  async getSteps(operation: string, expression: any, options: any = {}): Promise<any> {
    const request = {
      id: `req-${Date.now()}`,
      op: operation,
      expr: expression,
      ...options,
      want: ['Steps', 'LaTeX']
    };

    const response = await fetch(`${this.baseUrl}/steps`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    const data = await response.json();

    if (!data.ok) {
      throw new Error(`CAS Error: ${data.error.message}`);
    }

    return data.result;
  }

  async getRegistry(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/registry`);
    return response.json();
  }

  async clearRegistry(): Promise<void> {
    await fetch(`${this.baseUrl}/registry`, { method: 'DELETE' });
  }

  async deleteVariable(name: string): Promise<void> {
    await fetch(`${this.baseUrl}/registry/${name}`, { method: 'DELETE' });
  }
}

// Usage
const cas = new CASBridge();

// Basic computation
const result = await cas.compute('integrate', ['Power', 'x', 2], { vars: ['x'] });
console.log(result.latex);  // \frac{x^{3}}{3}

// Get step-by-step
const steps = await cas.getSteps('integrate', ['Multiply', ['Power', 'x', 2], ['Sin', 'x']], { vars: ['x'] });
steps.steps.forEach(step => {
  console.log(`${step.validated ? '✓' : '⚠'} ${step.explanation}`);
  console.log(`   ${step.latex}`);
});

// Variable assignment
await cas.compute('assign', ['Equal', 'a', 5]);
const registry = await cas.getRegistry();
console.log(registry.objects.a.value_text);  // "5"
```

### Python

```python
import requests
from typing import Any, Dict, List, Optional

class CASBridge:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def compute(
        self,
        operation: str,
        expression: Any,
        vars: Optional[List[str]] = None,
        assumptions: Optional[Dict] = None,
        want: List[str] = None
    ) -> Dict:
        if want is None:
            want = ["LaTeX", "MathJSON", "Text"]

        request = {
            "id": f"req-{int(time.time() * 1000)}",
            "op": operation,
            "expr": expression,
            "want": want
        }

        if vars:
            request["vars"] = vars
        if assumptions:
            request["assumptions"] = assumptions

        response = requests.post(
            f"{self.base_url}/cas",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()

        if not data["ok"]:
            raise Exception(f"CAS Error: {data['error']['message']}")

        return data["result"]

    def get_steps(
        self,
        operation: str,
        expression: Any,
        vars: Optional[List[str]] = None
    ) -> Dict:
        request = {
            "id": f"req-{int(time.time() * 1000)}",
            "op": operation,
            "expr": expression,
            "want": ["Steps", "LaTeX"]
        }

        if vars:
            request["vars"] = vars

        response = requests.post(
            f"{self.base_url}/steps",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()

        if not data["ok"]:
            raise Exception(f"CAS Error: {data['error']['message']}")

        return data["result"]

    def get_registry(self) -> Dict:
        response = requests.get(f"{self.base_url}/registry")
        return response.json()

    def clear_registry(self):
        requests.delete(f"{self.base_url}/registry")

    def delete_variable(self, name: str):
        requests.delete(f"{self.base_url}/registry/{name}")

# Usage
cas = CASBridge()

# Basic computation
result = cas.compute("integrate", ["Power", "x", 2], vars=["x"])
print(result["latex"])  # \frac{x^{3}}{3}

# Get step-by-step
steps = cas.get_steps(
    "integrate",
    ["Multiply", ["Power", "x", 2], ["Sin", "x"]],
    vars=["x"]
)

for step in steps["steps"]:
    badge = "✓" if step.get("validated") else "⚠"
    print(f"{badge} {step['explanation']}")
    print(f"   {step['latex']}")

# Variable assignment
cas.compute("assign", ["Equal", "a", 5])
registry = cas.get_registry()
print(registry["objects"]["a"]["value_text"])  # "5"
```

### React Example

```tsx
import React, { useState } from 'react';
import { CASBridge } from './cas-bridge';

const cas = new CASBridge('http://localhost:8000');

function IntegrationSolver() {
  const [expression, setExpression] = useState('x^2');
  const [result, setResult] = useState(null);
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleCompute = async () => {
    setLoading(true);
    try {
      // Parse expression to MathJSON (simplified example)
      const mathJSON = ['Power', 'x', 2];

      const result = await cas.compute('integrate', mathJSON, { vars: ['x'] });
      setResult(result);

      const stepsResult = await cas.getSteps('integrate', mathJSON, { vars: ['x'] });
      setSteps(stepsResult.steps);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={expression}
        onChange={(e) => setExpression(e.target.value)}
        placeholder="Enter expression"
      />
      <button onClick={handleCompute} disabled={loading}>
        {loading ? 'Computing...' : 'Integrate'}
      </button>

      {result && (
        <div>
          <h3>Result:</h3>
          <div dangerouslySetInnerHTML={{ __html: `$$${result.latex}$$` }} />
        </div>
      )}

      {steps.length > 0 && (
        <div>
          <h3>Step-by-Step Solution:</h3>
          {steps.map((step, i) => (
            <div key={i} style={{ marginLeft: step.depth * 20 }}>
              <p>
                {step.validated ? '✓' : '⚠'} {step.explanation}
              </p>
              <div dangerouslySetInnerHTML={{ __html: `$$${step.latex}$$` }} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Best Practices

### 1. Request IDs

Always use unique request IDs for tracking and debugging:

```javascript
const requestId = `${appName}-${Date.now()}-${Math.random().toString(36)}`;
```

### 2. Error Handling

Always check the `ok` field before accessing `result`:

```javascript
if (!data.ok) {
  // Handle error
  console.error(data.error);
  return;
}
```

### 3. Session Management

If using the registry across multiple users:
- Clear the registry between user sessions
- Or implement user-specific session IDs (future feature)

### 4. Step-by-Step Performance

The `/steps` endpoint is slower (10-20s) than `/cas` (<1s):
- Use `/cas` for immediate results
- Use `/steps` only when user explicitly requests explanations
- Consider caching common integrals

### 5. MathJSON Construction

Validate MathJSON before sending:

```javascript
function validateMathJSON(expr) {
  // Check structure
  if (Array.isArray(expr) && expr.length === 0) {
    throw new Error('Empty array');
  }
  // Check allowed operations
  if (Array.isArray(expr) && !ALLOWED_OPS.includes(expr[0])) {
    throw new Error(`Unsupported operation: ${expr[0]}`);
  }
}
```

### 6. Timeout Handling

For long-running operations, implement client-side timeout:

```javascript
const TIMEOUT = 30000; // 30 seconds

const fetchWithTimeout = (url, options) => {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), TIMEOUT)
    )
  ]);
};
```

### 7. Retry Logic

Implement exponential backoff for network errors:

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fetch(url, options);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 2 ** i * 1000));
    }
  }
}
```

## Support

For integration issues or questions:
- GitHub Issues: [https://github.com/SDNel/Claude/issues](https://github.com/SDNel/Claude/issues)
- API Documentation: http://localhost:8000/docs
- Source Code: [https://github.com/SDNel/Claude/tree/main/cas-bridge](https://github.com/SDNel/Claude/tree/main/cas-bridge)

---

**Happy integrating! 🚀**
