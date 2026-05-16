"""
T.U.N.T.A.S - Trackable Unit for Networked & Transparent Audit System
Main Entry Point & Router  |  v1.1 — Supabase Auth + localStorage
SPI PT. PG Candi Baru

PERUBAHAN v1.1 (Session Persistence Fix):
  Menggantikan streamlit-authenticator (cookie-based) dengan
  utils/auth_manager.py (Supabase Auth + localStorage bridge).

  MASALAH LAMA:
    streamlit-authenticator menyimpan JWT di browser cookie dengan
    SameSite=Lax. Browser modern memblokir third-party cookies di
    lingkungan iframe Streamlit Cloud → forced re-login setiap refresh.

  SOLUSI BARU:
    1. Supabase Auth mengelola JWT + refresh token
    2. localStorage menyimpan token (first-party, tidak kena SameSite)
    3. JS bridge membaca localStorage → set URL query_params
    4. Streamlit rerun → Python baca query_params → restore session

  ARSITEKTUR (tidak berubah dari v1.0):
    app.py = router murni, tidak pernah render UI untuk user yang belum login.
    pages/login_pg.py = render form login (satu siklus render bersih).
"""

from __future__ import annotations
import gc
gc.collect()

import os
import streamlit as st

from utils.styles import inject_global_css
from utils.icons  import icon_html
from utils.auth_manager import check_session, logout

# ─────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="T.U.N.T.A.S",
    page_icon=os.path.join("assets", "tuntas_logos.svg"),
    layout="wide",
)
inject_global_css()

# ── Definisi Halaman ───────────────────────────────────────────────────────────
pg_login  = st.Page("pages/login_pg.py",      title="Login")
pg_home   = st.Page("pages/0_Beranda.py",     title="Beranda",      default=True)
pg_dash   = st.Page("pages/1_Dashboard.py",   title="Dashboard")
pg_input  = st.Page("pages/2_Input_Audit.py", title="Input Temuan")
pg_action = st.Page("pages/3_Action_Plans.py",title="Action Plans")

# ─────────────────────────────────────────────────────────────────────────────
# 2. SESSION CHECK
#    Menggantikan: authenticator.login(location="unrendered")
#    check_session() menangani semua sumber: session_state → query_params → JS
# ─────────────────────────────────────────────────────────────────────────────
is_authenticated = check_session()

# ─────────────────────────────────────────────────────────────────────────────
# 3. ROUTING UTAMA
# ─────────────────────────────────────────────────────────────────────────────
if is_authenticated:

    pg = st.navigation(
        [pg_home, pg_dash, pg_input, pg_action],
        position="hidden",
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        user_name = st.session_state.get("name", "Pengguna")
        st.write(f"Halo, **{user_name}** 👋")
        st.divider()
        st.markdown("### MENU NAVIGASI")

        nav_items = [
            ("home",         pg_home,   "Beranda"),
            ("dashboard",    pg_dash,   "Dashboard"),
            ("input_temuan", pg_input,  "Input Temuan"),
            ("action_plans", pg_action, "Action Plans"),
        ]

        for ico, page_obj, label in nav_items:
            st.markdown(
                f'<div style="position:relative;height:0;top:5px;left:15px;'
                f'pointer-events:none;z-index:100;">'
                f'{icon_html(ico, size=18, color="white")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.page_link(page_obj, label="\u00a0" * 12 + label)

        st.divider()
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Bersihkan", type="primary", use_container_width=True,
                         help="Bersihkan cache data"):
                st.cache_data.clear()
                gc.collect()
                st.rerun()
        with col_2:
            if st.button("Keluar", type="secondary", use_container_width=True):
                logout()        # ← Menggantikan: authenticator.logout()
                st.rerun()

    pg.run()

else:
    # ── Tidak Terautentikasi → Delegasikan ke login_pg.py ────────────────────
    pg = st.navigation([pg_login], position="hidden")
    pg.run()

gc.collect()
