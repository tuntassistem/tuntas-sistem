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
from utils.styles import inject_global_css
from utils.icons import icon_html
from utils.quotes import get_random_quote

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="T.U.N.T.A.S", 
    page_icon=os.path.join("assets", "tuntas_logos.svg"),
    layout="wide"
)
inject_global_css()

# 2. DATA USER & AUTH (Official Streamlit Method to Plain Dict)
# .to_dict() adalah cara resmi untuk mengubah brankas AttrDict jadi Dict biasa
secrets_dict = st.secrets.to_dict()
credentials = secrets_dict["credentials"]
auth_config = secrets_dict["auth"]

# 3. INISIALISASI AUTHENTICATOR
authenticator = stauth.Authenticate(
    credentials,
    auth_config["cookie_name"],
    auth_config["cookie_key"],
    auth_config["cookie_expiry_days"]
)

# 4. LOGIKA AUTHENTIKASI (Silent Check Cookie)
authenticator.login(location='unrendered')

# --- GERBANG TAMPILAN UTAMA ---

# CASE A: USER SUDAH TERAUTENTIKASI
if st.session_state.get("authentication_status"):
    user_name = st.session_state["name"]
    
    # DEFINISI HALAMAN
    pg_home = st.Page("pages/0_Beranda.py", title="Beranda", default=True)
    pg_dash = st.Page("pages/1_Dashboard.py", title="Dashboard")
    pg_input = st.Page("pages/2_Input_Audit.py", title="Input Temuan")
    pg_action = st.Page("pages/3_Action_Plans.py", title="Action Plans")

    # INISIALISASI NAVIGASI
    pg = st.navigation([pg_home, pg_dash, pg_input, pg_action], position="hidden")

    # SIDEBAR CUSTOM
    with st.sidebar:
        st.write(f"Halo, **{user_name}** 👋")
        st.divider()
        
        st.markdown("### MENU NAVIGASI")
        nav_items = [
            ("home",         pg_home,   "Beranda"),
            ("dashboard",    pg_dash,   "Dashboard"),
            ("input_temuan", pg_input,  "Input Temuan"),
            ("action_plans", pg_action, "Action Plans"),
        ]

        for icon_k, page_obj, label in nav_items:
            current_pg_title = st.session_state.get("current_page_title", pg_home.title)
            is_active = (current_pg_title == page_obj.title)
            display_label = f"**{label}** ←" if is_active else label
            
            st.markdown(
                f"""
                <div style="position: relative; height: 0px; top: 5px; left: 15px; pointer-events: none; z-index: 100;">
                    {icon_html(icon_k, size=18, color="white")}
                </div>
                """, unsafe_allow_html=True
            )
            if st.page_link(page_obj, label=f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{display_label}"):
                st.session_state["current_page_title"] = page_obj.title
        
        st.divider()
        
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Bersihkan", type="primary", use_container_width=True, help="Hapus Cache & RAM"):
                st.cache_data.clear()
                gc.collect()
                st.rerun()
        with col_2:
            if st.button("Keluar", type="secondary", use_container_width=True):
                authenticator.logout(location='unrendered')
                st.session_state["authentication_status"] = None
                st.rerun()

    # JALANKAN HALAMAN
    pg.run()

# CASE B: USER BELUM LOGIN / GAGAL
else:
    # Sembunyikan sidebar saat login page
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="stSidebarCollapsedControl"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    col_img, col_login = st.columns([2, 1], gap="large")

    with col_img:
        selected_quote = get_random_quote()
        st.markdown(f"""
            <div style="background-color: #B4D9F3; padding: 40px; border-radius: 15px; border-left: 10px solid #1f77b4; margin-top: 50px;">
                <h2 style="color: #1f77b4; font-family: 'Georgia', serif; font-style: italic;">{selected_quote}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="margin-top: 30px;">
                <h1 style='margin-bottom: 0; color: #1f77b4;'>T.U.N.T.A.S <span style='font-size: 0.5em; color: #1f77b4;'>v1.0</span></h1>
                <p style='font-size: 1.1em; color: #555;'><i>Trackable Unit for Networked & Transparent Audit System</i></p>
                <hr style='margin-top: 0;'>
                <h4 style='color: #1f77b4;'>SPI PT. PG Candi Baru</h4>
            </div>
        """, unsafe_allow_html=True)

    with col_login:
        st.write("### Login System")
        authenticator.login(location='main')
        
        if st.session_state.get("authentication_status") is False:
            st.error('Username/password salah!')
        elif st.session_state.get("authentication_status") is None:
            st.caption('Masukkan kredensial SPI untuk mengakses data.')

# ── PEMBERSIHAN RAM AKHIR ─────────────────────────────────────────────────
gc.collect()
