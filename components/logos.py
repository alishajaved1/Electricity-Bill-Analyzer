"""Company logos (IESCO, KE, LESCO) loaded from assets/logos with graceful fallbacks."""
import base64
import html
from functools import lru_cache

import streamlit as st

from config import BASE_DIR, LOGO_DIR

COMPANIES = {
    "IESCO": {"name": "Islamabad Electric Supply Company", "short": "IESCO", "file": "iesco.png", "region": "Islamabad region"},
    "KE": {"name": "K-Electric", "short": "KE", "file": "ke.png", "region": "Karachi"},
    "LESCO": {"name": "Lahore Electric Supply Company", "short": "LESCO", "file": "lesco.png", "region": "Lahore region"},
}
ORDER = ["IESCO", "KE", "LESCO"]
FILE_PREFIX = {"IESCO": "IESCO", "KESC": "KE", "KE": "KE", "LESCO": "LESCO"}


@lru_cache(maxsize=16)
def asset_uri(relative: str, mime: str) -> str | None:
    """Base64 data-URI for a file under assets/ (relative path), or None if missing."""
    path = BASE_DIR / "assets" / relative
    try:
        return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    except OSError:
        return None


@lru_cache(maxsize=8)
def logo_uri(code: str) -> str | None:
    info = COMPANIES.get(code)
    if not info:
        return None
    try:
        return "data:image/png;base64," + base64.b64encode((LOGO_DIR / info["file"]).read_bytes()).decode()
    except OSError:
        return None


def logo_html(code: str | None, height: int = 64) -> str:
    """<img> of the real logo; if the file is missing, a plain text badge with the company name."""
    info = COMPANIES.get(code or "")
    if not info:
        return '<div class="logo-fallback">Select a company</div>'
    uri = logo_uri(code)
    if uri:
        return (f'<img class="co-img" src="{uri}" alt="{html.escape(info["name"])} logo" '
                f'style="height:{height}px;max-width:100%;width:auto;object-fit:contain">')
    return f'<div class="logo-fallback">{html.escape(info["short"])}</div>'


def provider_from_filename(name: str) -> str | None:
    return FILE_PREFIX.get(name.split("_")[0].upper())


def company_card_html(code: str, selected: bool = False, big: bool = False, delay: float = 0.0) -> str:
    i = COMPANIES[code]
    return (f'<div class="co-card fade {"sel" if selected else ""} {"big" if big else ""}" style="animation-delay:{delay}s"><div class="co-logo">{logo_html(code, 104 if big else 76)}</div>'
            f'<div class="co-name">{html.escape(i["name"])}</div><div class="co-sub">{html.escape(i["region"])}</div></div>')


def company_banner(code: str | None, label: str = "Electricity provider"):
    """Logo + name row used on results pages and bill details."""
    info = COMPANIES.get(code or "")
    if not info:
        return
    st.markdown(f'<div class="co-banner fade">{logo_html(code, 56)}<div><div class="co-sub">{html.escape(label)}</div>'
                f'<div class="co-name" style="font-size:1.1rem">{html.escape(info["name"])} ({info["short"]})</div></div></div>',
                unsafe_allow_html=True)


def company_side_card(code: str | None):
    """Compact logo card shown beside the upload section."""
    if code in COMPANIES:
        i = COMPANIES[code]
        st.markdown(f'<div class="co-card sel"><div class="co-logo">{logo_html(code, 84)}</div>'
                    f'<div class="co-name">{html.escape(i["short"])}</div><div class="co-sub">Selected company</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="co-card"><div class="co-logo"><div class="logo-fallback">No company selected</div></div>'
                    '<div class="co-sub">Choose IESCO, KE or LESCO</div></div>', unsafe_allow_html=True)


def providers_strip():
    items = "".join(f'<div class="strip-item">{logo_html(c, 46)}</div>' for c in ORDER)
    st.markdown(f'<div class="strip fade"><span style="color:#6a7394;font-weight:600">Works with bills from</span>{items}</div>', unsafe_allow_html=True)


def providers_cards(on_pick):
    """Landing-page company cards (logo, name, region) with a working call-to-action button each."""
    st.markdown('<div id="providers"></div><h2 style="margin-top:2.2rem">Supported electricity companies</h2>'
                '<p style="color:#6a7394;margin-top:-.4rem">Pick your company to get started - we read KE, LESCO and IESCO bill layouts.</p>',
                unsafe_allow_html=True)
    cols = st.columns(3, gap="large")
    for n, (col, code) in enumerate(zip(cols, ORDER)):
        with col:
            st.markdown(company_card_html(code, big=True, delay=0.12 * n), unsafe_allow_html=True)
            st.button(f"Analyze {COMPANIES[code]['short']} bills →", key=f"land_pick_{code}", on_click=on_pick, args=(code,), width="stretch")


def auth_picture(name: str) -> str:
    """HTML for the illustration on login/sign-up pages (empty string if the file is missing)."""
    uri = asset_uri(name, "image/jpeg")
    return f'<div class="auth-pic float"><img src="{uri}" alt="Billing illustration"></div>' if uri else ""
