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
    # TODO: Implement full MathJSON → SymPy conversion
    # This is a critical security component - must use allow-list approach

    if isinstance(mathjson, (int, float)):
        return sp.sympify(mathjson)

    if isinstance(mathjson, str):
        # Assume it's a symbol
        return sp.Symbol(mathjson)

    if isinstance(mathjson, list) and len(mathjson) > 0:
        operation = mathjson[0]
        args = mathjson[1:]

        # Map MathJSON operations to SymPy functions
        # TODO: Complete this mapping with all supported operations

        if operation == "Add":
            return sp.Add(*[mathjson_to_sympy(arg) for arg in args])
        elif operation == "Multiply":
            return sp.Mul(*[mathjson_to_sympy(arg) for arg in args])
        elif operation == "Power":
            return sp.Pow(mathjson_to_sympy(args[0]), mathjson_to_sympy(args[1]))
        elif operation == "Sin":
            return sp.sin(mathjson_to_sympy(args[0]))
        elif operation == "Cos":
            return sp.cos(mathjson_to_sympy(args[0]))
        elif operation == "Exp":
            return sp.exp(mathjson_to_sympy(args[0]))
        else:
            raise ValueError(f"Unsupported MathJSON operation: {operation}")

    if isinstance(mathjson, dict):
        # Handle matrix or special structures
        # TODO: Implement matrix parsing
        raise ValueError("Dict-based MathJSON not yet supported")

    raise ValueError(f"Invalid MathJSON format: {type(mathjson)}")


def sympy_to_mathjson(expr: Any) -> Any:
    """
    Convert SymPy expression to MathJSON.

    Args:
        expr: SymPy expression

    Returns:
        MathJSON representation (list/dict structure)
    """
    # TODO: Implement SymPy → MathJSON conversion
    # This is the reverse of mathjson_to_sympy

    if isinstance(expr, (sp.Integer, sp.Rational, sp.Float)):
        return float(expr)

    if isinstance(expr, sp.Symbol):
        return str(expr)

    if isinstance(expr, sp.Add):
        return ["Add"] + [sympy_to_mathjson(arg) for arg in expr.args]

    if isinstance(expr, sp.Mul):
        return ["Multiply"] + [sympy_to_mathjson(arg) for arg in expr.args]

    if isinstance(expr, sp.Pow):
        return ["Power", sympy_to_mathjson(expr.base), sympy_to_mathjson(expr.exp)]

    # TODO: Add more conversions

    raise ValueError(f"Cannot convert SymPy type to MathJSON: {type(expr)}")
