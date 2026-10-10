"""Runs the EnergyBot dialog body against a Streamlit stub: greeting, suggestion, local answer, history, clear."""
import os, sys, types
from unittest.mock import MagicMock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["API_KEY"] = ""; os.environ.pop("GEMINI_API_KEY", None)

shown, buttons = [], []
class SS(dict):
    __getattr__ = dict.get
    def __setattr__(self, k, v): self[k] = v
class Ctx(MagicMock):
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def button(self, label, **k): buttons.append(label); return False
    def text_input(self, *a, **k): return TYPED[0]
    def form_submit_button(self, *a, **k): return bool(TYPED[0])
TYPED = [""]
st = types.ModuleType("streamlit"); st.session_state = SS()
st.markdown = lambda *a, **k: None
st.caption = lambda *a, **k: None
st.columns = lambda spec, **k: [Ctx() for _ in range(spec if isinstance(spec, int) else len(spec))]
st.container = lambda **k: Ctx()
st.form = lambda *a, **k: Ctx()
st.spinner = lambda *a, **k: Ctx()
st.chat_message = lambda role, **k: (shown.append(("bubble", role)) or Ctx())
def _md(t, **k): shown.append(("md", t))
st.markdown = _md
st.button = lambda label, **k: buttons.append(label) or False
st.form_submit_button = lambda *a, **k: bool(TYPED[0])
st.text_input = lambda *a, **k: TYPED[0]
st.dialog = lambda *a, **k: (lambda f: f)
sys.modules["streamlit"] = st

from views import energybot_widget as w
from services import energybot_kb as kb
st.session_state.setdefault("eb_history", [])
w._dialog()
assert any(t == ("md", kb.GREETING) for t in shown), "greeting missing"
assert "How do I upload my bill?" in buttons, "suggested questions missing"
# suggestion click -> pending -> answered locally
st.session_state.eb_pending = "How do I upload my bill?"; shown.clear(); w._dialog()
h = st.session_state.eb_history
assert [m["role"] for m in h] == ["user", "assistant"] and "Analyze Bill" in h[1]["content"], h
# typed message through the form
TYPED[0] = "What is my total bill amount?"; w._dialog()
assert "can't see any bill" in st.session_state.eb_history[-1]["content"]
# api-less odd question -> friendly fallback, page keeps working
TYPED[0] = "tell me about rockets"; w._dialog()
assert "built-in help" in st.session_state.eb_history[-1]["content"]
w._clear(); assert st.session_state.eb_history == []
# open flag
w.open_bot(); assert st.session_state.eb_open is True
print("EnergyBot dialog smoke test OK")
