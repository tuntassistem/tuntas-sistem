"""
utils/export_utils.py — Utilitas Export Data T.U.N.T.A.S
=======================================================
Semua logika format & unduh CSV ada di sini.
Pages/*.py cukup memanggil satu fungsi render_export_*().

Prinsip:
  - build_csv_bytes() : helper generik → bytes UTF-8-sig (BOM) agar Excel
                        membuka tanpa masalah karakter Indonesia
  - render_export_*() : fungsi siap pakai untuk dipanggil di page
  - Data 5C (teks panjang) hanya diambil saat user klik tombol,
    bukan saat halaman dimuat (lazy fetch on demand)
"""

from __future__ import annotations

import io
import datetime
import streamlit as st
import pandas as pd
from supabase import Client
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# KONFIGURASI KOLOM EKSPOR
# Mendefinisikan kolom mana yang diekspor dan label yang tampil di CSV header.
# UUID internal (id, unit_kerja_id, finding_id) sengaja dikecualikan.
# ══════════════════════════════════════════════════════════════════════════════

_COLS_AUDIT_FINDINGS: dict[str, str] = {
    "nomor_temuan":         "Nomor Temuan",
    "nama_unit":            "Unit Kerja",
    "kabag_induk":          "Kepala Bagian",
    "judul_temuan":         "Judul Temuan",
    "tingkat_signifikansi": "Tingkat Signifikansi",
    "kategori_temuan":      "Kategori Temuan",
    "status_temuan":        "Status Temuan",
    "tgl_temuan":           "Tanggal Temuan",
    "auditor_pic":          "Auditor PIC",
    "sumber_data":          "Sumber Data",
    # Kolom 5C — hanya ada di ekspor lengkap
    "kondisi":              "Kondisi (Fakta)",
    "kriteria":             "Kriteria (Standar)",
    "sebab":                "Sebab (Akar Masalah)",
    "akibat":               "Akibat / Dampak",
    "rekomendasi":          "Rekomendasi SPI",
    "tanggapan_auditee":    "Tanggapan Auditee",
    "tgl_tanggapan":        "Tanggal Tanggapan",
}

_COLS_ACTION_PLANS: dict[str, str] = {
    "nomor_temuan":         "No. Temuan",
    "nama_unit":            "Unit Kerja",
    "kabag_induk":          "Kepala Bagian",
    "tingkat_signifikansi": "Signifikansi Temuan",
    "rencana_aksi":         "Rencana Aksi",
    "pic_pelaksana":        "PIC Pelaksana",
    "jabatan_pic":          "Jabatan PIC",
    "tgl_target":           "Target Selesai",
    "tgl_realisasi":        "Realisasi Aktual",
    "status_tl":            "Status Tindak Lanjut",
    "persentase_kemajuan":  "Kemajuan (%)",
    "bukti_dokumen":        "Referensi Bukti Dokumen",
    "catatan_verifikasi":   "Catatan Verifikasi SPI",
    "verifikator":          "Verifikator (SPI)",
    "tgl_verifikasi":       "Tanggal Verifikasi",
}


# ══════════════════════════════════════════════════════════════════════════════
# CORE HELPER
# ══════════════════════════════════════════════════════════════════════════════

def build_csv_bytes(df: pd.DataFrame, col_map: dict[str, str]) -> bytes:
    """
    Konversi DataFrame ke bytes CSV siap pakai di st.download_button.

    Encoding UTF-8-sig (BOM) dipilih agar Excel Windows membuka file
    tanpa karakter Indonesia (seperti é, ã) berubah menjadi kotak.

    Args:
        df      : DataFrame sumber (boleh hasil cache)
        col_map : dict kolom_df → label_header_csv

    Returns:
        bytes — langsung diteruskan ke parameter `data` di st.download_button
    """
    if df.empty:
        return "".encode("utf-8-sig")

    # Pilih kolom yang ada di KEDUANYA: df dan col_map (urutan sesuai col_map)
    avail   = [k for k in col_map if k in df.columns]
    df_out  = df[avail].copy()
    df_out.rename(columns={k: col_map[k] for k in avail}, inplace=True)

    # Categorical → string biasa agar CSV tidak menyimpan kode internal
    for col in df_out.columns:
        if pd.api.types.is_categorical_dtype(df_out[col]):
            df_out[col] = df_out[col].astype(str)

    # Tanggal → string ISO (YYYY-MM-DD), menghindari ambiguitas timezone
    for col in df_out.columns:
        if pd.api.types.is_datetime64_any_dtype(df_out[col]):
            df_out[col] = df_out[col].dt.strftime("%Y-%m-%d")

    buf = io.StringIO()
    df_out.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue().encode("utf-8-sig")


def _today() -> str:
    return datetime.date.today().strftime("%Y%m%d")


# ══════════════════════════════════════════════════════════════════════════════
# FETCH LENGKAP (termasuk kolom 5C) — hanya dipanggil on-demand
# ══════════════════════════════════════════════════════════════════════════════

def _fetch_full_findings(sb: Client) -> pd.DataFrame:
    """
    Ambil SEMUA kolom audit_findings termasuk teks 5C.
    Tidak di-cache — dipanggil hanya saat user klik tombol ekspor lengkap.
    """
    try:
        resp = sb.table("audit_findings").select(
            "nomor_temuan, judul_temuan, tingkat_signifikansi, "
            "kategori_temuan, status_temuan, tgl_temuan, auditor_pic, "
            "sumber_data, kondisi, kriteria, sebab, akibat, rekomendasi, "
            "tanggapan_auditee, tgl_tanggapan, "
            "unit_kerja(nama_unit, kabag_induk)"
        ).order("tgl_temuan", desc=True).execute()

        if not resp.data:
            return pd.DataFrame()

        df = pd.DataFrame(resp.data)
        if "unit_kerja" in df.columns:
            df["nama_unit"]   = df["unit_kerja"].apply(
                lambda x: x.get("nama_unit")   if isinstance(x, dict) else "")
            df["kabag_induk"] = df["unit_kerja"].apply(
                lambda x: x.get("kabag_induk") if isinstance(x, dict) else "")
            df.drop(columns=["unit_kerja"], inplace=True)
        return df

    except Exception as e:
        st.error(f"❌ Gagal mengambil data untuk ekspor: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
# RENDER FUNCTIONS — dipanggil satu baris dari pages/*.py
# ══════════════════════════════════════════════════════════════════════════════

def render_export_audit_findings(
    df: pd.DataFrame,
    sb: Optional[Client] = None,
    key: str = "exp_af",
) -> None:
    """
    Tampilkan kontrol ekspor CSV untuk tabel audit_findings.

    Mode "Tampilan saat ini" → ekspor dari df cache (cepat, tanpa kolom 5C).
    Mode "Lengkap (+ 5C)"    → query ulang ke DB saat tombol diklik (lazy).

    Args:
        df  : DataFrame dari fetch_audit_findings() (sudah ada di cache)
        sb  : admin client, wajib untuk mode ekspor lengkap
        key : prefix key unik untuk menghindari DuplicateWidgetID
    """
    mode = st.radio(
        "Mode ekspor temuan",
        ["Tampilan saat ini", "Lengkap (termasuk kolom 5C)"],
        horizontal=True,
        key=f"{key}_mode",
        help=(
            "**Tampilan saat ini** — kolom tabel yang terlihat, langsung unduh.\n\n"
            "**Lengkap** — mengambil ulang dari DB termasuk Kondisi, Kriteria, "
            "Sebab, Akibat, Rekomendasi. Klik 'Siapkan data' dulu."
        ),
    )

    if mode == "Tampilan saat ini":
        if df.empty:
            st.info("Tidak ada data untuk diekspor.")
            return
        st.download_button(
            label=f"⬇️ Unduh CSV ({len(df)} temuan)",
            data=build_csv_bytes(df, _COLS_AUDIT_FINDINGS),
            file_name=f"audit_findings_{_today()}.csv",
            mime="text/csv",
            key=f"{key}_dl",
        )

    else:  # Lengkap
        if sb is None:
            st.warning("⚠️ Koneksi admin diperlukan untuk ekspor lengkap.")
            return
        if st.button("🔄 Siapkan data lengkap (termasuk 5C)", key=f"{key}_prep"):
            with st.spinner("Mengambil semua kolom dari database..."):
                df_full = _fetch_full_findings(sb)
            if df_full.empty:
                st.error("Tidak ada data.")
                return
            # Simpan ke session_state agar tidak query ulang saat klik unduh
            st.session_state[f"{key}_full"] = df_full

        if f"{key}_full" in st.session_state:
            df_full = st.session_state[f"{key}_full"]
            st.download_button(
                label=f"⬇️ Unduh CSV Lengkap ({len(df_full)} temuan, termasuk 5C)",
                data=build_csv_bytes(df_full, _COLS_AUDIT_FINDINGS),
                file_name=f"audit_findings_lengkap_{_today()}.csv",
                mime="text/csv",
                key=f"{key}_full_dl",
            )

    st.caption(
        "📌 Encoding: **UTF-8 with BOM** — karakter Indonesia tampil benar di Excel."
    )


def render_export_action_plans(df: pd.DataFrame, key: str = "exp_ap") -> None:
    """
    Tombol unduh CSV untuk action_plans.
    Langsung dari cache — tidak perlu query ulang.
    """
    if df.empty:
        st.info("Tidak ada data tindak lanjut untuk diekspor.")
        return
    st.download_button(
        label=f"⬇️ Unduh Monitoring Tindak Lanjut CSV ({len(df)} item)",
        data=build_csv_bytes(df, _COLS_ACTION_PLANS),
        file_name=f"action_plans_spi_{_today()}.csv",
        mime="text/csv",
        key=key,
    )
