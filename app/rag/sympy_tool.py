import re

from sympy import sympify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application


_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _extract_expression(text: str) -> str | None:
    patterns = [
        r"=\s*([^=\n]+)$",
        r"calcule\s+(.+)",
        r"resultado\s+(?:de|da)?\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def verify_numeric_answer(question: str, answer: str) -> dict:
    expr_text = _extract_expression(question)
    if not expr_text:
        return {"verified": False, "reason": "no_expression"}
    try:
        expr = parse_expr(expr_text, transformations=_TRANSFORMATIONS)
        expected = sympify(expr)
        numbers = re.findall(r"-?\d+(?:[.,]\d+)?", answer)
        if not numbers:
            return {"verified": False, "reason": "no_number_in_answer"}
        candidate = sympify(numbers[-1].replace(",", "."))
        verified = abs(float(expected.evalf()) - float(candidate.evalf())) < 1e-6
        return {
            "verified": verified,
            "expected": str(expected),
            "found": str(candidate),
        }
    except Exception as exc:
        return {"verified": False, "reason": type(exc).__name__}
