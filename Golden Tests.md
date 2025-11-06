{
  "name": "differentiate_sin",
  "request": {
    "id": "g-001",
    "op": "differentiate",
    "expr": ["Sin", "x"],
    "vars": ["x"],
    "want": ["MathJSON", "LaTeX", "Text"]
  },
  "expected": {
    "latex": "\\cos\\left(x\\right)"
  }
}
{
  "name": "eigen_2x2",
  "request": {
    "id": "g-007",
    "op": "eigen",
    "expr": [[2, 0], [0, 3]],
    "want": ["Text", "MathJSON"]
  },
  "expected": {
    "text": "eigenvalues: [2, 3]"
  }
}
{
  "name": "integrate_definite_x2_0_1",
  "request": {
    "id": "g-003",
    "op": "integrate",
    "expr": ["Power", "x", 2],
    "vars": ["x"],
    "assumptions": { "bounds": [0, 1] },
    "want": ["Text", "LaTeX"]
  },
  "expected": {
    "text": "1/3"
  }
}
{
  "name": "integrate_indefinite_x2",
  "request": {
    "id": "g-002",
    "op": "integrate",
    "expr": ["Power", "x", 2],
    "vars": ["x"],
    "want": ["LaTeX"]
  },
  "expected": {
    "latex": "\\frac{x^{3}}{3}"
  }
}
{
  "name": "rref_sample",
  "request": {
    "id": "g-010",
    "op": "rref",
    "expr": [[1, 2, 3], [0, 1, 4], [5, 6, 0]],
    "want": ["Text"]
  },
  "expected": {
    "text": "rank=3"
  }
}
{
  "name": "series_exp_x_at_0_order_5",
  "request": {
    "id": "g-008",
    "op": "series",
    "expr": ["Exp", "x"],
    "vars": ["x"],
    "assumptions": { "around": 0, "order": 5 },
    "want": ["LaTeX"]
  },
  "expected": {
    "latex": "1+x+\\frac{x^{2}}{2}+\\frac{x^{3}}{6}+\\frac{x^{4}}{24}+\\mathcal{O}\\left(x^{5}\\right)"
  }
}
{
  "name": "simplify_expand_equivalence",
  "request": {
    "id": "g-004",
    "op": "expand",
    "expr": ["Power", ["Add", "x", 1], 3],
    "vars": ["x"],
    "want": ["LaTeX"]
  },
  "expected": {
    "latex": "x^{3}+3 x^{2}+3 x+1"
  }
}
{
  "name": "solve_linear_system",
  "request": {
    "id": "g-006",
    "op": "linsolve",
    "expr": { "A": [[2, 1], [1, 3]], "b": [1, 0] },
    "want": ["Text", "MathJSON"]
  },
  "expected": {
    "text": "x=3/5, y=-1/5"
  }
}
