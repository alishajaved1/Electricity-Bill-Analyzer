import streamlit as st

from components import charts
from components.ui import empty_state, page_header, show_df, stat_card
from config import kwh, money
from services import calculations as calc


def render():
    page_header("Usage Insights", "Understand your consumption patterns from the bills you analysed.")
    bills = st.session_state.bills
    if not bills:
        empty_state("No bills analysed yet", "Analyze at least two bills from different months to see reliable historical trends.")
        return
    df = calc.add_changes(calc.bills_frame(bills))
    df = df[df["month"] != "Unknown"].reset_index(drop=True)
    u = df.dropna(subset=["units"])

    if len(df) < 2:
        st.info("Only one bill with a known month is available. Upload more bills for month-over-month comparison. "
                "Meanwhile, here is the usage history printed on your bill (as extracted).")
    if not u.empty:
        c = st.columns(3)
        with c[0]:
            stat_card("Average consumption", kwh(u["units"].mean()), "⚡", "orange")
        hi, lo = u.loc[u["units"].idxmax()], u.loc[u["units"].idxmin()]
        with c[1]:
            stat_card("Highest month", f"{hi['month']} ({hi['units']:,.0f})", "🔺", "red")
        with c[2]:
            stat_card("Lowest month", f"{lo['month']} ({lo['units']:,.0f})", "🔻", "green")
        st.write("")
        a, b = st.columns(2)
        with a:
            charts.show(charts.bar(u, "units", "Monthly electricity units", "Units (kWh)"))
        with b:
            amt = df.dropna(subset=["amount"])
            if not amt.empty:
                charts.show(charts.trend_line(amt, "amount", "Monthly bill amounts", "Bill amount (Rs.)"))
    if len(df) >= 2:
        a, b = st.columns(2)
        with a:
            if df["units_change"].notna().any():
                charts.show(charts.change_bar(df, "units_change", "Month-over-month change in units", "kWh change"))
        with b:
            if df["amount_change"].notna().any():
                charts.show(charts.change_bar(df, "amount_change", "Month-over-month change in bill", "Rs. change"))
        t = df[["month", "units", "units_change", "units_change_pct", "amount", "amount_change", "amount_change_pct"]].copy()
        t.columns = ["Month", "Units", "Units change", "Units %", "Bill (Rs.)", "Bill change", "Bill %"]
        st.subheader("Consumption comparison")
        show_df(t.round(1))

    hist = calc.history_frame(bills)
    if not hist.empty:
        st.subheader("Usage history printed on your bills")
        st.caption("Taken from the bill-history table on the uploaded bills (as extracted by AI; check against the original).")
        charts.show(charts.bar(hist, "units", "Printed monthly usage history", "Units (kWh)", color="#3b4de0"))
