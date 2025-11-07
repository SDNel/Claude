# Phase 1b Research Report: MathLive Derivative Input

**Date:** 2025-11-07
**Researcher:** Claude
**Status:** ⚠️ Partially Complete - Test Verification Needed

---

## Executive Summary

Research into MathLive and Compute Engine has revealed **critical insights about derivative notation** that explain why `\frac{d}{dx}` notation fails in our application. This report summarizes findings and proposes solutions.

## 🔍 Key Findings

### Finding 1: The `\frac{d}{dx}` Ambiguity Problem

**Problem:** The Leibniz notation `\frac{d}{dx}` is **fundamentally ambiguous** in LaTeX:
- Could be interpreted as: `d ÷ (d × x)` (literal division with variables)
- Could be interpreted as: "derivative with respect to x" (calculus operator)

**Why It Fails:**
- Compute Engine has **no way to distinguish** between `d` as a variable vs. `d` as the differential operator
- Without semantic context, the parser defaults to treating `d` and `x` as variables
- Result: `["Multiply", ["Divide", "d", ["Multiply", "d", "x"]], ["Sin", "x"]]` ❌

**Source:** GitHub Issue #500 on arnog/mathlive explicitly discusses this ambiguity

### Finding 2: Correct Derivative Operations in MathJSON

Compute Engine provides **three derivative-related operations**:

| Operation | Purpose | When to Use |
|-----------|---------|-------------|
| `D` | Calculate symbolic derivative | **Primary operation** for computing derivatives |
| `ND` | Calculate numerical derivative | Approximation when symbolic fails |
| `Derivative` | Represent derivative symbolically | **Not for computation** - abstract operator only |

**Format:** `["D", expression, variable]`

**Examples:**
- Simple: `["D", ["Sin", "x"], "x"]` → derivative of sin(x) with respect to x
- Multiple vars: `["D", ["Sin", "x"], "x", "y"]` → partial derivatives
- Higher order: `["D", ["Sin", "x"], "x", "x"]` → second derivative (repeat variable)

### Finding 3: Alternative Derivative Notations

**Prime Notation (Lagrange):**
- LaTeX: `f'(x)` or `f^{\prime}(x)`
- Common in high school for simple derivatives
- Example from research: `\sin^{-1}\prime x` → some form of derivative MathJSON
- **Status:** Unknown what exact MathJSON this produces (needs testing)

**Partial Derivative Notation:**
- LaTeX: `\frac{\partial}{\partial x}`
- Uses `\partial` symbol instead of `d`
- **Status:** Unknown if Compute Engine handles this differently

**Newton's Dot Notation:**
- LaTeX: `\dot{x}` (single dot), `\ddot{x}` (double dot)
- Rare in high school context

### Finding 4: MathLive Virtual Keyboard Structure

**Default Keyboards:**
- `numeric` - Numbers and basic operations
- `symbols` - Where calculus operations would be
- `alphabetic` - Letters
- `greek` - Greek letters

**No default "calculus" keyboard** exists. The "Functions" keyboard was merged into "Symbols" in an earlier version.

**Critical Question:** What buttons exist on the Symbols keyboard for entering derivatives?

## ⚠️ Critical Unknowns (Require Testing)

### Unknown 1: Prime Notation MathJSON Output

**Question:** When a user types `f'(x)` in MathLive, what MathJSON does Compute Engine produce?

**Expected Possibilities:**
- `["D", "f", "x"]` (ideal)
- `["Derivative", "f", "x"]` (symbolic only, won't compute)
- Something with prime as a modifier: `["f_prime", "x"]`
- Power notation: `["Power", "f", "Prime"]` (would be wrong)

**Why It Matters:** If prime notation produces proper `D` function, we should recommend it to students.

### Unknown 2: Partial Derivative Parsing

**Question:** Does `\frac{\partial}{\partial x}` get parsed differently than `\frac{d}{dx}`?

**Hypothesis:** Might work because `\partial` is a distinct symbol, not an ambiguous letter.

### Unknown 3: MathLive Insert Menu

**Question:** Does MathLive have an "Insert → Derivative" menu option that produces proper MathJSON?

**Why It Matters:** If there's a template, students could use it without knowing LaTeX.

### Unknown 4: Virtual Keyboard Derivative Button

**Question:** Is there a dedicated button on the virtual keyboard for derivatives?

**Why It Matters:** Touch-friendly input for mobile/tablet users.

## 🔬 Test File Created

**Location:** `/home/user/Claude/cas-bridge/ui/derivative-test.html`

**Purpose:** Systematically test 13 different derivative notations to determine:
1. Which notation(s) produce proper `D` function in MathJSON
2. Which notations fail (parse as division)
3. What the exact MathJSON structure is for each

**Test Cases Include:**
- Prime notation: `f'(x)`, `f^{\prime}(x)`, `f''(x)`
- Leibniz notation: `\frac{d}{dx}`, `\frac{dy}{dx}`, `\frac{d^2y}{dx^2}`
- Partial derivatives: `\frac{\partial f}{\partial x}`
- Function derivatives: `\sin'(x)`
- Newton's notation: `\dot{x}`

**To Run:**
1. Open `http://localhost:8080/derivative-test.html` in browser
2. Tests run automatically on page load
3. Green boxes = success (proper derivative MathJSON)
4. Red boxes = failure (parsed as division)

## 📋 Backend Implications

### Issue 1: Allowlist Missing Operations

**Current allowlist has:**
```python
"Derivative",  # Has this
"Integral",    # Has this (but Compute Engine uses "Integrate")
```

**Needs to add:**
```python
"D",           # PRIMARY derivative operation
"ND",          # Numerical derivative
"Integrate",   # Actual integration operation name
"Limits",      # For definite integrals and limits
"Function",    # Structural operation in Compute Engine
"Block",       # Structural operation
"Tuple",       # Used in results
"Limit",       # For limit operations
```

### Issue 2: Parser Missing Handlers

**Current parser in `mathjson_parser.py` only handles ~20 operations.**

**Needs to add:**
- `D` function handler → `sp.diff(expr, var)`
- `Integrate` function handler (separate from old "Integral")
- `Limits` structure parser (extract bounds for definite integrals)
- `Function` and `Block` structural handlers
- `Tuple` handler for multiple return values

### Issue 3: Architecture Can't Handle Nested Calculus

**Problem:** Current API design assumes:
- User selects operation from dropdown (e.g., "differentiate")
- Operation applied to simple expression in `expr` field

**But real calculus involves nested operations:**
- FTC: `d/dx(∫ₐˣ sin(t) dt)` - derivative OF an integral
- Chain rule: `d/dx(sin(x²))` - derivative of composite function
- Integration by parts: `∫ u dv` where u and dv are themselves expressions

**Current Request Format:**
```json
{
  "op": "differentiate",
  "expr": ["Sin", "x"],
  "vars": ["x"]
}
```

**Problem:** Where do nested operations go? The `expr` should CONTAIN the derivative, not have it applied externally.

**Proposed Solution:** Add `"evaluate"` operation:
```json
{
  "op": "evaluate",
  "expr": ["D", ["Sin", "x"], "x"]  // Expression CONTAINS the operation
}
```

This allows arbitrary nesting and composition.

## 📊 Research Methodology

**Data Sources:**
1. CortexJS Compute Engine documentation (attempted access - blocked by 403)
2. MathLive GitHub issues (specifically #500 about MathJSON ambiguity)
3. Web search results about MathJSON format
4. Official changelog and release notes
5. Community discussions and Stack Overflow posts

**Research Constraints:**
- Primary documentation at cortexjs.io blocked (403 Forbidden errors)
- Had to rely on secondary sources and GitHub issues
- Could not access detailed API reference for D function
- Test file created but not yet executed

## ✅ Recommendations

### Immediate Actions:

1. **Run derivative-test.html** to determine which notation(s) work
2. **Based on test results:**
   - If prime notation works: Document it as the recommended method
   - If partial derivatives work: Add support and document
   - If nothing works: May need to add semantic hints or custom parsing

### Backend Updates Required:

1. **Update allowlist** (`app/security/allowlist.py`):
   - Add "D", "ND", "Integrate", "Limits", "Function", "Block", "Tuple", "Limit"

2. **Enhance parser** (`app/core/mathjson_parser.py`):
   - Add D operation handler
   - Add Limits structure parser
   - Add Function/Block structural handlers
   - Handle nested operations properly

3. **Add evaluate operation** (`app/core/operations.py`):
   - New operation type that evaluates self-contained calculus expressions
   - Don't apply external operation, just evaluate what's in expr

4. **Extract bounds intelligently**:
   - Check for Limits structure within Integrate operations
   - Parse bounds from nested structure, not just assumptions dict

### Documentation for Students:

Once we determine which notation works:
- Create simple guide: "How to Enter Derivatives"
- Show examples with virtual keyboard
- Provide visual templates if available
- Explain which notation to use when

## 🚧 Next Steps

**Phase 1b Completion Requires:**
1. ✅ Research completed (documented in this report)
2. ⏳ **Run derivative-test.html and analyze results**
3. ⏳ Document which notation(s) produce proper D function
4. ⏳ Update recommendation based on findings

**After Phase 1b:**
- Proceed to Phase 2: Update allowlist
- Proceed to Phase 3: Enhance parser
- Proceed to Phase 4: Add evaluate operation
- Continue through Phase 8: Comprehensive testing

---

## Appendix: Search Results Summary

**Key Discoveries:**
- Compute Engine can parse LaTeX to MathJSON
- D function exists for computing derivatives
- Derivative function exists but is symbolic only (not computational)
- Prime notation is mentioned in examples but exact output unknown
- `\frac{d}{dx}` ambiguity is a known issue in MathJSON parsing

**Documentation Gaps:**
- Exact D function syntax not found in accessible docs
- Prime notation MathJSON output not documented in search results
- Virtual keyboard button inventory not available

**Testing Required:**
- All 13 derivative notations in test file
- Virtual keyboard exploration (manual testing by user)
- Insert menu exploration (if it exists)

---

**Status:** Report complete, awaiting test results to finalize recommendations.
