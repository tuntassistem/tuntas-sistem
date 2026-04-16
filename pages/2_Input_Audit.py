"""
pages/2_Input_Audit.py — T.U.N.T.A.S Input Temuan Audit
=========================================================
Form pencatatan temuan standar 5C (IIA).
Identitas Korporat ID FOOD — Biru #0054A6 & Hijau #00A651
"""

import gc
gc.collect()

import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
import os

# 1. Load Icon
icon_path = os.path.join("assets", "tuntas_logos.svg")

st.set_page_config(
    page_title="Input Temuan — T.U.N.T.A.S",
    page_icon=icon_path,
    layout="wide",
)

from utils.styles import (
    inject_global_css, page_header, section_title, info_card,
    BLUE, GREEN, RED, AMBER, GRAY_200, GRAY_500, TEXT_MAIN,
    BLUE_LIGHT, GREEN_LIGHT,
)
from utils.icons import icon_html
from utils.supabase_client import (
    fetch_unit_kerja, fetch_audit_findings,
    get_supabase_admin, get_unit_options, clear_all_cache,
)
from utils.export_utils import render_export_audit_findings

inject_global_css()

# ── Header ────────────────────────────────────────────────────────────────────
page_header(
    "Input Temuan Audit",
    "Catat temuan hasil fieldwork menggunakan standar 5C · Institute of Internal Auditors",
    icon_name="input_temuan",
    icon_offset=-5
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:rgba(255,255,255,0.5);padding:0 0.5rem 0.5rem;">Panduan 5C</div>',
        unsafe_allow_html=True,
    )
    panduan = [
        ("1", "Kondisi",    "Fakta objektif yang ditemukan"),
        ("2", "Kriteria",   "Standar / SOP yang seharusnya"),
        ("3", "Sebab",      "Akar penyebab penyimpangan"),
        ("4", "Akibat",     "Dampak aktual / potensial"),
        ("5", "Rekomendasi","Saran perbaikan dari SPI"),
    ]
    for num, title, desc in panduan:
        st.markdown(
            f'<div style="padding:5px 8px;margin-bottom:4px;'
            f'border-left:3px solid rgba(255,255,255,0.3);'
            f'margin-left:8px;">'
            f'<div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.85);">'
            f'{num}. {title}</div>'
            f'<div style="font-size:0.68rem;color:rgba(255,255,255,0.5);">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.divider()
    st.markdown(
        f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);padding:0 0.5rem;">'
        f'Format No. Temuan:<br>'
        f'<strong style="color:rgba(255,255,255,0.7);">T-SPI-TAHUN-NNN</strong><br>'
        f'Contoh: T-SPI-2026-007</div>',
        unsafe_allow_html=True,
    )

# ── Load unit kerja ───────────────────────────────────────────────────────────
df_units = fetch_unit_kerja()
if df_units.empty:
    info_card(
        f'{icon_html("warning",16,RED)} &nbsp;'
        'Tidak dapat memuat data unit kerja. Periksa koneksi di <code>.streamlit/secrets.toml</code>',
        "red",
    )
    st.stop()

unit_options = get_unit_options(df_units)

# ── Tab: Form / Riwayat ───────────────────────────────────────────────────────
tab_form, tab_history = st.tabs([
    "Form Input Temuan Baru",
    "Riwayat & Export",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — FORM INPUT
# ════════════════════════════════════════════════════════════════════════════
with tab_form:
    with st.form("form_temuan", clear_on_submit=True):

        # ── Informasi Umum ────────────────────────────────────────────────
        section_title("Informasi Umum Temuan")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                f'{icon_html("file",13,BLUE)} &nbsp;Nomor Temuan *</label>',
                unsafe_allow_html=True,
            )
            nomor_temuan = st.text_input(
                "nomor_temuan_hidden", label_visibility="collapsed",
                placeholder="T-SPI-2026-001",
            )

            st.markdown(
                f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                f'{icon_html("dashboard",13,BLUE)} &nbsp;Unit Kerja yang Diaudit *</label>',
                unsafe_allow_html=True,
            )
            unit_selected = st.selectbox(
                "unit_hidden", label_visibility="collapsed",
                options=list(unit_options.keys()),
            )

            st.markdown(
                f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                f'{icon_html("calendar",13,BLUE)} &nbsp;Tanggal Temuan *</label>',
                unsafe_allow_html=True,
            )
            tgl_temuan = st.date_input("tgl_hidden", label_visibility="collapsed", value=date.today())

        with col2:
            st.markdown(
                f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                f'{icon_html("file",13,BLUE)} &nbsp;Judul / Ringkasan Temuan *</label>',
                unsafe_allow_html=True,
            )
            judul_temuan = st.text_input(
                "judul_hidden", label_visibility="collapsed",
                placeholder="Catat temuan kamu hari ini, bro",
            )

            st.markdown(
                f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                f'{icon_html("user",13,BLUE)} &nbsp;Auditor PIC</label>',
                unsafe_allow_html=True,
            )
            auditor_pic = st.text_input("auditor_hidden", label_visibility="collapsed", placeholder="Nama Anda")

            c2a, c2b = st.columns(2)
            with c2a:
                st.markdown(
                    f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                    f'{icon_html("shield_alert",13,BLUE)} &nbsp;Signifikansi *</label>',
                    unsafe_allow_html=True,
                )
                tingkat = st.selectbox(
                    "signif_hidden", label_visibility="collapsed",
                    options=["KRITIS","TINGGI","SEDANG","RENDAH"], index=2,
                )
            with c2b:
                st.markdown(
                    f'<label style="font-size:0.8rem;font-weight:600;color:{GRAY_500};">'
                    f'{icon_html("filter",13,BLUE)} &nbsp;Kategori</label>',
                    unsafe_allow_html=True,
                )
                kategori = st.selectbox(
                    "kat_hidden", label_visibility="collapsed",
                    options=["Kelemahan Kontrol","Ketidakpatuhan","Inefisiensi",
                             "Risiko Keuangan","Risiko Operasional","Risiko IT"],
                )

        st.divider()

        # ── Elemen 5C ─────────────────────────────────────────────────────
        section_title("Detail Temuan — Elemen 5C (Standar IIA)")

        # Info hint
        st.markdown(
            f'<div style="background:{BLUE_LIGHT};border-left:4px solid {BLUE};'
            f'padding:0.6rem 1rem;border-radius:0 8px 8px 0;'
            f'font-size:0.82rem;color:#1E3A5F;margin-bottom:0.75rem;">'
            f'{icon_html("info",14,BLUE)} &nbsp;'
            f'Isi minimal <strong>Kondisi</strong>, <strong>Kriteria</strong>, '
            f'dan <strong>Rekomendasi</strong> untuk temuan yang valid secara audit.'
            f'</div>',
            unsafe_allow_html=True,
        )

        kondisi = st.text_area(
            f"1️⃣  Kondisi — Fakta yang Ditemukan *",
            height=100,
            placeholder="Ada temuan apa hari ini, Bro?",
        )
        kriteria = st.text_area(
            "2️⃣  Kriteria — Standar / Kebijakan yang Seharusnya *",
            height=85,
            placeholder="Aturan mainnya harusnya gimana, nih?",
        )
        col_sc, col_ak = st.columns(2)
        with col_sc:
            sebab = st.text_area(
                "3️⃣  Sebab — Akar Penyebab",
                height=85,
                placeholder="Kira-kira kenapa bisa kejadian kayak gitu?",
            )
        with col_ak:
            akibat = st.text_area(
                "4️⃣  Akibat — Dampak Aktual / Potensial",
                height=85,
                placeholder="Kalau dibiarin, bakal ribet nggak ke depannya?",
            )
        rekomendasi = st.text_area(
            "5️⃣  Rekomendasi — Saran Perbaikan SPI *",
            height=100,
            placeholder="Saran kamu buat mereka apa?",
        )

        st.divider()

        # ── Respons Auditee ────────────────────────────────────────────────
        section_title("Respons Auditee (Opsional)")
        ca, cb = st.columns([2, 1])
        with ca:
            tanggapan = st.text_area(
                "Tanggapan Auditee",
                height=75,
                placeholder="Terus, kata mereka gimana? Aman?",
            )
        with cb:
            tgl_tanggapan = st.date_input("Tanggal Tanggapan", value=None)

        st.divider()

        # ── Submit ─────────────────────────────────────────────────────────
        col_b1, col_b2, _ = st.columns([1.2, 1, 3])
        with col_b1:
            submitted = st.form_submit_button(
                f"Simpan Temuan",
                type="primary",
                use_container_width=True,
            )
        with col_b2:
            st.form_submit_button("Reset Form", use_container_width=True)

    # ── Proses Submit ─────────────────────────────────────────────────────
    if submitted:
        errs = []
        if not nomor_temuan.strip(): errs.append("Nomor temuan wajib diisi.")
        if not judul_temuan.strip(): errs.append("Judul temuan wajib diisi.")
        if not kondisi.strip():      errs.append("Kondisi (1C) wajib diisi.")
        if not kriteria.strip():     errs.append("Kriteria (2C) wajib diisi.")
        if not rekomendasi.strip():  errs.append("Rekomendasi (5C) wajib diisi.")

        if errs:
            for e in errs:
                st.markdown(
                    f'<div style="background:{RED};color:white;padding:8px 14px;'
                    f'border-radius:8px;font-size:0.85rem;margin-bottom:4px;">'
                    f'{icon_html("warning",14,"white")} &nbsp;{e}</div>',
                    unsafe_allow_html=True,
                )
        else:
            payload = {
                "unit_kerja_id":        unit_options[unit_selected],
                "nomor_temuan":         nomor_temuan.strip().upper(),
                "judul_temuan":         judul_temuan.strip(),
                "kondisi":              kondisi.strip()     or None,
                "kriteria":             kriteria.strip()    or None,
                "sebab":                sebab.strip()       or None,
                "akibat":               akibat.strip()      or None,
                "rekomendasi":          rekomendasi.strip() or None,
                "tingkat_signifikansi": tingkat,
                "kategori_temuan":      kategori,
                "tgl_temuan":           tgl_temuan.isoformat(),
                "auditor_pic":          auditor_pic.strip() or None,
                "tanggapan_auditee":    tanggapan.strip()   or None,
                "tgl_tanggapan":        tgl_tanggapan.isoformat() if tgl_tanggapan else None,
                "sumber_data":          "Manual",
                "status_temuan":        "OPEN",
            }
            try:
                get_supabase_admin().table("audit_findings").insert(payload).execute()
                clear_all_cache()
                st.markdown(
                    f'<div class="tnt-card tnt-card-green">'
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'{icon_html("success",20,GREEN)}'
                    f'<strong style="color:{GREEN};font-size:0.95rem;">'
                    f'Temuan <code>{nomor_temuan.upper()}</code> berhasil disimpan!</strong>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.balloons()
            except ConnectionError as e:
                st.error(f"Koneksi gagal: {e}")
            except Exception as e:
                if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                    st.markdown(
                        f'<div class="tnt-card tnt-card-red">'
                        f'{icon_html("warning",16,RED)} &nbsp;'
                        f'Nomor <strong>{nomor_temuan.upper()}</strong> sudah ada. Gunakan nomor berbeda.'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(f"Gagal menyimpan: {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — RIWAYAT & EXPORT
# ════════════════════════════════════════════════════════════════════════════
with tab_history:
    col_prev, col_exp = st.columns([2, 1])

    with col_prev:
        section_title("10 Temuan Terbaru")
        try:
            sb = get_supabase_admin()
            resp = sb.table("audit_findings").select(
                "nomor_temuan, judul_temuan, tingkat_signifikansi, "
                "status_temuan, tgl_temuan, auditor_pic, sumber_data"
            ).order("created_at", desc=True).limit(10).execute()

            if resp.data:
                df_prev = pd.DataFrame(resp.data)

                # Badge warna signifikansi
                SIGN_COLOR = {"KRITIS": RED, "TINGGI": AMBER, "SEDANG": BLUE, "RENDAH": GREEN}
                STATUS_COLOR = {"OPEN": RED, "IN_PROGRESS": AMBER, "VERIFIED": BLUE, "CLOSED": GREEN}

                def _color_cells(val, mapping):
                    c = mapping.get(str(val), GRAY_500)
                    return f"background-color:{c}20; color:{c}; font-weight:600; border-radius:4px;"

                df_prev.rename(columns={
                    "nomor_temuan":"No. Temuan","judul_temuan":"Judul",
                    "tingkat_signifikansi":"Signifikansi","status_temuan":"Status",
                    "tgl_temuan":"Tgl Temuan","auditor_pic":"Auditor","sumber_data":"Sumber",
                }, inplace=True)
                df_prev["Judul"] = df_prev["Judul"].str[:65] + "…"

                styled = (
                    df_prev.style
                    .map(lambda v: _color_cells(v, SIGN_COLOR),   subset=["Signifikansi"])
                    .map(lambda v: _color_cells(v, STATUS_COLOR), subset=["Status"])
                )
                st.dataframe(styled, use_container_width=True, hide_index=True)
            else:
                info_card(f'{icon_html("info",14,BLUE)} &nbsp;Belum ada temuan dalam database.')
        except Exception as e:
            st.warning(f"Tidak dapat memuat riwayat: {e}")

    with col_exp:
        section_title("Export Data Temuan")
        st.markdown(
            f'<div class="tnt-card" style="font-size:0.82rem;line-height:1.6;">'
            f'{icon_html("download",14,BLUE)} &nbsp;Unduh seluruh data <strong>audit_findings</strong> '
            f'dalam format CSV.<br><br>'
            f'<span style="color:{GRAY_500};">Mode <em>Lengkap</em> menyertakan '
            f'kolom 5C (Kondisi, Kriteria, Sebab, Akibat, Rekomendasi).</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        try:
            df_af = fetch_audit_findings()
            render_export_audit_findings(df_af, sb=get_supabase_admin(), key="input_exp_af")
        except ConnectionError as e:
            st.warning(f"Koneksi admin gagal: {e}")

st.markdown(
    f'<p style="font-size:0.73rem;color:{GRAY_500};text-align:right;margin-top:1.5rem;">'
    f'T.U.N.T.A.S v1.0 · SPI PT. PG Candi Baru · 2026</p>',
    unsafe_allow_html=True,
)

# Paksa pembersihan memori setelah render selesai
gc.collect()
#feat: T.U.N.T.A.S v1.0 — SPI PT. PG Candi Baru
