"""
T.U.N.T.A.S - Trackable Unit for Networked & Transparent Audit System
Main Entry Point & Router
SPI PT. PG Candi Baru | v1.0

ARSITEKTUR ROUTING:
  app.py           → router murni: cek cookie, arahkan ke halaman yang tepat
  pages/login_pg   → halaman login (dirender sendiri, tidak campur di sini)
  pages/0_Beranda  → home setelah login berhasil

KENAPA DIPISAH?
  Double-render glitch terjadi karena dua hal yang berjalan bersamaan
  di file yang sama:
    1. authenticator.login(location='unrendered') → rerun internal saat
       pertama kali baca cookie
    2. UI login dirender di blok else yang sama

  Solusi: app.py TIDAK pernah merender UI apapun untuk user yang belum
  login. Ia hanya cek status lalu st.switch_page() ke login_pg.py.
  login_pg.py merender form-nya sendiri dalam satu siklus render yang
  bersih → glitch hilang, fungsi cookie tidak terganggu.
"""

from __future__ import annotations
import gc
gc.collect()

import os
import streamlit as st
import streamlit_authenticator as stauth

from utils.styles import inject_global_css
from utils.icons import icon_html

# ─────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="T.U.N.T.A.S",
    page_icon=os.path.join("assets", "tuntas_logos.svg"),
    layout="wide",
)
inject_global_css()

# ─────────────────────────────────────────────────────────────────────────────
# 2. BACA CREDENTIALS DARI secrets.toml
#
# Format yang dibutuhkan di .streamlit/secrets.toml:

_secrets  = st.secrets.to_dict()
_creds    = _secrets["credentials"]
_auth_cfg = _secrets["auth"]

# ─────────────────────────────────────────────────────────────────────────────
# 3. AUTHENTICATOR — disimpan di session_state agar TIDAK dibuat ulang
#    setiap rerun. Objek yang sama persis dibutuhkan agar cookie JWT
#    diverifikasi dengan kunci yang konsisten.
# ─────────────────────────────────────────────────────────────────────────────
if "authenticator" not in st.session_state:
    st.session_state["authenticator"] = stauth.Authenticate(
        _creds,
        _auth_cfg["cookie_name"],
        _auth_cfg["cookie_key"],
        _auth_cfg["cookie_expiry_days"],
    )

authenticator: stauth.Authenticate = st.session_state["authenticator"]

# ─────────────────────────────────────────────────────────────────────────────
# 4. SILENT COOKIE CHECK
#    Hanya membaca cookie — tidak merender UI apapun.
#    Hasil ditulis ke st.session_state["authentication_status"].
# ─────────────────────────────────────────────────────────────────────────────
authenticator.login(location="unrendered")

# ── Definisi Halaman ──────────────────────────────────────────────────────
pg_login  = st.Page("pages/login_pg.py",      title="Login")
pg_home   = st.Page("pages/0_Beranda.py",     title="Beranda",      default=True)
pg_dash   = st.Page("pages/1_Dashboard.py",   title="Dashboard")
pg_input  = st.Page("pages/2_Input_Audit.py", title="Input Temuan")
pg_action = st.Page("pages/3_Action_Plans.py",title="Action Plans")


# ─────────────────────────────────────────────────────────────────────────────
# 5. ROUTING UTAMA
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("authentication_status"):

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
        cur_title = st.session_state.get("current_page_title", pg_home.title)

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
                authenticator.logout(location="unrendered")
                st.session_state["authentication_status"] = None
                st.rerun()

    pg.run()

else:
    # ── Tidak Terautentikasi: Delegasikan sepenuhnya ke login_pg.py ──────────
    # app.py sama sekali tidak merender UI di sini → tidak ada double-render.
    pg = st.navigation([pg_login], position="hidden")
    pg.run()
# ─────────────────────────────────────────────────────────────────────────────
gc.collect()
