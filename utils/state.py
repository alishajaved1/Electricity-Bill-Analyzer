import uuid
from datetime import datetime

import streamlit as st


def init_state():
    d = st.session_state
    d.setdefault("page", "landing")
    d.setdefault("bills", [])
    d.setdefault("chat_history", [])
    d.setdefault("theme", "Light")
    d.setdefault("users", {})
    d.setdefault("eb_history", [])  # landing-page EnergyBot guide chat
    d.setdefault("eb_ai_calls", 0)


def navigate(page: str):
    st.session_state.page = page


def add_bill(data: dict, filename: str, warnings: list[str]) -> str:
    bill_id = uuid.uuid4().hex[:8]
    st.session_state.bills.append({
        "id": bill_id, "filename": filename, "data": data, "warnings": warnings,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "Saved",
    })
    return bill_id


def remove_bill(bill_id: str):
    st.session_state.bills = [b for b in st.session_state.bills if b["id"] != bill_id]


def clear_bills():
    st.session_state.bills = []
    st.session_state.chat_history = []
