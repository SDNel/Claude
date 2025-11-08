"""AI-powered step-by-step solution generation using Anthropic Claude."""

import json
from typing import List, Dict, Any
import anthropic
from sympy import latex
from app.config import settings


def generate_steps_with_ai(
    problem_latex: str,
    solution_latex: str,
    operation_type: str,
    max_steps: int = 15
) -> List[Dict[str, Any]]:
    """
    Generate step-by-step solution using Claude AI.

    Args:
        problem_latex: The original problem in LaTeX format
        solution_latex: The final solution in LaTeX format (from SymPy)
        operation_type: Type of operation (integrate, simplify, expand, etc.)
        max_steps: Maximum number of steps to generate

    Returns:
        List of steps with format:
        [
            {
                "expression": "x^3/3",
                "latex": "\\frac{x^3}{3}",
                "explanation": "Apply the power rule...",
                "depth": 0
            },
            ...
        ]
    """
    # Get API key from settings
    api_key = settings.anthropic_api_key
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured in .env file")

    # Create Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Design the prompt
    prompt = f"""You are a mathematics tutor helping students understand step-by-step solutions.

Given:
- Problem: {problem_latex}
- Operation: {operation_type}
- Final Answer: {solution_latex}

Your task is to provide a clear, pedagogical step-by-step explanation of how to get from the problem to the solution.

IMPORTANT REQUIREMENTS:
1. Each step should show INTERMEDIATE WORK (not just the rule name)
2. For integration by parts, show the calculation of u, du, v, dv explicitly
3. Group related substeps together (e.g., all work for one integration by parts)
4. Use clear narrative: "Now we need to...", "Next, integrate...", "Simplify to get..."
5. Each step should be mathematically complete and follow from the previous
6. Return EXACTLY {max_steps} or fewer steps (do not exceed this limit)

Return your response as a JSON array of steps. Each step must have:
- "expression": The mathematical expression in text form (e.g., "x^3/3")
- "latex": The expression in LaTeX format (e.g., "\\\\frac{{x^3}}{{3}}")
- "explanation": Clear explanation of what is happening in this step
- "depth": 0 for main steps, 1 for substeps, 2 for sub-substeps

Example format:
[
  {{
    "expression": "-x^2*cos(x) + integral(2*x*cos(x), x)",
    "latex": "-x^2\\\\cos(x) + \\\\int 2x\\\\cos(x)\\\\,dx",
    "explanation": "Apply integration by parts with u = x^2 and dv = sin(x) dx. We get du = 2x dx and v = -cos(x). Using the formula ∫u dv = uv - ∫v du, we have: -x^2 cos(x) - ∫(-cos(x))(2x) dx = -x^2 cos(x) + ∫2x cos(x) dx",
    "depth": 0
  }},
  {{
    "expression": "2*x*sin(x) - integral(2*sin(x), x)",
    "latex": "2x\\\\sin(x) - \\\\int 2\\\\sin(x)\\\\,dx",
    "explanation": "For the remaining integral ∫2x cos(x) dx, apply integration by parts again with u = 2x and dv = cos(x) dx. We get du = 2 dx and v = sin(x). This gives: 2x sin(x) - ∫2 sin(x) dx",
    "depth": 1
  }}
]

Return ONLY the JSON array, no additional text."""

    # Call Claude API
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (latest)
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the response
    response_text = message.content[0].text

    # Strip markdown code blocks if present
    # Claude sometimes wraps JSON in ```json ... ```
    response_text = response_text.strip()
    if response_text.startswith('```'):
        # Find the first newline after opening ```
        first_newline = response_text.find('\n')
        # Find the closing ```
        last_backticks = response_text.rfind('```')
        if first_newline != -1 and last_backticks != -1:
            response_text = response_text[first_newline+1:last_backticks].strip()

    # Parse JSON response
    try:
        steps = json.loads(response_text)

        # Validate structure
        if not isinstance(steps, list):
            raise ValueError("Response is not a list")

        for step in steps:
            if not all(key in step for key in ['expression', 'latex', 'explanation', 'depth']):
                raise ValueError(f"Step missing required fields: {step}")

        return steps

    except json.JSONDecodeError as e:
        # If JSON parsing fails, return error step
        return [{
            'expression': solution_latex,
            'latex': solution_latex,
            'explanation': f'AI response parsing failed: {str(e)}. Raw response: {response_text[:200]}',
            'depth': 0
        }]
    except Exception as e:
        return [{
            'expression': solution_latex,
            'latex': solution_latex,
            'explanation': f'AI step generation failed: {str(e)}',
            'depth': 0
        }]
