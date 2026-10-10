import html
import json
from datetime import datetime

import pandas as pd

from config import APP_NAME, money
from services.calculations import bills_frame, charge_rows, tax_rows


def bills_csv(bills) -> bytes:
    rows = []
    for b in bills:
        d = b["data"]
        rows.append({
            "bill_month": d.get("bill_month"), "provider": d.get("provider"), "tariff": d.get("tariff"),
            "sanctioned_load_kw": d.get("sanctioned_load_kw"), "reading_date": d.get("reading_date"),
            "issue_date": d.get("issue_date"), "due_date": d.get("due_date"),
            "previous_reading": d.get("previous_reading"), "current_reading": d.get("current_reading"),
            "units_consumed": d.get("units_consumed"), "total_charges": d.get("total_charges"),
            "total_taxes": d.get("total_taxes"), "current_bill": d.get("current_bill"),
            "arrears": d.get("arrears"), "payable_within_due_date": d.get("payable_within_due_date"),
            "payable_after_due_date": d.get("payable_after_due_date"), "status": b["status"],
        })
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def bills_json(bills) -> bytes:
    return json.dumps([{"id": b["id"], "saved_at": b["saved_at"], "status": b["status"], **b["data"]} for b in bills],
                      indent=2, ensure_ascii=False).encode("utf-8")


def report_html(bills, recommendations: str = "") -> bytes:
    """Self-contained printable report (use browser Print > Save as PDF)."""
    df = bills_frame(bills)
    parts = [f"<h1>{APP_NAME} - Report</h1><p>Generated {datetime.now():%Y-%m-%d %H:%M}. "
             f"Based on {len(bills)} bill(s) analysed in this session.</p>"]
    if not df.empty:
        t = df[["month", "provider", "units", "amount", "due_date"]].copy()
        t.columns = ["Month", "Provider", "Units (kWh)", "Current bill (Rs.)", "Due date"]
        parts.append("<h2>Bills</h2>" + t.to_html(index=False, border=0, na_rep="Not available"))
    for b in bills:
        d = b["data"]
        parts.append(f"<h2>{html.escape(str(d.get('bill_month') or 'Unknown month'))} - {html.escape(str(d.get('provider') or ''))}</h2>")
        c, t = charge_rows(d), tax_rows(d)
        if c:
            parts.append("<h3>Charges</h3><ul>" + "".join(f"<li>{html.escape(x['type'])}: {money(x['amount'])}</li>" for x in c) + "</ul>")
        if t:
            parts.append("<h3>Taxes</h3><ul>" + "".join(f"<li>{html.escape(x['type'])}: {money(x['amount'])}</li>" for x in t) + "</ul>")
        parts.append(f"<p>Current bill: <b>{money(d.get('current_bill'))}</b> | Payable by due date: "
                     f"<b>{money(d.get('payable_within_due_date'))}</b></p>")
    if recommendations:
        parts.append("<h2>AI recommendations</h2><div style='white-space:pre-wrap'>" + html.escape(recommendations) + "</div>")
    css = ("body{font-family:Segoe UI,Arial,sans-serif;max-width:860px;margin:30px auto;color:#1b2340}"
           "h1{color:#1c2461}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #dde3f5;padding:6px;text-align:left}"
           "th{background:#eef1ff}")
    return f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(parts)}</body></html>".encode("utf-8")
