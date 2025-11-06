"""Logging utilities with PII redaction."""

import hashlib
import json
import logging
from typing import Any

from app.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        # JSON logging for production
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            handlers=[logging.StreamHandler()],
        )
    else:
        # Standard logging for development
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )


def redact_expression(expr: Any, max_length: int = 50) -> str:
    """
    Redact or hash expression for logging.

    Args:
        expr: Expression to redact
        max_length: Maximum length before truncating

    Returns:
        Redacted/hashed expression string
    """
    if not settings.redact_expressions:
        # Return as-is if redaction is disabled
        expr_str = str(expr)
        if len(expr_str) > max_length:
            return expr_str[:max_length] + "..."
        return expr_str

    # Hash the expression for privacy
    expr_str = json.dumps(expr) if isinstance(expr, (dict, list)) else str(expr)
    expr_hash = hashlib.sha256(expr_str.encode()).hexdigest()[:16]
    return f"<redacted:{expr_hash}>"


def log_operation(
    operation: str, request_id: str, expr: Any, elapsed_ms: float, success: bool
) -> None:
    """
    Log a CAS operation with appropriate redaction.

    Args:
        operation: Operation name
        request_id: Request ID
        expr: Expression (will be redacted)
        elapsed_ms: Elapsed time in milliseconds
        success: Whether operation succeeded
    """
    logger = logging.getLogger("cas_bridge.operations")

    redacted = redact_expression(expr)
    status = "SUCCESS" if success else "FAILED"

    if settings.log_format == "json":
        log_data = {
            "operation": operation,
            "request_id": request_id,
            "expression": redacted,
            "elapsed_ms": elapsed_ms,
            "status": status,
        }
        logger.info(json.dumps(log_data))
    else:
        logger.info(
            f"{status} | op={operation} id={request_id} expr={redacted} time={elapsed_ms:.2f}ms"
        )
