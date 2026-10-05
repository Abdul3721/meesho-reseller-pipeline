# Agent Spec - Monthly Category Alert Agent

## 1. The Five Components

**Goal** - Keep category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with human approval before any message goes out.

**Tools** (all local, deterministic, no API key)
- `validate_feed(csv_path)` - Part 2 input guardrail over `monthly_category_revenue.csv`
- `mom_growth(previous, current)` - Part 2 MoM % (rounded to 2 decimals)
- `is_flagged(mom_pct, threshold=8.0)` - Part 2 three-state result: `flagged` / `not_flagged` / `escalate_exact_boundary`
- `fill_template(...)` in `part3_narrative/masking.py` - Part 3 Context -> Insight -> Implication drafting
- All imported **unmodified** by `mock_agent_runner.py`; Part 4 does not re-implement Part 2's maths.

**Memory / State** - The previous month's revenue per category, read from the Part 1 CSV (`month, category, revenue, n_orders`). Without it the next run cannot compute MoM.

**Planner** - The ordered 8-step workflow in section 2.

**Feedback Loop** - A human-approval checkpoint. Every drafted message is held (`action_taken = "drafted_and_held_for_approval"`) and is not considered sent until a person approves it. Simulated as a flag in the JSON; there is no email/SMTP integration.

## 2. Ordered Workflow (Planner)

1. Load the monthly revenue feed.
2. Run `validate_feed()`.
3. If **invalid** -> **Hard Stop**: report all errors, run nothing further.
4. If valid -> compute `mom_growth()` for every category vs. the previous month.
5. Run `is_flagged()` on every category.
6. Sort flagged categories by `abs(mom_pct)` descending.
   - 6b. Draft a message (Part 3 template) for **at most the top 3** by magnitude.
7. Log remaining flagged categories beyond the cap as **"suppressed, review manually"** - not dropped.
   - 7b. Separately log any `escalate_exact_boundary` category into `escalated_categories` - never merged into flagged or suppressed.
8. Emit **one** structured JSON object per run.

*Order matters:* you cannot sort before flagging, cannot decide what is suppressed before knowing what is drafted, and escalation is a separate branch from suppression.

## 3. Guardrails

| Guardrail | Rule | Enforced by |
| --- | --- | --- |
| **Input** | `validate_feed` must pass before anything else runs; invalid data is never silently skipped. | Step 3 hard stop |
| **Action** | No message is ever auto-sent - drafts are only held for human approval. Drafts are capped at 3 per run to prevent notification flooding. | Steps 6b-7, `action_taken` |
| **Output** | Every number in a drafted message traces back to a Part 1/2 value; no invented figures; resellers are never named (aliases only). | `fill_template` takes numbers only from its arguments |

## 4. Stopping Conditions

- **Success:** feed valid -> JSON emitted with `action_taken = "drafted_and_held_for_approval"`; waits for human approval.
- **Error (Hard Stop):** feed invalid -> `validation_status = "invalid"`, `action_taken = "hard_stop"`, full `validation_errors` list, no MoM calculation, no drafts, empty `flagged_categories` and `suppressed_categories`.

## 5. Output Schema (identical on every run, success or hard stop)

```json
{
  "run_month": "May",
  "validation_status": "valid | invalid",
  "validation_errors": [],
  "flagged_categories": [
    {"category": "...", "mom_pct": 0.0, "previous_revenue": 0.0,
     "current_revenue": 0.0, "drafted": true, "message": "..."}
  ],
  "suppressed_categories": [],
  "escalated_categories": [],
  "action_taken": "drafted_and_held_for_approval | hard_stop"
}
```

- `flagged_categories` lists every flagged category sorted by `abs(mom_pct)`; `drafted` is `true` for the top 3 (which also carry `message`), `false` for the rest.
- `suppressed_categories` lists the flagged-but-capped names. A category that was never flagged appears in neither list.
- `escalated_categories` is `[]` in the May, June and corrupted-feed scenarios (no real transition lands exactly on 8.0%) but the key always exists.

## 6. Given-When-Then Specs (reused from Part 2, phrased as agent behaviour)

1. **GIVEN** the feed holds Ethnic Wear April 104,520.77 and May 185,107.61, **WHEN** the agent runs for May, **THEN** Ethnic Wear has `mom_pct = 77.1`, is flagged and drafted first.
2. **GIVEN** Beauty & Personal Care May 35,542.11 and June 37,559.07, **WHEN** the agent runs for June, **THEN** `mom_pct = 5.67`, it is `not_flagged` and appears in neither `flagged_categories` nor `suppressed_categories`.
3. **GIVEN** a category moving exactly 100,000 -> 108,000 (8.0%), **WHEN** the agent evaluates it, **THEN** it is placed in `escalated_categories` and never drafted or suppressed.
4. **GIVEN** `corrupted_feed.csv`, **WHEN** the agent runs, **THEN** it returns `validation_status = "invalid"`, `action_taken = "hard_stop"` and exactly the 3 errors from Part 2, in order, with empty flagged and suppressed lists.

## 7. Scenario Acceptance Summary

| Scenario | Drafted (in order) | Suppressed | Neither |
| --- | --- | --- | --- |
| May | Ethnic Wear, Western Wear, Kids Wear | Beauty & Personal Care, Home & Kitchen | - |
| June | Ethnic Wear, Home & Kitchen, Kids Wear | Western Wear | Beauty & Personal Care |
| Corrupted feed | none (hard stop) | none | - |
