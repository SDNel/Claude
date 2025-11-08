"""Security layer - MathJSON allow-list validation."""

from typing import Any, Set

from app.config import settings

# Allow-listed MathJSON operations
# CRITICAL: This is the security boundary - only these operations are allowed
# Updated 2025-11-07: Added Compute Engine operations from Phase 1b research
ALLOWED_OPERATIONS: Set[str] = {
    # Arithmetic
    "Add",
    "Subtract",
    "Multiply",
    "Mul",  # Alias for Multiply
    "Divide",
    "Negate",
    "Power",
    "Sqrt",
    "Root",
    "Rational",  # Compute Engine uses this for fractions
    # Trigonometric
    "Sin",
    "Cos",
    "Tan",
    "Sec",
    "Csc",
    "Cot",
    "Arcsin",
    "Arccos",
    "Arctan",
    "ArcSin",  # Compute Engine capital versions
    "ArcCos",
    "ArcTan",
    # Hyperbolic
    "Sinh",
    "Cosh",
    "Tanh",
    "Sech",
    "Csch",
    "Coth",
    # Inverse Hyperbolic
    "Arcsinh",
    "Arccosh",
    "Arctanh",
    "ArcSinh",
    "ArcCosh",
    "ArcTanh",
    # Exponential & Logarithmic
    "Exp",
    "Log",
    "Ln",
    "Log10",
    # Special functions
    "Abs",
    "Factorial",
    "Gamma",
    # Calculus - COMPUTE ENGINE OPERATIONS
    "D",           # Primary derivative operation (computes derivatives)
    "ND",          # Numerical derivative approximation
    "Derivative",  # Symbolic derivative (representation only)
    "Integrate",   # Integration operation (Compute Engine name)
    "Integral",    # Old name (keep for backward compatibility)
    "Limit",       # Limit operation
    "Limits",      # Bounds structure for definite integrals/limits
    # Structural Operations (Compute Engine)
    "Function",    # Function definition structure
    "Block",       # Code block structure
    "Tuple",       # Multiple return values
    "List",        # Array/list structure
    "Sequence",    # Sequence of expressions
    "Apply",       # Function application (used for derivatives like sin'(x))
    "Prime",       # Prime notation marker
    "PartialDerivative",  # Partial derivative symbol
    "InvisibleOperator",  # Implicit multiplication (e.g., 2x, dx)
    "Error",       # Error nodes (we filter these in preprocessing)
    "LatexString",  # LaTeX string literals (in error messages)
    # Comparison
    "Equal",
    "Greater",
    "Less",
    "GreaterEqual",
    "LessEqual",
    "NotEqual",
    # Logical
    "And",
    "Or",
    "Not",
    # Constants (sometimes appear as operations)
    "Pi",
    "E",
    "Infinity",
    "NegativeInfinity",
}


def validate_mathjson(expr: Any, max_depth: int = 50, current_depth: int = 0) -> None:
    """
    Validate MathJSON expression against allow-list.

    This function ensures that only permitted operations are used
    and prevents deeply nested expressions (DoS protection).

    Args:
        expr: MathJSON expression to validate
        max_depth: Maximum nesting depth allowed
        current_depth: Current recursion depth

    Raises:
        ValueError: If expression contains disallowed operations or is too complex
    """
    # Check recursion depth (prevent stack overflow attacks)
    if current_depth > max_depth:
        raise ValueError(f"Expression too deeply nested (max depth: {max_depth})")

    # Primitives are always allowed
    if isinstance(expr, (int, float, bool)):
        return

    if isinstance(expr, str):
        # Check string length to prevent memory attacks
        if len(expr) > settings.max_expression_length:
            raise ValueError(f"Expression string too long (max: {settings.max_expression_length})")
        return

    # Validate list-based MathJSON
    if isinstance(expr, list):
        if len(expr) == 0:
            raise ValueError("Empty list in MathJSON")

        # Check if it's a matrix (nested list of numbers)
        if all(isinstance(row, list) for row in expr):
            # It's a matrix - validate each element
            for row in expr:
                for element in row:
                    validate_mathjson(element, max_depth, current_depth + 1)
            return

        operation = expr[0]

        # Ensure operation is a string
        if not isinstance(operation, str):
            raise ValueError(f"Invalid operation type: {type(operation)}")

        # Check against allow-list
        if operation not in ALLOWED_OPERATIONS:
            raise ValueError(f"Operation not allowed: {operation}")

        # Recursively validate arguments
        for arg in expr[1:]:
            validate_mathjson(arg, max_depth, current_depth + 1)

        return

    # Validate dict-based MathJSON (for matrices, etc.)
    if isinstance(expr, dict):
        # Validate matrix structures
        if "A" in expr or "b" in expr:
            # Linear system: {"A": [[...]], "b": [...]}
            if "A" in expr:
                validate_matrix(expr["A"])
            if "b" in expr:
                validate_vector(expr["b"])
            return

        # Other dict structures
        for key, value in expr.items():
            if not isinstance(key, str):
                raise ValueError(f"Invalid dict key type: {type(key)}")
            validate_mathjson(value, max_depth, current_depth + 1)
        return

    raise ValueError(f"Unsupported MathJSON type: {type(expr)}")


def validate_matrix(matrix: Any) -> None:
    """
    Validate matrix structure.

    Args:
        matrix: Matrix to validate (list of lists)

    Raises:
        ValueError: If matrix is invalid
    """
    if not isinstance(matrix, list):
        raise ValueError("Matrix must be a list")

    if len(matrix) == 0:
        raise ValueError("Matrix cannot be empty")

    # Check that all rows are lists of the same length
    row_length = None
    for i, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError(f"Matrix row {i} is not a list")

        if row_length is None:
            row_length = len(row)
        elif len(row) != row_length:
            raise ValueError(f"Matrix has inconsistent row lengths")

        # Validate all elements are numbers
        for j, elem in enumerate(row):
            if not isinstance(elem, (int, float)):
                raise ValueError(f"Matrix element [{i}][{j}] is not a number: {type(elem)}")

    # Size limits (prevent memory attacks)
    if len(matrix) > 100 or row_length and row_length > 100:
        raise ValueError("Matrix too large (max 100x100)")


def validate_vector(vector: Any) -> None:
    """
    Validate vector structure.

    Args:
        vector: Vector to validate (list of numbers)

    Raises:
        ValueError: If vector is invalid
    """
    if not isinstance(vector, list):
        raise ValueError("Vector must be a list")

    if len(vector) == 0:
        raise ValueError("Vector cannot be empty")

    if len(vector) > 100:
        raise ValueError("Vector too large (max 100 elements)")

    for i, elem in enumerate(vector):
        if not isinstance(elem, (int, float)):
            raise ValueError(f"Vector element [{i}] is not a number: {type(elem)}")
