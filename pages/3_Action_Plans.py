"""
pages/3_Action_Plans.py — T.U.N.T.A.S Monitoring Tindak Lanjut
===============================================================
Fitur inti SPI: update status, verifikasi lapangan, alert deadline.
"""

import gc
gc.collect()

import streamlit as st
import pandas as pd
from datetime import date
import os

# 1. Load Icon & Config
icon_path = os.path.join("assets", "tuntas_logos.svg")

st.set_page_config(
    page_title="Action Plans — T.U.N.T.A.S",
    page_icon=icon_path,
    layout="wide",
)

from utils.styles import (
    inject_global_css, page_header, section_title, info_card,
    BLUE, GREEN, RED, AMBER, GRAY_200, GRAY_500, TEXT_MAIN,
    STATUS_TL_COLORS, SIGNIF_COLORS, GREEN_LIGHT, RED_LIGHT,
    BLUE_LIGHT,
)
from utils.icons import icon_html
from utils.supabase_client import (
    fetch_action_plans, fetch_audit_findings,
    get_supabase_admin, get_finding_options, clear_all_cache,
)
from utils.export_utils import render_export_action_plans

inject_global_css()

# ── Header ────────────────────────────────────────────────────────────────────
page_header(
    "Action Plans — Monitoring & Verifikasi Tindak Lanjut",
    "T.U.N.T.A.S · Pantau dan perbarui status tindak lanjut rekomendasi audit secara real-time",
    icon_name="action_plans",
    icon_offset=-5
)

# ── Load Data ─────────────────────────────────────────────────────────────────
with st.spinner("Memuat data tindak lanjut..."):
    df_ap      = fetch_action_plans()
    df_finding = fetch_audit_findings()

# ── Sidebar Filter ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:rgba(255,255,255,0.5);padding:0 0.5rem 0.3rem;">Filter Global</div>',
        unsafe_allow_html=True,
    )
    STATUS_OPTS = ["Semua","OPEN","ON_PROGRESS","SELESAI_PARSIAL","CLOSED","MELEWATI_TARGET"]
    filter_status = st.selectbox("Status TL", STATUS_OPTS)

    kabag_list = ["Semua"]
    if not df_ap.empty and "kabag_induk" in df_ap.columns:
        kabag_list += sorted(df_ap["kabag_induk"].astype(str).dropna().unique().tolist())
    filter_kabag = st.selectbox("Kepala Bagian", kabag_list)

    signif_opts = ["Semua","KRITIS","TINGGI","SEDANG","RENDAH"]
    filter_signif = st.selectbox("Signifikansi Temuan", signif_opts)

    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        clear_all_cache()
        st.rerun()

# Terapkan filter ke dataframe utama
df_f = df_ap.copy()
if not df_ap.empty:
    if filter_status != "Semua" and "status_tl" in df_f.columns:
        df_f = df_f[df_f["status_tl"].astype(str) == filter_status]
    if filter_kabag  != "Semua" and "kabag_induk" in df_f.columns:
        df_f = df_f[df_f["kabag_induk"].astype(str) == filter_kabag]
    if filter_signif != "Semua" and "tingkat_signifikansi" in df_f.columns:
        df_f = df_f[df_f["tingkat_signifikansi"].astype(str) == filter_signif]

# ── Banner Alert ──────────────────────────────────────────────────────────────
if not df_ap.empty:
    df_late = df_ap[df_ap["status_tl"].astype(str) == "MELEWATI_TARGET"]
    if not df_late.empty:
        st.markdown(
            f'<div class="tnt-card tnt-card-red">'
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'{icon_html("warning",22,RED)}'
            f'<div>'
            f'<strong style="color:{RED};font-size:0.95rem;">'
            f'{len(df_late)} Tindak Lanjut Melewati Target Deadline</strong><br>'
            f'<span style="font-size:0.8rem;color:#7F1D1D;">'
            f'Segera koordinasikan dengan PIC terkait. Pertimbangkan eskalasi kepada Direktur.</span>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="tnt-card tnt-card-green">'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'{icon_html("success",18,GREEN)}'
            f'<strong style="color:{GREEN};">Tidak ada tindak lanjut yang melewati target. Semua on-track.</strong>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── KPI Scorecard ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total TL",       len(df_ap))
c2.metric("Open",             (df_ap["status_tl"]=="OPEN").sum() if not df_ap.empty else 0)
c3.metric("In Progress",      (df_ap["status_tl"]=="ON_PROGRESS").sum() if not df_ap.empty else 0)
c4.metric("Terlambat",        len(df_late), delta_color="inverse" if len(df_late) > 0 else "off")
c5.metric("Selesai (Closed)", (df_ap["status_tl"]=="CLOSED").sum() if not df_ap.empty else 0)

st.divider()

# ── Tab Utama ─────────────────────────────────────────────────────────────────
tab_list, tab_update, tab_tambah = st.tabs([
    "Daftar Tindak Lanjut",
    "Update Status",
    "Tambah Rencana TL",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — DAFTAR
# ════════════════════════════════════════════════════════════════════════════
with tab_list:
    LIMIT_VIEW = 15
    
    # 1. Definisikan dulu fungsinya di sini agar terbaca (Avoid NameError)
    def _tl_style(row):
        s = str(row.get("Status","")).upper()
        bg = {
            "MELEWATI_TARGET": "#fde8e8", 
            "CLOSED": "#dcfce7", 
            "ON_PROGRESS": "#dbeafe", 
            "SELESAI_PARSIAL": "#fef9c3", 
            "OPEN": "#fff7ed"
        }
        # Cari warna berdasarkan status
        color = next((v for k, v in bg.items() if k in s.replace(" ","_")), "")
        return [f"background-color:{color}; color:#1E293B"] * len(row) if color else [""] * len(row)

    # 2. Sorting & Filtering
    if not df_f.empty and "tgl_target" in df_f.columns:
        df_f = df_f.sort_values("tgl_target", ascending=False)

    total_data = len(df_f)
    df_to_show = df_f.head(LIMIT_VIEW).copy()

    section_title(f"Daftar Tindak Lanjut")
    
    if total_data > LIMIT_VIEW:
        st.caption(f"Menampilkan {LIMIT_VIEW} data terbaru. Gunakan filter sidebar untuk mencari data spesifik.")

    if not df_to_show.empty:
        DCOLS = {
            "nomor_temuan":"No. Temuan",
            "nama_unit":"Unit",
            "tingkat_signifikansi":"Signif.",
            "rencana_aksi":"Rencana Aksi",
            "pic_pelaksana":"PIC",
            "tgl_target":"Target",
            "status_tl":"Status",
            "persentase_kemajuan":"Kemajuan %",
        }
        
        av = {k:v for k,v in DCOLS.items() if k in df_to_show.columns}
        df_render = df_to_show[list(av.keys())].rename(columns=av)

        if "Rencana Aksi" in df_render.columns:
            df_render["Rencana Aksi"] = df_render["Rencana Aksi"].astype(str).apply(
                lambda x: x[:50] + "..." if len(x) > 50 else x
            )

        # 3. Sekarang _tl_style sudah aman dipanggil
        st.dataframe(
            df_render.style.apply(_tl_style, axis=1), 
            use_container_width=True, 
            hide_index=True, 
            height=500 
        )
        
        render_export_action_plans(df_f, key="ap_list_exp")
    else:
        info_card(f"Tidak ada tindak lanjut yang sesuai filter.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — UPDATE STATUS
# ════════════════════════════════════════════════════════════════════════════
with tab_update:
    section_title("Update Status Tindak Lanjut — Verifikasi SPI")

    if df_ap.empty:
        info_card("Belum ada data tindak lanjut.")
    else:
        tl_opts = {f"[{r['nomor_temuan']}] {str(r['rencana_aksi'])[:55]}… — {r['status_tl']}": r["id"] for _, r in df_ap.iterrows()}
        sel_label = st.selectbox("Pilih Tindak Lanjut untuk Diperbarui", list(tl_opts.keys()))

        if sel_label:
            sel_id = tl_opts[sel_label]
            row_cur = df_ap[df_ap["id"] == sel_id].iloc[0]

            st.markdown(f"""
                <div class="tnt-card" style="margin-bottom:1rem; font-size:0.85rem;">
                    <strong>Unit:</strong> {row_cur.get('nama_unit','—')} | <strong>PIC:</strong> {row_cur.get('pic_pelaksana','—')} | <strong>Target:</strong> {row_cur.get('tgl_target','—')}
                    <br><small>{row_cur.get('rencana_aksi','—')}</small>
                </div>
            """, unsafe_allow_html=True)

            with st.form("form_update_tl"):
                u1, u2 = st.columns(2)
                with u1:
                    status_list = ["OPEN","ON_PROGRESS","SELESAI_PARSIAL","CLOSED","MELEWATI_TARGET"]
                    new_status = st.selectbox("Status Baru *", status_list, index=status_list.index(row_cur['status_tl']) if row_cur['status_tl'] in status_list else 0)
                    new_pct = st.slider("Persentase Kemajuan *", 0, 100, 100 if new_status == "CLOSED" else int(row_cur.get('persentase_kemajuan',0)))
                with u2:
                    new_tgl_real = st.date_input("Tanggal Realisasi Aktual", value=None)
                    new_bukti = st.text_input("Referensi Bukti Dokumen")
                
                new_catatan = st.text_area("Catatan Verifikasi SPI *", placeholder="Deskripsikan hasil verifikasi lapangan...")
                u_submit = st.form_submit_button("Simpan Pembaruan", type="primary")

            if u_submit:
                if not new_catatan.strip():
                    st.error("Catatan verifikasi wajib diisi!")
                else:
                    try:
                        upd = {
                            "status_tl": new_status,
                            "persentase_kemajuan": new_pct,
                            "catatan_verifikasi": new_catatan.strip(),
                            "tgl_verifikasi": date.today().isoformat(),
                            "bukti_dokumen": new_bukti.strip() or None,
                            "tgl_realisasi": new_tgl_real.isoformat() if new_tgl_real else None,
                        }
                        get_supabase_admin().table("action_plans").update(upd).eq("id", sel_id).execute()
                        clear_all_cache()
                        st.success("Berhasil diperbarui!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal: {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — TAMBAH TL BARU (TANPA FILTER UNIT)
# ════════════════════════════════════════════════════════════════════════════
with tab_tambah:
    section_title("Tambah Rencana Tindak Lanjut Baru")

    # Pencarian Langsung Berdasarkan Judul/Nomor Temuan
    keyword = st.text_input("Cari Temuan (Ketik Nomor atau Judul)", placeholder="Contoh: 001, Kas, Inventaris...")

    # Logika Filtering Dataframe untuk Selectbox
    df_filtered = df_finding.copy()
    if keyword:
        df_filtered = df_filtered[
            df_filtered['judul_temuan'].str.contains(keyword, case=False, na=False) | 
            df_filtered['nomor_temuan'].str.contains(keyword, case=False, na=False)
        ]

    # Buat dictionary opsi: "[Nomor] Judul" -> ID
    finding_opts = {
        f"[{row['nomor_temuan']}] {row['judul_temuan']}": row['id'] 
        for _, row in df_filtered.iterrows()
    }

    if not finding_opts:
        st.info("Gunakan kolom pencarian di atas untuk menemukan temuan.")
    else:
        with st.form("form_tambah_tl", clear_on_submit=True):
            sel_finding = st.selectbox("Pilih Temuan Terkait *", options=list(finding_opts.keys()))

            t1, t2 = st.columns(2)
            with t1:
                tl_rencana = st.text_area("Rencana Aksi *", height=110)
                tl_pic = st.text_input("PIC Pelaksana *")
            with t2:
                tl_target = st.date_input("Target Selesai *")
                tl_urutan = st.number_input("Urutan TL", min_value=1, value=1)
            
            t_submit = st.form_submit_button("Simpan Rencana Tindak Lanjut", type="primary")

        if t_submit:
            if not tl_rencana or not tl_pic:
                st.error("Rencana Aksi dan PIC wajib diisi!")
            else:
                try:
                    tl_payload = {
                        "finding_id": finding_opts[sel_finding],
                        "urutan_tl": tl_urutan,
                        "rencana_aksi": tl_rencana.strip(),
                        "pic_pelaksana": tl_pic.strip(),
                        "tgl_target": tl_target.isoformat(),
                        "status_tl": "OPEN",
                        "persentase_kemajuan": 0
                    }
                    get_supabase_admin().table("action_plans").insert(tl_payload).execute()
                    clear_all_cache()
                    st.success("Berhasil disimpan!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal: {e}")

st.markdown(
    f'<p style="font-size:0.73rem;color:{GRAY_500};text-align:right;margin-top:1.5rem;">'
    f'T.U.N.T.A.S v1.0 · SPI PT. PG Candi Baru · 2026</p>',
    unsafe_allow_html=True,
)

# Paksa pembersihan memori setelah render selesai
gc.collect()
