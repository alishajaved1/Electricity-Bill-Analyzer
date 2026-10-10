"""Deterministic (Python) facts for the Level 2 questions. The language model only phrases these; it never does the maths.

Everything here is computed from values printed on the bill (usage_history table + Level 1 fields). Nothing is guessed:
if the history is missing, the fact says so.
"""
from __future__ import annotations

from datetime import date

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SUMMER, WINTER = (6, 7, 8), (12, 1, 2)


def _label(ym: str) -> str:
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def _g(x) -> str:
    return f"{x:,.2f}".rstrip("0").rstrip(".")


def _prior_month(ym: str, back: int) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    t = y * 12 + (m - 1) - back
    return f"{t // 12:04d}-{t % 12 + 1:02d}"


def _slope(ys: list[float]) -> tuple[float, float]:
    n = len(ys)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
    return b, my - b * mx


def history_facts(clean: dict) -> list[str]:
    """Facts about the printed month-by-month history. `clean` is the normalised extraction."""
    cur_month, cur_units = clean.get("bill_month"), clean.get("units_consumed")
    hist = sorted((clean.get("usage_history") or []), key=lambda h: h["month"])
    prev = [h for h in hist if h["month"] != cur_month]  # the table may or may not repeat the current month
    out = []
    if not hist:
        return ["No month-by-month usage history could be read from this bill, so history-based answers (highest month, averages, "
                "seasonal comparison, trend, forecast) are NOT available - say so instead of guessing."]
    out.append("History table (month: units): " + ", ".join(f"{_label(h['month'])}: {_g(h['units'])}" for h in hist)
               + f". Months in table: {len(hist)}. Current bill month: {cur_month or 'unknown'} with {cur_units if cur_units is not None else 'unknown'} billed units.")

    series = {h["month"]: h["units"] for h in hist}
    if cur_month and cur_units is not None:
        series.setdefault(cur_month, cur_units)
    top = max(series.items(), key=lambda kv: kv[1])
    ties = [m for m, v in series.items() if v == top[1]]
    out.append(f"Highest units month (history + current): {', '.join(_label(m) for m in ties)} with {_g(top[1])} units.")
    top_h = max(hist, key=lambda h: h["units"])
    out.append(f"Highest units month within the printed history table only: {_label(top_h['month'])} ({_g(top_h['units'])}).")

    vals = [h["units"] for h in hist]
    avg = sum(vals) / len(vals)
    out.append(f"Average units over the {len(vals)} history months: {avg:.2f}.")
    if cur_units is not None:
        d = cur_units - avg
        out.append(f"Current month {_g(cur_units)} vs that average: {d:+.2f} units ({d / avg * 100:+.1f}%)." if avg else "")
        if cur_month in [h["month"] for h in hist]:
            others = [h["units"] for h in hist if h["month"] != cur_month]
            if others:
                a2 = sum(others) / len(others)
                out.append(f"Average excluding the current month ({len(others)} months): {a2:.2f}; current month is {cur_units - a2:+.2f} vs that.")

    if cur_month:
        ly = _prior_month(cur_month, 12)
        if ly in series:
            d = (cur_units - series[ly]) if cur_units is not None else None
            if d is not None:
                word = "more" if d > 0 else "fewer" if d < 0 else "the same number of"
                out.append(f"Same month last year ({_label(ly)}): {_g(series[ly])} units; current {_g(cur_units)} -> {abs(d):g} {word} units ({d / series[ly] * 100:+.1f}%).")
        else:
            out.append(f"Same month last year ({_label(ly)}) is NOT in the printed history, so a year-on-year comparison is not possible.")

    summer = [h["units"] for h in hist if int(h["month"][5:]) in SUMMER]
    winter = [h["units"] for h in hist if int(h["month"][5:]) in WINTER]
    if summer and winter:
        sa, wa = sum(summer) / len(summer), sum(winter) / len(winter)
        out.append(f"Summer (Jun-Aug) months in history: {len(summer)}, total {_g(sum(summer))}, average {sa:.2f}. "
                   f"Winter (Dec-Feb) months: {len(winter)}, total {_g(sum(winter))}, average {wa:.2f}. "
                   f"Difference of averages (summer - winter): {sa - wa:+.2f} units/month; difference of totals: {sum(summer) - sum(winter):+g}"
                   + ("" if len(summer) == len(winter) else " (the number of summer and winter months differs, so prefer the averages)") + ".")
    else:
        out.append("The history does not contain both summer (Jun-Aug) and winter (Dec-Feb) months, so a summer-vs-winter difference cannot be computed.")

    last3 = hist[-3:]
    if len(last3) == 3:
        u = [h["units"] for h in last3]
        direction = "up" if u[0] < u[1] < u[2] else "down" if u[0] > u[1] > u[2] else "mixed (not steadily up or down)"
        out.append("Last 3 history months: " + ", ".join(f"{_label(h['month'])} {_g(h['units'])}" for h in last3)
                   + f" -> {direction}; change first to last: {u[2] - u[0]:+g} units.")

    if len(vals) >= 3:
        b, a = _slope(vals)
        proj = max(0.0, a + b * len(vals))
        out.append(f"ESTIMATE for next month: linear trend over {len(vals)} history months = {proj:.0f} units (slope {b:+.2f} units/month); "
                   f"simple average of the last 3 months = {sum(vals[-3:]) / 3:.0f}; all-month average = {avg:.0f}. "
                   "Seasonality is not modelled, so label this a rough estimate.")

    amounts = [h["bill_amount"] for h in hist if h.get("bill_amount") is not None]
    if amounts:
        out.append(f"Printed monthly bill amounts: {len(amounts)} months, total {_g(sum(amounts))}, average {sum(amounts) / len(amounts):.2f} per month "
                   "(set-aside figure for even spreading; use 12 months if all 12 are present).")
    else:
        out.append("No monthly bill amounts are printed in the history, so an even monthly set-aside cannot be computed from history; "
                   "only the current bill can be cited.")

    paid = [h for h in hist if h.get("payment") is not None or h.get("paid") is not None]
    if paid:
        unpaid = [h for h in hist if (h.get("payment") in (0, 0.0)) or (h.get("paid") is False)]
        out.append(f"Payment info present for {len(paid)} of {len(hist)} months; months showing zero/unpaid: "
                   + (", ".join(_label(h["month"]) for h in unpaid) if unpaid else "none") + ".")
    else:
        out.append("The history does not show payment status/amounts paid per month, so whether every bill was paid CANNOT be confirmed from the bill; "
                   "say that and mention any arrears figure printed on the bill.")
    return [x for x in out if x]


def bill_level_facts(l1: dict) -> list[str]:
    out = []
    w, a, cur, units = l1.get("payable_within_due_date"), l1.get("payable_after_due_date"), l1.get("current_bill"), l1.get("units_consumed")
    if w is not None and a is not None:
        out.append(f"Late payment surcharge printed/implied: payable after due date {_g(a)} - payable within due date {_g(w)} = {_g(a - w)}"
                   + (f" ({(a - w) / w * 100:.1f}% of the on-time amount)." if w else "."))
    else:
        out.append("Payable-after-due-date and/or payable-within-due-date is not available, so the late surcharge cannot be computed.")
    fpa = [c["amount"] for c in l1.get("charges") or [] if c["type"] == "fpa"]
    out.append(f"FPA/FCA charge lines (Level 1 type fpa): {fpa if fpa else 'none printed'}; bill month {l1.get('bill_month')}.")
    if cur is not None and units:
        out.append(f"ESTIMATE if the same units repeat: current bill {_g(cur)} / {_g(units)} units = {cur / units:.2f} per unit "
                   f"(average, includes fixed charges and taxes); the current bill itself ({_g(cur)}) is the best bill-based estimate for the same units. "
                   "Do not use outside tariff rates.")
    tt, tc = l1.get("total_taxes"), l1.get("current_bill")
    if tt is not None and tc:
        out.append(f"Taxes are {tt / tc * 100:.1f}% of the current bill ({_g(tt)} of {_g(tc)}).")
    if l1.get("current_reading") is not None and l1.get("previous_reading") is not None and units is not None:
        diff = l1["current_reading"] - l1["previous_reading"]
        out.append(f"Reading difference {_g(diff)} vs billed units {_g(units)}"
                   + ("" if abs(diff - units) <= 1 else " - these differ, which can indicate net metering or a multiplier; only say so if the bill itself shows it."))
    return out


def all_facts(clean: dict, l1: dict) -> str:
    return "\n".join(bill_level_facts(l1) + history_facts(clean))
