import streamlit as st

from components import charts
from components.ui import empty_state, page_header, show_df, stat_card
from config import get_api_key, kwh, money
from services import calculations as calc
from services.gemini_service import GeminiError, recommendations
from utils.exports import bills_csv, bills_json, report_html


def render():
    page_header("Reports", "Summaries, comparisons and recommendations based on your analysed bills.")
    bills = st.session_state.bills
    if not bills:
        empty_state("No data for a report yet", "Analyze and save at least one bill to generate a report.")
        return
    s = calc.dashboard_stats(bills)
    c = st.columns(4)
    with c[0]:
        stat_card("Bills analysed", s["count"], "🧾", "blue")
    with c[1]:
        stat_card("Average bill", money(s["avg_bill"], 0), "💳", "green")
    with c[2]:
        stat_card("Total units", kwh(s["total_units"]), "⚡", "orange")
    with c[3]:
        stat_card("Highest bill", money(s["max_bill"], 0), "📊", "red")

    df = calc.add_changes(calc.bills_frame(bills))
    st.subheader("Units and cost comparison")
    t = df[["month", "provider", "units", "amount", "units_change", "amount_change"]].copy()
    t.columns = ["Month", "Provider", "Units (kWh)", "Bill (Rs.)", "Units change", "Bill change (Rs.)"]
    show_df(t.round(1))
    if len(df) < 2:
        st.caption("Month-over-month analysis needs at least two bills.")

    st.subheader("Charges and taxes overview")
    bd = calc.breakdown_totals(bills)
    if bd.empty:
        st.caption("No charge or tax lines were extracted.")
    else:
        a, b = st.columns([1, 1])
        with a:
            charts.show(charts.donut(bd, "Where your money goes", money(bd["amount"].sum(), 0)))
        with b:
            bd2 = bd.copy()
            bd2.columns = ["Category", "Total (Rs.)"]
            show_df(bd2.round(2))

    st.subheader("Recommendations")
    obs = calc.observations(bills)
    for o in obs:
        st.markdown(f'<div class="rec">{o}</div>', unsafe_allow_html=True)
    if not obs:
        st.caption("Not enough data for calculated observations.")
    if st.button("✨ Generate AI recommendations", key="gen_recs", disabled=not get_api_key()):
        with st.spinner("Asking Gemini..."):
            try:
                st.session_state.ai_recs = recommendations(bills, "\n".join(obs) or "No computed observations.")
            except GeminiError as e:
                st.error(str(e))
    if not get_api_key():
        st.caption("Set GEMINI_API_KEY to enable AI-generated recommendations.")
    if st.session_state.get("ai_recs"):
        st.markdown(st.session_state["ai_recs"])

    st.subheader("Download")
    d = st.columns(3)
    d[0].download_button("⬇ CSV", bills_csv(bills), "electricity_report.csv", "text/csv", width="stretch", key="dl_csv_r")
    d[1].download_button("⬇ JSON", bills_json(bills), "electricity_report.json", "application/json", width="stretch", key="dl_json_r")
    d[2].download_button("🖨 Printable report (HTML)", report_html(bills, st.session_state.get("ai_recs", "")), "electricity_report.html",
                         "text/html", width="stretch", key="dl_html_r")
    st.caption("Open the HTML report in your browser and use Print → Save as PDF for a PDF copy.")
