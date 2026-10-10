import html
from datetime import date

import streamlit as st

from components.illustrations import EMPTY_SVG


def logo(dark=False):
    cls = "brand dark" if dark else "brand"
    return f'<div class="{cls}"><span class="bolt">⚡</span><span>Electricity Bill Analyzer</span></div>'


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="pagehead fade"><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>', unsafe_allow_html=True)


def stat_card(label, value, icon, tone):
    st.markdown(f'<div class="stat s-{tone} fade"><div class="ic">{icon}</div><div><div class="lbl">{html.escape(label)}</div>'
                f'<div class="val">{html.escape(str(value))}</div></div></div>', unsafe_allow_html=True)


def empty_state(title, text):
    st.markdown(f'<div class="card empty fade">{EMPTY_SVG}<h3>{html.escape(title)}</h3><p>{html.escape(text)}</p></div>', unsafe_allow_html=True)


def demo_tag(text="ILLUSTRATIVE DEMO DATA - not your real bills. It disappears once you save a bill."):
    st.markdown(f'<div class="demo-tag">🧪 {html.escape(text)}</div>', unsafe_allow_html=True)


def today_str() -> str:
    return date.today().strftime("%A, %d %B %Y")


def show_df(df, **kw):
    st.dataframe(df, width="stretch", hide_index=True, **kw)
