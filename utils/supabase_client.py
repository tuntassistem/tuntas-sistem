"""
utils/supabase_client.py — Data Access Layer (DAL) T.U.N.T.A.S
=============================================================
Optimized for RAM efficiency and stable performance.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import gc
from supabase import create_client, Client
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1. KONEKSI — Singleton via cache_resource
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def _get_client() -> Optional[Client]:
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except Exception as e:
        st.error(f"⚠️ Koneksi Supabase gagal: {e}")
        return None

@st.cache_resource(show_spinner=False)
def _get_admin_client() -> Optional[Client]:
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_role_key"])
    except Exception as e:
        st.error(f"⚠️ Koneksi Supabase admin gagal: {e}")
        return None

def get_supabase() -> Optional[Client]:
    return _get_client()

def get_supabase_admin() -> Client:
    client = _get_admin_client()
    if client is None:
        raise ConnectionError("Koneksi admin tidak tersedia. Periksa secrets.")
    return client


# ══════════════════════════════════════════════════════════════════════════════
# 2. HELPER INTERNAL (Memory & Data Processing)
# ══════════════════════════════════════════════════════════════════════════════

_CATEGORICAL = {
    "unit_kerja":     ["kabag_induk", "kategori_unit"],
    "audit_findings": ["tingkat_signifikansi", "kategori_temuan", "status_temuan", "sumber_data"],
    "action_plans":   ["status_tl"],
}

def _apply_dtypes(df: pd.DataFrame, table: str) -> pd.DataFrame:
    if df.empty: return df
    for col in _CATEGORICAL.get(table, []):
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df

def _safe_fetch(sb: Optional[Client], table: str, columns: str, extra_query=None) -> pd.DataFrame:
    if sb is None: return pd.DataFrame()
    try:
        q = sb.table(table).select(columns)
        if extra_query: q = extra_query(q)
        resp = q.execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ Gagal memuat '{table}': {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
# 3. FETCH FUNCTIONS (Optimized Cache)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, max_entries=1, show_spinner=False)
def fetch_unit_kerja() -> pd.DataFrame:
    COLS = "id, kode_unit, nama_unit, kabag_induk, kategori_unit"
    df = _safe_fetch(get_supabase(), "unit_kerja", COLS, 
                     extra_query=lambda q: q.eq("aktif", True).order("kode_unit"))
    return _apply_dtypes(df, "unit_kerja")

@st.cache_data(ttl=60, max_entries=1, show_spinner=False)
def fetch_audit_findings() -> pd.DataFrame:
    COLS = ("id, nomor_temuan, judul_temuan, tingkat_signifikansi, "
            "kategori_temuan, status_temuan, tgl_temuan, auditor_pic, "
            "sumber_data, unit_kerja(nama_unit, kabag_induk)")
    
    df = _safe_fetch(get_supabase(), "audit_findings", COLS, 
                     extra_query=lambda q: q.order("tgl_temuan", desc=True))
    
    if not df.empty and "unit_kerja" in df.columns:
        # Flattening lebih aman terhadap data null
        df["nama_unit"] = df["unit_kerja"].apply(lambda x: x.get("nama_unit") if isinstance(x, dict) else None)
        df["kabag_induk"] = df["unit_kerja"].apply(lambda x: x.get("kabag_induk") if isinstance(x, dict) else None)
        df.drop(columns=["unit_kerja"], inplace=True)
    
    if "tgl_temuan" in df.columns:
        df["tgl_temuan"] = pd.to_datetime(df["tgl_temuan"], errors="coerce")
        
    return _apply_dtypes(df, "audit_findings")

@st.cache_data(ttl=30, max_entries=1, show_spinner=False)
def fetch_action_plans() -> pd.DataFrame:
    COLS = ("id, finding_id, urutan_tl, rencana_aksi, pic_pelaksana, tgl_target, "
            "status_tl, persentase_kemajuan, audit_findings(nomor_temuan, judul_temuan, "
            "unit_kerja(nama_unit, kabag_induk))")
    
    df = _safe_fetch(get_supabase(), "action_plans", COLS, 
                     extra_query=lambda q: q.order("tgl_target"))
    
    if not df.empty and "audit_findings" in df.columns:
        # Deep Flattening (Action Plan -> Finding -> Unit)
        def get_nested(x, *keys):
            for key in keys:
                x = x.get(key, {}) if isinstance(x, dict) else {}
            return x if x else None

        df["nomor_temuan"] = df["audit_findings"].apply(lambda x: get_nested(x, "nomor_temuan"))
        df["nama_unit"] = df["audit_findings"].apply(lambda x: get_nested(x, "unit_kerja", "nama_unit"))
        df["kabag_induk"] = df["audit_findings"].apply(lambda x: get_nested(x, "unit_kerja", "kabag_induk"))
        df.drop(columns=["audit_findings"], inplace=True)

    if "persentase_kemajuan" in df.columns:
        df["persentase_kemajuan"] = pd.to_numeric(df["persentase_kemajuan"], errors="coerce").fillna(0).astype("int8")

    return _apply_dtypes(df, "action_plans")

@st.cache_data(ttl=60, max_entries=1, show_spinner=False)
def fetch_finding_detail(finding_id: str) -> dict:
    sb = get_supabase()
    if not sb: return {}
    try:
        resp = sb.table("audit_findings").select("id, nomor_temuan, judul_temuan, kondisi, kriteria, sebab, akibat, rekomendasi, status_temuan").eq("id", finding_id).single().execute()
        return resp.data or {}
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════════════════════
# 4. UTILS & MEMORY MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def clear_all_cache() -> None:
    """Hapus cache dan paksa Python membersihkan RAM (Garbage Collection)."""
    st.cache_data.clear()
    gc.collect() # <--- Kunci agar RAM tidak bengkak setelah update data

def get_unit_options(df_units: pd.DataFrame) -> dict[str, str]:
    if df_units.empty: return {}
    return {f"[{row['kode_unit']}] {row['nama_unit']}": row["id"] for _, row in df_units.iterrows()}

def get_finding_options(df_findings: pd.DataFrame) -> dict[str, str]:
    if df_findings.empty: return {}
    return {f"[{row['nomor_temuan']}] {str(row.get('judul_temuan', ''))[:50]}...": row["id"] for _, row in df_findings.iterrows()}
