import streamlit as st

from components.logos import company_banner
from components.ui import empty_state, page_header
from config import kwh, money
from services import calculations as calc
from utils.exports import bills_csv, bills_json
from utils.state import clear_bills, navigate, remove_bill
from views.analyze import render_bill_details


def _confirm_clear():
    clear_bills()
    st.session_state.confirm_clear = False
    st.session_state.pop("view_bill_id", None)


def render():
    page_header("Your Bill History", "View and manage the bills analysed in this session.")
    st.info("⏳ Session history is temporary. It is kept in memory and disappears if the page is refreshed or the app restarts. Download your data to keep it.")
    bills = st.session_state.bills
    if not bills:
        empty_state("Nothing here yet", "Analyzed bills you save will be listed here.")
        st.button("Analyze a bill", type="primary", on_click=navigate, args=("Analyze Bill",), key="hist_go")
        return

    d1, d2, d3, _ = st.columns([1, 1, 1.3, 2])
    d1.download_button("⬇ CSV", bills_csv(bills), "bills.csv", "text/csv", width="stretch", key="dl_csv_h")
    d2.download_button("⬇ JSON", bills_json(bills), "bills.json", "application/json", width="stretch", key="dl_json_h")
    if d3.button("🗑 Clear history", width="stretch", key="clear_h"):
        st.session_state.confirm_clear = True
    if st.session_state.get("confirm_clear"):
        st.warning("Remove all bills and chat history from this session? This cannot be undone.")
        y, n, _ = st.columns([1, 1, 3])
        y.button("Yes, clear", type="primary", on_click=_confirm_clear, key="yes_clear")
        n.button("Cancel", on_click=lambda: st.session_state.update(confirm_clear=False), key="no_clear")

    heads = st.columns([1.1, 1, 1, 1.3, 1.2, 1.2, 0.9, 0.9])
    for h, t in zip(heads, ["Bill month", "Provider", "Units", "Current bill", "Due date", "Status", "", ""]):
        h.markdown(f"**{t}**")
    for b in bills:
        d = b["data"]
        cols = st.columns([1.1, 1, 1, 1.3, 1.2, 1.2, 0.9, 0.9], vertical_alignment="center")
        cols[0].write(d.get("bill_month") or "Not available")
        cols[1].write(d.get("provider") or "Not available")
        cols[2].write(kwh(calc.num(d.get("units_consumed"))))
        cols[3].write(money(d.get("current_bill")))
        cols[4].write(d.get("due_date") or "Not available")
        cols[5].markdown(f'<span class="pill {"o" if "edited" in b["status"] else "g"}">{b["status"]}</span>', unsafe_allow_html=True)
        cols[6].button("View", key=f"view_{b['id']}", on_click=lambda i=b["id"]: st.session_state.update(view_bill_id=i))
        cols[7].button("Remove", key=f"rm_{b['id']}", on_click=remove_bill, args=(b["id"],))

    vid = st.session_state.get("view_bill_id")
    sel = next((b for b in bills if b["id"] == vid), None)
    if sel:
        st.divider()
        st.subheader(f"Bill details · {sel['data'].get('bill_month') or 'Unknown month'} · {sel['data'].get('provider') or ''}")
        company_banner(sel['data'].get('provider'))
        st.caption(f"Saved {sel['saved_at']} from file '{sel['filename']}'")
        for w in sel["warnings"]:
            st.warning(w)
        render_bill_details(sel["data"], "view")
