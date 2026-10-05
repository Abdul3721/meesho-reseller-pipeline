"""Part 4 - Mock agent runner.

Orchestrates the pipeline end to end:
    load feed -> validate_feed -> (hard stop if invalid) -> mom_growth -> is_flagged
    -> sort by abs(mom) -> draft top 3 -> suppress the rest -> escalate boundary cases -> emit ONE JSON.

Part 2 functions are IMPORTED UNMODIFIED and Part 3's template-fill is reused.
Nothing is ever sent: drafts are held for human approval. No API key, no network.

Usage (from anywhere):
    python part4_agent/mock_agent_runner.py --scenario may
    python part4_agent/mock_agent_runner.py --scenario june
    python part4_agent/mock_agent_runner.py --scenario corrupted
    python part4_agent/mock_agent_runner.py --scenario all
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "part2_engine"))
sys.path.insert(0, os.path.join(ROOT, "part3_narrative"))

from growth_engine import is_flagged, mom_growth, validate_feed  # noqa: E402  (Part 2, unmodified)
from masking import fill_template                               # noqa: E402  (Part 3 template-fill)

MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
MAX_DRAFTS = 3          # notification-flood guardrail
THRESHOLD = 8.0

FEED = os.path.join(ROOT, "part2_engine", "fixtures", "monthly_category_revenue.csv")
CORRUPTED = os.path.join(ROOT, "part2_engine", "fixtures", "corrupted_feed.csv")

# (csv path, run_month) for each acceptance scenario
SCENARIOS = {
    "may": (FEED, "May"),
    "june": (FEED, "June"),
    "corrupted": (CORRUPTED, "July"),
}


def _previous_month(month: str) -> str:
    return MONTH_ORDER[MONTH_ORDER.index(month) - 1]


def _load_revenue(csv_path: str) -> dict:
    """{month: {category: revenue}} - this is the agent's memory/state."""
    data: dict = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data.setdefault(row["month"], {})[row["category"]] = float(row["revenue"])
    return data


def run_agent(csv_path: str, run_month: str) -> dict:
    result = {
        "run_month": run_month,
        "validation_status": "valid",
        "validation_errors": [],
        "flagged_categories": [],
        "suppressed_categories": [],
        "escalated_categories": [],
        "action_taken": "drafted_and_held_for_approval",
    }

    # Steps 1-3: load feed, validate, HARD STOP if invalid (nothing else runs)
    ok, errors = validate_feed(csv_path)
    if not ok:
        result["validation_status"] = "invalid"
        result["validation_errors"] = errors
        result["action_taken"] = "hard_stop"
        return result

    revenue = _load_revenue(csv_path)
    prev_month = _previous_month(run_month)

    # Steps 4-5: MoM + three-state flag for every category
    rows = []
    for category, current in revenue[run_month].items():
        previous = revenue[prev_month][category]
        pct = mom_growth(previous, current)
        rows.append({"category": category, "mom_pct": pct, "previous_revenue": previous,
                     "current_revenue": current, "state": is_flagged(pct, THRESHOLD)})

    # Step 6: sort flagged by MAGNITUDE (abs), descending
    flagged = sorted((r for r in rows if r["state"] == "flagged"),
                     key=lambda r: abs(r["mom_pct"]), reverse=True)

    # Step 6b/7: draft top 3, suppress (log, never drop) the rest
    for rank, r in enumerate(flagged):
        entry = {"category": r["category"], "mom_pct": r["mom_pct"],
                 "previous_revenue": r["previous_revenue"],
                 "current_revenue": r["current_revenue"], "drafted": rank < MAX_DRAFTS}
        if entry["drafted"]:
            entry["message"] = fill_template(r["category"], r["previous_revenue"],
                                             r["current_revenue"], r["mom_pct"],
                                             run_month, prev_month)
        else:
            result["suppressed_categories"].append(r["category"])  # "suppressed, review manually"
        result["flagged_categories"].append(entry)

    # Step 7b: exact-boundary cases go to humans - never merged into flagged or suppressed
    result["escalated_categories"] = [r["category"] for r in rows
                                      if r["state"] == "escalate_exact_boundary"]
    # not_flagged categories appear in none of the lists. Step 8: caller emits the JSON.
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock Meesho monitoring agent (never sends anything).")
    parser.add_argument("--scenario", choices=[*SCENARIOS, "all"], default="all")
    parser.add_argument("--csv", help="custom feed path (use with --month)")
    parser.add_argument("--month", help="run month for --csv, e.g. June")
    args = parser.parse_args()

    if args.csv:
        print(json.dumps(run_agent(args.csv, args.month), indent=2, ensure_ascii=False))
        return
    names = list(SCENARIOS) if args.scenario == "all" else [args.scenario]
    for name in names:
        path, month = SCENARIOS[name]
        print(f"=== scenario: {name} ===")
        print(json.dumps(run_agent(path, month), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
