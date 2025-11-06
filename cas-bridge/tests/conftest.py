"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_request():
    """Sample CAS request for testing."""
    return {
        "id": "test-001",
        "op": "differentiate",
        "expr": ["Sin", "x"],
        "vars": ["x"],
        "want": ["MathJSON", "LaTeX", "Text"],
    }
