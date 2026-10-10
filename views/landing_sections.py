"""Landing-page sections: About hero, problem, features and a concise trust note.

All claims here describe what the project actually does (see services/energybot_kb.py). HTML is built as single-line
strings on purpose: blank lines or 4-space indents inside st.markdown would turn into Markdown code blocks.
"""
import html

import streamlit as st

from components.icons import icon
from components.illustrations import ABOUT_BILL_SVG

FEATURES = [
    ("eye", "AI-Powered Bill Reading", "Google Gemini helps read and interpret supported bill images and documents (PDF, JPG, PNG)."),
    ("list", "Structured Bill Information", "Extracted values are organised into readable fields that you can review and correct before saving."),
    ("calc", "Python-Based Calculations", "Python handles the arithmetic — sums, percentages, cost per unit — instead of asking the language model."),
    ("pie", "Bill Cost Breakdown", "See the charges, taxes, adjustments and totals that were extracted, with a chart of how they add up."),
    ("trend", "Usage and Trend Insights", "Visualise units and amounts over time when enough bill records are available."),
    ("chat", "EnergyBot Assistant", "Ask about how the app works and, once you have saved a bill, about your own extracted bill data."),
    ("file", "Bill History and Reports", "Review, remove and export bills from your current session (CSV or JSON) and print a report."),
    ("building", "Multiple Electricity Providers", "Designed around KE, LESCO and IESCO bill layouts."),
]

PROBLEM_FIELDS = ["Meter readings", "Billing units", "Billing periods", "Electricity charges", "Taxes and additional charges",
                  "Adjustments", "Total payable amount", "Due dates"]



def _a(href, label, extra=""):
    return f'<a class="lp-cta" href="{href}" {extra}>{html.escape(label)}</a>'


def about_intro():
    """A. About hero + short introduction (id=about)."""
    st.markdown(
        '<div id="about"></div><div class="lp-section"><div class="lp-hero lp-enter"><div>'
        '<h2>Making Electricity Bills Easier to Understand</h2>'
        '<p class="lp-sub">An AI-powered electricity bill analysis experience designed to turn complicated bill details into clear, useful insights for households in Pakistan.</p>'
        f'{_a("#how", "Explore How It Works")}</div>'
        f'<div class="lp-hero-art">{ABOUT_BILL_SVG}</div></div></div>', unsafe_allow_html=True)


def features():
    """D. Core features (id=features)."""
    cards = "".join(f'<div class="lp-card"><div class="lp-ic">{icon(i)}</div><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>' for i, t, d in FEATURES)
    st.markdown('<div id="features"></div><div class="lp-section"><div class="lp-reveal"><h2 class="lp-h2">Everything you need to decode your bill</h2>'
                '<p class="lp-sub">Everything below is available in the app today.</p></div>'
                f'<div class="lp-grid g4">{cards}</div></div>', unsafe_allow_html=True)


def problem():
    """The problem we solve (short)."""
    chips = "".join(f"<li>{html.escape(f)}</li>" for f in PROBLEM_FIELDS)
    st.markdown(
        '<div id="about-details"></div><div class="lp-section"><div class="lp-split lp-reveal"><div>'
        '<h2 class="lp-h2">The problem we solve</h2>'
        '<p class="lp-sub">An electricity bill packs a lot into one page, and the details can be hard to take in quickly. '
        'Electricity Bill Analyzer organises the information it extracts into a clearer format, so you can review the important values and understand your bill more easily.</p></div>'
        f'<ul class="lp-chips" aria-label="Fields found on an electricity bill">{chips}</ul></div></div>'
        , unsafe_allow_html=True)


def trust_note():
    """Short privacy + limitation note (replaces the long privacy, limitations and FAQ sections). id=privacy."""
    st.markdown(
        '<div id="privacy"></div><div class="lp-section"><div class="lp-note" role="note"><div class="lp-ic">' + icon("shield", 20) + '</div><div>'
        '<b>Privacy and accuracy</b>'
        '<p>Bills are sent to Google Gemini to be read and kept only in your session (no database). '
        'AI extraction can make mistakes, so review the values against your original bill. This app does not replace the official bill.</p></div></div></div>',
        unsafe_allow_html=True)
