"""
utils/icons.py — Lucide Icon Renderer untuk T.U.N.T.A.S
========================================================
Menggunakan library `lucide` (Python) yang membaca SVG langsung
dari bundel zip-nya, lalu merender ikon sebagai inline HTML
via st.markdown() — tanpa ketergantungan pada package eksternal
yang belum tersedia di PyPI (streamlit-lucide tidak ada di pip).

Cara pakai:
    from utils.icons import icon, icon_html, ICONS

    # Render ikon langsung ke halaman
    icon("house", size=24, color="#0054A6")

    # Dapatkan HTML string (untuk dipakai di dalam st.markdown blok)
    html = icon_html("circle-check", size=20, color="#00A651")
    st.markdown(f'<p>{html} Data tersimpan</p>', unsafe_allow_html=True)

    # Judul dengan ikon di kiri
    icon_header("layout-dashboard", "Dashboard Monitoring", level=2)
"""

from __future__ import annotations
import zipfile
import os
import streamlit as st

# ── Lokasi zip Lucide ─────────────────────────────────────────────────────────
import lucide as _lucide_pkg
_ZIP_PATH = os.path.join(os.path.dirname(_lucide_pkg.__file__), "lucide.zip")

# ── Cache SVG di memori (baca zip hanya sekali per proses) ───────────────────
_SVG_CACHE: dict[str, str] = {}


def _load_svg_inner(name: str) -> str:
    """
    Baca file `{name}.svg` dari lucide.zip dan kembalikan isi dalamnya
    (tanpa tag <svg>...</svg> luar) agar bisa diinjeksi ke SVG custom.
    Raise KeyError jika nama ikon tidak ditemukan.
    """
    if name in _SVG_CACHE:
        return _SVG_CACHE[name]

    with zipfile.ZipFile(_ZIP_PATH) as z:
        fname = f"{name}.svg"
        if fname not in z.namelist():
            raise KeyError(
                f"Ikon '{name}' tidak ditemukan di Lucide. "
                f"Coba nama kebab-case, contoh: 'layout-dashboard'."
            )
        raw = z.read(fname).decode("utf-8")

    # Ambil konten dalam tag <svg> … </svg>
    inner = raw.split(">", 1)[1].rsplit("</svg>", 1)[0].strip()
    _SVG_CACHE[name] = inner
    return inner


# ── Warna standar T.U.N.T.A.S ────────────────────────────────────────────────
BLUE  = "#0054A6"   # ID FOOD primary
GREEN = "#00A651"   # ID FOOD success/green
RED   = "#DC2626"   # Danger / kritis
AMBER = "#D97706"   # Warning
GRAY  = "#64748B"   # Muted / netral


# ── Pemetaan ikon semantik T.U.N.T.A.S ──────────────────────────────────────
ICONS: dict[str, str] = {
    # Navigasi
    "home":           "house",
    "dashboard":      "layout-dashboard",
    "input_temuan":   "clipboard-plus",
    "action_plans":   "list-checks",
    # Status
    "kritis":         "triangle-alert",
    "tinggi":         "circle-alert",
    "closed":         "circle-check",
    "warning":        "triangle-alert",
    "success":        "circle-check",
    "info":           "circle-alert",
    # Aksi
    "save":           "save",
    "download":       "download",
    "refresh":        "refresh-cw",
    "search":         "search",
    "filter":         "filter",
    "plus":           "plus",
    "eye":            "eye",
    # Data / chart
    "chart":          "chart-bar-big",
    "trending":       "trending-up",
    "file":           "file-text",
    "calendar":       "calendar",
    "clock":          "clock",
    "user":           "user",
    # Sistem
    "check":          "check",
    "close":          "x",
    "shield":         "shield-check",
    "shield_alert":   "shield-alert",
}


def icon_html(
    name: str,
    size: int = 18,
    color: str = BLUE,
    stroke_width: float = 1.75,
    extra_style: str = "",
) -> str:
    """
    Kembalikan string HTML <svg> untuk ikon Lucide.

    Args:
        name         : nama ikon (key dari ICONS atau nama Lucide langsung)
        size         : ukuran px (lebar = tinggi)
        color        : warna stroke (#hex)
        stroke_width : ketebalan garis (default Lucide: 2)
        extra_style  : CSS tambahan untuk tag <svg>

    Returns:
        str — HTML <svg> siap dipakai di st.markdown(..., unsafe_allow_html=True)
    """
    lucide_name = ICONS.get(name, name)
    try:
        inner = _load_svg_inner(lucide_name)
    except KeyError:
        # Fallback: bullet hitam jika ikon tidak ditemukan
        return f'<span style="color:{color}; font-size:{size}px;">•</span>'

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" '
        f'stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle; flex-shrink:0; {extra_style}">'
        f"{inner}</svg>"
    )


def icon(
    name: str,
    size: int = 20,
    color: str = BLUE,
    stroke_width: float = 1.75,
) -> None:
    """
    Render ikon Lucide langsung ke halaman Streamlit.
    Setara dengan st.markdown(icon_html(...), unsafe_allow_html=True).
    """
    st.markdown(
        icon_html(name, size=size, color=color, stroke_width=stroke_width),
        unsafe_allow_html=True,
    )


def icon_text(
    icon_name: str,
    text: str,
    size: int = 18,
    color: str = BLUE,
    text_style: str = "font-weight:600; font-size:1rem;",
    gap: int = 8,
) -> None:
    """
    Render baris ikon + teks berdampingan (inline-flex).
    Cocok untuk item menu sidebar atau label section.

    Contoh:
        icon_text("home", "Beranda")
        icon_text("dashboard", "Dashboard", color=GREEN)
    """
    svg = icon_html(icon_name, size=size, color=color)
    st.markdown(
        f'<div style="display:inline-flex; align-items:center; gap:{gap}px;">'
        f"{svg}"
        f'<span style="{text_style}">{text}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def icon_header(
    icon_name: str,
    text: str,
    level: int = 2,
    color: str = BLUE,
    icon_size: int = 28,
) -> None:
    """
    Render heading (h1–h4) dengan ikon Lucide di sebelah kiri.

    Args:
        icon_name : nama ikon
        text      : teks heading
        level     : 1–4 (setara h1–h4)
        color     : warna ikon
        icon_size : ukuran ikon px
    """
    sizes = {1: "1.9rem", 2: "1.5rem", 3: "1.2rem", 4: "1rem"}
    fs = sizes.get(level, "1.2rem")
    svg = icon_html(icon_name, size=icon_size, color=color)
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">'
        f"{svg}"
        f'<span style="font-size:{fs}; font-weight:700; color:#1E293B;">{text}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def status_badge(
    label: str,
    color: str,
    icon_name: str | None = None,
    icon_size: int = 14,
) -> str:
    """
    Kembalikan HTML badge berwarna (tidak di-render, kembalikan string).
    Gunakan di dalam st.markdown().

    Contoh:
        st.markdown(status_badge("CLOSED", GREEN, "closed"), unsafe_allow_html=True)
    """
    ico = icon_html(icon_name, size=icon_size, color="white") if icon_name else ""
    return (
        f'<span style="display:inline-flex; align-items:center; gap:4px; '
        f'background:{color}; color:white; padding:2px 10px; '
        f'border-radius:20px; font-size:0.75rem; font-weight:600;">'
        f"{ico}{label}</span>"
    )
