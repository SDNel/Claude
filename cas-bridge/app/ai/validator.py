"""Validation logic for AI-generated step-by-step solutions."""

import sympy as sp
from typing import List, Dict, Any


def validate_steps(steps: List[Dict[str, Any]], problem_expr: Any, solution_expr: Any) -> List[Dict[str, Any]]:
    """
    Validate AI-generated steps by checking mathematical equivalence.

    For each consecutive pair of steps, we verify that they are mathematically
    equivalent (possibly after substitution, simplification, etc.).

    Args:
        steps: List of steps from AI with expression, latex, explanation, depth
        problem_expr: The original problem (SymPy expression)
        solution_expr: The final solution (SymPy expression) - our anchor point

    Returns:
        Steps list with added 'validated' field (True/False/None)
    """
    if not steps:
        return steps

    validated_steps = []

    for i, step in enumerate(steps):
        validated_step = step.copy()

        try:
            # Parse the step's expression to SymPy
            # Note: step['expression'] is a string like "x^3/3" or "-x^2*cos(x) + integral(2*x*cos(x), x)"
            step_expr = _parse_expression_safe(step['expression'])

            if step_expr is None:
                # Can't parse - mark as unverified
                validated_step['validated'] = None
                validated_step['validation_note'] = "Could not parse expression"
            elif i == 0:
                # First step - we can't validate against a previous step
                # Just mark it as unverified for now
                validated_step['validated'] = None
                validated_step['validation_note'] = "First step (no previous step to compare)"
            else:
                # Compare with previous step
                prev_step = steps[i-1]
                prev_expr = _parse_expression_safe(prev_step['expression'])

                if prev_expr is None:
                    validated_step['validated'] = None
                    validated_step['validation_note'] = "Previous step could not be parsed"
                else:
                    # Check if they are mathematically equivalent
                    # For integrals, we can't always verify intermediate steps directly
                    # So we'll be lenient and just check if they simplify to each other
                    is_valid = _check_equivalence(prev_expr, step_expr)

                    if is_valid:
                        validated_step['validated'] = True
                        validated_step['validation_note'] = "Verified"
                    else:
                        validated_step['validated'] = False
                        validated_step['validation_note'] = "Not equivalent to previous step"

        except Exception as e:
            # Validation failed - mark as unverified
            validated_step['validated'] = None
            validated_step['validation_note'] = f"Validation error: {str(e)[:50]}"

        validated_steps.append(validated_step)

    # Special validation: Check if the last step matches the solution
    if validated_steps:
        last_step = validated_steps[-1]
        try:
            last_expr = _parse_expression_safe(steps[-1]['expression'])
            if last_expr is not None and _check_equivalence(last_expr, solution_expr):
                last_step['validated'] = True
                last_step['validation_note'] = "Matches final solution ✓"
            elif last_expr is not None:
                # Last step doesn't match solution - this is a red flag!
                last_step['validated'] = False
                last_step['validation_note'] = "Does NOT match final solution ⚠"
        except:
            pass

    return validated_steps


def _parse_expression_safe(expr_str: str) -> Any:
    """
    Safely parse a string expression to SymPy.

    Returns None if parsing fails.
    """
    try:
        # Try to parse using sympify
        # Note: This won't work for strings like "integral(2*x*cos(x), x)"
        # For now, we'll skip those
        if 'integral' in expr_str.lower() or '∫' in expr_str:
            # Can't easily parse integral expressions from text
            return None

        return sp.sympify(expr_str)
    except:
        return None


def _check_equivalence(expr1: Any, expr2: Any) -> bool:
    """
    Check if two SymPy expressions are mathematically equivalent.

    Uses multiple strategies:
    1. Direct equality
    2. Difference simplifies to zero
    3. Ratio simplifies to one (for non-zero expressions)
    """
    try:
        # Strategy 1: Direct equality
        if expr1 == expr2:
            return True

        # Strategy 2: Difference equals zero
        diff = sp.simplify(expr1 - expr2)
        if diff == 0:
            return True

        # Strategy 3: Expand and compare
        if sp.expand(expr1) == sp.expand(expr2):
            return True

        # Strategy 4: Simplify both and compare
        if sp.simplify(expr1) == sp.simplify(expr2):
            return True

        return False
    except:
        return False
