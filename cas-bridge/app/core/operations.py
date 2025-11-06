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
        result_expr = _linsolve(request.expr)
    elif request.op.value == "rref":
        result_expr = _rref(request.expr)
    elif request.op.value == "eigen":
        result_expr = _eigen(request.expr)
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


# Operation implementations (stubs - to be implemented)


def _simplify(expr: Any) -> Any:
    """Simplify expression."""
    # TODO: Implement using sympy.simplify()
    raise NotImplementedError("simplify not yet implemented")


def _expand(expr: Any) -> Any:
    """Expand expression."""
    # TODO: Implement using sympy.expand()
    raise NotImplementedError("expand not yet implemented")


def _factor(expr: Any) -> Any:
    """Factor expression."""
    # TODO: Implement using sympy.factor()
    raise NotImplementedError("factor not yet implemented")


def _differentiate(expr: Any, vars: Optional[list]) -> Any:
    """Differentiate expression."""
    # TODO: Implement using sympy.diff()
    raise NotImplementedError("differentiate not yet implemented")


def _integrate(expr: Any, vars: Optional[list], assumptions: Optional[dict], steps: bool) -> Any:
    """Integrate expression."""
    # TODO: Implement using sympy.integrate() and integral_steps()
    raise NotImplementedError("integrate not yet implemented")


def _limit(expr: Any, vars: Optional[list], assumptions: Optional[dict]) -> Any:
    """Compute limit."""
    # TODO: Implement using sympy.limit()
    raise NotImplementedError("limit not yet implemented")


def _series(expr: Any, vars: Optional[list], assumptions: Optional[dict]) -> Any:
    """Compute series expansion."""
    # TODO: Implement using sympy.series()
    raise NotImplementedError("series not yet implemented")


def _solve(expr: Any, vars: Optional[list]) -> Any:
    """Solve equation."""
    # TODO: Implement using sympy.solve()
    raise NotImplementedError("solve not yet implemented")


def _linsolve(expr: Any) -> Any:
    """Solve linear system."""
    # TODO: Implement using sympy.linsolve()
    raise NotImplementedError("linsolve not yet implemented")


def _rref(expr: Any) -> Any:
    """Compute reduced row echelon form."""
    # TODO: Implement using sympy Matrix.rref()
    raise NotImplementedError("rref not yet implemented")


def _eigen(expr: Any) -> Any:
    """Compute eigenvalues."""
    # TODO: Implement using sympy Matrix.eigenvals()
    raise NotImplementedError("eigen not yet implemented")


# Output formatters (stubs - to be implemented)


def _to_mathjson(expr: Any) -> Any:
    """Convert SymPy expression to MathJSON."""
    # TODO: Implement SymPy → MathJSON conversion
    raise NotImplementedError("mathjson formatter not yet implemented")


def _to_latex(expr: Any) -> str:
    """Convert SymPy expression to LaTeX."""
    # TODO: Implement using sympy.latex()
    raise NotImplementedError("latex formatter not yet implemented")


def _to_text(expr: Any) -> str:
    """Convert SymPy expression to text."""
    # TODO: Implement using str() or sympy.pretty()
    raise NotImplementedError("text formatter not yet implemented")
