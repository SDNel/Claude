"""MathJSON to SymPy expression converter."""

from typing import Any

import sympy as sp


def mathjson_to_sympy(mathjson: Any) -> Any:
    """
    Convert MathJSON expression to SymPy expression.

    Args:
        mathjson: MathJSON expression (list or dict structure)

    Returns:
        SymPy expression

    Raises:
        ValueError: If MathJSON is malformed or unsupported

    MathJSON format examples:
        ["Add", "x", 1] -> x + 1
        ["Multiply", 2, "x"] -> 2*x
        ["Power", "x", 2] -> x**2
        ["Sin", "x"] -> sin(x)
    """
    if isinstance(mathjson, (int, float)):
        return sp.sympify(mathjson)

    if isinstance(mathjson, str):
        # Assume it's a symbol
        return sp.Symbol(mathjson)

    if isinstance(mathjson, list) and len(mathjson) > 0:
        # Check if it's a matrix (nested list of numbers)
        if all(isinstance(row, list) for row in mathjson):
            return sp.Matrix(mathjson)

        operation = mathjson[0]
        args = mathjson[1:]

        # Map MathJSON operations to SymPy functions (allow-list approach)
        # Updated 2025-11-07: Added Compute Engine operations from Phase 1b research
        operation_map = {
            # Arithmetic
            "Add": lambda args: sp.Add(*[mathjson_to_sympy(arg) for arg in args]),
            "Subtract": lambda args: sp.Add(mathjson_to_sympy(args[0]), sp.Mul(-1, mathjson_to_sympy(args[1]))),
            "Multiply": lambda args: sp.Mul(*[mathjson_to_sympy(arg) for arg in args]),
            "Mul": lambda args: sp.Mul(*[mathjson_to_sympy(arg) for arg in args]),  # Alias for Multiply
            "Divide": lambda args: sp.Mul(mathjson_to_sympy(args[0]), sp.Pow(mathjson_to_sympy(args[1]), -1)),
            "Negate": lambda args: sp.Mul(-1, mathjson_to_sympy(args[0])),
            "Power": lambda args: sp.Pow(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1])),
            "Sqrt": lambda args: sp.sqrt(mathjson_to_sympy(args[0])),
            "Rational": lambda args: sp.Rational(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1])),

            # Trigonometric
            "Sin": lambda args: sp.sin(mathjson_to_sympy(args[0])),
            "Cos": lambda args: sp.cos(mathjson_to_sympy(args[0])),
            "Tan": lambda args: sp.tan(mathjson_to_sympy(args[0])),
            "Sec": lambda args: sp.sec(mathjson_to_sympy(args[0])),
            "Csc": lambda args: sp.csc(mathjson_to_sympy(args[0])),
            "Cot": lambda args: sp.cot(mathjson_to_sympy(args[0])),

            # Inverse trigonometric (both capitalization variants)
            "Arcsin": lambda args: sp.asin(mathjson_to_sympy(args[0])),
            "Arccos": lambda args: sp.acos(mathjson_to_sympy(args[0])),
            "Arctan": lambda args: sp.atan(mathjson_to_sympy(args[0])),
            "ArcSin": lambda args: sp.asin(mathjson_to_sympy(args[0])),
            "ArcCos": lambda args: sp.acos(mathjson_to_sympy(args[0])),
            "ArcTan": lambda args: sp.atan(mathjson_to_sympy(args[0])),

            # Hyperbolic
            "Sinh": lambda args: sp.sinh(mathjson_to_sympy(args[0])),
            "Cosh": lambda args: sp.cosh(mathjson_to_sympy(args[0])),
            "Tanh": lambda args: sp.tanh(mathjson_to_sympy(args[0])),
            "Sech": lambda args: sp.sech(mathjson_to_sympy(args[0])),
            "Csch": lambda args: sp.csch(mathjson_to_sympy(args[0])),
            "Coth": lambda args: sp.coth(mathjson_to_sympy(args[0])),

            # Inverse hyperbolic (both capitalization variants)
            "Arcsinh": lambda args: sp.asinh(mathjson_to_sympy(args[0])),
            "Arccosh": lambda args: sp.acosh(mathjson_to_sympy(args[0])),
            "Arctanh": lambda args: sp.atanh(mathjson_to_sympy(args[0])),
            "ArcSinh": lambda args: sp.asinh(mathjson_to_sympy(args[0])),
            "ArcCosh": lambda args: sp.acosh(mathjson_to_sympy(args[0])),
            "ArcTanh": lambda args: sp.atanh(mathjson_to_sympy(args[0])),

            # Exponential and logarithmic
            "Exp": lambda args: sp.exp(mathjson_to_sympy(args[0])),
            "Ln": lambda args: sp.log(mathjson_to_sympy(args[0])),
            "Log": lambda args: sp.log(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1]) if len(args) > 1 else 10),

            # Calculus - COMPUTE ENGINE OPERATIONS
            "D": lambda args: _handle_d_operation(args),  # Derivative
            "ND": lambda args: _handle_nd_operation(args),  # Numerical derivative
            "Integrate": lambda args: _handle_integrate_operation(args),  # Integration
            "Limit": lambda args: _handle_limit_operation(args),  # Limit
            "Limits": lambda args: _handle_limits_structure(args),  # Bounds structure

            # Structural Operations
            "Function": lambda args: _handle_function_structure(args),
            "Block": lambda args: _handle_block_structure(args),
            "Tuple": lambda args: tuple(mathjson_to_sympy(arg) for arg in args),
            "List": lambda args: [mathjson_to_sympy(arg) for arg in args],
            "Sequence": lambda args: [mathjson_to_sympy(arg) for arg in args],

            # Other
            "Abs": lambda args: sp.Abs(mathjson_to_sympy(args[0])),
            "Equal": lambda args: sp.Eq(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1])),
            "Factorial": lambda args: sp.factorial(mathjson_to_sympy(args[0])),
            "Gamma": lambda args: sp.gamma(mathjson_to_sympy(args[0])),
        }

        if operation in operation_map:
            return operation_map[operation](args)
        else:
            raise ValueError(f"Unsupported MathJSON operation: {operation}")

    if isinstance(mathjson, dict):
        # Handle special structures (e.g., linear system: {"A": [[...]], "b": [...]})
        if "A" in mathjson and "b" in mathjson:
            return {
                "A": sp.Matrix(mathjson["A"]),
                "b": sp.Matrix(mathjson["b"])
            }
        raise ValueError("Unsupported dict-based MathJSON structure")

    raise ValueError(f"Invalid MathJSON format: {type(mathjson)}")


# Helper functions for Compute Engine operations (added 2025-11-07)

def _handle_d_operation(args: list) -> Any:
    """
    Handle D (derivative) operation from Compute Engine.

    Format: ["D", expression, variable, ...additional variables for higher order]
    Examples:
        ["D", ["Sin", "x"], "x"] -> derivative of sin(x) w.r.t. x
        ["D", "f", "x", "x"] -> second derivative
    """
    if len(args) < 2:
        raise ValueError("D operation requires at least 2 arguments: expression and variable")

    expr = mathjson_to_sympy(args[0])
    variables = [mathjson_to_sympy(arg) for arg in args[1:]]

    # Apply differentiation for each variable (supports higher order derivatives)
    result = expr
    for var in variables:
        result = sp.diff(result, var)

    return result


def _handle_nd_operation(args: list) -> Any:
    """
    Handle ND (numerical derivative) operation.

    For now, we compute symbolic derivative and let SymPy evaluate numerically if needed.
    """
    # ND is similar to D but intended for numerical approximation
    # For symbolic computation, treat it the same as D
    return _handle_d_operation(args)


def _handle_integrate_operation(args: list) -> Any:
    """
    Handle Integrate operation from Compute Engine.

    Compute Engine format:
        ["Integrate", ["Function", ["Block", expr], var], ["Limits", var, lower, upper]]
        or
        ["Integrate", ["Function", ["Block", expr], var]]  # indefinite

    We need to extract the expression, variable, and optional bounds.
    """
    if len(args) < 1:
        raise ValueError("Integrate operation requires at least 1 argument")

    # First arg is usually a Function structure: ["Function", ["Block", expr], var]
    if isinstance(args[0], list) and args[0][0] == "Function":
        func_struct = args[0]
        # Extract expression from Function/Block structure
        if len(func_struct) >= 3 and isinstance(func_struct[1], list) and func_struct[1][0] == "Block":
            expr = mathjson_to_sympy(func_struct[1][1])  # Expression inside Block
            var = sp.Symbol(func_struct[2]) if isinstance(func_struct[2], str) else mathjson_to_sympy(func_struct[2])
        else:
            raise ValueError("Unexpected Function structure in Integrate operation")
    else:
        # Fallback: assume first arg is expression (may not work for all cases)
        expr = mathjson_to_sympy(args[0])
        var = None  # Will need to infer or extract from next arg

    # Check for Limits structure (definite integral)
    if len(args) >= 2 and isinstance(args[1], list) and args[1][0] == "Limits":
        limits_struct = args[1]
        # ["Limits", var, lower, upper]
        if len(limits_struct) >= 4:
            var = sp.Symbol(limits_struct[1]) if isinstance(limits_struct[1], str) else mathjson_to_sympy(limits_struct[1])
            lower = mathjson_to_sympy(limits_struct[2])
            upper = mathjson_to_sympy(limits_struct[3])
            return sp.integrate(expr, (var, lower, upper))

    # Indefinite integral
    if var is None:
        # Try to infer variable from expression
        free_symbols = expr.free_symbols
        if len(free_symbols) == 1:
            var = list(free_symbols)[0]
        else:
            raise ValueError("Cannot infer integration variable - please specify")

    return sp.integrate(expr, var)


def _handle_limit_operation(args: list) -> Any:
    """
    Handle Limit operation from Compute Engine.

    Format: ["Limit", ["Function", ["Block", expr], var], point]
    """
    if len(args) < 2:
        raise ValueError("Limit operation requires at least 2 arguments")

    # Extract expression and variable from Function structure
    if isinstance(args[0], list) and args[0][0] == "Function":
        func_struct = args[0]
        if len(func_struct) >= 3 and isinstance(func_struct[1], list) and func_struct[1][0] == "Block":
            expr = mathjson_to_sympy(func_struct[1][1])
            var = sp.Symbol(func_struct[2]) if isinstance(func_struct[2], str) else mathjson_to_sympy(func_struct[2])
        else:
            raise ValueError("Unexpected Function structure in Limit operation")
    else:
        # Fallback
        expr = mathjson_to_sympy(args[0])
        var = None

    # Get limit point
    point = mathjson_to_sympy(args[1])

    # Check for direction (if provided)
    direction = "+-"  # two-sided by default
    if len(args) >= 3:
        direction_arg = args[2]
        if isinstance(direction_arg, str):
            direction = direction_arg

    if var is None:
        free_symbols = expr.free_symbols
        if len(free_symbols) == 1:
            var = list(free_symbols)[0]
        else:
            raise ValueError("Cannot infer limit variable")

    return sp.limit(expr, var, point, dir=direction)


def _handle_limits_structure(args: list) -> Any:
    """
    Handle Limits structure (bounds for integrals/limits).

    Format: ["Limits", var, lower, upper]
    Returns a tuple: (var, lower, upper)
    """
    if len(args) < 3:
        raise ValueError("Limits structure requires at least 3 arguments: var, lower, upper")

    var = sp.Symbol(args[0]) if isinstance(args[0], str) else mathjson_to_sympy(args[0])
    lower = mathjson_to_sympy(args[1])
    upper = mathjson_to_sympy(args[2])

    return (var, lower, upper)


def _handle_function_structure(args: list) -> Any:
    """
    Handle Function structure from Compute Engine.

    Format: ["Function", ["Block", expr], var]
    This represents a lambda function. We extract the expression.
    """
    if len(args) < 1:
        raise ValueError("Function structure requires at least 1 argument")

    # If first arg is Block, extract expression from it
    if isinstance(args[0], list) and args[0][0] == "Block":
        return mathjson_to_sympy(args[0][1])

    # Otherwise, just convert the first argument
    return mathjson_to_sympy(args[0])


def _handle_block_structure(args: list) -> Any:
    """
    Handle Block structure from Compute Engine.

    Format: ["Block", expr]
    Simply extracts and converts the expression.
    """
    if len(args) < 1:
        raise ValueError("Block structure requires at least 1 argument")

    return mathjson_to_sympy(args[0])


def sympy_to_mathjson(expr: Any) -> Any:
    """
    Convert SymPy expression to MathJSON.

    Args:
        expr: SymPy expression

    Returns:
        MathJSON representation (list/dict structure)
    """
    # Handle numbers - be comprehensive about SymPy number types
    if isinstance(expr, (sp.Integer, sp.Rational, sp.Float, sp.core.numbers.One,
                         sp.core.numbers.Zero, sp.core.numbers.NegativeOne)):
        if isinstance(expr, sp.Rational) and expr.q != 1:
            return ["Divide", int(expr.p), int(expr.q)]
        # Convert to Python int or float
        if isinstance(expr, sp.Float):
            return float(expr)
        return int(expr)

    # Handle symbols
    if isinstance(expr, sp.Symbol):
        return str(expr)

    # Handle matrices
    if isinstance(expr, sp.Matrix):
        # Convert to nested list, ensuring all elements are properly serialized
        result = []
        for i in range(expr.rows):
            row = []
            for j in range(expr.cols):
                # Recursively convert each element
                row.append(sympy_to_mathjson(expr[i, j]))
            result.append(row)
        return result

    # Handle tuples/lists (e.g., from solve)
    if isinstance(expr, (tuple, list)):
        return [sympy_to_mathjson(item) for item in expr]

    # Handle FiniteSet (from solve, eigenvals, etc.)
    if isinstance(expr, sp.FiniteSet):
        return [sympy_to_mathjson(item) for item in expr]

    # Arithmetic operations
    if isinstance(expr, sp.Add):
        return ["Add"] + [sympy_to_mathjson(arg) for arg in expr.args]

    if isinstance(expr, sp.Mul):
        # Check for division pattern (a * b^(-1))
        args = list(expr.args)
        if len(args) == 2 and isinstance(args[1], sp.Pow) and args[1].exp == -1:
            return ["Divide", sympy_to_mathjson(args[0]), sympy_to_mathjson(args[1].base)]
        return ["Multiply"] + [sympy_to_mathjson(arg) for arg in args]

    if isinstance(expr, sp.Pow):
        # Handle square root
        if expr.exp == sp.Rational(1, 2):
            return ["Sqrt", sympy_to_mathjson(expr.base)]
        return ["Power", sympy_to_mathjson(expr.base), sympy_to_mathjson(expr.exp)]

    # Trigonometric functions
    if isinstance(expr, sp.sin):
        return ["Sin", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.cos):
        return ["Cos", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.tan):
        return ["Tan", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.sec):
        return ["Sec", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.csc):
        return ["Csc", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.cot):
        return ["Cot", sympy_to_mathjson(expr.args[0])]

    # Inverse trigonometric
    if isinstance(expr, sp.asin):
        return ["ArcSin", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.acos):
        return ["ArcCos", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.atan):
        return ["ArcTan", sympy_to_mathjson(expr.args[0])]

    # Exponential and logarithmic
    if isinstance(expr, sp.exp):
        return ["Exp", sympy_to_mathjson(expr.args[0])]
    if isinstance(expr, sp.log):
        if len(expr.args) == 1:
            return ["Ln", sympy_to_mathjson(expr.args[0])]
        else:
            return ["Log", sympy_to_mathjson(expr.args[0]), sympy_to_mathjson(expr.args[1])]

    # Other functions
    if isinstance(expr, sp.Abs):
        return ["Abs", sympy_to_mathjson(expr.args[0])]

    if isinstance(expr, sp.Eq):
        return ["Equal", sympy_to_mathjson(expr.lhs), sympy_to_mathjson(expr.rhs)]

    # Handle special values
    if expr == sp.pi:
        return "pi"
    if expr == sp.E:
        return "e"
    if expr == sp.I:
        return "i"
    if expr == sp.oo:
        return "Infinity"
    if expr == -sp.oo:
        return "-Infinity"

    # If we can't convert, try string representation as fallback
    return str(expr)
