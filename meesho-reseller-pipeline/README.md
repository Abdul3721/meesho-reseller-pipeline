# Meesho Reseller Growth & Alert Intelligence Pipeline

One integrated monthly monitoring pipeline:
**SQL -> Python guardrails -> Narrative -> Agent -> Human approval.**
SQL calculates the numbers, Python validates and applies the growth rule, the narrative layer
communicates verified information, and the agent orchestrates it all. **No message is ever sent
automatically.**

## Zero API keys

The whole pipeline runs **offline with no API key** - narratives use deterministic template-filling
(`part3_narrative/masking.py`), and there is no LLM SDK, email/SMTP or network dependency.
Requires only Python 3.9+ (standard library) and the `sqlite3` CLI (or any SQLite client).

## 1. Regenerate the dataset

```bash
python data/generate_dataset.py
```

Fixed seed (`random.Random(42)`), 24 resellers (4 regions x 6), 900 orders (300 per month, April-June 2026).
Writes `data/resellers.csv`, `data/orders.csv`, `data/meesho_reseller.db`. Do not change the seed, weights or row counts.

## 2. Run every Part, in order

```bash
# Part 1 - SQL (writes the five answers; Q1 is saved as part1_sql/output/monthly_category_revenue.csv)
sqlite3 data/meesho_reseller.db < part1_sql/queries.sql

# Part 2 - guardrail & growth engine (4 required Given-When-Then tests)
cd part2_engine && python -m unittest -v && cd ..

# Part 3 - masking self-test (alias + positive + negative leak test) and template-fill demo
python part3_narrative/masking.py
#   prompt_pack.md and narrative_report.md are the written deliverables

# Part 4 - mock agent: May, June and corrupted-feed scenarios
python part4_agent/mock_agent_runner.py --scenario all
```

## 3. How the Parts connect

```
Part 1 monthly_category_revenue.csv   (month, category, revenue, n_orders)
        |
        v
Part 2 validate_feed() -> mom_growth() -> is_flagged()
        |
        v
Part 3 template-fill (prompt_pack.md logic) consumes Part 2's verified MoM + flag
        |
        v
Part 4 mock_agent_runner.py imports Part 2 UNMODIFIED + reuses Part 3's template-fill
        |
        v
One JSON object per run -> drafts held for human approval
```

Part 4 does not re-implement Part 2's maths - it imports it.

## 4. Part -> workflow pattern

| Part | Pattern it implements |
| --- | --- |
| Part 1 -> Part 2 | Compute real numbers first, then hand off verified values (compute-then-hand-off). |
| Part 2 | Input guardrail: validate before any calculation; three-state result with human escalation at the boundary. |
| Part 3 | Context -> Insight -> Implication drafting with FACT / HYPOTHESIS labels and data masking. |
| Part 4 | Intake -> Summary -> Report Draft -> Validate, with a hard stop on invalid input and a human-approval gate. |

## Repository structure

```
README.md
data/            generate_dataset.py, resellers.csv, orders.csv, meesho_reseller.db
part1_sql/       queries.sql, output/*.csv
part2_engine/    growth_engine.py, test_growth_engine.py, fixtures/{corrupted_feed.csv, monthly_category_revenue.csv}
part3_narrative/ prompt_pack.md, narrative_report.md, masking.py
part4_agent/     agent_spec.md, mock_agent_runner.py
```
