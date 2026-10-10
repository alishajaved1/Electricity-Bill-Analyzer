import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--navy:#141a4d;--navy2:#1c2461;--royal:#3b4de0;--indigo:#4f46e5;--bg:#f5f7ff;--card:#ffffff;--ink:#141a3a;--muted:#6a7394;
--green:#22b573;--orange:#f59e0b;--red:#ef4444;--border:#e3e8f7;--shadow:0 6px 24px rgba(40,55,140,.08)}
html,body,[class*="css"],.stApp{font-family:'Inter','Segoe UI',Arial,sans-serif;color:var(--ink)}
.stApp{background:var(--bg)}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1180px}
h1,h2,h3{color:var(--ink);letter-spacing:-.02em}
.fade{animation:fadeUp .55s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.float{animation:floaty 5s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* sidebar */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#141a4d,#0f1440)}
section[data-testid="stSidebar"] *{color:#e6e9ff}
section[data-testid="stSidebar"] .stButton>button{width:100%;justify-content:flex-start;background:transparent;border:0;color:#cfd5ff;
 font-weight:500;padding:.6rem .9rem;border-radius:10px;transition:all .2s}
section[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.08);color:#fff;transform:translateX(3px)}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:var(--royal);color:#fff;box-shadow:0 6px 16px rgba(59,77,224,.4)}
.brand{display:flex;align-items:center;gap:.55rem;font-weight:700;font-size:1.02rem}
.brand .bolt{font-size:1.5rem;color:#8b93ff}
.brand.dark{color:var(--ink)}.brand.dark .bolt{color:var(--indigo)}

/* buttons */
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border-radius:10px;font-weight:600;transition:all .2s;border:1px solid var(--border)}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 6px 16px rgba(59,77,224,.18)}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(135deg,#4f46e5,#3b4de0);color:#fff;border:0}
.stTextInput input,.stTextArea textarea{border-radius:10px}

/* cards */
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.1rem 1.3rem;box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(40,55,140,.13)}
.stat{display:flex;align-items:center;gap:.9rem;border-radius:16px;padding:1rem 1.2rem;border:1px solid var(--border);box-shadow:var(--shadow);transition:transform .2s}
.stat:hover{transform:translateY(-3px)}
.stat .ic{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;background:#fff}
.stat .lbl{font-size:.78rem;color:var(--muted);font-weight:500}.stat .val{font-size:1.4rem;font-weight:700}
.s-blue{background:#e6efff}.s-green{background:#e3f8ee}.s-orange{background:#fff1d6}.s-red{background:#ffe6e8}
.pagehead h1{font-size:1.9rem;margin:0}.pagehead p{color:var(--muted);margin:.2rem 0 1rem}
.pill{display:inline-block;padding:.15rem .6rem;border-radius:999px;font-size:.74rem;font-weight:600}
.pill.g{background:#e3f8ee;color:#12814f}.pill.o{background:#fff1d6;color:#a86500}.pill.r{background:#ffe6e8;color:#b42318}.pill.b{background:#e6efff;color:#2c3fc2}
.demo-tag{background:#fff1d6;color:#a86500;border:1px dashed #f5b942;border-radius:10px;padding:.45rem .8rem;font-size:.82rem;margin-bottom:.6rem}
.empty{text-align:center;padding:2rem 1rem}.empty h3{margin:.4rem 0}.empty p{color:var(--muted)}
.rec{border-left:4px solid var(--orange);background:#fffaf0;border-radius:8px;padding:.6rem .9rem;margin:.4rem 0}

/* landing */
.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:2rem;align-items:center;padding:2rem 0}
.hero h1{font-size:3rem;line-height:1.1;font-weight:800;margin:0 0 1rem}.hero h1 span{color:var(--royal)}
.hero p{font-size:1.08rem;color:#3d4670;max-width:34rem}
.navlinks{display:flex;gap:1.6rem;align-items:center;padding-top:.45rem}.navlinks a{color:var(--ink);text-decoration:none;font-weight:500;font-size:.92rem}
.navlinks a:hover{color:var(--royal)}
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.step .n{width:34px;height:34px;border-radius:50%;background:var(--royal);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;margin-bottom:.5rem}
.footer{margin-top:3rem;padding:1.4rem;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem;text-align:center}
.auth-side{background:linear-gradient(160deg,#141a4d,#1c2461);border-radius:18px;padding:2rem;color:#fff;min-height:420px}
.auth-side *{color:#fff}.auth-side li{margin:.5rem 0;list-style:none}
@media (max-width:820px){.hero{grid-template-columns:1fr}.hero h1{font-size:2.1rem}.feat-grid,.steps{grid-template-columns:1fr}.navlinks{display:none}}
</style>
"""


EXTRA = """
<style>
.co-card{background:#fff;border:2px solid var(--border);border-radius:16px;padding:1rem .8rem;text-align:center;box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s,border-color .2s}
.co-card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(40,55,140,.15)}
.co-card.sel{border-color:var(--royal);box-shadow:0 0 0 4px rgba(59,77,224,.12),var(--shadow)}
.co-logo{height:92px;display:flex;align-items:center;justify-content:center;margin-bottom:.4rem}
.co-img{display:block;margin:0 auto}
.co-name{font-weight:700;font-size:.95rem;color:var(--ink)}.co-sub{font-size:.78rem;color:var(--muted)}
.logo-fallback{display:inline-block;padding:.6rem 1rem;border-radius:12px;background:#eef1ff;color:#2c3fc2;font-weight:700}
.co-banner{display:flex;align-items:center;gap:1rem;background:#fff;border:1px solid var(--border);border-radius:14px;padding:.7rem 1rem;margin:.3rem 0 .8rem;box-shadow:var(--shadow)}
.strip{display:flex;flex-wrap:wrap;align-items:center;gap:1.6rem;margin:1.2rem 0 0;padding:.8rem 1.2rem;background:#fff;border:1px solid var(--border);border-radius:16px}
.strip-item{display:flex;align-items:center}
.hero-pic img{width:100%;border-radius:22px;border:6px solid #fff;box-shadow:0 20px 50px rgba(40,55,140,.25);display:block}
.co-card{position:relative;overflow:hidden}
.co-card::before{content:"";position:absolute;left:0;top:0;height:4px;width:0;background:linear-gradient(90deg,#3b4de0,#22b573,#f59e0b);transition:width .45s ease}
.co-card:hover::before,.co-card.sel::before{width:100%}
.co-card::after{content:"";position:absolute;top:0;left:-70%;width:45%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.65),transparent);transform:skewX(-20deg);transition:left .7s ease}
.co-card:hover::after{left:130%}
.co-img{transition:transform .35s ease}.co-card:hover .co-img{transform:scale(1.08) rotate(-1.5deg)}
.co-card.big{padding:1.8rem 1rem 1.4rem;border-radius:20px}.co-card.big .co-logo{height:130px}.co-card.big .co-name{font-size:1.08rem}
.co-card.big:hover{transform:translateY(-8px) scale(1.02);box-shadow:0 18px 40px rgba(59,77,224,.22);border-color:#b9c3f7}
.auth-pic{background:#fff;border-radius:16px;padding:.7rem;margin-top:1.2rem;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.auth-pic img{display:block;width:100%;max-height:300px;object-fit:contain;border-radius:10px}
.train-thumb{border-radius:10px;overflow:hidden}
</style>
"""

DARK_SOFT = "<style>:root{--bg:#eaf0ff}</style>"


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(EXTRA, unsafe_allow_html=True)
    if st.session_state.get("theme") == "Soft blue":
        st.markdown(DARK_SOFT, unsafe_allow_html=True)
