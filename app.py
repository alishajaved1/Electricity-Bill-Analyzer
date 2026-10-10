"""Electricity Bill Analyzer - run with:  streamlit run app.py"""
import streamlit as st

from components.styles import inject_css
from components.ui import logo
from config import APP_NAME, PAGE_ICONS, PAGES
from utils import auth
from utils.state import init_state, navigate
from views import analyze, assistant, auth_pages, dashboard, history, landing, reports, settings, training, trends

st.set_page_config(page_title=APP_NAME, page_icon="⚡", layout="wide", initial_sidebar_state="auto")
init_state()
inject_css()

PRIVATE = {"Dashboard": dashboard.render, "Analyze Bill": analyze.render, "Training Bills": training.render, "Usage Trends": trends.render,
           "Bill History": history.render, "AI Assistant": assistant.render, "Reports": reports.render,
           "Settings": settings.render}
PUBLIC = {"landing": landing.render, "login": auth_pages.login_page, "signup": auth_pages.signup_page}


def sidebar():
    with st.sidebar:
        st.markdown(logo(), unsafe_allow_html=True)
        st.write("")
        for p in PAGES:
            st.button(f"{PAGE_ICONS[p]}  {p}", key=f"nav_{p}", type="primary" if st.session_state.page == p else "secondary",
                      on_click=navigate, args=(p,), width="stretch")
        st.write("")
        st.button("⏻  Logout", key="logout", width="stretch", on_click=lambda: (auth.logout(), navigate("landing")))
        st.caption("🧪 Demo session · data is temporary")


def main():
    page = st.session_state.page
    if auth.is_authenticated():
        if page not in PRIVATE:
            page = st.session_state.page = "Dashboard"
        sidebar()
        PRIVATE[page]()
        return
    if page in PRIVATE:  # protect dashboard pages
        page = st.session_state.page = "login"
        st.warning("Please log in to access that page.")
    st.markdown('<style>section[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none}</style>',
                unsafe_allow_html=True)
    PUBLIC.get(page, landing.render)()


main()
