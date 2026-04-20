"""
T.U.N.T.A.S - Trackable Unit for Networked & Transparent Audit System
Main Entry Point & Authentication Gate
Optimized for Memory Management & Secure Secret Handling
"""

from __future__ import annotations
import gc

# ── PEMBERSIHAN RAM AWAL ──────────────────────────────────────────────────
gc.collect()

import streamlit as st
import streamlit_authenticator as stauth
import os
import gc
from utils.styles import inject_global_css
from utils.icons import icon_html
from utils.quotes import get_random_quote

# --- CONFIG ---
st.set_page_config(page_title="T.U.N.T.A.S", layout="wide")
inject_global_css()

# --- LOAD AUTH ---
try:
    auth_data = st.secrets.to_dict()
    authenticator = stauth.Authenticate(
        auth_data["credentials"],
        auth_data["auth"]["cookie_name"],
        auth_data["auth"]["cookie_key"],
        auth_data["auth"]["cookie_expiry_days"]
    )
except Exception as e:
    st.error("Secrets.toml tidak valid!")
    st.stop()

# --- LOGIKA GERBANG (LOGIN) ---
def login_gate():
    # Sembunyikan Sidebar
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    
    col_img, col_login = st.columns([2, 1], gap="large")
    with col_img:
        st.markdown(f"<h2>{get_random_quote()}</h2>", unsafe_allow_html=True)
        st.markdown("<h1>T.U.N.T.A.S v1.0</h1><p>SPI PT. PG Candi Baru</p>", unsafe_allow_html=True)

    with col_login:
        st.write("### Login System")
        # PANGGIL LOGIN SEKALI SAJA DI SINI
        name, authentication_status, username = authenticator.login(location='main')
        
        if authentication_status is False:
            st.error('Username/password salah!')
        elif authentication_status is None:
            st.caption('Masukkan kredensial SPI.')
        
        return authentication_status

# --- JALANKAN SISTEM ---
# 1. Cek Cookie secara diam-diam dulu
authenticator.login(location='unrendered')

if st.session_state.get("authentication_status"):
    # --- JIKA SUDAH LOGIN (DASHBOARD UTAMA) ---
    st.session_state["authenticator"] = authenticator
    
    # Inisialisasi Halaman
    pg_home = st.Page("pages/0_Beranda.py", title="Beranda", default=True)
    pg_dash = st.Page("pages/1_Dashboard.py", title="Dashboard")
    pg_input = st.Page("pages/2_Input_Audit.py", title="Input Temuan")
    pg_action = st.Page("pages/3_Action_Plans.py", title="Action Plans")

    pg = st.navigation([pg_home, pg_dash, pg_input, pg_action], position="hidden")

    # Sidebar Custom
    with st.sidebar:
        st.write(f"Halo, **{st.session_state['name']}** 👋")
        st.divider()
        # Navigasi Manual
        for icon_k, page_obj, label in [("home", pg_home, "Beranda"), ("dashboard", pg_dash, "Dashboard"), ("input_temuan", pg_input, "Input Temuan"), ("action_plans", pg_action, "Action Plans")]:
            active = (st.session_state.get("current_page_title") == page_obj.title)
            display = f"**{label}** ←" if active else label
            st.markdown(f'<div style="position:relative;top:32px;left:15px;pointer-events:none;">{icon_html(icon_k, 18, "white")}</div>', unsafe_allow_html=True)
            if st.page_link(page_obj, label=f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{display}"):
                st.session_state["current_page_title"] = page_obj.title
        
        st.divider()
        if st.button("Keluar", width="stretch"):
            authenticator.logout(location='unrendered')
            st.session_state["authentication_status"] = None
            st.rerun()

    pg.run()

else:
    # --- JIKA BELUM LOGIN (TAMPILKAN GATE) ---
    if login_gate():
        st.rerun()

# ── PEMBERSIHAN RAM AKHIR ─────────────────────────────────────────────────
gc.collect()
