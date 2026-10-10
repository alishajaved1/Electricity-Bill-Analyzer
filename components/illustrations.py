"""Original lightweight SVG illustrations (no remote images)."""

HERO_SVG = """
<svg class="float" viewBox="0 0 460 380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Electricity bill illustration" style="width:100%;max-width:480px">
<defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dfe6ff"/><stop offset="1" stop-color="#eef2ff"/></linearGradient></defs>
<circle cx="230" cy="190" r="165" fill="url(#g1)"/>
<rect x="105" y="45" width="215" height="270" rx="14" fill="#fff" stroke="#dbe2f7" stroke-width="2"/>
<text x="125" y="82" font-family="Inter,Arial" font-weight="700" font-size="14" fill="#1c2461">ELECTRICITY BILL</text>
<path d="M280 62 l-16 26 h12 l-8 22 l24 -30 h-13 l9 -18z" fill="#f59e0b"/>
<rect x="125" y="105" width="140" height="7" rx="3" fill="#dbe2f7"/><rect x="125" y="122" width="170" height="7" rx="3" fill="#e7ecfa"/>
<rect x="125" y="139" width="120" height="7" rx="3" fill="#e7ecfa"/>
<rect x="130" y="230" width="24" height="46" rx="3" fill="#3b4de0"/><rect x="164" y="212" width="24" height="64" rx="3" fill="#4f6bff"/>
<rect x="198" y="190" width="24" height="86" rx="3" fill="#3b4de0"/><rect x="232" y="205" width="24" height="71" rx="3" fill="#22b573"/>
<rect x="258" y="205" width="95" height="120" rx="12" fill="#2b36a8"/><rect x="270" y="217" width="71" height="26" rx="5" fill="#cfd8ff"/>
<g fill="#6f80ff"><rect x="270" y="254" width="20" height="14" rx="3"/><rect x="296" y="254" width="20" height="14" rx="3"/><rect x="322" y="254" width="19" height="14" rx="3"/>
<rect x="270" y="276" width="20" height="14" rx="3"/><rect x="296" y="276" width="20" height="14" rx="3"/><rect x="322" y="276" width="19" height="14" rx="3"/>
<rect x="270" y="298" width="20" height="14" rx="3"/><rect x="296" y="298" width="20" height="14" rx="3"/></g>
<rect x="322" y="298" width="19" height="14" rx="3" fill="#f59e0b"/>
<path d="M375 300 q-34 -30 -4 -80 q42 22 4 80z" fill="#22b573"/><path d="M375 300 q-4 -40 -4 -80" stroke="#157a4e" stroke-width="2" fill="none"/>
<path d="M375 296 q26 -14 38 -50 q-38 0 -38 50z" fill="#35c98a"/>
<path d="M356 300 h38 l-6 40 h-26z" fill="#3b4de0"/>
</svg>
"""

EMPTY_SVG = """
<svg viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg" style="width:110px" aria-hidden="true">
<rect x="25" y="10" width="60" height="78" rx="8" fill="#eef2ff" stroke="#c9d3f5" stroke-width="2"/>
<rect x="35" y="26" width="38" height="5" rx="2" fill="#c9d3f5"/><rect x="35" y="38" width="30" height="5" rx="2" fill="#dbe2f7"/>
<path d="M92 40 l-12 20 h9 l-6 18 l18 -24 h-10 l7 -14z" fill="#f59e0b"/></svg>
"""


# Original illustration for the About hero: a bill with verified fields (no real numbers shown).
ABOUT_BILL_SVG = (
    '<svg class="lp-bill-svg" viewBox="0 0 440 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustration of an electricity bill with verified fields" focusable="false">'
    '<defs><linearGradient id="abg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e5edff"/><stop offset="1" stop-color="#e4fbff"/></linearGradient>'
    '<linearGradient id="abh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2563eb"/><stop offset="1" stop-color="#06b6d4"/></linearGradient></defs>'
    '<circle cx="220" cy="170" r="150" fill="url(#abg)"/>'
    '<g class="lp-float"><rect x="110" y="34" width="220" height="272" rx="16" fill="#fff" stroke="#d6e2ff" stroke-width="2"/>'
    '<rect x="110" y="34" width="220" height="48" rx="16" fill="url(#abh)"/><rect x="110" y="64" width="220" height="18" fill="url(#abh)"/>'
    '<text x="128" y="64" font-family="Inter,Arial,sans-serif" font-weight="800" font-size="14" fill="#fff">ELECTRICITY BILL</text>'
    '<path d="M300 44 l-12 20 h9 l-6 16 l18 -23 h-10 l7 -13z" fill="#fbbf24"/>'
    '<g font-family="Inter,Arial,sans-serif" font-size="11" font-weight="600" fill="#5b678d">'
    '<text x="128" y="108">Units billed</text><text x="128" y="144">Charges</text><text x="128" y="180">Taxes</text><text x="128" y="216">Due date</text><text x="128" y="252" fill="#1e3a8a" font-weight="800">Total payable</text></g>'
    '<g fill="#e6edff"><rect x="214" y="98" width="84" height="12" rx="6"/><rect x="214" y="134" width="84" height="12" rx="6"/><rect x="214" y="170" width="84" height="12" rx="6"/><rect x="214" y="206" width="84" height="12" rx="6"/></g>'
    '<rect x="214" y="242" width="84" height="14" rx="7" fill="#c7d7ff"/>'
    '<g fill="#10b981"><circle cx="312" cy="104" r="8"/><circle cx="312" cy="140" r="8"/><circle cx="312" cy="176" r="8"/><circle cx="312" cy="212" r="8"/></g>'
    '<g stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M308 104 l3 3 l5 -6"/><path d="M308 140 l3 3 l5 -6"/><path d="M308 176 l3 3 l5 -6"/><path d="M308 212 l3 3 l5 -6"/></g></g>'
    '<g class="lp-float2"><circle cx="352" cy="262" r="30" fill="#7c3aed"/><g fill="#fff"><circle cx="340" cy="262" r="4"/><circle cx="352" cy="262" r="4"/><circle cx="364" cy="262" r="4"/></g></g>'
    '<g class="lp-float2" style="animation-delay:-2s"><rect x="62" y="226" width="74" height="40" rx="14" fill="#2563eb"/><rect x="74" y="238" width="42" height="6" rx="3" fill="#fff"/><rect x="74" y="250" width="28" height="6" rx="3" fill="#fff" opacity=".7"/></g>'
    '</svg>'
)
