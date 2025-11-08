"""Pydantic models for API requests and responses."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CasOperation(str, Enum):
    """Supported CAS operations."""

    SIMPLIFY = "simplify"
    EXPAND = "expand"
    FACTOR = "factor"
    DIFFERENTIATE = "differentiate"
    INTEGRATE = "integrate"
    LIMIT = "limit"
    SERIES = "series"
    SOLVE = "solve"
    LINSOLVE = "linsolve"
    RREF = "rref"
    EIGEN = "eigen"
    STEPS = "steps"
    EVALUATE = "evaluate"  # Added 2025-11-07: For self-contained calculus expressions
    ASSIGN = "assign"  # Added 2025-11-08: For variable/function assignments


class OutputFormat(str, Enum):
    """Output format options."""

    MATHJSON = "MathJSON"
    LATEX = "LaTeX"
    TEXT = "Text"
    STEPS = "Steps"


class ResultForm(str, Enum):
    """Result form options."""

    EXPANDED = "expanded"
    FACTORED = "factored"
    CANONICAL = "canonical"


class CasBackend(str, Enum):
    """CAS backend options."""

    COMPUTE_ENGINE = "compute-engine"
    REMOTE_SYMPY = "remote-sympy"
    GIAC_WASM = "giac-wasm"
    PYODIDE_SYMPY = "pyodide-sympy"


class CasOptions(BaseModel):
    """Optional operation parameters."""

    form: Optional[ResultForm] = None
    timeout_ms: Optional[int] = Field(None, alias="timeoutMs", ge=1, le=5000)
    degree_limit: Optional[int] = Field(None, alias="degreeLimit", ge=1, le=20)


class CasRequest(BaseModel):
    """Request model for CAS operations."""

    id: str
    op: CasOperation
    expr: Any  # MathJSON expression (nested list/dict structure)
    vars: Optional[List[str]] = None
    assumptions: Optional[Dict[str, Any]] = None
    options: Optional[CasOptions] = None
    want: Optional[List[OutputFormat]] = Field(
        default_factory=lambda: [OutputFormat.MATHJSON, OutputFormat.LATEX, OutputFormat.TEXT]
    )


class StepNode(BaseModel):
    """Hierarchical step-by-step explanation node."""

    rule: Optional[str] = None
    before: Optional[Any] = None  # MathJSON
    after: Optional[Any] = None  # MathJSON
    explanation: Optional[str] = None
    children: Optional[List["StepNode"]] = None


class CasResult(BaseModel):
    """Result data from CAS operation."""

    mathjson: Optional[Any] = None
    latex: Optional[str] = None
    text: Optional[str] = None
    steps: Optional[StepNode] = None


class CasError(BaseModel):
    """Error information."""

    code: str
    message: str
    details: Optional[Any] = None


class CasStats(BaseModel):
    """Operation statistics."""

    elapsed_ms: float = Field(alias="elapsedMs")
    backend: CasBackend
    cached: Optional[bool] = False


class CasResponse(BaseModel):
    """Response model for CAS operations."""

    id: str
    ok: bool
    result: Optional[CasResult] = None
    error: Optional[CasError] = None
    stats: Optional[CasStats] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "1.0.0"
