"""
pages/login_pg.py — Halaman Login T.U.N.T.A.S
===============================================
Halaman ini dirender HANYA ketika user belum terautentikasi.
app.py menggunakan st.switch_page() untuk mengarahkan ke sini,
sehingga tidak ada double-render di app.py.

Setelah login berhasil, st.switch_page() mengembalikan user ke app.py
yang akan mendeteksi authentication_status = True dan menampilkan
halaman yang sebenarnya.

CATATAN PENTING:
  - Halaman ini TIDAK memanggil authenticator.login(location='unrendered')
    karena itu sudah dilakukan di app.py. Di sini cukup render form saja.
  - Authenticator diambil dari st.session_state["authenticator"] yang
    sudah diinisialisasi di app.py — objek yang SAMA agar cookie konsisten.
"""

from __future__ import annotations
import gc
gc.collect()

import os
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Jika session_state["authenticator"] belum ada (user buka login_pg langsung
# tanpa melalui app.py), paksa balik ke app.py untuk inisialisasi cookie dulu.
# ─────────────────────────────────────────────────────────────────────────────
if "authenticator" not in st.session_state:
    st.switch_page("app.py")

# Jika sudah login (misal: tekan back di browser), langsung balik ke home
if st.session_state.get("authentication_status"):
    st.switch_page("app.py")

authenticator = st.session_state["authenticator"]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — login page tidak butuh sidebar
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Login — T.U.N.T.A.S",
    page_icon=os.path.join("assets", "tuntas_logos.svg"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sembunyikan sidebar & hamburger menu di halaman login
st.markdown(
    """
    <style>
        [data-testid="stSidebar"]               { display: none !important; }
        [data-testid="stSidebarCollapsedControl"]{ display: none !important; }
        #MainMenu                               { visibility: hidden; }
        footer                                  { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT LOGIN
# ─────────────────────────────────────────────────────────────────────────────
col_branding, col_form = st.columns([2, 1], gap="large")

with col_branding:
    # Banner quote / branding
    from utils.quotes import get_random_quote

    # Inisialisasi quote sekali per session agar tidak berubah saat form diisi
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
        '<span style="font-size:0.5em; color:#1f77b4;">v1.0</span></h1>'
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

    # ── Render form login ──────────────────────────────────────────────────────
    # Ini satu-satunya tempat form dirender → tidak ada duplikasi render
    authenticator.login(location="main")

    auth_status = st.session_state.get("authentication_status")

    if auth_status is True:
        # Login berhasil → kembalikan ke router utama (app.py)
        # app.py akan mendeteksi status True dan menampilkan halaman utama
        st.success("✅ Login berhasil! Mengarahkan...")
        st.rerun()

    elif auth_status is False:
        st.error("❌ Username atau password salah.")
        st.caption("Hubungi admin SPI jika Anda lupa kredensial.")

    else:
        # auth_status is None → belum ada input
        st.caption("🔒 Masukkan kredensial SPI untuk mengakses sistem.")

    # Catatan versi di bawah form
    st.markdown(
        '<div style="margin-top:2rem; font-size:0.72rem; color:#94A3B8; text-align:center;">'
        'T.U.N.T.A.S v1.0 &nbsp;·&nbsp; SPI PT. PG Candi Baru &nbsp;·&nbsp; 2026'
        '</div>',
        unsafe_allow_html=True,
    )

gc.collect()
