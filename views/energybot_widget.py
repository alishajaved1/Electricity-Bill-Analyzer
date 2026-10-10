"""Floating EnergyBot (landing page): a fixed button that opens a chat dialog.

Uses native Streamlit widgets only (st.dialog + a form), so it never interferes with other inputs and
interactions inside the dialog rerun only the dialog, not the whole landing page.
"""
import html

import streamlit as st

from components.logos import asset_uri
from services import energybot_kb as kb
from services.energybot import MAX_QUESTION_CHARS, reply

MAX_HISTORY = 40


def open_bot():
    st.session_state.eb_open = True


def _avatar() -> str:
    uri = asset_uri("energybot_avatar.png", "image/png")
    return uri or "🤖"


def _ask(question: str):
    st.session_state.eb_pending = question


def _clear():
    st.session_state.eb_history = []


def _show(role: str, text: str):
    with st.chat_message(role, avatar=_avatar() if role == "assistant" else "🙂"):
        st.markdown(text)


@st.dialog(kb.BOT_TITLE, width="large")
def _dialog():
    uri = asset_uri("energybot_avatar.png", "image/png")
    img = f'<img src="{uri}" alt="EnergyBot avatar">' if uri else ""
    st.markdown(f'<div class="eb-head">{img}<div><b>{html.escape(kb.BOT_NAME)}</b><small><span class="eb-dot"></span>Website guide · answers from built-in help</small></div></div>',
                unsafe_allow_html=True)
    history = st.session_state.setdefault("eb_history", [])

    box = st.container(height=340, border=True)
    if not history:
        st.caption("Try a question:")
        cols = st.columns(2)
        for i, s in enumerate(kb.SUGGESTED_QUESTIONS):
            cols[i % 2].button(s, key=f"eb_sug_{i}", on_click=_ask, args=(s,), width="stretch")

    with st.form("eb_form", clear_on_submit=True, border=False):
        c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
        text = c1.text_input("Message EnergyBot", placeholder="Ask about the website, uploads, privacy…", max_chars=MAX_QUESTION_CHARS,
                             label_visibility="collapsed")
        sent = c2.form_submit_button("Send", type="primary", width="stretch")
    st.button("Clear chat", key="eb_clear", on_click=_clear)

    question = st.session_state.pop("eb_pending", None)
    if sent and (text or "").strip():
        question = text.strip()

    with box:
        _show("assistant", kb.GREETING)
        for m in history:
            _show(m["role"], m["content"])
        if question:
            _show("user", question)
            with st.chat_message("assistant", avatar=_avatar()):
                with st.spinner("EnergyBot is thinking…"):
                    r = reply(history, question, st.session_state.get("eb_ai_calls", 0))
                st.markdown(r.text)
            if r.used_ai:
                st.session_state.eb_ai_calls = st.session_state.get("eb_ai_calls", 0) + 1
            history += [{"role": "user", "content": question}, {"role": "assistant", "content": r.text}]
            del history[:-MAX_HISTORY]
    st.markdown('<div class="eb-note">EnergyBot is a guide to this website. It can&rsquo;t see your bills here and can make mistakes; verify important details in the app or on your official bill.</div>',
                unsafe_allow_html=True)


def render():
    """Call once per landing-page run: draws the floating button and opens the dialog when requested."""
    st.button("💬 Ask EnergyBot", key="eb_fab", on_click=open_bot, help="Chat with EnergyBot, your guide to this website")
    if st.session_state.pop("eb_open", False):
        _dialog()
