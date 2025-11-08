"""Session management for variable registry.

In-memory storage for assigned variables and functions.
In production, this should be replaced with Redis or session-based storage.
"""

from typing import Any, Dict, Optional
import sympy as sp

# Global variable registry (session-based in production)
# Key: session_id (for now using 'default' as single session)
# Value: dict of variable_name -> sympy expression
_variable_registry: Dict[str, Dict[str, Any]] = {}


def get_session_registry(session_id: str = "default") -> Dict[str, Any]:
    """
    Get the variable registry for a session.

    Args:
        session_id: Session identifier (default: "default")

    Returns:
        Dictionary mapping variable names to SymPy expressions
    """
    if session_id not in _variable_registry:
        _variable_registry[session_id] = {}
    return _variable_registry[session_id]


def assign_variable(name: str, value: Any, session_id: str = "default") -> Any:
    """
    Assign a value to a variable in the session.

    Args:
        name: Variable name
        value: SymPy expression to assign
        session_id: Session identifier

    Returns:
        The assigned value
    """
    registry = get_session_registry(session_id)
    registry[name] = value
    return value


def get_variable(name: str, session_id: str = "default") -> Optional[Any]:
    """
    Get a variable value from the session.

    Args:
        name: Variable name
        session_id: Session identifier

    Returns:
        SymPy expression or None if not found
    """
    registry = get_session_registry(session_id)
    return registry.get(name)


def delete_variable(name: str, session_id: str = "default") -> bool:
    """
    Delete a variable from the session.

    Args:
        name: Variable name
        session_id: Session identifier

    Returns:
        True if deleted, False if not found
    """
    registry = get_session_registry(session_id)
    if name in registry:
        del registry[name]
        return True
    return False


def clear_session(session_id: str = "default") -> None:
    """
    Clear all variables in a session.

    Args:
        session_id: Session identifier
    """
    if session_id in _variable_registry:
        _variable_registry[session_id] = {}


def list_variables(session_id: str = "default") -> Dict[str, Any]:
    """
    List all variables in a session.

    Args:
        session_id: Session identifier

    Returns:
        Dictionary of all variables
    """
    return get_session_registry(session_id).copy()
