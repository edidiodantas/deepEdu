import re

from sympy import sympify
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _extract_expression(text: str) -> str | None:
    cleaned = (text or "").strip()
    if not cleaned:
        return None

    for pattern in (
        r"calcule\s+(.+)",
        r"resolva\s+(.+)",
        r"resultado\s+(?:de|da)?\s*(.+)",
        r"quanto\s+(?:e|é)\s+(.+)",
    ):
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip("?.").strip()

    # Equação "expr = número" → avalia o lado esquerdo (não o número isolado).
    eq = re.match(
        r"^([^=]+?)=\s*(-?\d+(?:[.,]\d+)?)\s*\??$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if eq:
        left = eq.group(1).strip()
        if any(op in left for op in "+-*/^()"):
            return left

    # Expressão aritmética pura.
    compact = cleaned.replace(" ", "").rstrip("?")
    if re.fullmatch(r"[\d\+\-\*/\(\)\.,^]+", compact):
        return compact
    return None


def verify_numeric_answer(question: str, answer: str) -> dict:
    expr_text = _extract_expression(question)
    if not expr_text:
        return {"verified": False, "reason": "no_expression"}
    try:
        expr = parse_expr(expr_text, transformations=_TRANSFORMATIONS)
        expected = sympify(expr)
        expected_f = float(expected.evalf())
        numbers = re.findall(r"-?\d+(?:[.,]\d+)?", answer or "")
        if not numbers:
            return {"verified": False, "reason": "no_number_in_answer", "expected": str(expected)}
        # Prefere o último número "solto" da resposta (resultado final).
        candidate = sympify(numbers[-1].replace(",", "."))
        verified = abs(expected_f - float(candidate.evalf())) < 1e-6
        return {
            "verified": verified,
            "expected": str(expected),
            "found": str(candidate),
        }
    except Exception as exc:
        return {"verified": False, "reason": type(exc).__name__}
