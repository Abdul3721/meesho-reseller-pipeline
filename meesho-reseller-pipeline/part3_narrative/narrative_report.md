# Narrative Report - Meesho Reseller Growth & Alert Intelligence

All numbers below come from Part 1 (SQL) and Part 2 (`growth_engine.py`). Nothing is invented.
Every statement is labelled **FACT** (supported by the data) or **HYPOTHESIS** (a proposed cause, not proven).

---

## 3.2 Worked Narratives

### Narrative 1 - May: Ethnic Wear, +77.1% MoM (flagged)

**Context:** Ethnic Wear category revenue, April vs. May 2026 (INR 104,520.77 to INR 185,107.61).

**Insight:** Ethnic Wear revenue grew **77.1%** month-on-month, well above the 8% alert threshold, and it was the largest increase of any category in May. - **FACT**

**Implication:** Before treating this as a lasting trend, confirm whether a May promotion, festive campaign or new listings in Ethnic Wear overlapped with the jump, and check whether stock levels can support the higher volume in June. The data shows the size of the jump, not its cause. - **HYPOTHESIS** (a May promotional overlap is a possible driver; this data does not prove it).

**Self-score (one sentence each):**
- **Specificity - passes:** it names Ethnic Wear, April and May 2026, and the exact figures 104,520.77, 185,107.61 and 77.1%.
- **Audience fit - passes:** it frames the number as a business outcome for a regional manager, with no SQL or statistical jargon.
- **Completeness - passes:** Context, Insight and Implication are all present and nothing is skipped.
- **Actionability - passes:** it names two concrete checks (the May promotional calendar and June stock levels) instead of a vague "look into it".

### Narrative 2 - June: Ethnic Wear, -58.74% MoM (flagged in the opposite direction)

**Context:** Ethnic Wear category revenue, May vs. June 2026 (INR 185,107.61 to INR 76,371.53).

**Insight:** Ethnic Wear revenue fell **58.74%** month-on-month, the largest absolute swing of any category in June and well beyond the 8% threshold. - **FACT**

**Implication:** Confirm May's promotional calendar for Ethnic Wear before assuming June's drop is organic, since an unusually high May base would exaggerate the decline; then compare June's Ethnic Wear order count (52) with April's (64) to see whether volume or order value moved. - **HYPOTHESIS** (that May's base was promotion-inflated is a possible explanation, not established by this data).

**Self-score (one sentence each):**
- **Specificity - passes:** it names Ethnic Wear, May and June 2026, and the exact figures 185,107.61, 76,371.53 and -58.74%.
- **Audience fit - passes:** it explains the drop in terms of a promotion-inflated base, which a regional manager can act on directly.
- **Completeness - passes:** all three parts are present, with the cause clearly separated from the fact.
- **Actionability - passes:** it names exactly what to verify (May's promo calendar and a June vs. April order-count comparison).

---

## 3.4 Data Masking - Top-Reseller Narrative

Resellers are referenced only by region and alias (`alias_for()` in `masking.py`), never by name.

**Context:** Top resellers by total spend across April-June 2026, limited to those above INR 50,000 (Part 1, Q3).

**Insight:** The highest-spending reseller was **ALIAS-19** (West region) with INR 75,295.09, followed by **ALIAS-22** (West) at INR 73,882.33, **ALIAS-12** (South) at INR 69,936.46, **ALIAS-06** (North) at INR 64,238.97 and **ALIAS-05** (North) at INR 61,825.02. - **FACT**

**Implication:** Two of the top five sit in the West region, so the regional manager should review whether these accounts are getting the right support, since losing one would be felt in the region's total. The idea that these resellers are driven by repeat bulk buying is a possibility only. - **HYPOTHESIS**

**Leak checks** (run in `masking.py`):
- Positive: this narrative contains none of the raw reseller names, so `assert_no_raw_names_leak(text, names)` returns `True`.
- Negative: a version still containing "Mumbai Reseller 1" verbatim returns `False`, proving the check is real and not always-`True`.

---

## 3.3 Chart-Choice Justification (text only - no images)

**Q1. Which month had the highest total revenue?**
Monthly totals are April INR 419,417.43, May INR 444,594.25 and June INR 398,055.24, so **May** is highest. This is a *univariate* comparison of one measure (total revenue) across three months. A **vertical bar chart** is the right choice: the message (May is highest) is clear within 10 seconds, and the **y-axis must start at zero** so bar heights are honest and small differences are not exaggerated. A single series needs **no legend**, and **no 3D** effects should be used since they distort bar heights.

**Q2. What % share does Ethnic Wear represent of April's total revenue?**
Ethnic Wear's April revenue is INR 104,520.77 of INR 419,417.43, a **24.92%** share. This is a part-to-whole question on one month, a *univariate* breakdown by category. A **single horizontal bar chart (or a simple pie with only five slices)** works, but a sorted bar chart is preferred because the share is readable within 10 seconds with direct labels, and the **axis starts at zero**. With one series a **legend is not needed**; if a pie is used it must be **2D, not 3D**.

**Q3. How do the four regions compare on total revenue?**
North INR 337,125.46, West INR 333,106.33, South INR 316,736.68 and East INR 275,098.45. This is a *univariate* comparison of one measure across four categories. A **bar chart sorted by value** makes the ranking clear in 10 seconds; the **y-axis starts at zero** (the regions are close, so a truncated axis would exaggerate the gaps); there is **one series, so no legend**; and **no 3D**. If region were split by month it would become *multivariate*, and then a grouped bar chart with a legend would be justified.
