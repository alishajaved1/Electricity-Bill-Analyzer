import importlib.metadata as md
import platform

import streamlit as st

from components.ui import page_header
from config import APP_NAME, APP_VERSION, get_api_key, get_model_name
from utils.state import clear_bills

PKGS = ["streamlit", "google-genai", "python-dotenv", "pandas", "Pillow", "plotly", "pymupdf"]


def render():
    page_header("Settings", "Preferences, AI status, privacy and session data.")
    a, b = st.columns(2)
    with a:
        st.subheader("Appearance")
        st.selectbox("Theme preference", ["Light", "Soft blue"], key="theme")
        st.subheader("Display units")
        st.text_input("Currency", "Pakistani Rupee (Rs. / PKR)", disabled=True)
        st.text_input("Energy unit", "kWh", disabled=True)
        st.subheader("Session data")
        st.caption(f"{len(st.session_state.bills)} bill(s) and {len(st.session_state.chat_history)} chat message(s) in this session.")
        if st.button("Clear all session data", key="settings_clear"):
            st.session_state.confirm_settings_clear = True
        if st.session_state.get("confirm_settings_clear"):
            st.warning("This removes saved bills and chat history. Continue?")
            y, n = st.columns(2)
            if y.button("Yes, clear", type="primary", key="settings_yes"):
                clear_bills()
                st.session_state.pop("ai_recs", None)
                st.session_state.confirm_settings_clear = False
                st.success("Session data cleared.")
            if n.button("Cancel", key="settings_no"):
                st.session_state.confirm_settings_clear = False
                st.rerun()
    with b:
        st.subheader("AI assistant status")
        if get_api_key():
            st.success("Gemini API key detected (hidden for security).")
        else:
            st.error("Gemini API key not configured. Add GEMINI_API_KEY to `.env` (local) or Streamlit Secrets (cloud).")
        st.text_input("Gemini model", get_model_name(), disabled=True, help="Change with GEMINI_MODEL in .env or Secrets")
        st.subheader("Privacy")
        st.markdown("- Bills are sent to Google Gemini only when you click **Analyze Bill** or ask EnergyBot.\n"
                    "- Names, addresses, CNIC and account/meter numbers are not extracted or stored.\n"
                    "- No database: data lives in Streamlit session state (server memory for your session) and is lost on refresh/restart.\n"
                    "- Login is a demo; passwords are hashed in memory and never stored in plaintext.")
        st.subheader("About")
        st.caption(f"{APP_NAME} v{APP_VERSION} · Python {platform.python_version()}")
        rows = []
        for p in PKGS:
            try:
                rows.append(f"{p} {md.version(p)}")
            except md.PackageNotFoundError:
                rows.append(f"{p} (not installed)")
        st.caption(" · ".join(rows))
