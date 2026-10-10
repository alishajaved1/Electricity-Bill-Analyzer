import pandas as pd
import streamlit as st

from components import charts
from components.logos import COMPANIES, ORDER, company_card_html
from components.ui import demo_tag, page_header, show_df, stat_card, today_str
from config import kwh, money
from services import calculations as calc
from utils import auth
from utils.state import navigate

DEMO = pd.DataFrame({"month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "amount": [6000, 7500, 10500, 6200, 9800, 12500]})
DEMO_DONUT = pd.DataFrame({"category": ["AC", "Lights", "Fans", "Others"], "amount": [35, 25, 20, 20]})


def _pick(code):
    st.session_state.selected_provider = code
    st.session_state.pop("prov_radio", None)


def company_selector():
    st.subheader("Choose your electricity company")
    sel = st.session_state.get("selected_provider")
    cols = st.columns(3)
    for col, code in zip(cols, ORDER):
        with col:
            st.markdown(company_card_html(code, sel == code), unsafe_allow_html=True)
            st.button("✓ Selected" if sel == code else f"Select {COMPANIES[code]['short']}", key=f"pick_{code}",
                      type="primary" if sel == code else "secondary", on_click=_pick, args=(code,), width="stretch")
    if sel:
        st.button(f"Analyze a {COMPANIES[sel]['short']} bill →", key="pick_go", on_click=navigate, args=("Analyze Bill",))
    st.write("")


def render():
    bills = st.session_state.bills
    page_header(f"Welcome, {auth.current_name()}!", f"Here's your electricity overview · {today_str()}")
    s = calc.dashboard_stats(bills)
    c = st.columns(4)
    with c[0]:
        stat_card("Total Bills Analyzed", s["count"], "🧾", "blue")
    with c[1]:
        stat_card("Average Monthly Bill", money(s["avg_bill"], 0), "💳", "green")
    with c[2]:
        stat_card("Total Units Consumed", kwh(s["total_units"]), "⚡", "orange")
    with c[3]:
        stat_card("Highest Bill", money(s["max_bill"], 0), "📊", "red")
    st.write("")
    company_selector()

    left, right = st.columns([1.5, 1])
    df = calc.bills_frame(bills)
    df = df[df["month"] != "Unknown"] if not df.empty else df
    if not bills:
        demo_tag()
        left.plotly_chart(charts.trend_line(DEMO, "amount", "Monthly Bill Trend (illustrative)", "Rs."), width="stretch", config={"displaylogo": False})
        right.plotly_chart(charts.donut(DEMO_DONUT, "Energy Usage Breakdown (illustrative)", "Demo"), width="stretch", config={"displaylogo": False})
    else:
        with left:
            if df["amount"].notna().sum() >= 1:
                charts.show(charts.trend_line(df.dropna(subset=["amount"]), "amount", "Monthly Bill Trend", "Bill amount (Rs.)"))
            else:
                st.info("No bill amounts available yet.")
        with right:
            bd = calc.breakdown_totals(bills)
            if bd.empty:
                st.info("No charge lines were extracted, so a breakdown cannot be drawn.")
            else:
                charts.show(charts.donut(bd, "Charges & Taxes Breakdown", money(bd["amount"].sum(), 0)))

    l2, r2 = st.columns([1.5, 1])
    with l2:
        st.subheader("Recent Bills")
        if bills:
            t = df.tail(5)[["month", "provider", "units", "amount", "due_date", "status"]].copy()
            t.columns = ["Month", "Provider", "Units (kWh)", "Bill (Rs.)", "Due date", "Status"]
            show_df(t)
        else:
            st.caption("No bills yet. Your analysed bills will appear here.")
        st.button("➕ Analyze another bill", type="primary", on_click=navigate, args=("Analyze Bill",), key="dash_analyze")
    with r2:
        st.subheader("Latest recommendations")
        obs = calc.observations(bills)
        if st.session_state.get("ai_recs"):
            st.markdown(st.session_state["ai_recs"])
        elif obs:
            for o in obs[:4]:
                st.markdown(f'<div class="rec">{o}</div>', unsafe_allow_html=True)
            st.caption("Calculated from your bills. Generate Gemini recommendations on the Reports page.")
        else:
            st.caption("Analyse a bill to see evidence-based recommendations here.")
