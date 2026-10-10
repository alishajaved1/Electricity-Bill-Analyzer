import streamlit as st

from components.logos import COMPANIES, company_banner, provider_from_filename
from components.ui import empty_state, page_header
from config import TRAINING_DIR
from utils.state import navigate


def _use(name: str, code):
    st.session_state.practice_file = name
    st.session_state.analysis_draft = None
    if code:
        st.session_state.selected_provider = code
        st.session_state.pop("prov_radio", None)
    navigate("Analyze Bill")


def render():
    page_header("Training Bills / Practice", "Sample KE, LESCO and IESCO bills to try the extraction workflow.")
    st.info("These sample bills are for practising and testing the extraction. The AI is **not trained** on them; "
            "Gemini reads each bill fresh. Personal details on the samples are covered with grey boxes.")
    files = sorted(p for p in TRAINING_DIR.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")) if TRAINING_DIR.exists() else []
    if not files:
        empty_state("No training bills found", "Place sample bill images in assets/training_bills/ to use them here.")
        return
    cols = st.columns(3)
    for i, f in enumerate(files):
        code = provider_from_filename(f.name)
        with cols[i % 3]:
            with st.container(border=True):
                company_banner(code, "Sample bill")
                try:
                    st.image(str(f), width="stretch")
                except Exception:  # noqa: BLE001
                    st.caption("Preview unavailable.")
                st.caption(f.name)
                st.button("Use for practice", key=f"practice_{f.name}", type="primary", on_click=_use, args=(f.name, code), width="stretch")
