"""Schema + normalisation of model output. Never invents values: unknown stays None."""
from __future__ import annotations

import re
from datetime import datetime

from services.calculations import check_consistency

CHARGE_TYPES = {"energy", "fixed", "fpa", "quarterly_adjustment", "surcharge", "meter_rent", "subsidy", "other"}
TAX_TYPES = {"gst", "electricity_duty", "income_tax", "municipal_tax", "other_tax"}
NUM_FIELDS = ["sanctioned_load_kw", "previous_reading", "current_reading", "units_consumed", "total_charges",
              "total_taxes", "current_bill", "arrears", "payable_within_due_date", "payable_after_due_date"]
DATE_FIELDS = ["reading_date", "issue_date", "due_date"]
REQUIRED_FOR_REVIEW = ["provider", "bill_month", "units_consumed", "current_bill", "due_date"]
PROVIDERS = {"KE": "KE", "K-ELECTRIC": "KE", "KELECTRIC": "KE", "KESC": "KE", "LESCO": "LESCO", "IESCO": "IESCO"}

FIELD_LABELS = {
    "provider": "Electricity provider", "tariff": "Tariff / category", "sanctioned_load_kw": "Sanctioned load (kW)",
    "bill_month": "Bill month", "reading_date": "Reading date", "issue_date": "Issue date", "due_date": "Due date",
    "previous_reading": "Previous meter reading", "current_reading": "Current meter reading",
    "units_consumed": "Units consumed (kWh)", "total_charges": "Total charges (Rs.)", "total_taxes": "Total taxes (Rs.)",
    "current_bill": "Current bill amount (Rs.)", "arrears": "Arrears / previous dues (Rs.)",
    "payable_within_due_date": "Payable within due date (Rs.)", "payable_after_due_date": "Payable after due date (Rs.)",
}


def to_number(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if float(v) == float(v) else None
    s = str(v).strip()
    if not s or s.lower() in ("null", "none", "n/a", "not available"):
        return None
    neg = s.upper().endswith("CR") or s.startswith("(") or s.startswith("-")
    s = re.sub(r"(?i)cr|rs\.?|pkr|[,\s()]", "", s).lstrip("-")
    try:
        x = float(s)
    except ValueError:
        return None
    return -abs(x) if neg else x


def clean_date(v, fmt="%Y-%m-%d"):
    if not v:
        return None
    try:
        datetime.strptime(str(v).strip(), fmt)
        return str(v).strip()
    except ValueError:
        return None


def _lines(items, allowed, fallback):
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        amt = to_number(it.get("amount"))
        if amt is None:
            continue
        t = str(it.get("type", fallback)).strip().lower()
        out.append({"type": t if t in allowed else fallback, "amount": amt})
    return out


def normalize_extraction(raw: dict) -> tuple[dict, list[str]]:
    """Return (clean_dict_with_all_keys, warnings)."""
    warns = []
    d = {}
    prov = str(raw.get("provider") or "").upper().replace(" ", "")
    d["provider"] = PROVIDERS.get(prov)
    d["tariff"] = (str(raw["tariff"]).strip() or None) if raw.get("tariff") else None
    d["bill_month"] = clean_date(raw.get("bill_month"), "%Y-%m")
    for f in DATE_FIELDS:
        d[f] = clean_date(raw.get(f))
        if raw.get(f) and d[f] is None:
            warns.append(f"'{FIELD_LABELS[f]}' was read as '{raw.get(f)}', which is not a valid YYYY-MM-DD date, so it was left blank.")
    for f in NUM_FIELDS:
        d[f] = to_number(raw.get(f))
    d["charges"] = _lines(raw.get("charges"), CHARGE_TYPES, "other")
    d["taxes"] = _lines(raw.get("taxes"), TAX_TYPES, "other_tax")
    hist = []
    for h in raw.get("usage_history") or []:
        if isinstance(h, dict) and clean_date(h.get("month"), "%Y-%m") and to_number(h.get("units")) is not None:
            hist.append({"month": h["month"], "units": to_number(h["units"]), "bill_amount": to_number(h.get("bill_amount")),
                         "payment": to_number(h.get("payment"))})
    d["usage_history"] = hist
    d["notes"] = [str(n) for n in (raw.get("notes") or [])][:8]

    missing = [FIELD_LABELS[k] for k in REQUIRED_FOR_REVIEW if d.get(k) in (None, "")]
    if missing:
        warns.append("Not available / unreadable: " + ", ".join(missing) + ". Please check the bill image and edit if needed.")
    warns += check_consistency(d)
    warns += d["notes"]
    return d, warns
