"""
pages/login_pg.py — Halaman Login T.U.N.T.A.S  v1.1
=====================================================
Form login menggunakan Supabase Auth via utils/auth_manager.

PERUBAHAN dari v1.0:
  - Hapus ketergantungan pada st.session_state["authenticator"]
  - Form email + password custom (bukan authenticator.login())
  - Login via auth_manager.login() → Supabase Auth
  - Setelah login berhasil: token otomatis tersimpan di localStorage
    sehingga user tidak perlu login ulang meski refresh halaman
"""

from __future__ import annotations
import gc
gc.collect()

import os
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Guard: Jika sudah login, balik ke router utama
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("authentication_status"):
    st.switch_page("app.py")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — login page tidak butuh sidebar
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Login — T.U.N.T.A.S",
    page_icon=os.path.join("assets", "tuntas_logos.svg"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sembunyikan sidebar & hamburger di halaman login
st.markdown(
    """
    <style>
        [data-testid="stSidebar"]                { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        #MainMenu                                { visibility: hidden; }
        footer                                   { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Import setelah set_page_config
from utils.quotes       import get_random_quote
from utils.auth_manager import login   # ← fungsi login baru

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT LOGIN: Branding (kiri) | Form (kanan)
# ─────────────────────────────────────────────────────────────────────────────
col_branding, col_form = st.columns([2, 1], gap="large")

with col_branding:
    # Quote diinisialisasi sekali per session agar tidak berubah saat form diketik
    if "login_quote" not in st.session_state:
        st.session_state["login_quote"] = get_random_quote()

    st.markdown(
        f'<div style="background-color:#B4D9F3; padding:40px; border-radius:15px; '
        f'border-left:10px solid #1f77b4; margin-top:50px;">'
        f'<h2 style="color:#1f77b4; font-family:Georgia,serif; font-style:italic;">'
        f'{st.session_state["login_quote"]}'
        f'</h2>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="margin-top:30px;">'
        '<h1 style="margin-bottom:0; color:#1f77b4;">T.U.N.T.A.S '
        '<span style="font-size:0.5em; color:#1f77b4;">v1.1</span></h1>'
        '<p style="font-size:1.1em; color:#555;"><i>'
        'Trackable Unit for Networked &amp; Transparent Audit System'
        '</i></p>'
        '<hr style="margin-top:0;">'
        '<h4 style="color:#1f77b4;">SPI PT. PG Candi Baru</h4>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_form:
    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔐 Login Sistem")

    # ── Form Login ─────────────────────────────────────────────────────────
    # Menggunakan st.form agar tidak rerun setiap karakter diketik
    with st.form("form_login", clear_on_submit=False):
        st.markdown(
            '<p style="font-size:0.82rem; color:#475569; margin-bottom:0.3rem;">'
            'Masukkan kredensial SPI untuk mengakses sistem.</p>',
            unsafe_allow_html=True,
        )

        email    = st.text_input("Email",    placeholder="auditor@pgcandibaru.com",  key="login_email")
        password = st.text_input("Password", placeholder="••••••••••",               type="password", key="login_password")

        submitted = st.form_submit_button(
            "Masuk →",
            type="primary",
            use_container_width=True,
        )

    # ── Proses Login ────────────────────────────────────────────────────────
    if submitted:
        if not email.strip() or not password:
            st.error("Email dan password wajib diisi.")
        else:
            with st.spinner("Memverifikasi kredensial..."):
                success, message = login(email, password)

            if success:
                st.success(f"✅ {message} Mengarahkan ke sistem...")
                # Beri waktu sebentar agar JS localStorage writer ter-render
                # sebelum rerun (penting untuk persistensi)
                st.rerun()
            else:
                st.error(f"❌ {message}")
                st.caption("Hubungi admin SPI jika Anda lupa kredensial.")

    # ── Catatan versi ───────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin-top:2rem; font-size:0.72rem; color:#94A3B8; text-align:center;">'
        'T.U.N.T.A.S v1.1 &nbsp;·&nbsp; SPI PT. PG Candi Baru &nbsp;·&nbsp; 2026<br>'
        '<span style="font-size:0.68rem;">Secured by Supabase Auth</span>'
        '</div>',
        unsafe_allow_html=True,
    )

gc.collect()
