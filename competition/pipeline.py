"""Competition pipeline: bill images + CSV templates -> completed level1.csv / level2.csv.

Level 1: Gemini extraction -> normalised to the exact schema (services.extraction).
Level 2: Gemini answers each question using the bill image, the Level 1 JSON and Python-computed facts.
No answer is ever hand-written: failures are logged and clearly worded, never silently faked.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from config import get_api_key, get_model_name, get_provider
from services import calculations as calc
from services.extraction import normalize_extraction
from competition.facts import all_facts
from services.gemini_service import GeminiError, answer_question, extract_bill
from utils.files import prepare_upload

L1_COLS = ["bill_id", "json"]
L2_COLS = ["bill_id", "question_id", "question", "answer"]
SCHEMA_ORDER = ["provider", "tariff", "sanctioned_load_kw", "bill_month", "reading_date", "issue_date", "due_date",
                "previous_reading", "current_reading", "units_consumed", "charges", "total_charges", "taxes", "total_taxes",
                "current_bill", "arrears", "payable_within_due_date", "payable_after_due_date"]
EXTS = (".png", ".jpg", ".jpeg")


def _n(x):
    if x is None:
        return None
    return int(x) if float(x).is_integer() else round(float(x), 2)


def to_level1(clean: dict) -> dict:
    """Exactly the competition schema, in order; unknown values are null, lists may be empty."""
    out = {}
    for k in SCHEMA_ORDER:
        v = clean.get(k)
        if k == "charges":
            v = [{"type": c["type"], "amount": _n(c["amount"])} for c in (v or []) if c.get("amount") not in (None, 0)]
        elif k == "taxes":
            v = [{"type": t["type"], "amount": _n(t["amount"])} for t in (v or [])]
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            v = _n(v)
        out[k] = v
    return out


def empty_level1() -> dict:
    return to_level1({"charges": [], "taxes": []})


def find_bill(bills_dir: Path, bill_id: str) -> Path | None:
    for p in bills_dir.iterdir():
        if p.stem == bill_id and p.suffix.lower() in EXTS:
            return p
    return None


def bill_facts(clean: dict) -> str:
    """Python-computed facts handed to the model (it phrases them, it does not calculate)."""
    l1 = to_level1(clean)
    base = [f"{i['metric']}: {i['value']} ({i['how']})" for i in calc.analyze_bill(clean) if i["value"] is not None]
    return "\n".join(base + [all_facts(clean, l1)]) or "No computed facts available."


def _retry(fn, attempts=3, wait=20):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except GeminiError as e:
            if str(e) == "MISSING_KEY":
                raise
            last = e
            time.sleep(wait * (i + 1))
    raise last


def _read_template(path: Path, cols: list[str]) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != cols:
            raise ValueError(f"{path.name}: expected columns {cols}, found {reader.fieldnames}")
        return list(reader)


def _write(path: Path, cols: list[str], rows: list[dict]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def run(bills_dir: str, templates_dir: str, out_dir: str, delay: float = 3.0, log=print) -> dict:
    if get_provider() != "google":
        raise SystemExit("MODEL_PROVIDER must be 'google' (only Google Gemini is implemented).")
    if not get_api_key():
        raise SystemExit("No API key found. Set API_KEY (or GEMINI_API_KEY) in .env - see .env.example.")
    bills_dir, templates_dir, out_dir = Path(bills_dir), Path(templates_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    l1_rows = _read_template(templates_dir / "level1.csv", L1_COLS)
    l2_rows = _read_template(templates_dir / "level2.csv", L2_COLS)
    log(f"Model: {get_model_name()} | Level 1 rows: {len(l1_rows)} | Level 2 rows: {len(l2_rows)}")
    errors, cache = [], {}

    for row in l1_rows:
        bid = row["bill_id"]
        path = find_bill(bills_dir, bid)
        clean, payload = None, None
        if path is None:
            errors.append(f"{bid}: image not found in {bills_dir}")
            log(f"[L1] {bid}: image NOT FOUND")
        else:
            try:
                mime, mbytes, _ = prepare_upload(path.name, path.read_bytes())
                clean, _w = normalize_extraction(_retry(lambda: extract_bill(mbytes, mime)))
                payload = (mime, mbytes)
                log(f"[L1] {bid}: ok")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{bid}: extraction failed ({e})")
                log(f"[L1] {bid}: FAILED - {e}")
            time.sleep(delay)
        cache[bid] = (clean, payload)
        row["json"] = json.dumps(to_level1(clean) if clean else empty_level1(), ensure_ascii=False, separators=(",", ":"))
    _write(out_dir / "level1.csv", L1_COLS, l1_rows)

    for row in l2_rows:
        bid, qid = row["bill_id"], row["question_id"]
        clean, payload = cache.get(bid, (None, None))
        try:
            if not clean or not payload:
                raise GeminiError("the bill could not be read")
            l1 = json.dumps(to_level1(clean), ensure_ascii=False)
            row["answer"] = _retry(lambda: answer_question(payload[1], payload[0], l1, bill_facts(clean), row["question"]))
            log(f"[L2] {bid} {qid}: ok")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{bid} {qid}: {e}")
            row["answer"] = f"An answer could not be generated automatically for this question ({e})."
            log(f"[L2] {bid} {qid}: FAILED - {e}")
        time.sleep(delay)
    _write(out_dir / "level2.csv", L2_COLS, l2_rows)
    log(f"Done. Wrote {out_dir/'level1.csv'} and {out_dir/'level2.csv'}. Problems: {len(errors)}")
    return {"level1_rows": len(l1_rows), "level2_rows": len(l2_rows), "errors": errors}
