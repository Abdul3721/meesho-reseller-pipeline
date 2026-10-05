"""Part 2 - Python Guardrail & Growth-Detection Engine.

Three functions, imported UNMODIFIED by part4_agent/mock_agent_runner.py:
    mom_growth(previous, current)  -> float
    is_flagged(mom_pct, threshold) -> str   ("flagged" | "not_flagged" | "escalate_exact_boundary")
    validate_feed(csv_path)        -> (bool, list[str])
"""
import csv


def mom_growth(previous: float, current: float) -> float:
    """Month-on-Month growth percentage, rounded to 2 decimals."""
    if previous == 0:
        raise ValueError("previous revenue is 0; MoM growth is undefined")
    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    """Three-state result - deliberately NOT a boolean.

    abs(mom_pct) >  threshold -> "flagged"
    abs(mom_pct) <  threshold -> "not_flagged"
    abs(mom_pct) == threshold -> "escalate_exact_boundary" (a human decides)
    """
    magnitude = abs(mom_pct)
    if magnitude > threshold:
        return "flagged"
    if magnitude < threshold:
        return "not_flagged"
    return "escalate_exact_boundary"


def validate_feed(csv_path: str) -> tuple[bool, list[str]]:
    """Input guardrail over a month,category,revenue,n_orders CSV.

    Checks four problems on EVERY row (one pass, errors kept in row order):
      missing category / missing revenue / non-numeric revenue / negative revenue.
    Returns (True, []) if clean, else (False, [error strings...]).
    """
    errors: list[str] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line = reader.line_num  # header is line 1, first data row is line 2
            month = (row.get("month") or "").strip()
            category = (row.get("category") or "").strip()
            revenue = (row.get("revenue") or "").strip()

            if not category:
                errors.append(f"line {line}: missing category (month={month})")

            if not revenue:
                errors.append(f"line {line}: missing revenue (category={category})")
                continue

            try:
                value = float(revenue)
            except ValueError:
                errors.append(f"line {line}: revenue not numeric: {revenue!r}")
                continue

            if value < 0:
                errors.append(
                    f"line {line}: negative revenue ({value}) for category={category}"
                )
    return (len(errors) == 0, errors)
