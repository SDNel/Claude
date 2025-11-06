"""Golden fixture tests - validates against expected outputs."""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Load all golden fixtures
GOLDENS_DIR = Path(__file__).parent.parent.parent / "goldens"


def load_golden_fixtures() -> list[Dict[str, Any]]:
    """Load all golden test fixtures from the goldens directory."""
    fixtures = []
    for json_file in GOLDENS_DIR.glob("*.json"):
        with open(json_file, "r") as f:
            # Each file contains one JSON object
            fixture = json.load(f)
            fixtures.append(fixture)
    return fixtures


GOLDEN_FIXTURES = load_golden_fixtures()


@pytest.fixture
def client() -> TestClient:
    """Test client fixture."""
    return TestClient(app)


@pytest.mark.parametrize("fixture", GOLDEN_FIXTURES, ids=[f["name"] for f in GOLDEN_FIXTURES])
def test_golden_fixture(client: TestClient, fixture: Dict[str, Any]) -> None:
    """
    Test each golden fixture.

    Sends the request to /cas endpoint and validates response
    against expected values.
    """
    request_data = fixture["request"]
    expected = fixture["expected"]

    # Send request
    response = client.post("/cas", json=request_data)

    # Check response status
    assert response.status_code == 200, f"Failed for {fixture['name']}: {response.text}"

    # Parse response
    result = response.json()

    assert result["ok"] is True, f"Operation failed for {fixture['name']}"
    assert result["result"] is not None, f"No result for {fixture['name']}"

    # Validate expected fields
    if "latex" in expected:
        assert result["result"]["latex"] is not None
        # Normalize and compare LaTeX (allow minor variations)
        actual_latex = normalize_latex(result["result"]["latex"])
        expected_latex = normalize_latex(expected["latex"])
        assert actual_latex == expected_latex, (
            f"LaTeX mismatch for {fixture['name']}: "
            f"expected '{expected_latex}', got '{actual_latex}'"
        )

    if "text" in expected:
        assert result["result"]["text"] is not None
        # Text comparison (may need normalization)
        assert normalize_text(result["result"]["text"]) == normalize_text(expected["text"])

    if "mathjson" in expected:
        assert result["result"]["mathjson"] is not None
        # TODO: Add MathJSON comparison logic


def normalize_latex(latex: str) -> str:
    """
    Normalize LaTeX for comparison.

    Removes extra whitespace, normalizes unicode, etc.
    """
    # Remove extra whitespace
    latex = " ".join(latex.split())

    # Normalize common variations
    latex = latex.replace("\\left(", "(")
    latex = latex.replace("\\right)", ")")
    latex = latex.replace("\\left[", "[")
    latex = latex.replace("\\right]", "]")

    # Remove unnecessary spaces around operators
    latex = latex.replace(" + ", "+")
    latex = latex.replace(" - ", "-")
    latex = latex.replace(" \\cdot ", "*")

    return latex.strip()


def normalize_text(text: str) -> str:
    """
    Normalize text output for comparison.

    Removes extra whitespace and normalizes formatting.
    """
    return " ".join(text.split()).strip().lower()
