"""
0_Beranda.py — T.U.N.T.A.S Beranda
==============================
Trackable Unit for Networked & Transparent Audit System
SPI PT. PG Candi Baru | Identitas Korporat ID FOOD
"""

import gc
gc.collect()

import streamlit as st
from datetime import date
from PIL import Image
import os

# 1. Load Icon
icon_path = os.path.join("assets", "tuntas_logos.svg")

# 2. Set Page Config
st.set_page_config(
    page_title="T.U.N.T.A.S — SPI PT. PG Candi Baru",
    page_icon=icon_path,
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
from utils.styles import inject_global_css, page_header, info_card, section_title, BLUE, GREEN, RED, AMBER, GRAY_500
from utils.icons import icon_html, icon_text, ICONS
from utils.supabase_client import fetch_audit_findings, fetch_action_plans

inject_global_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Identitas sistem
    st.markdown(
        f"""
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
                SPI · PT. PG Candi Baru
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="padding:0 0.8rem; font-size:0.78rem; color:rgba(255,255,255,0.6);">'
        f'{icon_html("calendar",14,"rgba(255,255,255,0.6)")} &nbsp;{date.today().strftime("%d %B %Y")}<br>'
        f'{icon_html("user",14,"rgba(255,255,255,0.6)")} &nbsp;Tim SPI'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        '<div style="padding:0 0.8rem;font-size:0.68rem;color:rgba(255,255,255,0.4);line-height:1.6;">'
        'T.U.N.T.A.S v1.0<br>UNESA × PG Candi Baru<br>Muhammad Hamzah Nashirudin'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Header Utama ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#003D7A 0%,#0054A6 55%,#1A7FD4 100%);
                padding:2rem 2.2rem; border-radius:16px; margin-bottom:1.8rem;
                position:relative; overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
                    background:rgba(255,255,255,0.05);border-radius:50%;"></div>
        <div style="position:absolute;bottom:-20px;right:80px;width:100px;height:100px;
                    background:rgba(255,255,255,0.04);border-radius:50%;"></div>
        <div style="position:relative;">
            <div style="font-size:2.2rem;font-weight:900;color:white;
                        letter-spacing:0.06em;line-height:1;">T.U.N.T.A.S</div>
            <div style="font-size:0.82rem;color:rgba(255,255,255,0.65);
                        margin-top:4px;font-weight:400;letter-spacing:0.02em;">
                Trackable Unit for Networked &amp; Transparent Audit System
            </div>
            <div style="margin-top:12px;font-size:0.9rem;color:rgba(255,255,255,0.85);font-weight:500;">
                Satuan Pengawas Internal (SPI) &nbsp;·&nbsp; PT. PG Candi Baru &nbsp;·&nbsp;
                Maret – Juni 2026
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Load Data ─────────────────────────────────────────────────────────────────
with st.spinner("Memuat data dari Supabase..."):
    df_finding = fetch_audit_findings()
    df_ap      = fetch_action_plans()

# ── KPI Scorecard ─────────────────────────────────────────────────────────────
section_title("Ringkasan Status Pengawasan")

c1, c2, c3, c4, c5 = st.columns(5)

total_temuan  = len(df_finding)
temuan_open   = int((df_finding["status_temuan"].astype(str) == "OPEN").sum())    if not df_finding.empty else 0
temuan_kritis = int((df_finding["tingkat_signifikansi"].astype(str) == "KRITIS").sum()) if not df_finding.empty else 0
tl_terlambat  = int((df_ap["status_tl"].astype(str) == "MELEWATI_TARGET").sum())  if not df_ap.empty else 0
tl_selesai    = int((df_ap["status_tl"].astype(str) == "CLOSED").sum())           if not df_ap.empty else 0

c1.metric("Total Temuan",   total_temuan)
c2.metric("Temuan Open",    temuan_open,
          delta=f"{temuan_open} belum ditutup" if temuan_open > 0 else "Semua selesai",
          delta_color="inverse" if temuan_open > 0 else "normal")
c3.metric("Temuan Kritis",  temuan_kritis,
          delta=f"+{temuan_kritis} perlu eskalasi" if temuan_kritis > 0 else "Nihil",
          delta_color="inverse" if temuan_kritis > 0 else "off")
c4.metric("TL Terlambat",   tl_terlambat,
          delta_color="inverse" if tl_terlambat > 0 else "normal")
c5.metric("TL Selesai",     tl_selesai)

st.divider()

# ── Konten 2 Kolom ────────────────────────────────────────────────────────────
col_l, col_r = st.columns([1.3, 1])

with col_l:
    section_title("Tentang Sistem")

    st.markdown(
        f"""
        <div class="tnt-card" style="border-left:4px solid {BLUE}; background:#EEF4FF;">
            <div style="font-size:0.95rem; line-height:1.75; color:#1E293B;">
                <strong>T.U.N.T.A.S</strong> adalah sistem manajemen audit internal
                berbasis web untuk SPI PT. PG Candi Baru yang memungkinkan:
                <ul style="margin:0.5rem 0 0 0; padding-left:1.1rem;">
                    <li>Pencatatan temuan audit standar <strong>5C (IIA)</strong></li>
                    <li>Monitoring tindak lanjut rekomendasi secara <strong>real-time</strong></li>
                    <li>Visualisasi interaktif untuk pelaporan kepada <strong>Direktur</strong></li>
                    <li>Alert otomatis tindak lanjut yang melewati <strong>deadline</strong></li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Lingkup Pengawasan SPI")
    
    st.markdown(
        f"""
        <div class="tnt-card" style="margin-top:0.5rem;"> 
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.82rem;">
                <div style="padding:6px 10px; background:{BLUE};color:white;
                            border-radius:6px; font-weight:500;">
                    {icon_html("file", 13, "white")} &nbsp;Keuangan / IT / MR
                </div>
                <div style="padding:6px 10px; background:{BLUE};color:white;
                            border-radius:6px; font-weight:500;">
                    {icon_html("user", 13, "white")} &nbsp;SDM &amp; Umum
                </div>
                <div style="padding:6px 10px; background:{BLUE};color:white;
                            border-radius:6px; font-weight:500;">
                    {icon_html("trending", 13, "white")} &nbsp;Tanaman
                </div>
                <div style="padding:6px 10px; background:{BLUE};color:white;
                            border-radius:6px; font-weight:500;">
                    {icon_html("chart", 13, "white")} &nbsp;Instalasi
                </div>
                <div style="padding:6px 10px; background:{BLUE};color:white;
                            border-radius:6px; font-weight:500;">
                    {icon_html("shield", 13, "white")} &nbsp;Pabrikasi
                </div>
                <div style="padding:6px 10px; background:{BLUE};color:white;
                            border-radius:6px; font-weight:500;">
                    {icon_html("eye", 13, "white")} &nbsp;Quality Assurance
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_r:
    section_title("Panduan Penggunaan")

    guide = [
        ("dashboard",    "Dashboard",      "Visualisasi KPI & grafik interaktif",    BLUE),
        ("input_temuan", "Input Temuan",   "Catat temuan baru standar 5C IIA",       BLUE),
        ("action_plans", "Action Plans",   "Update & verifikasi tindak lanjut",      GREEN),
    ]
    for ico, name, desc, color in guide:
        st.markdown(
            f'<div class="tnt-card" style="margin-bottom:6px;padding:0.8rem 1rem;">'
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<div style="background:{color};border-radius:8px;padding:7px;">'
            f'{icon_html(ico, 18, "white")}'
            f'</div>'
            f'<div>'
            f'<div style="font-weight:700;font-size:0.88rem;color:#1E293B;">{name}</div>'
            f'<div style="font-size:0.78rem;color:{GRAY_500};">{desc}</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    section_title("Skala Signifikansi Temuan")
    badges = [
        ("KRITIS", RED,   "Eskalasi segera ke Direktur"),
        ("TINGGI", AMBER, "Tindakan dalam waktu dekat"),
        ("SEDANG", BLUE,  "Pantau & rencanakan perbaikan"),
        ("RENDAH", GREEN, "Monitor berkala"),
    ]
    for label, color, desc in badges:
        st.markdown(
            f'</div>'
            f'</div>'
            f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
            f'<span style="background:{color};color:white;padding:2px 10px;'
            f'border-radius:20px;font-size:0.72rem;font-weight:700;'
            f'min-width:58px;text-align:center;">{label}</span>'
            f'<span style="font-size:0.8rem;color:{GRAY_500};">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ── Alert Aktif ───────────────────────────────────────────────────────────────
section_title("Peringatan Aktif")
has_alert = False

if not df_ap.empty:
    df_late = df_ap[df_ap["status_tl"].astype(str) == "MELEWATI_TARGET"]
    if not df_late.empty:
        has_alert = True
        st.markdown(
            f'<div class="tnt-card tnt-card-red">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
            f'{icon_html("warning", 18, RED)}'
            f'<strong style="color:{RED};">{len(df_late)} Tindak Lanjut Melewati Target Deadline</strong>'
            f'</div>'
            f'<p style="margin:0;font-size:0.83rem;color:#7F1D1D;">Segera koordinasikan dengan PIC terkait dan lakukan eskalasi jika diperlukan.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        COLS_SHOW = ["nomor_temuan","nama_unit","pic_pelaksana","tgl_target","status_tl"]
        cols_av = {c:{"nomor_temuan":"No. Temuan","nama_unit":"Unit","pic_pelaksana":"PIC",
                      "tgl_target":"Target","status_tl":"Status"}[c]
                   for c in COLS_SHOW if c in df_late.columns}
        st.dataframe(df_late[list(cols_av.keys())].rename(columns=cols_av),
                     use_container_width=True, hide_index=True)

if not df_finding.empty:
    df_ko = df_finding[
        (df_finding["tingkat_signifikansi"].astype(str) == "KRITIS") &
        (df_finding["status_temuan"].astype(str) == "OPEN")
    ]
    if not df_ko.empty:
        has_alert = True
        st.markdown(
            f'<div class="tnt-card tnt-card-red" style="margin-top:8px;">'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'{icon_html("kritis", 18, RED)}'
            f'<strong style="color:{RED};">{len(df_ko)} Temuan KRITIS masih berstatus OPEN — perhatian segera diperlukan</strong>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

if not has_alert:
    st.markdown(
        f'<div class="tnt-card tnt-card-green">'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'{icon_html("success", 18, GREEN)}'
        f'<strong style="color:{GREEN};">Tidak ada peringatan aktif. Semua tindak lanjut on-track.</strong>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.divider()
st.markdown(
    f'<p style="font-size:0.75rem;color:{GRAY_500};text-align:center;">'
    f'T.U.N.T.A.S v1.0 &nbsp;·&nbsp; SPI PT. PG Candi Baru &nbsp;·&nbsp; 2026 &nbsp;·&nbsp; '
    f'Data diperbarui otomatis dari Supabase</p>',
    unsafe_allow_html=True,
)

# Paksa pembersihan memori setelah render selesai
gc.collect()
