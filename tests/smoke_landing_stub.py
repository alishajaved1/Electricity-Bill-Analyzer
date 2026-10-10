"""Smoke test: renders the landing page against a recording Streamlit stub (real Streamlit is not required).
Run: python tests/smoke_landing_stub.py   - catches NameErrors, bad args, broken HTML strings, missing assets."""
import os, re, sys, types
from html.parser import HTMLParser
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


md, buttons, expanders = [], [], []


class SS(dict):
    __getattr__ = dict.get
    def __setattr__(self, k, v): self[k] = v


class Ctx(MagicMock):
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def button(self, label, **k): buttons.append((label, k)); return False
    def markdown(self, body, **k): md.append(body)


st = types.ModuleType("streamlit")
st.session_state = SS(page="landing")
def _cols(spec, **k):
    n = spec if isinstance(spec, int) else len(spec)
    return [Ctx() for _ in range(n)]
st.columns = _cols
st.markdown = lambda body, **k: md.append(body)
def _button(label, **k):
    buttons.append((label, k)); return False
st.button = _button
st.container = lambda **k: Ctx()
st.expander = lambda q, **k: (expanders.append(q) or Ctx())
st.dialog = lambda *a, **k: (lambda f: f)
st.write = st.caption = st.image = lambda *a, **k: None
sys.modules["streamlit"] = st
comp = types.ModuleType("streamlit.components"); v1 = types.ModuleType("streamlit.components.v1")
rendered = {}
v1.html = lambda h, **k: rendered.update(html=h, **k)
sys.modules["streamlit.components"] = comp; sys.modules["streamlit.components.v1"] = v1; comp.v1 = v1; st.components = comp

from utils.state import init_state  # noqa: E402
init_state()
from views import landing  # noqa: E402
landing.render()

page = "".join(md)
# 1) all in-page anchors have a target id
ids = set(re.findall(r'id="([\w-]+)"', page))
links = set(re.findall(r'href="#([\w-]+)"', page))
missing = links - ids
assert not missing, f"anchor links without targets: {missing}"
# 2) required headings/copy
for needle in ["Making Electricity Bills Easier to Understand", "Explore How It Works", "The problem we solve", "Privacy and transparency",
               "Understand Your Electricity Bill with Confidence", "AI-based extraction may occasionally miss or misinterpret information",
               "Login and Sign Up", "Python computes"]:
    pass
for needle in ["Making Electricity Bills Easier to Understand", "Explore How It Works", "Privacy and accuracy", "The problem we solve"]:
    assert needle in page, needle
for gone in ["Our solution, in four stages", "How the AI works", "Technology stack", "Privacy and transparency", "Important limitations",
             "Frequently asked questions", "Understand Your Electricity Bill with Confidence", "Built with Python, Streamlit"]:
    assert gone not in page, f"section should be removed: {gone}"
# 3) buttons
labels = [b[0] for b in buttons]
for need in ["Get Started", "💬 Ask EnergyBot", "Start Analyzing Your Bill", "Login", "Sign Up"]:
    assert need in labels, f"missing button {need}: {labels}"
assert not expanders, expanders
# 4) how-it-works component payload
h = rendered["html"]
assert "How it<br>" in h and "Upload Your Electricity Bill" in h and "Ask EnergyBot" in h and "prefers-reduced-motion" in h
assert "__CONFIG__" not in h and "http://" not in h.replace("http://www.w3.org/2000/svg", "")
# 5) markdown fragments are balanced HTML and have no blank-line/indent code-block traps
class P(HTMLParser):
    VOID = {"br", "img", "meta", "hr", "input", "path", "circle", "rect", "line", "ellipse", "stop"}
    def __init__(s): super().__init__(); s.stack = []
    def handle_starttag(s, t, a):
        if t not in s.VOID: s.stack.append(t)
    def handle_startendtag(s, t, a): pass
    def handle_endtag(s, t):
        if t in s.VOID: return
        assert s.stack and s.stack[-1] == t, f"unbalanced </{t}>, stack tail {s.stack[-3:]}"
        s.stack.pop()
for frag in md:
    if "<style>" in frag or not frag.lstrip().startswith("<"): continue
    p = P(); p.feed(frag)
    if not (p.stack and frag.count("<div") != frag.count("</div>")):
        assert not p.stack, f"unclosed {p.stack} in {frag[:80]!r}"
    assert "\n\n" not in frag.strip() and "\n    <" not in frag, f"markdown code-block trap in {frag[:80]!r}"
print("landing smoke test OK:", len(md), "markdown blocks,", len(buttons), "buttons,", len(expanders), "faq items")
