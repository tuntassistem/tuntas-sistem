"""
pages/0_Beranda.py — T.U.N.T.A.S Beranda
=========================================
Trackable Unit for Networked & Transparent Audit System
SPI PT. PG Candi Baru | v1.1

CHANGELOG v1.1 — Alignment Fix:
  Sebelumnya semua konten dijejal ke 2 kolom (kiri & kanan) sehingga
  "Lingkup Pengawasan SPI" (kolom kiri, bawah) dan "Skala Signifikansi
  Temuan" (kolom kanan, bawah) tidak pernah sejajar karena tinggi
  konten di atasnya berbeda.

  Solusi: pisah menjadi 2 baris horizontal yang terpisah:
    Baris 1 → col_kiri: "Tentang Sistem"
               col_kanan: "Panduan Penggunaan"
    Baris 2 → col_kiri: "Lingkup Pengawasan SPI"     ← SEJAJAR
               col_kanan: "Skala Signifikansi Temuan" ← SEJAJAR

  Karena berada di st.columns() yang SAMA dan merupakan elemen
  pertama di baris masing-masing, keduanya selalu dimulai dari
  titik vertikal yang identik.
"""

import gc
gc.collect()

import streamlit as st
from datetime import date
import os

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
_ICON_PATH = os.path.join("assets", "tuntas_logos.svg")

st.set_page_config(
    page_title="T.U.N.T.A.S — SPI PT. PG Candi Baru",
    page_icon=_ICON_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "T.U.N.T.A.S v1.0\n"
            "Trackable Unit for Networked & Transparent Audit System\n"
            "SPI PT. PG Candi Baru\n"
            "Dikembangkan oleh Muhammad Hamzah Nashirudin, UNESA 2026."
        )
    },
)

# Import setelah set_page_config
from utils.styles import (
    inject_global_css, section_title,
    BLUE, GREEN, RED, AMBER, GRAY_500,
)
from utils.icons import icon_html
from utils.supabase_client import fetch_audit_findings, fetch_action_plans

inject_global_css()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1.4rem 0.8rem 1rem 0.8rem; text-align:center;">
            <div style="font-size:2rem; font-weight:900; letter-spacing:0.05em;
                        color:white; line-height:1;">T.U.N.T.A.S</div>
            <div style="font-size:0.6rem; color:rgba(255,255,255,0.65);
                        font-weight:500; letter-spacing:0.12em;
                        text-transform:uppercase; margin-top:4px; line-height:1.4;">
                Trackable Unit for<br>Networked &amp; Transparent<br>Audit System
            </div>
            <div style="margin-top:10px; padding-top:10px;
                        border-top:1px solid rgba(255,255,255,0.15);
                        font-size:0.72rem; color:rgba(255,255,255,0.55);">
                SPI &middot; PT. PG Candi Baru
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _today_str = date.today().strftime("%d %B %Y")
    st.markdown(
        f'<div style="padding:0 0.8rem; font-size:0.78rem; color:rgba(255,255,255,0.6);">'
        f'{icon_html("calendar", 14, "rgba(255,255,255,0.6)")}&nbsp;{_today_str}<br>'
        f'{icon_html("user",     14, "rgba(255,255,255,0.6)")}&nbsp;Tim SPI'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        '<div style="padding:0 0.8rem; font-size:0.68rem; '
        'color:rgba(255,255,255,0.4); line-height:1.6;">'
        'T.U.N.T.A.S v1.0<br>UNESA &times; PG Candi Baru<br>Muhammad Hamzah Nashirudin'
        '</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# HEADER UTAMA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:linear-gradient(135deg,#003D7A 0%,#0054A6 55%,#1A7FD4 100%);
                padding:2rem 2.2rem; border-radius:16px; margin-bottom:1.8rem;
                position:relative; overflow:hidden;">
        <div style="position:absolute; top:-40px; right:-40px; width:180px; height:180px;
                    background:rgba(255,255,255,0.05); border-radius:50%;"></div>
        <div style="position:absolute; bottom:-20px; right:80px; width:100px; height:100px;
                    background:rgba(255,255,255,0.04); border-radius:50%;"></div>
        <div style="position:relative;">
            <div style="font-size:2.2rem; font-weight:900; color:white;
                        letter-spacing:0.06em; line-height:1;">T.U.N.T.A.S</div>
            <div style="font-size:0.82rem; color:rgba(255,255,255,0.65);
                        margin-top:4px; font-weight:400; letter-spacing:0.02em;">
                Trackable Unit for Networked &amp; Transparent Audit System
            </div>
            <div style="margin-top:12px; font-size:0.9rem;
                        color:rgba(255,255,255,0.85); font-weight:500;">
                Satuan Pengawas Internal (SPI) &nbsp;&middot;&nbsp;
                PT. PG Candi Baru &nbsp;&middot;&nbsp; Maret &ndash; Juni 2026
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA — guard clause jika DataFrame kosong
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data dari Supabase..."):
    df_finding = fetch_audit_findings()
    df_ap      = fetch_action_plans()

# ─────────────────────────────────────────────────────────────────────────────
# KPI SCORECARD
# ─────────────────────────────────────────────────────────────────────────────
section_title("Ringkasan Status Pengawasan")

c1, c2, c3, c4, c5 = st.columns(5)

total_temuan  = len(df_finding)
temuan_open   = (
    int((df_finding["status_temuan"].astype(str) == "OPEN").sum())
    if not df_finding.empty and "status_temuan" in df_finding.columns else 0
)
temuan_kritis = (
    int((df_finding["tingkat_signifikansi"].astype(str) == "KRITIS").sum())
    if not df_finding.empty and "tingkat_signifikansi" in df_finding.columns else 0
)
tl_terlambat  = (
    int((df_ap["status_tl"].astype(str) == "MELEWATI_TARGET").sum())
    if not df_ap.empty and "status_tl" in df_ap.columns else 0
)
tl_selesai    = (
    int((df_ap["status_tl"].astype(str) == "CLOSED").sum())
    if not df_ap.empty and "status_tl" in df_ap.columns else 0
)

c1.metric("Total Temuan",  total_temuan)
c2.metric("Temuan Open",   temuan_open,
          delta=f"{temuan_open} belum ditutup" if temuan_open > 0 else "Semua selesai",
          delta_color="inverse" if temuan_open > 0 else "normal")
c3.metric("Temuan Kritis", temuan_kritis,
          delta=f"+{temuan_kritis} perlu eskalasi" if temuan_kritis > 0 else "Nihil",
          delta_color="inverse" if temuan_kritis > 0 else "off")
c4.metric("TL Terlambat",  tl_terlambat,
          delta_color="inverse" if tl_terlambat > 0 else "normal")
c5.metric("TL Selesai",    tl_selesai)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# BARIS 1: Tentang Sistem (kiri) | Panduan Penggunaan (kanan)
# ═════════════════════════════════════════════════════════════════════════════
col_l, col_r = st.columns([1.3, 1])

# ── KIRI: Tentang Sistem ──────────────────────────────────────────────────────
with col_l:
    section_title("Tentang Sistem")
    st.markdown(
        f'<div class="tnt-card" '
        f'style="border-left:4px solid {BLUE}; background:#EEF4FF;">'
        f'<div style="font-size:0.95rem; line-height:1.75; color:#1E293B;">'
        f'<strong>T.U.N.T.A.S</strong> adalah sistem manajemen audit internal '
        f'berbasis web untuk SPI PT. PG Candi Baru yang memungkinkan:'
        f'<ul style="margin:0.5rem 0 0 0; padding-left:1.1rem;">'
        f'<li>Pencatatan temuan audit standar <strong>5C (IIA)</strong></li>'
        f'<li>Monitoring tindak lanjut rekomendasi secara <strong>real-time</strong></li>'
        f'<li>Visualisasi interaktif untuk pelaporan kepada <strong>Direktur</strong></li>'
        f'<li>Alert otomatis tindak lanjut yang melewati <strong>deadline</strong></li>'
        f'</ul>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── KANAN: Panduan Penggunaan ─────────────────────────────────────────────────
with col_r:
    section_title("Panduan Penggunaan")
    guide = [
        ("dashboard",    "Dashboard",    "Visualisasi KPI & grafik interaktif",  BLUE),
        ("input_temuan", "Input Temuan", "Catat temuan baru standar 5C IIA",     BLUE),
        ("action_plans", "Action Plans", "Update & verifikasi tindak lanjut",    GREEN),
    ]
    for ico, name, desc, color in guide:
        st.markdown(
            f'<div class="tnt-card" style="margin-bottom:6px; padding:0.8rem 1rem;">'
            f'<div style="display:flex; align-items:center; gap:10px;">'
            f'<div style="background:{color}; border-radius:8px; padding:7px;">'
            f'{icon_html(ico, 18, "white")}'
            f'</div>'
            f'<div>'
            f'<div style="font-weight:700; font-size:0.88rem; color:#1E293B;">{name}</div>'
            f'<div style="font-size:0.78rem; color:{GRAY_500};">{desc}</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ═════════════════════════════════════════════════════════════════════════════
# BARIS 2: Lingkup Pengawasan SPI (kiri) | Skala Signifikansi (kanan)
#
# ALIGNMENT FIX:
# Kedua section ini berada di st.columns() yang SAMA dan masing-masing
# adalah elemen PERTAMA di kolomnya → selalu dimulai dari titik vertikal
# yang identik → sejajar secara alami tanpa CSS tambahan.
# ═════════════════════════════════════════════════════════════════════════════
col_l2, col_r2 = st.columns([1.3, 1])

# ── KIRI: Lingkup Pengawasan SPI ──────────────────────────────────────────────
with col_l2:
    section_title("Lingkup Pengawasan SPI")

    kabag_units = [
        ("file",    "Keuangan / IT / MR"),
        ("user",    "SDM &amp; Umum"),
        ("trending","Tanaman"),
        ("chart",   "Instalasi"),
        ("shield",  "Pabrikasi"),
        ("eye",     "Quality Assurance"),
    ]
    grid_items = "".join(
        f'<div style="padding:7px 12px; background:{BLUE}; color:white; '
        f'border-radius:6px; font-weight:500; font-size:0.82rem; '
        f'display:flex; align-items:center; gap:6px;">'
        f'{icon_html(ico, 13, "white")}&nbsp;{lbl}'
        f'</div>'
        for ico, lbl in kabag_units
    )
    st.markdown(
        f'<div class="tnt-card">'
        f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">'
        f'{grid_items}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── KANAN: Skala Signifikansi Temuan ─────────────────────────────────────────
with col_r2:
    section_title("Skala Signifikansi Temuan")

    badges = [
        ("KRITIS", RED,   "Eskalasi segera ke Direktur"),
        ("TINGGI", AMBER, "Tindakan dalam waktu dekat"),
        ("SEDANG", BLUE,  "Pantau & rencanakan perbaikan"),
        ("RENDAH", GREEN, "Monitor berkala"),
    ]

    badge_rows = "".join(
        f'<div style="display:flex; align-items:center; gap:10px; '
        f'padding:8px 0; border-bottom:1px solid #F1F5F9;">'
        f'<span style="background:{color}; color:white; padding:3px 12px; '
        f'border-radius:20px; font-size:0.72rem; font-weight:700; '
        f'min-width:64px; text-align:center; white-space:nowrap;">{label}</span>'
        f'<span style="font-size:0.82rem; color:{GRAY_500};">{desc}</span>'
        f'</div>'
        for label, color, desc in badges
    )
    st.markdown(
        f'<div class="tnt-card">'
        f'{badge_rows}'
        f'</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ALERT AKTIF
# ─────────────────────────────────────────────────────────────────────────────
section_title("Peringatan Aktif")
has_alert = False

# -- Alert 1: TL Terlambat ----------------------------------------------------
if not df_ap.empty and "status_tl" in df_ap.columns:
    df_late = df_ap[df_ap["status_tl"].astype(str) == "MELEWATI_TARGET"]
    if not df_late.empty:
        has_alert = True
        st.markdown(
            f'<div class="tnt-card tnt-card-red">'
            f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">'
            f'{icon_html("warning", 18, RED)}'
            f'<strong style="color:{RED};">'
            f'{len(df_late)} Tindak Lanjut Melewati Target Deadline'
            f'</strong>'
            f'</div>'
            f'<p style="margin:0; font-size:0.83rem; color:#7F1D1D;">'
            f'Segera koordinasikan dengan PIC terkait dan lakukan eskalasi jika diperlukan.'
            f'</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        _cols_map = {
            "nomor_temuan":  "No. Temuan",
            "nama_unit":     "Unit",
            "pic_pelaksana": "PIC",
            "tgl_target":    "Target",
            "status_tl":     "Status",
        }
        _avail = {k: v for k, v in _cols_map.items() if k in df_late.columns}
        if _avail:
            st.dataframe(
                df_late[list(_avail.keys())].rename(columns=_avail),
                use_container_width=True,
                hide_index=True,
            )

# -- Alert 2: Temuan KRITIS masih OPEN ----------------------------------------
if not df_finding.empty and {"tingkat_signifikansi", "status_temuan"}.issubset(df_finding.columns):
    df_ko = df_finding[
        (df_finding["tingkat_signifikansi"].astype(str) == "KRITIS") &
        (df_finding["status_temuan"].astype(str) == "OPEN")
    ]
    if not df_ko.empty:
        has_alert = True
        st.markdown(
            f'<div class="tnt-card tnt-card-red" style="margin-top:8px;">'
            f'<div style="display:flex; align-items:center; gap:8px;">'
            f'{icon_html("kritis", 18, RED)}'
            f'<strong style="color:{RED};">'
            f'{len(df_ko)} Temuan KRITIS masih berstatus OPEN — perhatian segera diperlukan'
            f'</strong>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# -- Semua OK -----------------------------------------------------------------
if not has_alert:
    st.markdown(
        f'<div class="tnt-card tnt-card-green">'
        f'<div style="display:flex; align-items:center; gap:8px;">'
        f'{icon_html("success", 18, GREEN)}'
        f'<strong style="color:{GREEN};">'
        f'Tidak ada peringatan aktif. Semua tindak lanjut on-track.'
        f'</strong>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    f'<p style="font-size:0.75rem; color:{GRAY_500}; text-align:center;">'
    f'T.U.N.T.A.S v1.0 &nbsp;&middot;&nbsp; SPI PT. PG Candi Baru &nbsp;&middot;&nbsp; 2026 '
    f'&nbsp;&middot;&nbsp; Data diperbarui otomatis dari Supabase'
    f'</p>',
    unsafe_allow_html=True,
)

gc.collect()
