"""Styles for the upgraded landing page (About, features, trust note, EnergyBot)."""
import streamlit as st

LANDING_CSS = """
<style>
html,body,.stApp,[data-testid="stMain"],section.main{scroll-behavior:smooth}
.stApp{overflow-x:hidden}
[id]{scroll-margin-top:16px}
.navlinks{gap:1.05rem;flex-wrap:nowrap;white-space:nowrap}.navlinks a{font-size:.88rem}
.lp-section{margin-top:3rem;min-width:0}
.lp-h2{font-size:clamp(1.55rem,3.2vw,2.25rem);font-weight:800;letter-spacing:-.025em;line-height:1.15;margin:0 0 .5rem;color:var(--ink)}
.lp-sub{color:#4a5580;max-width:64ch;font-size:1.04rem;line-height:1.6;margin:0}
.lp-grid{display:grid;gap:1rem;margin-top:1.4rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr))}
.lp-grid.g4{grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr))}
.lp-card{min-width:0;background:#fff;border:1px solid var(--border);border-radius:18px;padding:1.15rem 1.2rem;box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s,border-color .2s}
.lp-card:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(40,55,140,.14);border-color:#cdd8f8}
.lp-card h4{margin:.7rem 0 .3rem;font-size:1.04rem;font-weight:700;color:var(--ink)}
.lp-card p{margin:0;color:#56618a;font-size:.93rem;line-height:1.55}
.lp-ic{width:44px;height:44px;border-radius:13px;display:flex;align-items:center;justify-content:center;color:#fff;background:linear-gradient(135deg,#2563eb,#06b6d4)}
.lp-card:nth-child(4n+2) .lp-ic{background:linear-gradient(135deg,#10b981,#06b6d4)}
.lp-card:nth-child(4n+3) .lp-ic{background:linear-gradient(135deg,#7c3aed,#6366f1)}
.lp-card:nth-child(4n+4) .lp-ic{background:linear-gradient(135deg,#4f46e5,#2563eb)}
.ic-svg{display:block}

/* about hero */
.lp-hero{display:grid;grid-template-columns:1.15fr 1fr;gap:2rem;align-items:center;border:1px solid var(--border);border-radius:28px;padding:2.2rem 2.2rem;
 background:radial-gradient(700px 300px at 0 0,#e7efff,transparent 60%),radial-gradient(600px 300px at 100% 100%,#e2fbff,transparent 60%),#fbfcff;min-width:0}
.lp-hero h2{font-size:clamp(1.8rem,4vw,2.9rem);line-height:1.08;font-weight:800;letter-spacing:-.03em;margin:0 0 .9rem;color:var(--ink)}
.lp-hero .lp-sub{font-size:1.1rem}
.lp-cta{display:inline-flex;align-items:center;gap:.5rem;margin-top:1.4rem;padding:.8rem 1.35rem;border-radius:12px;color:#fff!important;font-weight:700;text-decoration:none!important;
 background:linear-gradient(135deg,#4f46e5,#2563eb);box-shadow:0 10px 24px rgba(59,77,224,.32);transition:transform .2s,box-shadow .2s}
.lp-cta:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(59,77,224,.4)}
.lp-hero-art{min-width:0;text-align:center}.lp-bill-svg{width:100%;max-width:440px;height:auto}
.lp-float{animation:lpFloat 6s ease-in-out infinite}.lp-float2{animation:lpFloat 5s ease-in-out infinite}
@keyframes lpFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.lp-enter{animation:lpEnter .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes lpEnter{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

/* problem */
.lp-split{display:grid;grid-template-columns:1fr 1.1fr;gap:2rem;align-items:start}
.lp-chips{display:flex;flex-wrap:wrap;gap:.55rem;margin:0;padding:0;list-style:none}
.lp-chips li{padding:.45rem .85rem;border-radius:999px;background:#fff;border:1px solid var(--border);font-weight:600;font-size:.9rem;color:#2b3770;box-shadow:0 2px 8px rgba(40,55,140,.05)}

/* concise trust note */
.lp-note{display:flex;gap:1rem;align-items:flex-start;border-radius:18px;padding:1.1rem 1.3rem;background:#f4f7ff;border:1px solid var(--border)}
.lp-note .lp-ic{flex:none;width:40px;height:40px;border-radius:12px}
.lp-note b{color:var(--ink)}.lp-note p{margin:.2rem 0 0;color:#56618a;font-size:.93rem;line-height:1.55}

/* scroll-driven reveal where supported (calm, one fade), otherwise plain */
@supports (animation-timeline: view()){
 .lp-reveal{animation:lpEnter linear both;animation-timeline:view();animation-range:entry 0% cover 24%}
}

/* floating EnergyBot button (a real st.button, positioned fixed) */
.st-key-eb_fab{position:fixed!important;right:22px;bottom:22px;z-index:1000;width:auto!important}
.st-key-eb_fab button{border:0;border-radius:999px;padding:.7rem 1.15rem .7rem .95rem;color:#fff;font-weight:700;background:linear-gradient(135deg,#4f46e5,#2563eb 60%,#06b6d4);
 box-shadow:0 14px 34px rgba(37,70,200,.45);min-height:3rem}
.st-key-eb_fab button:hover{transform:translateY(-3px);box-shadow:0 18px 40px rgba(37,70,200,.55);color:#fff}
.st-key-eb_fab button p{color:#fff!important;margin:0;font-weight:700}
.st-key-eb_fab{animation:lpEnter .8s ease 1.2s both}
@media (max-width:560px){.st-key-eb_fab{right:12px;bottom:12px}}

/* EnergyBot dialog */
.eb-head{display:flex;align-items:center;gap:.8rem;margin:-.2rem 0 .6rem}
.eb-head img{width:46px;height:46px;border-radius:50%;box-shadow:0 4px 14px rgba(40,55,140,.2)}
.eb-head b{display:block;color:var(--ink)}.eb-head small{color:#56618a}
.eb-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;margin-right:.35rem}
[data-testid="stDialog"] [data-testid="stChatMessage"]{animation:lpEnter .35s ease both;border-radius:16px}
.eb-note{font-size:.78rem;color:#6a7394;margin-top:.4rem}

@media (max-width:860px){
 .lp-hero{grid-template-columns:1fr;padding:1.5rem 1.2rem}.lp-split{grid-template-columns:1fr}
 }
@media (prefers-reduced-motion:reduce){
 .lp-float,.lp-float2,.lp-enter,.lp-reveal,.st-key-eb_fab,[data-testid="stDialog"] [data-testid="stChatMessage"]{animation:none!important}
 html,body,.stApp,[data-testid="stMain"],section.main{scroll-behavior:auto}
}
</style>
"""


def inject_landing_css():
    st.markdown(LANDING_CSS, unsafe_allow_html=True)
