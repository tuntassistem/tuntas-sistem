"""
pages/1_Dashboard.py — T.U.N.T.A.S Dashboard Monitoring (Memory Optimized)
===========================================================================
Dashboard ramping untuk performa maksimal.
"""

import gc
gc.collect()

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

# 1. Load Icon & Config
icon_path = os.path.join("assets", "tuntas_logos.svg")

st.set_page_config(
    page_title="Dashboard — T.U.N.T.A.S",
    page_icon=icon_path,
    layout="wide",
)

from utils.styles import (
    inject_global_css, page_header, section_title, info_card,
    BLUE, GREEN, RED, GRAY_500, STATUS_TEMUAN_COLORS, SIGNIF_COLORS
)
from utils.icons import icon_html
from utils.supabase_client import fetch_audit_findings, fetch_action_plans, clear_all_cache

inject_global_css()

# ── Header ────────────────────────────────────────────────────────────────────
page_header(
    "Dashboard Monitoring Audit",
    "T.U.N.T.A.S · Visualisasi Ringkas & Cepat",
    icon_name="dashboard",
    icon_offset=-5
)

# ── Load Data ─────────────────────────────────────────────────────────────────
with st.spinner("Memuat data..."):
    df_finding = fetch_audit_findings()
    df_ap      = fetch_action_plans()

if df_finding.empty and df_ap.empty:
    info_card(f'{icon_html("info",16,BLUE)} &nbsp;Database kosong.')
    st.stop()

# ── Sidebar Filter ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;color:rgba(255,255,255,0.5);">Filter</div>', unsafe_allow_html=True)
    
    kabag_list = ["Semua"]
    if "kabag_induk" in df_finding.columns:
        kabag_list += sorted(df_finding["kabag_induk"].astype(str).dropna().unique().tolist())
    filter_kabag = st.selectbox("Kepala Bagian", kabag_list)

    filter_signif = st.multiselect(
        "Signifikansi",
        ["KRITIS","TINGGI","SEDANG","RENDAH"],
        default=["KRITIS","TINGGI","SEDANG","RENDAH"],
    )
    st.divider()
    if st.button("Refresh Data", use_container_width=True):
        clear_all_cache()
        st.rerun()

# ── Optimasi Data (Reference Only) ───────────────────────────────────────────
# Menggunakan filter langsung pada dataframe tanpa .copy() eksplisit kecuali diperlukan
df_f = df_finding
if filter_kabag != "Semua":
    df_f = df_f[df_f["kabag_induk"].astype(str) == filter_kabag]
if filter_signif:
    df_f = df_f[df_f["tingkat_signifikansi"].astype(str).isin(filter_signif)]

# ── KPI Scorecard (Tetap Ringan) ──────────────────────────────────────────────
section_title("Indikator Kinerja Pengawasan")
c1, c2, c3, c4, c5 = st.columns(5)

# Hitung metrik secara efisien
t_open   = (df_f["status_temuan"] == "OPEN").sum() if not df_f.empty else 0
t_kritis = (df_f["tingkat_signifikansi"] == "KRITIS").sum() if not df_f.empty else 0
tl_late  = (df_ap["status_tl"] == "MELEWATI_TARGET").sum() if not df_ap.empty else 0
avg_prog = df_ap["persentase_kemajuan"].mean() if not df_ap.empty else 0.0

c1.metric("Total Temuan",          len(df_f))
c2.metric("Temuan Open",           int(t_open),   delta_color="inverse" if t_open > 0 else "normal")
c3.metric("Temuan Kritis",         int(t_kritis), delta_color="inverse" if t_kritis > 0 else "off")
c4.metric("TL Melewati Target",    int(tl_late),  delta_color="inverse" if tl_late > 0 else "normal")
c5.metric("Rata-rata Kemajuan",    f"{avg_prog:.1f}%")

st.divider()

# ── Visualisasi Utama (Baris 1) ────────────────────────────────────────────────
col_chart, col_aging = st.columns([1, 1])

with col_chart:
    section_title("Distribusi Status Temuan")
    if not df_f.empty:
        # Agregasi ringan untuk bar chart
        sc = df_f["status_temuan"].value_counts().reset_index()
        sc.columns = ["Status", "Jumlah"]
        
        fig = px.bar(
            sc, x="Status", y="Jumlah",
            color="Status", color_discrete_map=STATUS_TEMUAN_COLORS,
            text="Jumlah"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=320, showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans"),
            xaxis_title="", yaxis_title="Jumlah"
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        info_card("Tidak ada data.")

with col_aging:
    section_title("Top 10 Aging (Temuan Terlama)")
    # Filter Aging secara efisien langsung dari dataframe induk
    if not df_f.empty:
        df_ag = df_f[df_f["status_temuan"] != "CLOSED"]
        if not df_ag.empty:
            # Kalkulasi hari tanpa .copy()
            days_open = (pd.Timestamp.today() - pd.to_datetime(df_ag["tgl_temuan"], errors="coerce")).dt.days
            df_ag_view = df_ag.assign(hari=days_open).nlargest(10, "hari")
            
            # Tampilkan kolom esensial saja
            show_cols = {"nomor_temuan": "No.", "nama_unit": "Unit", "hari": "Hari"}
            st.dataframe(
                df_ag_view[list(show_cols.keys())].rename(columns=show_cols),
                use_container_width=True, hide_index=True, height=275
            )
        else:
            info_card(f'{icon_html("success",16,GREEN)} &nbsp;Semua temuan sudah closed.')

# ── Footer & RAM Cleanup ──────────────────────────────────────────────────────
st.markdown(
    f'<p style="font-size:0.73rem;color:{GRAY_500};text-align:right;margin-top:3rem;">'
    f'T.U.N.T.A.S v1.0 · Mode Performa Tinggi · {datetime.datetime.now().year}</p>',
    unsafe_allow_html=True,
)

# Paksa pembersihan memori setelah render selesai
gc.collect()
