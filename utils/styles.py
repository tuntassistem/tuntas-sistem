"""
utils/styles.py — Shared CSS & Design Tokens T.U.N.T.A.S
=========================================================
Satu tempat untuk semua CSS global dan design token.
Dipanggil sekali di awal setiap page: inject_global_css()

ID FOOD Brand Colors:
  BLUE  #0054A6  — primary, stabilitas
  GREEN #00A651  — success, sustainabilitas
"""

import streamlit as st

# ── Design Tokens ─────────────────────────────────────────────────────────────
BLUE        = "#0054A6"
BLUE_DARK   = "#003D7A"
BLUE_LIGHT  = "#EEF4FF"
BLUE_MID    = "#DBEAFE"

GREEN       = "#00A651"
GREEN_DARK  = "#007A3D"
GREEN_LIGHT = "#ECFDF5"

RED         = "#DC2626"
RED_LIGHT   = "#FEF2F2"
AMBER       = "#D97706"
AMBER_LIGHT = "#FFFBEB"

GRAY_50     = "#F8FAFC"
GRAY_100    = "#F1F5F9"
GRAY_200    = "#E2E8F0"
GRAY_500    = "#64748B"
GRAY_700    = "#334155"
GRAY_900    = "#0F172A"

TEXT_MAIN   = "#1E293B"
TEXT_MUTED  = "#64748B"

# Status → warna
STATUS_TL_COLORS: dict[str, str] = {
    "OPEN":            AMBER,
    "ON_PROGRESS":     BLUE,
    "SELESAI_PARSIAL": "#7C3AED",
    "CLOSED":          GREEN,
    "MELEWATI_TARGET": RED,
}

STATUS_TEMUAN_COLORS: dict[str, str] = {
    "OPEN":        RED,
    "IN_PROGRESS": AMBER,
    "VERIFIED":    BLUE,
    "CLOSED":      GREEN,
}

SIGNIF_COLORS: dict[str, str] = {
    "KRITIS": RED,
    "TINGGI": AMBER,
    "SEDANG": BLUE,
    "RENDAH": GREEN,
}


# ── CSS Global ────────────────────────────────────────────────────────────────

_GLOBAL_CSS = f"""
<style>
/* CSS untuk memperbaiki posisi halaman yang 'melorot' */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
}}
/* ── Reset & Base ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {TEXT_MAIN};
}}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {BLUE_DARK} 0%, {BLUE} 100%) !important;
    border-right: none !important;
}}
[data-testid="stSidebar"] * {{
    color: rgba(255,255,255,0.92) !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.15) !important;
}}
[data-testid="stSidebar"] .stSelectbox div div {{
    color: #1E293B !important;
}}
[data-testid="stSidebarNav"] {{
    padding-top: 0 !important;
}}
/* Nav links di sidebar */
[data-testid="stSidebarNav"] a {{
    color: rgba(255,255,255,0.85) !important;
    border-radius: 8px;
    padding: 6px 12px;
    transition: background 0.2s;
}}
[data-testid="stSidebarNav"] a:hover {{
    background: rgba(255,255,255,0.12) !important;
    color: white !important;
}}
[data-testid="stSidebarNav"] a[aria-selected="true"] {{
    background: rgba(255,255,255,0.18) !important;
    color: white !important;
    font-weight: 600;
}}

/* ── Main content area ────────────────────────────────────────────────────── */
.main .block-container {{
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1400px;
}}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {{
    background: {BLUE} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.45rem 1.1rem !important;
    transition: background 0.2s, transform 0.1s !important;
    box-shadow: 0 1px 3px rgba(0,84,166,0.25) !important;
}}
.stButton > button:hover {{
    background: {BLUE_DARK} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,84,166,0.35) !important;
}}
/* Tombol primary (type="primary") → Hijau ID FOOD */
.stButton > button[kind="primary"] {{
    background: {GREEN} !important;
    box-shadow: 0 1px 3px rgba(0,166,81,0.25) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {GREEN_DARK} !important;
    box-shadow: 0 4px 12px rgba(0,166,81,0.35) !important;
}}

/* ── Form inputs ──────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {{
    border: 1.5px solid {GRAY_200} !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(0,84,166,0.1) !important;
}}

/* ── Slider ───────────────────────────────────────────────────────────────── */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {BLUE} !important;
}}
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {{
    color: {BLUE} !important;
}}

/* ── Metrics ─────────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: white;
    border: 1px solid {GRAY_200};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
}}
[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: {BLUE};
    border-radius: 12px 0 0 12px;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {TEXT_MUTED} !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: {TEXT_MAIN} !important;
}}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    border-bottom: 2px solid {GRAY_200} !important;
    gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 0 !important;
    font-weight: 500 !important;
    color: {TEXT_MUTED} !important;
    padding: 0.5rem 1.2rem !important;
}}
.stTabs [aria-selected="true"] {{
    color: {BLUE} !important;
    border-bottom: 2px solid {BLUE} !important;
    font-weight: 700 !important;
}}

/* ── Expander ─────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {{
    font-weight: 600 !important;
    color: {BLUE} !important;
    border-radius: 8px !important;
    background: {BLUE_LIGHT} !important;
    padding: 0.5rem 1rem !important;
}}

/* ── Dataframe ────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid {GRAY_200};
}}

/* ── Download button ──────────────────────────────────────────────────────── */
.stDownloadButton > button {{
    background: white !important;
    color: {BLUE} !important;
    border: 1.5px solid {BLUE} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stDownloadButton > button:hover {{
    background: {BLUE_LIGHT} !important;
}}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr {{
    border: none;
    border-top: 1px solid {GRAY_200};
    margin: 1.25rem 0;
}}

/* ── Alert boxes ─────────────────────────────────────────────────────────── */
.stAlert {{
    border-radius: 10px !important;
    border: none !important;
}}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.stSpinner > div {{
    border-top-color: {BLUE} !important;
}}

/* ── T.U.N.T.A.S custom components ───────────────────────────────────────── */
.tnt-page-header {{
    background: linear-gradient(135deg, {BLUE_DARK} 0%, {BLUE} 60%, #1A7FD4 100%);
    padding: 1.4rem 1.8rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}}
.tnt-page-header::after {{
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}}
.tnt-page-header h2 {{
    color: white !important;
    margin: 0 0 4px 0;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.01em;
}}
.tnt-page-header p {{
    color: rgba(255,255,255,0.78);
    margin: 0;
    font-size: 0.85rem;
    font-weight: 400;
}}

.tnt-card {{
    background: white;
    border: 1px solid {GRAY_200};
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}}
.tnt-card-blue {{
    border-left: 4px solid {BLUE};
    background: {BLUE_LIGHT};
}}
.tnt-card-green {{
    border-left: 4px solid {GREEN};
    background: {GREEN_LIGHT};
}}
.tnt-card-red {{
    border-left: 4px solid {RED};
    background: {RED_LIGHT};
}}
.tnt-card-amber {{
    border-left: 4px solid {AMBER};
    background: {AMBER_LIGHT};
}}

.tnt-section-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {TEXT_MUTED};
    margin: 1.2rem 0 0.5rem 0;
}}

footer {{ visibility: hidden; }}
</style>
"""


def inject_global_css() -> None:
    """Inject CSS global T.U.N.T.A.S ke halaman. Dipanggil sekali per page."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


# ── Komponen UI reusable ──────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", icon_name: str = "", icon_offset: int = 0) -> None:
    """
    Render header halaman bergaya T.U.N.T.A.S.
    icon_offset: gunakan nilai negatif (misal: -4) untuk menaikkan ikon.
    """
    from utils.icons import icon_html
    
    # Bungkus ikon dengan div yang punya transform untuk naik-turun
    ico_html_raw = icon_html(icon_name, size=28, color="rgba(255,255,255,0.9)") if icon_name else ""
    ico = f'<div style="transform: translateY({icon_offset}px); line-height: 0;">{ico_html_raw}</div>' if icon_name else ""
    
    sub = f'<p style="margin:0; opacity:0.8; font-size:0.9rem;">{subtitle}</p>' if subtitle else ""
    
    st.markdown(
        f'<div class="tnt-page-header" style="margin-bottom: 1.5rem;">'
        f'  <div style="display:flex; align-items:center; gap:14px;">'
        f'    {ico}'
        f'    <div style="display:flex; flex-direction:column; justify-content:center;">'
        f'      <h2 style="margin:0; padding:0; line-height:1.2;">{title}</h2>'
        f'      {sub}'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def info_card(text: str, variant: str = "blue") -> None:
    """Render kartu info berwarna. variant: blue | green | red | amber"""
    st.markdown(
        f'<div class="tnt-card tnt-card-{variant}">'
        f'<p style="margin:0; font-size:0.875rem; line-height:1.6;">{text}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    """Label section kecil uppercase."""
    st.markdown(
        f'<p class="tnt-section-title">{text}</p>',
        unsafe_allow_html=True,
    )
