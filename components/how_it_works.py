"""Animated, keyboard-friendly "How It Works" experience.

Rendered as one self-contained HTML component (components/hiw/*). The step state lives on the client
(and is mirrored on `window.parent`), so Streamlit reruns never reset the animation.
Falls back to a static four-card layout if the component API is unavailable.
"""
from __future__ import annotations

import html
import json
from functools import lru_cache
from pathlib import Path

import streamlit as st

from utils.state import navigate

ASSET_DIR = Path(__file__).parent / "hiw"

STEPS = [
    {"label": "Upload", "title": "Upload Your Electricity Bill",
     "desc": "Upload a photo, scan, or PDF of your electricity bill to begin your analysis."},
    {"label": "Verify", "title": "Verify Your Bill Details",
     "desc": "Review the information extracted from your bill and correct any unclear or inaccurate fields before continuing."},
    {"label": "Review", "title": "Explore Your Bill Insights",
     "desc": "Understand your electricity units, charges, taxes, total payable amount, and usage trends through clear visual reports."},
    {"label": "Ask", "title": "Ask EnergyBot",
     "desc": "Chat with EnergyBot to understand your bill, explore AI-powered insights, and discover practical ways to save electricity."},
]
CTA_LABEL = "Start Analyzing Your Bill"

# The real Streamlit button is only a bridge for the in-component call-to-action.
_HIDE_BRIDGE = "<style>.st-key-hiw_start{display:none}</style>"


@lru_cache(maxsize=1)
def build_html() -> str:
    css = (ASSET_DIR / "hiw.css").read_text(encoding="utf-8")
    body = (ASSET_DIR / "hiw.html").read_text(encoding="utf-8")
    js = (ASSET_DIR / "hiw.js").read_text(encoding="utf-8")
    cfg = json.dumps({"steps": STEPS, "cta": CTA_LABEL}, ensure_ascii=False).replace("</", "<\\/")
    js = js.replace("/*__CONFIG__*/ null", cfg)
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style></head><body>{body}<script>{js}</script></body></html>'


def _static_fallback():
    cards = "".join(f'<div class="card step"><div class="n">{n}</div><h4 style="margin:0 0 .3rem">{html.escape(s["title"])}</h4>'
                    f'<p style="color:#6a7394;margin:0;font-size:.9rem">{html.escape(s["desc"])}</p></div>' for n, s in enumerate(STEPS, 1))
    st.markdown(f'<div class="steps">{cards}</div>', unsafe_allow_html=True)


def render():
    """Render the section. The call-to-action inside step 4 triggers the hidden `hiw_start` button."""
    ok = True
    try:
        from streamlit.components.v1 import html as component_html
        component_html(build_html(), height=720, scrolling=False)
    except Exception:  # noqa: BLE001  - never break the landing page
        ok = False
        _static_fallback()
    if ok:
        st.markdown(_HIDE_BRIDGE, unsafe_allow_html=True)
    st.button(CTA_LABEL, key="hiw_start", type="primary", on_click=navigate, args=("signup",))
