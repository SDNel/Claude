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

            # Trigonometric
            "Sin": lambda args: sp.sin(mathjson_to_sympy(args[0])),
            "Cos": lambda args: sp.cos(mathjson_to_sympy(args[0])),
            "Tan": lambda args: sp.tan(mathjson_to_sympy(args[0])),
            "Sec": lambda args: sp.sec(mathjson_to_sympy(args[0])),
            "Csc": lambda args: sp.csc(mathjson_to_sympy(args[0])),
            "Cot": lambda args: sp.cot(mathjson_to_sympy(args[0])),

            # Inverse trigonometric
            "ArcSin": lambda args: sp.asin(mathjson_to_sympy(args[0])),
            "ArcCos": lambda args: sp.acos(mathjson_to_sympy(args[0])),
            "ArcTan": lambda args: sp.atan(mathjson_to_sympy(args[0])),

            # Exponential and logarithmic
            "Exp": lambda args: sp.exp(mathjson_to_sympy(args[0])),
            "Ln": lambda args: sp.log(mathjson_to_sympy(args[0])),
            "Log": lambda args: sp.log(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1]) if len(args) > 1 else 10),

            # Other
            "Abs": lambda args: sp.Abs(mathjson_to_sympy(args[0])),
            "Equal": lambda args: sp.Eq(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1])),
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


def sympy_to_mathjson(expr: Any) -> Any:
    """
    Convert SymPy expression to MathJSON.

    Args:
        expr: SymPy expression

    Returns:
        MathJSON representation (list/dict structure)
    """
    # Handle numbers
    if isinstance(expr, (sp.Integer, sp.Rational)):
        if isinstance(expr, sp.Rational) and expr.q != 1:
            return ["Divide", int(expr.p), int(expr.q)]
        return int(expr)

    if isinstance(expr, sp.Float):
        return float(expr)

    # Handle symbols
    if isinstance(expr, sp.Symbol):
        return str(expr)

    # Handle matrices
    if isinstance(expr, sp.Matrix):
        return expr.tolist()

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
