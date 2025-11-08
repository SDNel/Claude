"""API route handlers."""

import time
from typing import Any, List, Dict

from fastapi import APIRouter, HTTPException, status

from app.api.models import CasRequest, CasResponse, CasResult, CasStats, HealthResponse
from app.config import settings
from app.core.operations import execute_operation
from app.core.session import export_session, clear_session, delete_variable

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version="1.0.0")


@router.post("/cas", response_model=CasResponse, tags=["CAS Operations"])
async def cas_exec(request: CasRequest) -> CasResponse:
    """
    Execute a symbolic math operation.

    Accepts MathJSON expressions and returns results in requested formats.
    """
    start_time = time.time()

    try:
        # Execute the operation
        result = await execute_operation(request)

        elapsed_ms = (time.time() - start_time) * 1000

        return CasResponse(
            id=request.id,
            ok=True,
            result=result,
            stats=CasStats(
                elapsedMs=elapsed_ms,
                backend=settings.backend_name,  # type: ignore
                cached=False,
            ),
        )

    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "TIMEOUT", "message": str(e)},
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_INPUT", "message": str(e)},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


@router.post("/steps", response_model=CasResponse, tags=["CAS Operations"])
async def cas_steps(request: CasRequest) -> CasResponse:
    """
    Execute operation and return step-by-step explanation.

    Populates the result.steps field with detailed computation steps.
    """
    start_time = time.time()

    try:
        # Force steps to be included
        if request.want is None:
            request.want = []
        if "Steps" not in [w.value for w in request.want]:
            from app.api.models import OutputFormat
            request.want.append(OutputFormat.STEPS)

        # Execute the operation
        result = await execute_operation(request, include_steps=True)

        elapsed_ms = (time.time() - start_time) * 1000

        return CasResponse(
            id=request.id,
            ok=True,
            result=result,
            stats=CasStats(
                elapsedMs=elapsed_ms,
                backend=settings.backend_name,  # type: ignore
                cached=False,
            ),
        )

    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "TIMEOUT", "message": str(e)},
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_INPUT", "message": str(e)},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


@router.get("/registry", tags=["Registry"])
async def get_registry() -> Dict[str, Any]:
    """
    Get the session registry with all stored variables.

    Returns dictionary with stored objects organized by type.
    """
    try:
        return export_session()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


@router.delete("/registry", tags=["Registry"])
async def clear_registry() -> Dict[str, str]:
    """Clear all variables from the session registry."""
    try:
        clear_session()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


@router.delete("/registry/{variable_name}", tags=["Registry"])
async def delete_variable_endpoint(variable_name: str) -> Dict[str, str]:
    """Delete a specific variable from the session registry."""
    try:
        deleted = delete_variable(variable_name)
        if deleted:
            return {"status": "deleted", "variable": variable_name}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": f"Variable '{variable_name}' not found"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )
