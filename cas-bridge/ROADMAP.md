# CAS Bridge - Roadmap & Future Enhancements

This document tracks planned features, known issues, and enhancement ideas for future development.

---

## 🔴 High Priority

### Matrix Entry UX Improvement
**Status:** Planned
**Priority:** High
**Created:** 2025-11-08

**Problem:**
- MathLive's built-in matrix entry is limited to 5×5 grid selector
- Not scalable for larger matrices (6×6, 10×10, etc.)
- Forces students to use Mathematica-style `[[1,2],[3,4]]` syntax for larger matrices
- Clunky UX compared to GeoGebra/Desmos

**Proposed Solution:**
Implement GeoGebra-style modal interface:
1. Click "Matrix" button → Modal appears
2. Specify dimensions (rows × columns)
3. Choose type (empty, identity, zero)
4. Template inserted into math field with placeholders
5. Tab/Arrow navigation between cells

**Implementation Plan:**
- **Phase 1** (Quick Win): External UI button with modal
  - Add button next to math input field
  - JavaScript modal for dimension input
  - Generate LaTeX template programmatically
  - Insert using MathLive API

- **Phase 2** (Long-term): Integrate into MathLive keyboard
  - Customize virtual keyboard
  - Replace/augment built-in matrix button
  - Unified experience

**Additional Features:**
- Row/column vector shortcuts
- Bracket style options (parentheses, square, determinant)
- Smart presets (identity, diagonal, zero matrices)
- Compatible matrix suggestions (for multiplication)

**Files to Modify:**
- `ui/index.html` - Add button and modal UI
- `ui/index.html` - JavaScript for template generation
- Future: MathLive keyboard customization

---

## 🟡 Medium Priority

### Variable Lookup in Expressions
**Status:** Planned
**Priority:** Medium
**Created:** 2025-11-08

**Description:**
After assigning `A = 5`, typing `A + 3` should look up the stored value and compute `8`.

**Current State:**
- Variables are stored in session registry
- Not yet retrieved when used in subsequent expressions

**Implementation:**
- Modify `mathjson_to_sympy()` to check registry for symbols
- Substitute stored values before computation
- Handle undefined variables gracefully

### Variable Registry UI
**Status:** Planned
**Priority:** Medium
**Created:** 2025-11-08

**Description:**
Display stored variables in sidebar or panel.

**Features:**
- List all assigned variables with values
- Clear individual variables
- Clear all variables
- Edit/update variables
- Export/import session

**Design Considerations:**
- Collapsible sidebar (like GeoGebra)
- Show variable name, type, value preview
- Click to insert into expression

### Expression History
**Status:** Planned
**Priority:** Medium
**Created:** 2025-11-08

**Description:**
Track previous calculations with ability to recall/reuse.

**Features:**
- Show recent expressions and results
- Click to copy/reuse
- Save history to local storage
- Clear history

---

## 🟢 Low Priority / Nice-to-Have

### Partial Derivatives with Specific Variables
**Status:** Deferred
**Priority:** Low
**Created:** 2025-11-08

**Description:**
Support `∂/∂y` and `∂/∂xᵢ` for functions of multiple variables.

**Current State:**
- `∂/∂x f(x,y)` works (infers variable)
- Cannot explicitly specify which variable for partial derivative

**Notes:**
- May require additional notation detection
- Low priority - current auto-detection works for most cases

### Step-by-Step Solutions
**Status:** Deferred
**Priority:** Low

**Description:**
Show detailed solution steps for calculus operations, solving equations, etc.

**Notes:**
- Backend already has `steps` parameter
- Need to implement step generation logic
- UI for displaying steps

### Plot/Graph Support
**Status:** Idea
**Priority:** Low

**Description:**
Add ability to plot functions and visualize results.

**Considerations:**
- Integration with plotting library (Plotly, D3)
- 2D function plots
- 3D surface plots
- Parametric plots

---

## ✅ Completed

### Assignment Detection & Variable Registry
**Status:** ✅ Completed
**Completed:** 2025-11-08

- Distinguish `A = 5` (assignment) from `x² = 4` (equation)
- Classify function definitions `f(x) = x²`
- Store variables in session registry
- Handle matrix assignments

### Partial Derivative Support (∂/∂x)
**Status:** ✅ Completed
**Completed:** 2025-11-08

- Detect `∂/∂x` from virtual keyboard
- Pattern detection and conversion
- Auto-infer variable when ambiguous

### Simplified UI (Auto-Operation Detection)
**Status:** ✅ Completed
**Completed:** 2025-11-08

- Removed operation dropdown
- Auto-detect: derivative, integral, equation, assignment, etc.
- Single "Evaluate" button

### Derivative Notation Support (d/dx)
**Status:** ✅ Completed
**Completed:** 2025-11-07

- Support `d/dx` from both virtual and real keyboard
- Handle `f'(x)` prime notation
- Support undefined functions

---

## 📋 Known Issues

### None currently tracked

---

## 💡 Ideas / Future Exploration

- **LaTeX Export:** Export results as LaTeX for papers/documents
- **Session Persistence:** Save session state to cloud/account
- **Collaboration:** Share sessions with others
- **Mobile Optimization:** Improve mobile/tablet experience
- **Keyboard Shortcuts:** Power-user shortcuts for common operations
- **Dark Mode:** Theme support
- **Multiple CAS Backends:** Switch between SymPy, Maxima, SageMath
- **Unit Support:** Handle physical units (meters, seconds, etc.)
- **Custom Functions:** User-defined functions beyond Lambda

---

*Last Updated: 2025-11-08*
