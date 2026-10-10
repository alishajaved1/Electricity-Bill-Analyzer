import streamlit as st

from components import how_it_works
from components.illustrations import HERO_SVG
from components.landing_styles import inject_landing_css
from components.logos import asset_uri, providers_cards
from components.ui import logo
from config import APP_NAME
from utils.state import navigate
from views import energybot_widget, landing_sections as sections

def _pick(code):
    st.session_state.selected_provider = code
    st.session_state.pop("prov_radio", None)
    navigate("signup")


def render():
    inject_landing_css()
    st.markdown('<div id="home"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2.3, 4.6, .9, 1.1], vertical_alignment="center")
    c1.markdown(logo(dark=True), unsafe_allow_html=True)
    c2.markdown('<div class="navlinks"><a href="#home">Home</a><a href="#providers">Companies</a><a href="#about">About</a><a href="#how">How It Works</a><a href="#features">Features</a><a href="#privacy">Privacy</a></div>',
                unsafe_allow_html=True)
    c3.button("Login", key="nav_login", on_click=navigate, args=("login",), width="stretch")
    c4.button("Sign Up", key="nav_signup", type="primary", on_click=navigate, args=("signup",), width="stretch")

    left, right = st.columns([1.1, 1], vertical_alignment="center", gap="large")
    with left:
        st.markdown('<div class="fade"><h1 style="font-size:2.9rem;line-height:1.1;font-weight:800;margin:1.5rem 0 1rem">Smart Insights<br>for <span style="color:#3b4de0">Smarter Energy Use</span></h1>'
                    '<p style="font-size:1.08rem;color:#3d4670">Upload your electricity bill, understand every cost, track consumption over time and '
                    'receive AI-powered insights grounded in your own bills.</p></div>', unsafe_allow_html=True)
        b1, b2, _ = st.columns([1, 1, 1.2])
        b1.button("Get Started", key="hero_start", type="primary", on_click=navigate, args=("signup",), width="stretch")
        b2.markdown('<a href="#features" style="display:block;text-align:center;padding:.5rem;border:1px solid #c9d3f5;border-radius:10px;'
                    'background:#fff;color:#141a3a;text-decoration:none;font-weight:600">Learn More</a>', unsafe_allow_html=True)
    hero = asset_uri("hero_bill.jpg", "image/jpeg")
    if hero:
        right.markdown(f'<div class="hero-pic float"><img src="{hero}" alt="Electric bill with calculator and pen"></div>', unsafe_allow_html=True)
    else:  # graceful fallback if the photo is missing
        right.markdown(HERO_SVG, unsafe_allow_html=True)
    providers_cards(_pick)

    sections.about_intro()                    # introduction (About hero)

    st.markdown('<div id="how"></div><div class="lp-section" style="margin-top:3rem"></div>', unsafe_allow_html=True)
    how_it_works.render()                     # animated four-step experience

    sections.features()                       # core features
    sections.problem()                        # short "problem we solve"
    sections.trust_note()                     # concise privacy + accuracy note

    st.markdown(f'<div class="footer">⚡ {APP_NAME} · Bill-analysis assistance only, not a replacement for your official bill.</div>', unsafe_allow_html=True)
    energybot_widget.render()                 # floating EnergyBot button (+ chat dialog when opened)
