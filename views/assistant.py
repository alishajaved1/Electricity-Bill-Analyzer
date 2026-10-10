import streamlit as st

from components.ui import page_header
from config import get_api_key, get_model_name
from services.gemini_service import GeminiError, chat

SUGGESTIONS = ["What is my total bill amount?", "How many units did I consume?", "Explain my taxes in simple English.",
               "Why is this bill higher than my previous bill?", "What is the due date?", "How can I reduce electricity consumption?"]


def render():
    page_header("EnergyBot - AI Assistant", "Ask questions about your analysed bills, charges, taxes and saving habits.")
    bills = st.session_state.bills
    key_ok = bool(get_api_key())
    if not key_ok:
        st.warning("**Gemini API key not configured.** EnergyBot cannot answer until `GEMINI_API_KEY` is set "
                   "(`.env` locally, or Secrets on Streamlit Cloud). See Settings for status.")
    elif not bills:
        st.info("No bills analysed yet. EnergyBot can share general tips, but bill-specific answers need an analysed bill.")
    else:
        st.caption(f"Using data from {len(bills)} saved bill(s). Model: {get_model_name()}. Bill data (no names/addresses) is sent to Gemini to answer.")

    pending = st.session_state.pop("pending_q", None)
    typed = st.chat_input("Ask EnergyBot about your bill...", disabled=not key_ok)
    q = typed or (pending if key_ok else None)

    top = st.columns([1, 1, 4])
    if top[0].button("Clear chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

    if q:
        history = list(st.session_state.chat_history)
        with st.spinner("EnergyBot is thinking..."):
            try:
                answer = chat(history, q, bills)
                st.session_state.chat_history += [{"role": "user", "content": q}, {"role": "assistant", "content": answer}]
            except GeminiError as e:
                st.error(str(e))
    if not st.session_state.chat_history:
        st.markdown("**Try asking:**")
        cols = st.columns(3)
        for i, s in enumerate(SUGGESTIONS):
            cols[i % 3].button(s, key=f"sug_{i}", disabled=not key_ok, width="stretch",
                               on_click=lambda t=s: st.session_state.update(pending_q=t))
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"], avatar="🧑" if m["role"] == "user" else "⚡"):
            st.markdown(m["content"])
    st.caption("EnergyBot answers from your extracted bill data. General tips are labelled and are not guaranteed savings.")
