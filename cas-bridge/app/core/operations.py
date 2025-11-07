"""Core mathematical operations using SymPy."""

from typing import Any, Optional

from app.api.models import CasRequest, CasResult, OutputFormat
from app.core.mathjson_parser import mathjson_to_sympy
from app.security.allowlist import validate_mathjson


async def execute_operation(request: CasRequest, include_steps: bool = False) -> CasResult:
    """
    Execute a mathematical operation on the given expression.

    Args:
        request: CAS request with operation and expression
        include_steps: Whether to include step-by-step explanation

    Returns:
        CasResult with output in requested formats

    Raises:
        ValueError: If the operation or expression is invalid
        TimeoutError: If the operation exceeds timeout
    """
    # Validate expression against allow-list
    validate_mathjson(request.expr)

    # Convert MathJSON to SymPy
    sympy_expr = mathjson_to_sympy(request.expr)

    # Execute operation based on type
    result_expr = None
    steps = None

    if request.op.value == "simplify":
        result_expr = _simplify(sympy_expr)
    elif request.op.value == "expand":
        result_expr = _expand(sympy_expr)
    elif request.op.value == "factor":
        result_expr = _factor(sympy_expr)
    elif request.op.value == "differentiate":
        result_expr = _differentiate(sympy_expr, request.vars)
    elif request.op.value == "integrate":
        result_expr = _integrate(sympy_expr, request.vars, request.assumptions, include_steps)
        if include_steps:
            steps = result_expr.get("steps")
            result_expr = result_expr.get("result")
    elif request.op.value == "limit":
        result_expr = _limit(sympy_expr, request.vars, request.assumptions)
    elif request.op.value == "series":
        result_expr = _series(sympy_expr, request.vars, request.assumptions)
    elif request.op.value == "solve":
        result_expr = _solve(sympy_expr, request.vars)
    elif request.op.value == "linsolve":
        result_expr = _linsolve(sympy_expr)
    elif request.op.value == "rref":
        result_expr = _rref(sympy_expr)
    elif request.op.value == "eigen":
        result_expr = _eigen(sympy_expr)
    elif request.op.value == "evaluate":
        result_expr = _evaluate(sympy_expr)
    else:
        raise ValueError(f"Unsupported operation: {request.op}")

    # Format output
    result = CasResult()

    if request.want:
        for fmt in request.want:
            if fmt == OutputFormat.MATHJSON:
                result.mathjson = _to_mathjson(result_expr)
            elif fmt == OutputFormat.LATEX:
                result.latex = _to_latex(result_expr)
            elif fmt == OutputFormat.TEXT:
                result.text = _to_text(result_expr)
            elif fmt == OutputFormat.STEPS and include_steps:
                result.steps = steps

    return result


# Operation implementations

import sympy as sp


def _simplify(expr: Any) -> Any:
    """Simplify expression."""
    return sp.simplify(expr)


def _expand(expr: Any) -> Any:
    """Expand expression."""
    return sp.expand(expr)


def _factor(expr: Any) -> Any:
    """Factor expression."""
    return sp.factor(expr)


def _differentiate(expr: Any, vars: Optional[list]) -> Any:
    """Differentiate expression."""
    if not vars or len(vars) == 0:
        raise ValueError("differentiate requires at least one variable")

    # Convert var from string to symbol if needed
    var = sp.Symbol(vars[0]) if isinstance(vars[0], str) else vars[0]

    # Differentiate
    return sp.diff(expr, var)


def _integrate(expr: Any, vars: Optional[list], assumptions: Optional[dict], steps: bool) -> Any:
    """Integrate expression."""
    if not vars or len(vars) == 0:
        raise ValueError("integrate requires at least one variable")

    # Convert var from string to symbol if needed
    var = sp.Symbol(vars[0]) if isinstance(vars[0], str) else vars[0]

    # Check if it's definite or indefinite
    if assumptions and ("bounds" in assumptions or ("lower" in assumptions and "upper" in assumptions)):
        # Definite integral
        if "bounds" in assumptions:
            bounds = assumptions["bounds"]
            lower, upper = bounds[0], bounds[1]
        else:
            lower = assumptions["lower"]
            upper = assumptions["upper"]
        result = sp.integrate(expr, (var, lower, upper))
    else:
        # Indefinite integral
        result = sp.integrate(expr, var)

    if steps:
        # For now, return result without steps (steps require additional library)
        return {"result": result, "steps": None}

    return result


def _limit(expr: Any, vars: Optional[list], assumptions: Optional[dict]) -> Any:
    """Compute limit."""
    if not vars or len(vars) == 0:
        raise ValueError("limit requires at least one variable")

    if not assumptions or "point" not in assumptions:
        raise ValueError("limit requires a 'point' in assumptions")

    # Convert var from string to symbol if needed
    var = sp.Symbol(vars[0]) if isinstance(vars[0], str) else vars[0]
    point = assumptions["point"]

    # Handle direction if specified
    direction = assumptions.get("direction", "+-")  # Default: both sides

    # Map user-friendly direction names to SymPy's format
    direction_map = {
        "two-sided": "+-",
        "from-left": "-",
        "from-right": "+",
        "+-": "+-",
        "-": "-",
        "+": "+"
    }

    direction = direction_map.get(direction, "+-")

    return sp.limit(expr, var, point, dir=direction)


def _series(expr: Any, vars: Optional[list], assumptions: Optional[dict]) -> Any:
    """Compute series expansion."""
    if not vars or len(vars) == 0:
        raise ValueError("series requires at least one variable")

    # Convert var from string to symbol if needed
    var = sp.Symbol(vars[0]) if isinstance(vars[0], str) else vars[0]

    # Get point and order from assumptions
    point = assumptions.get("point", 0) if assumptions else 0
    order = assumptions.get("order", 6) if assumptions else 6

    # Compute series expansion
    result = sp.series(expr, var, point, order)

    # Remove O(...) term for cleaner output
    return result.removeO()


def _solve(expr: Any, vars: Optional[list]) -> Any:
    """Solve equation."""
    if not vars or len(vars) == 0:
        # Try to solve for all free symbols
        result = sp.solve(expr)
    else:
        # Convert var from string to symbol if needed
        var = sp.Symbol(vars[0]) if isinstance(vars[0], str) else vars[0]
        result = sp.solve(expr, var)

    return result


def _linsolve(expr: Any) -> Any:
    """Solve linear system."""
    # expr should be a dict with "A" and "b" keys
    if not isinstance(expr, dict) or "A" not in expr or "b" not in expr:
        raise ValueError("linsolve requires a dict with 'A' (matrix) and 'b' (vector)")

    A = expr["A"]
    b = expr["b"]

    # Solve Ax = b
    # linsolve returns a FiniteSet of solutions
    result = sp.linsolve((A, b))

    # Convert to list for easier handling
    if result:
        return list(result)[0] if len(result) == 1 else list(result)
    return result


def _rref(expr: Any) -> Any:
    """Compute reduced row echelon form."""
    if not isinstance(expr, sp.Matrix):
        raise ValueError("rref requires a matrix")

    # rref() returns (reduced_matrix, pivot_columns)
    reduced, pivots = expr.rref()

    # Return just the reduced matrix
    return reduced


def _eigen(expr: Any) -> Any:
    """Compute eigenvalues."""
    if not isinstance(expr, sp.Matrix):
        raise ValueError("eigen requires a matrix")

    # eigenvals() returns a dict {eigenvalue: multiplicity}
    eigenvals = expr.eigenvals()

    # Convert to list of eigenvalues
    result = []
    for val, mult in eigenvals.items():
        for _ in range(mult):
            result.append(val)

    return result


def _evaluate(expr: Any) -> Any:
    """
    Evaluate a self-contained expression.

    Added 2025-11-07 to support self-contained calculus expressions from Compute Engine.

    This operation doesn't apply any external operation - it evaluates the expression
    as-is. This is useful when the MathJSON already contains operations like D, Integrate,
    or Limit that were parsed from MathLive input.

    Examples:
        ["D", ["Sin", "x"], "x"] -> cos(x)
        ["Integrate", ...] -> evaluated integral
        ["Limit", ...] -> evaluated limit

    The expression has already been converted to SymPy by mathjson_to_sympy(),
    which handles D, Integrate, Limit, etc. and returns the computed result.
    So we just need to simplify/evaluate it.
    """
    # The mathjson_to_sympy conversion already handled the operations
    # (D -> sp.diff, Integrate -> sp.integrate, etc.)
    # Now we just simplify the result
    return sp.simplify(expr)


# Output formatters

from app.core.mathjson_parser import sympy_to_mathjson


def _to_mathjson(expr: Any) -> Any:
    """Convert SymPy expression to MathJSON."""
    return sympy_to_mathjson(expr)


def _to_latex(expr: Any) -> str:
    """Convert SymPy expression to LaTeX."""
    return sp.latex(expr)


def _to_text(expr: Any) -> str:
    """Convert SymPy expression to text."""
    return str(expr)
