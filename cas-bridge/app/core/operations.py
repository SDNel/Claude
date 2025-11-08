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

    # Execute operation based on type
    result_expr = None
    steps = None
    sympy_expr = None

    # Special handling for assign - don't convert entire expression to SymPy
    # (matrices in equations don't work well in SymPy)
    if request.op.value == "assign":
        result_expr = _assign(request.expr)
    else:
        # Convert MathJSON to SymPy for all other operations
        sympy_expr = mathjson_to_sympy(request.expr)

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
    # Apply simplification
    expr = sp.simplify(expr)

    # For expressions that don't simplify symbolically (like e^(π*i)),
    # evaluate numerically then convert back to exact form
    # This handles Euler's formula: e^(π*i) → -1
    try:
        # Check if expression has imaginary unit or complex exponentials
        if expr.has(sp.I) or expr.has(sp.exp):
            # Evaluate to high precision
            numerical = expr.evalf(30)
            # Try to find exact symbolic form
            exact = sp.nsimplify(numerical, rational=False, tolerance=1e-10)
            # Only use exact form if it's simpler
            if len(str(exact)) < len(str(expr)):
                return exact
    except:
        pass

    return expr


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
        # Extract step-by-step solution using SymPy's integral_steps
        step_list = _extract_integration_steps(expr, var)
        return {"result": result, "steps": step_list}

    return result


def _extract_integration_steps(expr: Any, var: Any) -> list:
    """
    Extract step-by-step integration using SymPy's manualintegrate.

    Returns a list of steps with explanations in the format:
    [
        {
            "expression": "x^3/3",
            "latex": "\\frac{x^3}{3}",
            "explanation": "Apply power rule: ∫x^n dx = x^(n+1)/(n+1)"
        },
        ...
    ]
    """
    try:
        from sympy.integrals.manualintegrate import integral_steps
        from sympy import latex

        # Get the step tree
        step_obj = integral_steps(expr, var)

        # Recursively extract steps
        def extract_steps_recursive(step_obj, depth=0):
            steps = []
            rule_name = type(step_obj).__name__
            result = step_obj.eval()

            # Create step with explanation
            step = {
                'expression': str(result),
                'latex': latex(result),
                'depth': depth,
                'explanation': _get_integration_rule_explanation(step_obj, rule_name)
            }
            steps.append(step)

            # Recursively extract substeps
            for attr in ['v_step', 'second_step', 'substep', 'rewritten_step']:
                if hasattr(step_obj, attr):
                    substep_obj = getattr(step_obj, attr)
                    if substep_obj:
                        substeps = extract_steps_recursive(substep_obj, depth + 1)
                        steps.extend(substeps)

            return steps

        return extract_steps_recursive(step_obj)

    except Exception as e:
        # If manualintegrate fails, return a simple message
        return [{
            'expression': str(sp.integrate(expr, var)),
            'latex': sp.latex(sp.integrate(expr, var)),
            'depth': 0,
            'explanation': f'Integration computed (step-by-step unavailable: {str(e)})'
        }]


def _get_integration_rule_explanation(step_obj, rule_name: str) -> str:
    """Generate human-readable explanation for integration rule."""
    # Use conditional logic instead of dictionary to avoid evaluating f-strings prematurely
    if rule_name == 'PowerRule':
        return f"Apply power rule: ∫x^n dx = x^(n+1)/(n+1) + C"
    elif rule_name == 'ConstantRule':
        return f"Constant rule: ∫k dx = kx + C"
    elif rule_name == 'ConstantTimesRule':
        return f"Constant multiple rule: ∫k·f(x) dx = k·∫f(x) dx"
    elif rule_name == 'AddRule':
        return f"Sum rule: ∫(f + g) dx = ∫f dx + ∫g dx"
    elif rule_name == 'SinRule':
        return f"Integrate sine: ∫sin(x) dx = -cos(x) + C"
    elif rule_name == 'CosRule':
        return f"Integrate cosine: ∫cos(x) dx = sin(x) + C"
    elif rule_name == 'ExpRule':
        return f"Integrate exponential: ∫e^x dx = e^x + C"
    elif rule_name == 'LogRule':
        return f"Integrate logarithm: ∫ln(x) dx = x·ln(x) - x + C"
    elif rule_name == 'ArctanRule':
        return f"Integrate 1/(x²+1): ∫1/(x²+1) dx = arctan(x) + C"
    elif rule_name == 'PartsRule':
        # Only access .u and .dv if it's actually a PartsRule
        return f"Integration by parts: u = {step_obj.u}, dv = {step_obj.dv}"
    elif rule_name == 'URule':
        return f"U-substitution"
    elif rule_name == 'RewriteRule':
        return f"Rewrite expression to a more integrable form"
    else:
        return f"Apply {rule_name}"



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
    """
    Solve linear system.

    Supports two formats:
    1. Matrix form: {"A": matrix, "b": vector} for Ax = b
    2. List of equations: [eq1, eq2, ...] for system of equations
    """
    # Format 1: Dict with "A" and "b" keys (existing format)
    if isinstance(expr, dict) and "A" in expr and "b" in expr:
        A = expr["A"]
        b = expr["b"]

        # Solve Ax = b
        result = sp.linsolve((A, b))

        # Convert to list for easier handling
        if result:
            return list(result)[0] if len(result) == 1 else list(result)
        return result

    # Format 2: List of equations (from ["List", eq1, eq2, ...])
    # expr should be a list/tuple of Equality objects
    if isinstance(expr, (list, tuple)):
        equations = [eq for eq in expr if isinstance(eq, sp.Equality)]

        if len(equations) == 0:
            raise ValueError("linsolve requires at least one equation")

        # Extract all variables from equations
        variables = set()
        for eq in equations:
            variables.update(eq.free_symbols)

        # Solve system
        result = sp.solve(equations, variables)

        return result

    raise ValueError("linsolve requires a dict with 'A' and 'b' or a list of equations")


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


def _assign(mathjson_expr: Any) -> Any:
    """
    Handle variable and function assignments.

    Added 2025-11-08 to support variable registry.

    Assignments are expressions with Equal where the left-hand side is:
    - A simple identifier: A = [[1,2],[3,4]]
    - A function definition: f(x) = x² + 1

    Args:
        mathjson_expr: The MathJSON expression ["Equal", lhs, rhs]

    Returns:
        The assigned value (right-hand side) as a SymPy expression

    Examples:
        A = 5 → stores A=5, returns 5
        f(x) = x² → stores f as function, returns x²
        M = [[1,2],[3,4]] → stores M as Matrix, returns Matrix
    """
    from app.core.session import assign_variable

    # Validate structure
    if not isinstance(mathjson_expr, list) or mathjson_expr[0] != "Equal":
        raise ValueError("Assign operation requires an equation with =")

    if len(mathjson_expr) < 3:
        raise ValueError("Invalid assignment structure - missing lhs or rhs")

    lhs_mathjson = mathjson_expr[1]
    rhs_mathjson = mathjson_expr[2]

    # Convert RHS to SymPy
    rhs_sympy = mathjson_to_sympy(rhs_mathjson)

    # Case 1: Simple variable assignment (A = value)
    if isinstance(lhs_mathjson, str):
        variable_name = lhs_mathjson
        assign_variable(variable_name, rhs_sympy, mathjson=mathjson_expr)
        return rhs_sympy

    # Case 1.5: Implicit multiplication parsed as identifier (expr → e*x*p*r)
    # MathLive parses multi-letter identifiers as implicit multiplication
    # Example: ["Multiply", "ExponentialE", "x", "p", "r"] should be variable "expr"
    # where "ExponentialE" represents the letter "e" (parsed as Euler's constant)
    if (isinstance(lhs_mathjson, list) and len(lhs_mathjson) >= 2 and
        lhs_mathjson[0] in ("Multiply", "InvisibleOperator")):
        args = lhs_mathjson[1:]

        # Map MathJSON constants to their single-letter equivalents
        # MathLive may parse "e" as "ExponentialE", "i" as "ImaginaryI"
        CONSTANT_TO_LETTER = {
            'ExponentialE': 'e',
            'ImaginaryI': 'i'
        }

        # Convert args, mapping constants to letters where applicable
        converted_args = [
            CONSTANT_TO_LETTER.get(arg, arg) if isinstance(arg, str) else arg
            for arg in args
        ]

        # Check if all converted args are single-letter strings
        if all(isinstance(arg, str) and len(arg) == 1 and arg.isalpha() for arg in converted_args):
            # Concatenate to form variable name
            variable_name = ''.join(converted_args)

            # Verify it's a valid identifier
            if variable_name.isidentifier():
                assign_variable(variable_name, rhs_sympy, mathjson=mathjson_expr)
                return rhs_sympy

    # Case 2: Function definition (f(x) = expr)
    # Known MathJSON operations that should not be treated as function names
    KNOWN_OPERATIONS = {
        'Add', 'Subtract', 'Multiply', 'Mul', 'Divide', 'Negate', 'Power', 'Sqrt', 'Root',
        'Sin', 'Cos', 'Tan', 'Sec', 'Csc', 'Cot',
        'Exp', 'Log', 'Ln', 'Abs', 'Factorial',
        'D', 'Derivative', 'Integrate', 'Limit',
        'Equal', 'List', 'Tuple', 'Matrix',
        'InvisibleOperator', 'Apply', 'Prime'
    }

    if isinstance(lhs_mathjson, list) and len(lhs_mathjson) >= 2:
        func_name = lhs_mathjson[0]
        if isinstance(func_name, str) and func_name not in KNOWN_OPERATIONS:
            # Create SymPy Lambda function
            # Extract argument symbols from lhs
            args = lhs_mathjson[1:]
            arg_symbols = [sp.Symbol(arg) if isinstance(arg, str) else arg for arg in args]

            # Create Lambda
            func = sp.Lambda(tuple(arg_symbols), rhs_sympy)
            assign_variable(func_name, func, mathjson=mathjson_expr)
            return rhs_sympy

    # Fallback: store as-is
    raise ValueError(f"Unsupported assignment type: {lhs_mathjson}")


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
