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
import os

# 1. Load Icon
icon_path = os.path.join("assets", "tuntas_logos.svg")

# 2. Set Page Config (Wajib di urutan pertama)
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
from utils.styles import inject_global_css, section_title, BLUE, GREEN, RED, AMBER, GRAY_500
from utils.icons import icon_html
from utils.supabase_client import fetch_audit_findings, fetch_action_plans

inject_global_css()

# ── CSS SAKTI (FIXED: Tanpa awalan 'f' agar tidak SyntaxError di kurung kurawal) ──
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] {
        display: flex;
        align-items: stretch;
    }
    [data-testid="stVerticalBlock"] {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .spacer-card {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .scope-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:1.4rem 0.8rem 1rem 0.8rem; text-align:center;">
            <div style="font-size:2rem; font-weight:900; color:white; line-height:1;">T.U.N.T.A.S</div>
            <div style="font-size:0.6rem; color:rgba(255,255,255,0.65);
                        font-weight:500; text-transform:uppercase; margin-top:4px; line-height:1.4;">
                Trackable Unit for<br>Networked &amp; Transparent<br>Audit System
            </div>
            <div style="margin-top:10px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.15);
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

# ── Header Utama ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#003D7A 0%,#0054A6 55%,#1A7FD4 100%);
                padding:2rem 2.2rem; border-radius:16px; margin-bottom:1.8rem;
                position:relative; overflow:hidden;">
        <div style="position:relative;">
            <div style="font-size:2.2rem;font-weight:900;color:white;line-height:1;">T.U.N.T.A.S</div>
            <div style="font-size:0.82rem;color:rgba(255,255,255,0.65);margin-top:4px;">
                Trackable Unit for Networked &amp; Transparent Audit System
            </div>
            <div style="margin-top:12px;font-size:0.9rem;color:rgba(255,255,255,0.85);font-weight:500;">
                Satuan Pengawas Internal (SPI) &nbsp;·&nbsp; PT. PG Candi Baru
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Load Data ─────────────────────────────────────────────────────────────────
with st.spinner("Memuat data..."):
    df_finding = fetch_audit_findings()
    df_ap      = fetch_action_plans()

# ── KPI Scorecard ─────────────────────────────────────────────────────────────
section_title("Ringkasan Status Pengawasan")
c1, c2, c3, c4, c5 = st.columns(5)

if not df_finding.empty and not df_ap.empty:
    total_temuan  = len(df_finding)
    temuan_open   = int((df_finding["status_temuan"].astype(str) == "OPEN").sum())
    temuan_kritis = int((df_finding["tingkat_signifikansi"].astype(str) == "KRITIS").sum())
    tl_terlambat  = int((df_ap["status_tl"].astype(str) == "MELEWATI_TARGET").sum())
    tl_selesai    = int((df_ap["status_tl"].astype(str) == "CLOSED").sum())

    c1.metric("Total Temuan", total_temuan)
    c2.metric("Temuan Open", temuan_open, delta=f"{temuan_open} sisa", delta_color="inverse")
    c3.metric("Temuan Kritis", temuan_kritis, delta=f"+{temuan_kritis} eskalasi", delta_color="inverse")
    c4.metric("TL Terlambat", tl_terlambat, delta_color="inverse")
    c5.metric("TL Selesai", tl_selesai)

st.divider()

# ── Konten 2 Kolom ────────────────────────────────────────────────────────────
col_l, col_r = st.columns([1.3, 1])

with col_l:
    section_title("Tentang Sistem")
    st.markdown(
        f"""
        <div class="tnt-card" style="border-left:4px solid {BLUE}; background:#EEF4FF;">
            <div style="font-size:0.92rem; line-height:1.7; color:#1E293B;">
                <strong>T.U.N.T.A.S</strong> adalah sistem manajemen audit internal untuk SPI PT. PG Candi Baru yang memungkinkan:
                <ul style="margin-top:5px; margin-bottom:0;">
                    <li>Pencatatan temuan audit standar <strong>5C (IIA)</strong></li>
                    <li>Monitoring tindak lanjut rekomendasi secara <strong>real-time</strong></li>
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
        <div class="tnt-card spacer-card">
            <div class="scope-grid">
                <div style="padding:10px; background:{BLUE}; color:white; border-radius:6px;">{icon_html("file", 13, "white")} &nbsp;Keuangan / IT / MR</div>
                <div style="padding:10px; background:{BLUE}; color:white; border-radius:6px;">{icon_html("user", 13, "white")} &nbsp;SDM & Umum</div>
                <div style="padding:10px; background:{BLUE}; color:white; border-radius:6px;">{icon_html("trending", 13, "white")} &nbsp;Tanaman</div>
                <div style="padding:10px; background:{BLUE}; color:white; border-radius:6px;">{icon_html("chart", 13, "white")} &nbsp;Instalasi</div>
                <div style="padding:10px; background:{BLUE}; color:white; border-radius:6px;">{icon_html("shield", 13, "white")} &nbsp;Pabrikasi</div>
                <div style="padding:10px; background:{BLUE}; color:white; border-radius:6px;">{icon_html("eye", 13, "white")} &nbsp;Quality Assurance</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_r:
    section_title("Panduan Penggunaan")
    for ico, name, desc, color in [("dashboard", "Dashboard", "Visualisasi KPI", BLUE), 
                                   ("input_temuan", "Input Temuan", "Standar 5C IIA", BLUE),
                                   ("action_plans", "Action Plans", "Update tindak lanjut", GREEN)]:
        st.markdown(
            f"""
            <div class="tnt-card" style="margin-bottom:8px; padding:0.6rem 1rem;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="background:{color}; border-radius:8px; padding:6px;">{icon_html(ico, 16, "white")}</div>
                    <div>
                        <div style="font-weight:700; font-size:0.85rem;">{name}</div>
                        <div style="font-size:0.75rem; color:{GRAY_500};">{desc}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("Skala Signifikansi Temuan")
    badges_html = "".join([f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <span style="background:{c}; color:white; padding:2px 10px; border-radius:20px; 
            font-size:0.72rem; font-weight:700; min-width:65px; text-align:center;">{l}</span>
            <span style="font-size:0.8rem; color:{GRAY_500};">{d}</span>
        </div>""" for l, c, d in [("KRITIS", RED, "Eskalasi segera ke Direktur"), 
                                 ("TINGGI", AMBER, "Tindakan dekat"), 
                                 ("SEDANG", BLUE, "Pantau perbaikan"), 
                                 ("RENDAH", GREEN, "Monitor berkala")]])

    st.markdown(
        f"""
        <div class="tnt-card spacer-card">
            {badges_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Alert Aktif (FIXED: Ganti use_container_width dengan width="stretch") ─────
st.divider()
section_title("Peringatan Aktif")

if not df_ap.empty:
    df_late = df_ap[df_ap["status_tl"].astype(str) == "MELEWATI_TARGET"]
    if not df_late.empty:
        st.error(f"⚠️ {len(df_late)} Tindak Lanjut Melewati Target Deadline")
        st.dataframe(df_late[["nomor_temuan","nama_unit","tgl_target"]], width="stretch", hide_index=True)
    else:
        st.success("✅ Tidak ada peringatan aktif. Semua tindak lanjut on-track.")

st.markdown(
    f'<p style="font-size:0.75rem;color:{GRAY_500};text-align:center;margin-top:2rem;">'
    f'T.U.N.T.A.S v1.0 &nbsp;·&nbsp; SPI PT. PG Candi Baru &nbsp;·&nbsp; 2026</p>',
    unsafe_allow_html=True,
)

gc.collect()
