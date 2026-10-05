# Prompt Pack - Category Movement Alert

> Works fully offline. `masking.fill_template()` fills this template deterministically.
> No LLM API and no API key is needed. (An LLM could be plugged in later behind an
> environment variable, but every check below must still pass with zero keys set.)

## 1. Trigger

Run this prompt for a category **only when** Part 2's `is_flagged(mom_pct)` returns `"flagged"`
(i.e. `abs(mom_pct) > 8.0`). Categories that return `"not_flagged"` get no prompt.
A category that returns `"escalate_exact_boundary"` is **not** drafted - it goes to a human via
`escalated_categories`.

## 2. Input list

| Placeholder | Meaning | Source |
| --- | --- | --- |
| `{category}` | Category name, e.g. Ethnic Wear | Part 1 CSV |
| `{previous_revenue}` | Revenue in the prior month (INR) | Part 1 CSV |
| `{current_revenue}` | Revenue in the current month (INR) | Part 1 CSV |
| `{mom_pct}` | Month-on-month % change | Part 2 `mom_growth()` |
| `{month}` | Current month name, e.g. May | Part 1 CSV |
| `{prev_month}` | Prior month name, e.g. April | Part 1 CSV |

## 3. Prompt

```text
You are drafting a short monthly update for a regional category manager at Meesho.
Write for a business reader, not a data engineer. Use ONLY the values supplied below.

Inputs:
  category         = {category}
  previous_revenue = {previous_revenue}   (month: {prev_month})
  current_revenue  = {current_revenue}    (month: {month})
  mom_pct          = {mom_pct}

Write exactly three parts:

CONTEXT     - State what is being measured and over what period
              (category revenue, {prev_month} vs. {month}).
INSIGHT     - State what happened using the exact mom_pct and revenue values.
              End the sentence with the label "FACT".
IMPLICATION - Give one specific, actionable next step that names exactly what to check or do.
              If it proposes a cause, label it "HYPOTHESIS" and say the data does not prove it.

Rules:
  1. No number outside the supplied placeholders may ever be stated.
  2. Never name an individual reseller; refer to resellers only by region + alias.
  3. Never present a cause as proven. Causes are always HYPOTHESIS.
  4. Do not say "look into {category}" - name the specific thing to verify.
```

## 4. Checklist (validate every output before it is considered ready)

- [ ] Every number in the text appears in the supplied inputs (`previous_revenue`, `current_revenue`, `mom_pct`) - nothing invented.
- [ ] Category name, `{month}` and `{prev_month}` are named correctly (specific, no vague references).
- [ ] Context, Insight and Implication are all present - nothing skipped.
- [ ] The Insight is labelled **FACT**; any proposed cause in the Implication is labelled **HYPOTHESIS**.
- [ ] The Implication names a concrete next step (not "look into it").
- [ ] No raw reseller name appears (`assert_no_raw_names_leak(text, names)` returns `True`).
- [ ] Direction matches the sign of `mom_pct` (grew vs. fell) and the tone does not overstate.

## Self-scoring against the 4 refinement criteria

Applied to the prompt itself and to the template-filled outputs:

- **Specificity - passes:** the prompt requires the exact category, months and numbers via placeholders, so no vague references can appear.
- **Audience fit - passes:** it instructs the writer to address a regional manager in business language, not SQL or statistical jargon.
- **Completeness - passes:** it mandates all three parts (Context, Insight, Implication) and the checklist verifies none is skipped.
- **Actionability - passes:** rule 4 forbids vague suggestions and requires the Implication to name exactly what to check or do.
