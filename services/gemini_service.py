"""Google Gemini integration (official `google-genai` SDK). Key comes from config only."""
from __future__ import annotations

import json
import re

from config import get_api_key, get_model_name

try:
    from google import genai
    from google.genai import types
except ImportError:  # keeps the rest of the app alive if the SDK is missing
    genai = None
    types = None


class GeminiError(Exception):
    """Carries a message that is safe to show to the user."""


EXTRACTION_PROMPT = """You are a careful data-extraction engine for Pakistani electricity bills (K-Electric/KE, LESCO, IESCO).
The bill may be a scan, screenshot or tilted photo, partly in Urdu. Grey boxes hide personal data.
Return ONLY one JSON object with exactly these keys:
provider ("KE"|"LESCO"|"IESCO"), tariff (string exactly as printed), sanctioned_load_kw (number),
bill_month ("YYYY-MM"), reading_date, issue_date, due_date ("YYYY-MM-DD"),
previous_reading, current_reading, units_consumed (numbers),
charges: [{"type": "energy|fixed|fpa|quarterly_adjustment|surcharge|meter_rent|subsidy|other", "amount": number}],
total_charges (printed subtotal), taxes: [{"type": "gst|electricity_duty|income_tax|municipal_tax|other_tax", "amount": number}],
total_taxes (printed subtotal), current_bill, arrears, payable_within_due_date, payable_after_due_date,
usage_history: [{"month": "YYYY-MM", "units": number, "bill_amount": number|null, "payment": number|null}] (only from the printed bill-history table; payment only if a paid/payment column is printed; include every printed row, never invent rows),
notes: [short strings describing anything unreadable or uncertain].
Rules:
- Copy values exactly as printed. Do not recalculate, round or correct anything.
- Amounts are plain numbers in PKR (no commas or currency). Credits (e.g. 38209CR, or a minus sign) are negative. Subsidies are negative.
- Use null for anything not printed, blank, hidden by a grey box or unreadable. NEVER guess or invent a value.
- charges: one entry per line of the charges section; skip blank or 0 lines; keep repeated types separate. Use fpa for FPA/FCA.
- taxes: one entry per line of the tax/government section (classify by section, not by name). If only a combined tax is printed, use [] and fill total_taxes.
- If several late-payment amounts are shown, payable_after_due_date is the highest one.
- Do NOT output names, addresses, CNIC, account/reference/consumer/meter numbers.
- Dates: convert printed dates such as "22 SEP 26", "22-Apr-2026" or "21st Apr 2026" to YYYY-MM-DD (two-digit years are 20xx). bill_month such as "SEP 26" or "Jun-26" becomes "2026-09" / "2026-06".
- tariff: exactly as printed (e.g. A1-R, A-1a(01)). sanctioned_load_kw: from Sanc Load / S.Load / San Load.
- units_consumed: the units billed for the current month as printed. arrears: previous dues carried forward, keep the printed sign (CR is negative); null if blank.
- current_bill: the printed amount for this month's bill. payable_within_due_date / payable_after_due_date: printed payable amounts.
- Output JSON only, no markdown."""

CHAT_SYSTEM = """You are EnergyBot, an assistant inside the Electricity Bill Analyzer website.
Answer in clear, simple English (the user may write in Roman Urdu; you may reply in the same mix if they do).
Use ONLY the BILL DATA provided below for facts about the user's bills. If the data does not contain what is needed, say so plainly - never invent numbers, tariffs or rates.
Clearly label: [From your bill] for extracted facts, [Calculated] for arithmetic you derive from those facts (show the numbers used), and [General tip] for generic energy-saving advice.
Never claim a specific rupee saving unless it can be computed from the data; otherwise say it is not possible to quantify from the bill.
Keep answers concise. Do not repeat personal identifiers."""


def friendly_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "api key" in msg or "api_key" in msg or "permission" in msg or "401" in msg or "403" in msg or "unauthenticated" in msg:
        return "The Gemini API key was rejected. Check that GEMINI_API_KEY is correct and enabled in Google AI Studio."
    if "429" in msg or "quota" in msg or "resource_exhausted" in msg or "rate" in msg:
        return "Gemini quota or rate limit reached. Please wait a minute and try again."
    if "404" in msg or "not found" in msg or "not supported" in msg:
        return f"The model '{get_model_name()}' is not available for your API key. Set GEMINI_MODEL to another model in your .env / Secrets."
    if "timeout" in msg or "connect" in msg or "network" in msg or "unavailable" in msg or "503" in msg:
        return "Could not reach the Gemini service. Check your internet connection and try again."
    return "Gemini could not complete the request. Please try again."


def _client():
    if genai is None:
        raise GeminiError("The google-genai package is not installed. Run: pip install -r requirements.txt")
    key = get_api_key()
    if not key:
        raise GeminiError("MISSING_KEY")
    return genai.Client(api_key=key)


def _parse_json(text: str) -> dict:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            return json.loads(m.group(0))
        raise


def extract_bill(data: bytes, mime: str) -> dict:
    """Send the bill image/PDF to Gemini and return the raw parsed JSON dict."""
    client = _client()
    try:
        resp = client.models.generate_content(
            model=get_model_name(),
            contents=[types.Part.from_bytes(data=data, mime_type=mime), EXTRACTION_PROMPT],
            config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json"),
        )
    except Exception as exc:  # noqa: BLE001
        raise GeminiError(friendly_error(exc)) from exc
    try:
        parsed = _parse_json(resp.text)
    except Exception as exc:  # noqa: BLE001
        raise GeminiError("The AI response could not be understood as bill data. Try a clearer image.") from exc
    if not isinstance(parsed, dict):
        raise GeminiError("The AI response was not in the expected format. Try again.")
    return parsed


def bills_context(bills) -> str:
    """Compact, non-identifying bill data for the assistant (identifiers are never extracted)."""
    if not bills:
        return "No bills have been analysed yet."
    items = []
    for b in bills:
        d = {k: v for k, v in b["data"].items() if k != "notes"}
        items.append(d)
    return json.dumps(items, ensure_ascii=False)


def chat(history: list[dict], question: str, bills) -> str:
    client = _client()
    contents = [types.Content(role="user" if m["role"] == "user" else "model", parts=[types.Part(text=m["content"])])
                for m in history[-10:]]
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    system = CHAT_SYSTEM + "\n\nBILL DATA (JSON, amounts in PKR):\n" + bills_context(bills)
    try:
        resp = client.models.generate_content(
            model=get_model_name(), contents=contents,
            config=types.GenerateContentConfig(system_instruction=system, temperature=0.3))
        return (resp.text or "").strip() or "I could not generate an answer. Please rephrase your question."
    except Exception as exc:  # noqa: BLE001
        raise GeminiError(friendly_error(exc)) from exc


def recommendations(bills, stats_text: str) -> str:
    q = ("Using only the bill data and these Python-computed statistics, give 4-6 short, evidence-based recommendations "
         "(billing anomalies, taxes, usage changes, practical energy-saving habits). Label each as [From your bill] or "
         "[General tip]. Do not invent rupee savings.\n\nStatistics:\n" + stats_text)
    return chat([], q, bills)


ANSWER_SYSTEM = """You answer a customer's question about ONE Pakistani electricity bill (the bill image is attached).
Rules:
- Write in plain English, even if parts of the bill are in Urdu.
- Use ONLY information visible on the bill, the extracted JSON and the Python-computed facts provided. Never use outside tariff or rate knowledge.
- Get numbers right. Prefer the Python-computed facts for arithmetic; re-check any other calculation carefully and show the figures used.
- If the bill does not show a needed value, say so plainly instead of guessing.
- Label any estimate as an estimate and explain how it was calculated.
- If the question can be read in more than one way, state the meaning you used or answer both.
- Never include names, addresses, CNIC, account/reference/consumer/meter numbers.
- Be concise: 2-5 sentences."""


def answer_question(data: bytes, mime: str, bill_json: str, facts: str, question: str) -> str:
    """Answer one competition-style question about one bill (image + extracted JSON + Python facts)."""
    client = _client()
    text = f"QUESTION: {question}\n\nEXTRACTED BILL JSON:\n{bill_json}\n\nPYTHON-COMPUTED FACTS:\n{facts}"
    try:
        resp = client.models.generate_content(
            model=get_model_name(), contents=[types.Part.from_bytes(data=data, mime_type=mime), text],
            config=types.GenerateContentConfig(system_instruction=ANSWER_SYSTEM, temperature=0.1))
    except Exception as exc:  # noqa: BLE001
        raise GeminiError(friendly_error(exc)) from exc
    out = (resp.text or "").strip()
    if not out:
        raise GeminiError("Gemini returned an empty answer.")
    return out


def guide_chat(history: list[dict], question: str, system: str, max_tokens: int = 500) -> str:
    """Website-guide chat (EnergyBot on the landing page). No bill data is ever passed in here."""
    client = _client()
    contents = [types.Content(role="user" if m["role"] == "user" else "model", parts=[types.Part(text=m["content"])])
                for m in history[-6:]]
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    try:
        resp = client.models.generate_content(
            model=get_model_name(), contents=contents,
            config=types.GenerateContentConfig(system_instruction=system, temperature=0.2, max_output_tokens=max_tokens))
        return (resp.text or "").strip()
    except Exception as exc:  # noqa: BLE001
        raise GeminiError(friendly_error(exc)) from exc
