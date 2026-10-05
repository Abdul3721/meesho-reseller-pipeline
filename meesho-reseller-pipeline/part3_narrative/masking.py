"""Part 3 - data masking + deterministic template-fill. No LLM, no API key, fully offline."""

# ---------------------------------------------------------------- masking
def alias_for(reseller_id: str) -> str:
    """RS019 -> ALIAS-19, RS006 -> ALIAS-06.

    Slices off the "RS0" prefix of the 5-char ID and keeps the remaining digits
    exactly as they are (no re-padding / re-formatting).
    """
    return "ALIAS-" + reseller_id[3:]


def assert_no_raw_names_leak(text: str, names) -> bool:
    """True if NO raw reseller name appears in `text`; False the moment one does."""
    for name in names:
        if name and name in text:
            return False
    return True


# ------------------------------------------------- narrative template-fill
# Mirrors the Prompt section of prompt_pack.md (Context -> Insight -> Implication).
NARRATIVE_TEMPLATE = (
    "**Context:** {category} category revenue, {prev_month} vs. {month} 2026 "
    "(INR {previous_revenue} -> INR {current_revenue}).\n\n"
    "**Insight:** {category} revenue {direction} {abs_mom_pct}% month-on-month "
    "(MoM = {mom_pct}%). - FACT\n\n"
    "**Implication:** {implication} - HYPOTHESIS, not proven by this data."
)

_IMPLICATION_UP = (
    "Confirm whether a {month} promotion, price change or new listings drove the rise "
    "in {category} before treating it as repeatable, and check that stock can support it"
)
_IMPLICATION_DOWN = (
    "Check whether a {prev_month} promotion or stock-out inflated the {prev_month} base "
    "for {category}, and review {month} pricing and inventory before assuming the drop is organic"
)


def fill_template(category, previous_revenue, current_revenue, mom_pct, month, prev_month) -> str:
    """Deterministic template-fill. Every number comes from the supplied arguments only."""
    going_up = mom_pct > 0
    implication = (_IMPLICATION_UP if going_up else _IMPLICATION_DOWN).format(
        category=category, month=month, prev_month=prev_month
    )
    return NARRATIVE_TEMPLATE.format(
        category=category,
        month=month,
        prev_month=prev_month,
        previous_revenue=f"{previous_revenue:,.2f}",
        current_revenue=f"{current_revenue:,.2f}",
        mom_pct=f"{mom_pct:+.2f}",
        abs_mom_pct=f"{abs(mom_pct):.2f}",
        direction="grew" if going_up else "fell",
        implication=implication,
    )


# ----------------------------------------------------------------- self-test
if __name__ == "__main__":
    RAW_NAMES = [
        "Mumbai Reseller 1", "Mumbai Reseller 4", "Hyderabad Reseller 6",
        "Lucknow Reseller 6", "Jaipur Reseller 5", "Ahmedabad Reseller 6",
    ]
    assert alias_for("RS019") == "ALIAS-19"
    assert alias_for("RS006") == "ALIAS-06"

    safe = f"West reseller {alias_for('RS019')} led total spend."
    assert assert_no_raw_names_leak(safe, RAW_NAMES) is True            # positive case

    leaky = "Mumbai Reseller 1 led total spend in the West region."
    assert assert_no_raw_names_leak(leaky, RAW_NAMES) is False           # NEGATIVE case

    print("masking self-test passed (alias + positive + negative leak test)")
    print()
    print(fill_template("Ethnic Wear", 104520.77, 185107.61, 77.10, "May", "April"))
