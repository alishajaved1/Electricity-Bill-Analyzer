import pandas as pd
import streamlit as st

from components import charts
from components.logos import COMPANIES, ORDER, company_banner, company_side_card
from components.ui import empty_state, page_header, show_df, stat_card
from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, TRAINING_DIR, get_api_key, money
from services import calculations as calc
from services.extraction import DATE_FIELDS, FIELD_LABELS, NUM_FIELDS, PROVIDERS, clean_date, normalize_extraction, to_number
from services.gemini_service import GeminiError, extract_bill
from utils.files import prepare_upload
from utils.state import add_bill, navigate
from utils.validation import validate_upload

SCALARS = list(FIELD_LABELS.keys())


def scalar_table(d: dict) -> pd.DataFrame:
    return pd.DataFrame({"Field": [FIELD_LABELS[k] for k in SCALARS],
                         "Value": ["" if d.get(k) is None else str(d[k]) for k in SCALARS]})


def apply_edits(original: dict, edited: pd.DataFrame) -> tuple[dict, list[str]]:
    """Convert the edited text table back to typed values. Unparseable entries become None."""
    new, notes = dict(original), []
    for key, val in zip(SCALARS, edited["Value"].tolist()):
        val = (val or "").strip()
        if val == "":
            new[key] = None
        elif key in NUM_FIELDS:
            n = to_number(val)
            new[key] = n
            if n is None:
                notes.append(f"'{FIELD_LABELS[key]}' could not be read as a number and was left blank.")
        elif key in DATE_FIELDS:
            new[key] = clean_date(val)
            if new[key] is None:
                notes.append(f"'{FIELD_LABELS[key]}' must be YYYY-MM-DD and was left blank.")
        elif key == "bill_month":
            new[key] = clean_date(val, "%Y-%m")
            if new[key] is None:
                notes.append("Bill month must be YYYY-MM and was left blank.")
        elif key == "provider":
            new[key] = PROVIDERS.get(val.upper().replace(" ", ""))
            if new[key] is None:
                notes.append("Provider must be KE, LESCO or IESCO and was left blank.")
        else:
            new[key] = val
    return new, notes


def _missing_key_box():
    st.error("**Gemini API key not configured.** Bill extraction needs a key, and no fake results are shown without one.")
    st.markdown("**Local:** copy `.env.example` to `.env` and set `GEMINI_API_KEY=...`, then restart Streamlit.  \n"
                "**Streamlit Cloud:** App → Settings → Secrets → add `GEMINI_API_KEY = \"your key\"`.  \n"
                "Get a free key from Google AI Studio (aistudio.google.com).")


def _save(draft_key):
    draft = st.session_state.analysis_draft
    editor_state = st.session_state.get(f"editor_{draft_key}")
    table = scalar_table(draft["data"])
    if isinstance(editor_state, dict) and editor_state.get("edited_rows"):
        for idx, change in editor_state["edited_rows"].items():
            if "Value" in change:
                table.loc[int(idx), "Value"] = change["Value"]
    final, notes = apply_edits(draft["data"], table)
    changed = final != draft["data"]
    add_bill(final, draft["filename"], draft["warnings"] + notes)
    st.session_state.bills[-1]["status"] = "Saved (edited)" if changed else "Saved"
    st.session_state.analysis_draft = None
    st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1
    st.session_state.pop("practice_file", None)
    st.session_state.flash = "Bill saved to your session history."


def _discard():
    st.session_state.analysis_draft = None
    st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1
    st.session_state.pop("practice_file", None)


def render_bill_details(d: dict, key_prefix: str, editable_key: str | None = None):
    """Shared tabbed view of one extracted bill (used here and on Bill History)."""
    t1, t2, t3 = st.tabs(["Extracted information", "Charges & taxes", "Calculations"])
    with t1:
        if editable_key:
            st.caption("Blank = not available / unreadable on the bill. Edit the Value column only if the bill clearly shows it.")
            st.data_editor(scalar_table(d), hide_index=True, width="stretch", disabled=["Field"], key=f"editor_{editable_key}")
        else:
            t = scalar_table(d)
            t["Value"] = t["Value"].replace("", "Not available")
            show_df(t)
    with t2:
        c, t = calc.charge_rows(d), calc.tax_rows(d)
        a, b = st.columns(2)
        with a:
            st.markdown("**Charges**")
            if c:
                show_df(pd.DataFrame([{"Type": x["type"].replace("_", " ").title(), "Amount (Rs.)": x["amount"]} for x in c]))
            else:
                st.caption("No charge lines extracted.")
            st.caption(f"Printed subtotal: {money(d.get('total_charges'))} · Sum of lines: {money(calc.sum_rows(c))}")
        with b:
            st.markdown("**Taxes**")
            if t:
                show_df(pd.DataFrame([{"Type": x["type"].replace("_", " ").title(), "Amount (Rs.)": x["amount"]} for x in t]))
            else:
                st.caption("No separate tax lines extracted (some bills print only a combined tax).")
            st.caption(f"Printed subtotal: {money(d.get('total_taxes'))} · Sum of lines: {money(calc.sum_rows(t))}")
        pos = [{"category": x["type"].replace("_", " ").title(), "amount": x["amount"]} for x in c + t if x["amount"] > 0]
        if pos:
            charts.show(charts.donut(pd.DataFrame(pos).groupby("category", as_index=False).sum(), "Charge & tax composition"))
    with t3:
        rows = [{"Metric": i["metric"], "Value": "Not available" if i["value"] is None else f"{i['value']:,.2f}",
                 "Type": "Printed on bill" if i["source"] == "printed" else "Calculated by app", "How": i["how"]} for i in calc.analyze_bill(d)]
        if rows:
            show_df(pd.DataFrame(rows))
        else:
            st.caption("Not enough data for calculations.")


def _sync_provider():
    st.session_state.selected_provider = st.session_state.get("prov_radio")


def _clear_practice():
    st.session_state.pop("practice_file", None)
    st.session_state.analysis_draft = None


def render():
    page_header("Analyze Your Electricity Bill", "Upload a KE, LESCO or IESCO bill (PDF, JPG, PNG) to extract and review its details.")
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))
        st.button("View in Bill History", on_click=navigate, args=("Bill History",), key="goto_hist")
    st.session_state.setdefault("analysis_draft", None)
    sel = st.session_state.get("selected_provider")

    logo_col, up_col = st.columns([1, 3.2], gap="large", vertical_alignment="center")
    with logo_col:
        company_side_card(sel)
    with up_col:
        st.radio("Electricity company", ORDER, index=ORDER.index(sel) if sel in ORDER else None, horizontal=True, key="prov_radio",
                 on_change=_sync_provider, format_func=lambda c: COMPANIES[c]["short"])
        up = st.file_uploader("Drag and drop your bill here, or browse", type=list(ALLOWED_EXTENSIONS),
                              key=f"uploader_{st.session_state.get('uploader_key', 0)}",
                              help=f"PDF, JPG, JPEG or PNG, max {MAX_UPLOAD_MB} MB")
        st.caption(f"Supported formats: PDF, JPG, JPEG, PNG (max {MAX_UPLOAD_MB} MB). Your file is sent to Google Gemini for reading. "
                   "Names, addresses and ID numbers are not extracted.")

    practice = st.session_state.get("practice_file")
    if up:
        name, raw = up.name, up.getvalue()
        st.session_state.pop("practice_file", None)
    elif practice and (TRAINING_DIR / practice).is_file():
        name, raw = practice, (TRAINING_DIR / practice).read_bytes()
        st.info(f"Practice bill loaded: **{practice}**")
        st.button("Remove practice bill", key="rm_practice", on_click=_clear_practice)
    else:
        st.session_state.analysis_draft = None
        empty_state("Drop a bill to get started", "Upload a photo, scan or PDF, or load a sample from Training Bills.")
        st.button("Browse training bills", key="to_training", on_click=navigate, args=("Training Bills",))
        return

    err = validate_upload(name, raw)
    if err:
        st.error(err)
        return
    try:
        mime, model_bytes, preview = prepare_upload(name, raw)
    except Exception:  # noqa: BLE001
        st.error("This file could not be opened. It may be corrupted or password-protected.")
        return

    file_key = f"{name}_{len(raw)}"
    col_prev, col_act = st.columns([1, 1.4], gap="large")
    with col_prev:
        st.markdown("**Bill preview**")
        st.image(preview, width="stretch")
    with col_act:
        draft = st.session_state.analysis_draft
        if not draft or draft["key"] != file_key:
            st.markdown("Ready to analyze.")
            if st.button("Analyze Bill", type="primary", key="run_analyze"):
                if not get_api_key():
                    _missing_key_box()
                    return
                data = warns = None
                with st.status("Analyzing your bill...", expanded=True) as status:
                    prog = st.progress(10, text="Preparing the bill image")
                    try:
                        prog.progress(30, text="Reading the bill with Gemini (10-30 seconds)")
                        rawdict = extract_bill(model_bytes, mime)
                        prog.progress(80, text="Validating extracted values")
                        data, warns = normalize_extraction(rawdict)
                        prog.progress(100, text="Done")
                        status.update(label="Extraction complete", state="complete", expanded=False)
                    except GeminiError as e:
                        status.update(label="Extraction failed", state="error")
                        if str(e) == "MISSING_KEY":
                            _missing_key_box()
                        else:
                            st.error(str(e))
                    except Exception:  # noqa: BLE001
                        status.update(label="Extraction failed", state="error")
                        st.error("Something went wrong while processing the bill. Please try again or use a clearer image.")
                if data is None:
                    return
                dup = [b for b in st.session_state.bills if b["data"].get("bill_month") == data["bill_month"]
                       and b["data"].get("provider") == data["provider"] and b["data"].get("current_bill") == data["current_bill"]]
                if dup:
                    warns.append("A bill with the same month, provider and amount is already in your history.")
                st.session_state.analysis_draft = {"key": file_key, "filename": name, "data": data, "warnings": warns}
                st.rerun()
        else:
            d = draft["data"]
            det = d.get("provider")
            st.success("Extraction complete. Please review the details below before saving.")
            company_banner(det or sel, "Detected provider" if det else "Selected provider")
            if det and sel and det != sel:
                st.warning(f"You selected {sel}, but this bill looks like a {det} bill. Showing the detected company.")
            c1, c2 = st.columns(2)
            with c1:
                stat_card("Current bill", money(d.get("current_bill")), "💳", "blue")
            with c2:
                stat_card("Due date", d.get("due_date") or "Not available", "📅", "orange")
            c3, c4 = st.columns(2)
            with c3:
                stat_card("Payable by due date", money(d.get("payable_within_due_date")), "✅", "green")
            with c4:
                stat_card("Payable after due date", money(d.get("payable_after_due_date")), "⚠️", "red")
            for w in draft["warnings"]:
                st.warning(w)

    draft = st.session_state.analysis_draft
    if draft and draft["key"] == file_key:
        st.markdown("### Review extracted data")
        render_bill_details(draft["data"], "draft", editable_key=file_key)
        b1, b2, _ = st.columns([1.3, 1, 2])
        b1.button("Save to session history", type="primary", on_click=_save, args=(file_key,), key="save_bill", width="stretch")
        b2.button("Discard", on_click=_discard, key="discard_bill", width="stretch")
        st.caption("History is temporary: it is kept only for this browser session and is lost on refresh or restart.")
