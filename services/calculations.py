"""All arithmetic is done here in Python - never by the language model."""
from __future__ import annotations

import pandas as pd


def num(v):
    if isinstance(v, bool) or v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def charge_rows(d: dict) -> list[dict]:
    return [x for x in (d.get("charges") or []) if num(x.get("amount")) is not None]


def tax_rows(d: dict) -> list[dict]:
    return [x for x in (d.get("taxes") or []) if num(x.get("amount")) is not None]


def sum_rows(rows) -> float | None:
    return round(sum(num(r["amount"]) for r in rows), 2) if rows else None


def analyze_bill(d: dict) -> list[dict]:
    """Derived metrics. Each item: metric, value, how (formula + inputs), source (printed|calculated)."""
    out = []
    units, cur, prev = num(d.get("units_consumed")), num(d.get("current_reading")), num(d.get("previous_reading"))
    bill, within, after = num(d.get("current_bill")), num(d.get("payable_within_due_date")), num(d.get("payable_after_due_date"))
    tc, tt = num(d.get("total_charges")), num(d.get("total_taxes"))
    cs, ts = sum_rows(charge_rows(d)), sum_rows(tax_rows(d))

    if units is not None:
        out.append({"metric": "Units consumed (kWh)", "value": units, "how": "Printed on the bill", "source": "printed"})
    if cur is not None and prev is not None:
        diff = round(cur - prev, 2)
        note = "Meter reading difference (current - previous)."
        if units is not None and abs(diff - units) > 1:
            note += " Differs from billed units - bill may use a multiplying factor, multiple registers or net metering."
        out.append({"metric": "Reading difference", "value": diff, "how": f"{cur:,.0f} - {prev:,.0f}. {note}", "source": "calculated"})
    if cs is not None:
        out.append({"metric": "Sum of charge lines (Rs.)", "value": cs, "how": f"Sum of {len(charge_rows(d))} extracted charge lines", "source": "calculated"})
    if ts is not None:
        out.append({"metric": "Sum of tax lines (Rs.)", "value": ts, "how": f"Sum of {len(tax_rows(d))} extracted tax lines", "source": "calculated"})
    total_charges = tc if tc is not None else cs
    total_taxes = tt if tt is not None else ts
    if total_charges is not None:
        out.append({"metric": "Total charges (Rs.)", "value": total_charges,
                    "how": "Printed subtotal" if tc is not None else "Calculated from charge lines", "source": "printed" if tc is not None else "calculated"})
    if total_taxes is not None:
        out.append({"metric": "Total taxes (Rs.)", "value": total_taxes,
                    "how": "Printed subtotal" if tt is not None else "Calculated from tax lines", "source": "printed" if tt is not None else "calculated"})
    if bill is not None and units and units > 0:
        out.append({"metric": "Average cost per unit (Rs./kWh)", "value": round(bill / units, 2),
                    "how": f"Current bill {bill:,.2f} / units {units:,.0f} (includes taxes and all charges)", "source": "calculated"})
    elif units is not None and units <= 0:
        out.append({"metric": "Average cost per unit (Rs./kWh)", "value": None,
                    "how": "Not calculated: units are zero or negative (possible net metering or credit)", "source": "calculated"})
    if total_taxes is not None and total_charges not in (None, 0):
        out.append({"metric": "Taxes as % of charges", "value": round(total_taxes / total_charges * 100, 2),
                    "how": f"Taxes {total_taxes:,.2f} / charges {total_charges:,.2f}", "source": "calculated"})
    if total_taxes is not None and bill not in (None, 0) and bill > 0:
        out.append({"metric": "Taxes as % of current bill", "value": round(total_taxes / bill * 100, 2),
                    "how": f"Taxes {total_taxes:,.2f} / current bill {bill:,.2f}", "source": "calculated"})
    if within is not None and after is not None:
        out.append({"metric": "Late-payment extra (Rs.)", "value": round(after - within, 2),
                    "how": f"Payable after due date {after:,.2f} - payable by due date {within:,.2f}", "source": "calculated"})
    return out


def check_consistency(d: dict) -> list[str]:
    warns = []
    cs, ts = sum_rows(charge_rows(d)), sum_rows(tax_rows(d))
    tc, tt = num(d.get("total_charges")), num(d.get("total_taxes"))
    if cs is not None and tc is not None and abs(cs - tc) > 1:
        warns.append(f"Charge lines add up to {cs:,.2f} but the printed subtotal is {tc:,.2f}. A line may be missing or misread.")
    if ts is not None and tt is not None and abs(ts - tt) > 1:
        warns.append(f"Tax lines add up to {ts:,.2f} but the printed tax subtotal is {tt:,.2f}. A line may be missing or misread.")
    cur, prev, units = num(d.get("current_reading")), num(d.get("previous_reading")), num(d.get("units_consumed"))
    if None not in (cur, prev, units) and abs((cur - prev) - units) > 1:
        warns.append("Billed units differ from (current - previous reading). This can be normal (multiplying factor, several meter registers, net metering).")
    return warns


# ---------- multi-bill helpers ----------
def bills_frame(bills) -> pd.DataFrame:
    rows = []
    for b in bills:
        d = b["data"]
        rows.append({"id": b["id"], "month": d.get("bill_month") or "Unknown", "provider": d.get("provider") or "Unknown",
                     "units": num(d.get("units_consumed")), "amount": num(d.get("current_bill")),
                     "due_date": d.get("due_date") or "Not available", "status": b.get("status", "Saved")})
    df = pd.DataFrame(rows, columns=["id", "month", "provider", "units", "amount", "due_date", "status"])
    return df.sort_values("month", kind="stable").reset_index(drop=True) if not df.empty else df


def add_changes(df: pd.DataFrame) -> pd.DataFrame:
    """Month-over-month change columns (NaN when a value is missing)."""
    df = df.copy()
    if df.empty:
        return df
    df["amount_change"] = df["amount"].diff()
    df["amount_change_pct"] = df["amount"].pct_change(fill_method=None) * 100
    df["units_change"] = df["units"].diff()
    df["units_change_pct"] = df["units"].pct_change(fill_method=None) * 100
    return df.replace([float("inf"), float("-inf")], pd.NA)


def dashboard_stats(bills) -> dict:
    df = bills_frame(bills)
    amounts = df["amount"].dropna() if not df.empty else pd.Series(dtype=float)
    units = df["units"].dropna() if not df.empty else pd.Series(dtype=float)
    return {
        "count": len(bills),
        "avg_bill": float(amounts.mean()) if len(amounts) else None,
        "total_units": float(units.sum()) if len(units) else None,
        "max_bill": float(amounts.max()) if len(amounts) else None,
    }


def breakdown_totals(bills) -> pd.DataFrame:
    """Aggregate charge + tax lines by type across bills."""
    rows = []
    for b in bills:
        for c in charge_rows(b["data"]):
            rows.append({"category": str(c.get("type", "other")).replace("_", " ").title(), "amount": num(c["amount"])})
        for t in tax_rows(b["data"]):
            rows.append({"category": "Tax: " + str(t.get("type", "other_tax")).replace("_", " ").title(), "amount": num(t["amount"])})
    if not rows:
        return pd.DataFrame(columns=["category", "amount"])
    df = pd.DataFrame(rows).groupby("category", as_index=False)["amount"].sum()
    return df[df["amount"] > 0].sort_values("amount", ascending=False)


def history_frame(bills) -> pd.DataFrame:
    """Usage history printed on the bills themselves (deduplicated by month)."""
    rows = {}
    for b in bills:
        for h in b["data"].get("usage_history") or []:
            m = h.get("month")
            if m and num(h.get("units")) is not None:
                rows[m] = {"month": m, "units": num(h["units"]), "bill_amount": num(h.get("bill_amount"))}
    return pd.DataFrame(sorted(rows.values(), key=lambda r: r["month"]), columns=["month", "units", "bill_amount"])


def observations(bills) -> list[str]:
    """Plain, evidence-based observations computed in Python (no AI, no invented savings)."""
    from config import money
    out = []
    df = add_changes(bills_frame(bills))
    if df.empty:
        return out
    latest_bill = max(bills, key=lambda b: b["data"].get("bill_month") or "")
    d = latest_bill["data"]
    month = d.get("bill_month") or "the latest bill"
    items = {i["metric"]: i for i in analyze_bill(d)}
    if "Taxes as % of current bill" in items:
        out.append(f"Taxes are {items['Taxes as % of current bill']['value']:.1f}% of the {month} bill ({items['Taxes as % of current bill']['how']}).")
    if "Average cost per unit (Rs./kWh)" in items and items["Average cost per unit (Rs./kWh)"]["value"] is not None:
        out.append(f"Average all-in cost for {month} was {money(items['Average cost per unit (Rs./kWh)']['value'])} per kWh ({items['Average cost per unit (Rs./kWh)']['how']}).")
    if "Late-payment extra (Rs.)" in items and items["Late-payment extra (Rs.)"]["value"] and items["Late-payment extra (Rs.)"]["value"] > 0:
        out.append(f"Paying after the due date adds {money(items['Late-payment extra (Rs.)']['value'])} ({items['Late-payment extra (Rs.)']['how']}).")
    arrears = num(d.get("arrears"))
    if arrears is not None and arrears > 1:
        out.append(f"Arrears of {money(arrears)} are carried forward in the {month} bill.")
    elif arrears is not None and arrears < -1:
        out.append(f"The {month} bill shows a credit balance of {money(abs(arrears))} brought forward.")
    units = num(d.get("units_consumed"))
    if units is not None and units <= 0:
        out.append(f"Billed units for {month} are {units:,.0f}; this can indicate net metering or an adjustment, so unit-based ratios were skipped.")
    if len(df) >= 2:
        last = df.iloc[-1]
        if last["amount_change_pct"] is not pd.NA and pd.notna(last["amount_change_pct"]):
            out.append(f"Bill amount changed {last['amount_change']:+,.0f} Rs. ({last['amount_change_pct']:+.1f}%) from {df.iloc[-2]['month']} to {last['month']}.")
        if pd.notna(last["units_change"]):
            out.append(f"Units changed {last['units_change']:+,.0f} kWh from {df.iloc[-2]['month']} to {last['month']}.")
    return out
