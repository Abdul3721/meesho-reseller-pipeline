# Part 1 Output Notes

Files here: `monthly_category_revenue.csv` (Q1, 15 rows), `q2_region_revenue.csv`, `q3_top_resellers.csv`,
`q4_zero_order_reseller.csv`, `q5_june_delivered_aov.csv`.

## COUNT(*) vs COUNT(order_id) for RS024

RS024 (Ahmedabad Reseller 6) has never placed an order. After `resellers LEFT JOIN orders`, the
unmatched reseller **still produces one row** in the result, with NULL in every column that would
come from `orders`.

| Query (for RS024) | Result | Why |
| --- | --- | --- |
| `COUNT(*)` | **1** | Counts rows. The LEFT JOIN row exists even though every joined column is NULL. |
| `COUNT(order_id)` | **0** | Counts only non-NULL values of `order_id`; it is NULL on the unmatched row. |

So `COUNT(*)` cannot be trusted to detect zero orders - it reports one order that does not exist.
`COUNT(order_id)` (or filtering `WHERE order_id IS NULL`) is the correct test. Both queries are in
`part1_sql/queries.sql` (Q4b) and return these values side by side.
