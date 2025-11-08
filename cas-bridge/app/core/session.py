"""Session management with enhanced variable registry.

Phase 2: Enhanced type system with metadata and dual storage.
Stores both SymPy objects (for computation) and MathJSON (for display/export).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import sympy as sp


class ObjectType(Enum):
    """Types of mathematical objects that can be stored."""
    SCALAR = "scalar"
    EXPRESSION = "expression"
    MATRIX = "matrix"
    VECTOR = "vector"
    FUNCTION = "function"
    OPERATOR = "operator"
    COORDINATE_SYSTEM = "coordinate_system"
    UNKNOWN = "unknown"


@dataclass
class StoredObject:
    """Enhanced storage for mathematical objects."""
    name: str
    type: ObjectType
    value: Any  # SymPy object
    latex: str
    mathjson: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Export to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'type': self.type.value,
            'latex': self.latex,
            'mathjson': self.mathjson,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class SessionRegistry:
    """Enhanced session registry with type classification and metadata."""

    def __init__(self):
        self.objects: Dict[str, StoredObject] = {}
        self.default_coordinate_system = 'cartesian'

    def assign(self, name: str, value: Any, mathjson: Any = None,
               type_hint: Optional[ObjectType] = None) -> Any:
        """
        Store an object in the registry.

        Args:
            name: Variable name
            value: SymPy expression/object
            mathjson: Original MathJSON (optional, for editing/export)
            type_hint: Optional type override

        Returns:
            The stored value
        """
        # Infer type from SymPy object
        obj_type = type_hint or self._infer_type(value)

        # Extract metadata
        metadata = self._extract_metadata(value, obj_type)

        # Generate LaTeX
        latex = self._generate_latex(value, obj_type)

        # Create stored object
        obj = StoredObject(
            name=name,
            type=obj_type,
            value=value,
            latex=latex,
            mathjson=mathjson,
            metadata=metadata
        )

        # Store it
        self.objects[name] = obj

        return value

    def get(self, name: str) -> Optional[StoredObject]:
        """Retrieve a stored object."""
        return self.objects.get(name)

    def get_value(self, name: str) -> Optional[Any]:
        """Retrieve just the SymPy value."""
        obj = self.get(name)
        return obj.value if obj else None

    def delete(self, name: str) -> bool:
        """Delete an object from the registry."""
        if name in self.objects:
            del self.objects[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all objects."""
        self.objects = {}

    def list_all(self) -> List[StoredObject]:
        """Get all stored objects."""
        return list(self.objects.values())

    def list_by_type(self, obj_type: ObjectType) -> List[StoredObject]:
        """Get all objects of a specific type."""
        return [obj for obj in self.objects.values() if obj.type == obj_type]

    def export_session(self) -> Dict:
        """Export entire session to dictionary."""
        return {
            'objects': {name: obj.to_dict() for name, obj in self.objects.items()},
            'settings': {
                'coordinate_system': self.default_coordinate_system
            }
        }

    def _infer_type(self, value: Any) -> ObjectType:
        """Infer object type from SymPy object."""

        # Matrix
        if isinstance(value, sp.Matrix):
            # Check if it's a column or row vector
            if value.shape[1] == 1 or value.shape[0] == 1:
                return ObjectType.VECTOR
            return ObjectType.MATRIX

        # Function (Lambda)
        if isinstance(value, sp.Lambda):
            return ObjectType.FUNCTION

        # List (could be vector or list of equations)
        if isinstance(value, (list, tuple)):
            # If all elements are numbers or expressions, it's a vector
            if all(isinstance(elem, (int, float, sp.Expr)) for elem in value):
                return ObjectType.VECTOR
            return ObjectType.UNKNOWN

        # Numeric constant
        if isinstance(value, (int, float, sp.Integer, sp.Float, sp.Rational)):
            return ObjectType.SCALAR

        # Single symbol
        if isinstance(value, sp.Symbol):
            return ObjectType.SCALAR

        # Expression with variables
        if isinstance(value, sp.Expr):
            if value.free_symbols:
                return ObjectType.EXPRESSION
            else:
                return ObjectType.SCALAR

        return ObjectType.UNKNOWN

    def _extract_metadata(self, value: Any, obj_type: ObjectType) -> Dict[str, Any]:
        """Extract type-specific metadata."""
        metadata = {}

        if obj_type == ObjectType.MATRIX:
            metadata['dimensions'] = list(value.shape)
            metadata['is_square'] = value.shape[0] == value.shape[1]

        elif obj_type == ObjectType.VECTOR:
            if isinstance(value, sp.Matrix):
                metadata['length'] = max(value.shape)
                metadata['orientation'] = 'column' if value.shape[1] == 1 else 'row'
            elif isinstance(value, (list, tuple)):
                metadata['length'] = len(value)

        elif obj_type == ObjectType.FUNCTION:
            if isinstance(value, sp.Lambda):
                metadata['arguments'] = [str(arg) for arg in value.variables]
                metadata['arity'] = len(value.variables)

        elif obj_type == ObjectType.EXPRESSION:
            metadata['variables'] = [str(sym) for sym in value.free_symbols]
            metadata['complexity'] = len(str(value))

        elif obj_type == ObjectType.SCALAR:
            if isinstance(value, sp.Expr):
                metadata['is_constant'] = len(value.free_symbols) == 0
                if isinstance(value, (sp.Integer, sp.Rational)):
                    metadata['numeric_type'] = 'integer' if isinstance(value, sp.Integer) else 'rational'
                elif isinstance(value, sp.Float):
                    metadata['numeric_type'] = 'float'

        return metadata

    def _generate_latex(self, value: Any, obj_type: ObjectType) -> str:
        """Generate LaTeX representation."""
        try:
            return sp.latex(value)
        except Exception:
            return str(value)


# Global registry instance (session-based in production)
_global_registry = SessionRegistry()


def get_registry(session_id: str = "default") -> SessionRegistry:
    """
    Get the registry for a session.

    For now, returns global registry.
    In production, would be session-based (Redis, etc.)
    """
    return _global_registry


def assign_variable(name: str, value: Any, mathjson: Any = None,
                    session_id: str = "default") -> Any:
    """Assign a variable to the session registry."""
    registry = get_registry(session_id)
    return registry.assign(name, value, mathjson)


def get_variable(name: str, session_id: str = "default") -> Optional[Any]:
    """Get a variable value from the session registry."""
    registry = get_registry(session_id)
    return registry.get_value(name)


def delete_variable(name: str, session_id: str = "default") -> bool:
    """Delete a variable from the session registry."""
    registry = get_registry(session_id)
    return registry.delete(name)


def clear_session(session_id: str = "default") -> None:
    """Clear all variables in a session."""
    registry = get_registry(session_id)
    registry.clear()


def list_variables(session_id: str = "default") -> List[StoredObject]:
    """List all variables in a session."""
    registry = get_registry(session_id)
    return registry.list_all()


def export_session(session_id: str = "default") -> Dict:
    """Export session to dictionary."""
    registry = get_registry(session_id)
    return registry.export_session()
