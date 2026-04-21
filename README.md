# 🚀 T.U.N.T.A.S 
## Trackable Unit for Networked & Transparent Audit System

> **Satuan Pengawas Internal (SPI) — PT. PG Candi Baru**
> Stack: Python · Streamlit · Supabase (PostgreSQL Cloud)
> Identitas Korporat: **ID FOOD** — Biru `#0054A6` & Hijau `#00A651`
> Periode: Maret – Juni 2026 | Program Magang S1 Manajemen UNESA

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![UNESA](https://img.shields.io/badge/University-UNESA-003366?style=for-the-badge&logo=unicef&logoColor=FFCC00)](https://www.unesa.ac.id)
[![Maintainer](https://img.shields.io/badge/Maintainer-SPI_PGCB-0054A6?style=for-the-badge)](https://www.pgcandibaru.com/)

---

## Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Arsitektur & Routing](#arsitektur--routing)
- [Struktur Folder](#struktur-folder)
- [Deskripsi Halaman](#deskripsi-halaman)
- [Instalasi](#instalasi)
- [Konfigurasi Supabase](#konfigurasi-supabase)
- [Konfigurasi Secrets](#konfigurasi-secrets)
- [Desain & Brand](#desain--brand)
- [Deploy ke Streamlit Cloud](#deploy-ke-streamlit-cloud)
- [Kredit](#kredit)

---

## Fitur Utama

| Fitur | Keterangan |
|---|---|
| 🔐 **Autentikasi JWT** | Login berbasis cookie dengan `streamlit-authenticator`. Objek authenticator disimpan di `session_state` agar konsisten di seluruh rerun. |
| 📋 **Input Temuan 5C** | Form standar Institute of Internal Auditors (IIA): Kondisi, Kriteria, Sebab, Akibat, Rekomendasi. |
| 📊 **Dashboard Interaktif** | Visualisasi distribusi status temuan (bar chart Plotly), Top-10 aging, dan KPI scorecard. |
| ✅ **Monitoring Action Plans** | Update status tindak lanjut, verifikasi lapangan SPI, alert otomatis deadline terlampaui. |
| 🚨 **Alert System** | Banner merah otomatis untuk TL `MELEWATI_TARGET` dan temuan `KRITIS` yang masih `OPEN`. |
| 📥 **Export CSV** | Unduh data audit findings & action plans dalam format CSV UTF-8 BOM (kompatibel Excel Indonesia). |
| 🎨 **Branding ID FOOD** | Tema visual konsisten menggunakan design token biru `#0054A6` dan hijau `#00A651`. |

---

## Arsitektur & Routing

T.U.N.T.A.S menggunakan pola **Router Murni** untuk menghindari *double-render glitch* yang umum terjadi saat mengombinasikan `streamlit-authenticator` dengan multi-page apps.

```
┌─────────────────────────────────────────────────────────────┐
│                         app.py                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Inisialisasi Authenticator (sekali, di           │   │
│  │     session_state)                                   │   │
│  │  2. Silent cookie check → location="unrendered"     │   │
│  │  3. Routing berdasarkan authentication_status        │   │
│  └─────────────────────────────────────────────────────┘   │
│              │                         │                    │
│       Status = True             Status = False/None         │
│              ▼                         ▼                    │
│   ┌──────────────────┐     ┌─────────────────────┐        │
│   │  Sidebar + Menu  │     │  pages/login_pg.py  │        │
│   │  ─────────────── │     │  (render form saja) │        │
│   │  0_Beranda.py    │     └─────────────────────┘        │
│   │  1_Dashboard.py  │                                     │
│   │  2_Input_Audit   │                                     │
│   │  3_Action_Plans  │                                     │
│   └──────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

**Kenapa dipisah?**
`app.py` **tidak pernah merender UI** untuk user yang belum login — ia hanya membaca cookie lalu mendelegasikan rendering ke `login_pg.py`. Ini memastikan satu siklus render yang bersih, sehingga fungsi cookie JWT tidak terganggu.

---

## Struktur Folder

```
tuntas/
├── app.py                          # Router utama + sidebar + autentikasi
│
├── pages/
│   ├── login_pg.py                 # Halaman login (form + branding)
│   ├── 0_Beranda.py                # Home: KPI, lingkup, panduan, alert aktif
│   ├── 1_Dashboard.py              # Visualisasi: status, aging, scorecard
│   ├── 2_Input_Audit.py            # Form temuan 5C + riwayat + export
│   └── 3_Action_Plans.py           # Monitoring TL: update, tambah, verifikasi
│
├── utils/
│   ├── __init__.py
│   ├── supabase_client.py          # Data Access Layer (DAL) — fetch & mutasi
│   ├── export_utils.py             # Export CSV UTF-8 BOM (kompatibel Excel)
│   ├── icons.py                    # Lucide icon renderer (inline SVG, no dep)
│   ├── styles.py                   # Design tokens & CSS global ID FOOD
│   └── quotes.py                   # Quote rotasi untuk halaman login
│
├── assets/
│   └── tuntas_logos.svg            # Logo T.U.N.T.A.S (page icon)
│
├── .streamlit/
│   ├── config.toml                 # Tema Streamlit (primary #0054A6)
│   └── secrets.toml                # ⚠️ Buat manual — JANGAN di-commit!
│
├── supabase_schema.sql             # Schema DB (jalankan di Supabase SQL Editor)
├── requirements.txt
└── .gitignore
```

---

## Deskripsi Halaman

### 🏠 `0_Beranda.py` — Beranda
Halaman awal setelah login. Berisi:
- **KPI Scorecard** (5 metrik): Total Temuan, Temuan Open, Temuan Kritis, TL Terlambat, TL Selesai
- **Tentang Sistem**: deskripsi fitur T.U.N.T.A.S
- **Panduan Penggunaan**: shortcut ke tiap modul
- **Lingkup Pengawasan SPI**: grid unit kerja yang diaudit (Keuangan/IT/MR, SDM & Umum, Tanaman, Instalasi, Pabrikasi, QA)
- **Skala Signifikansi**: legenda warna KRITIS → RENDAH
- **Peringatan Aktif**: alert otomatis untuk TL terlambat dan temuan KRITIS yang masih OPEN

---

### 📊 `1_Dashboard.py` — Dashboard Monitoring
Visualisasi interaktif berbasis Plotly:
- **KPI Scorecard**: Temuan Open, Temuan Kritis, TL Melewati Target, Rata-rata Kemajuan TL
- **Distribusi Status Temuan**: bar chart dengan color map per status
- **Top 10 Aging**: tabel temuan non-closed paling lama terbuka (dalam hari)
- **Filter Sidebar**: per Kepala Bagian & multi-select Signifikansi

---

### 📋 `2_Input_Audit.py` — Input Temuan Audit
Form pencatatan temuan standar **5C (IIA)**:

| Elemen | Keterangan |
|---|---|
| **1 — Kondisi** | Fakta objektif yang ditemukan |
| **2 — Kriteria** | Standar / SOP yang seharusnya berlaku |
| **3 — Sebab** | Akar penyebab penyimpangan |
| **4 — Akibat** | Dampak aktual / potensial |
| **5 — Rekomendasi** | Saran perbaikan dari SPI |

Field tambahan: Nomor Temuan (format `TEM-SPI-TAHUN-NNN`), Unit Kerja, Tanggal, Auditor PIC, Tingkat Signifikansi (`KRITIS` / `TINGGI` / `SEDANG` / `RENDAH`), Kategori, dan Respons Auditee.

Tab **Riwayat & Export**: tabel 10 temuan terbaru + tombol unduh CSV seluruh `audit_findings`.

---

### ✅ `3_Action_Plans.py` — Monitoring Tindak Lanjut
Modul verifikasi SPI:
- **Banner Alert**: peringatan merah jika ada TL `MELEWATI_TARGET`, hijau jika semua on-track
- **KPI Scorecard**: Total TL, Open, In Progress, Terlambat, Selesai (Closed)
- **Tab Daftar**: tabel 15 TL terbaru dengan color-coding per status, sortir by `tgl_target`
- **Tab Update Status**: form verifikasi lapangan (status baru, persentase kemajuan, tanggal realisasi, referensi bukti, catatan SPI)
- **Tab Tambah Rencana TL**: form tambah tindak lanjut baru dengan pencarian temuan by nomor/judul
- **Filter Sidebar**: per Status TL, Kepala Bagian, Signifikansi Temuan

**Status TL yang tersedia:**

| Status | Makna |
|---|---|
| `OPEN` | Belum dimulai |
| `ON_PROGRESS` | Sedang berjalan |
| `SELESAI_PARSIAL` | Sebagian selesai |
| `CLOSED` | Selesai & terverifikasi SPI |
| `MELEWATI_TARGET` | Melampaui deadline target |

---

## Instalasi

```bash
git clone https://github.com/USERNAME/tuntas-pgcb.git
cd tuntas-pgcb

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Dependensi Utama

```
streamlit
streamlit-authenticator
supabase
pandas
plotly
pillow
```

---

## Konfigurasi Supabase

1. Buat project di [supabase.com](https://supabase.com)
2. Buka **SQL Editor → New Query** → paste isi `supabase_schema.sql` → klik **Run**
3. Pastikan tabel `unit_kerja`, `audit_findings`, dan `action_plans` terbuat dengan benar
4. Salin **Project URL** dan **anon public key** dari **Settings → API**

---

## Konfigurasi Secrets

Buat file `.streamlit/secrets.toml` secara manual. **Jangan commit file ini ke Git.**

```toml
# ── Supabase ──────────────────────────────────────────────
[supabase]
url              = "https://YOUR_PROJECT_REF.supabase.co"
key              = "YOUR_ANON_PUBLIC_KEY"
service_role_key = "YOUR_SERVICE_ROLE_KEY"

# ── Streamlit Authenticator ────────────────────────────────
# Format credentials mengikuti skema streamlit-authenticator v0.3+
[credentials]
# Contoh minimal — sesuaikan dengan struktur yang dibutuhkan
# versi stauth yang dipakai

[auth]
cookie_name        = "tuntas_auth"
cookie_key         = "GANTI_DENGAN_RANDOM_STRING_PANJANG"
cookie_expiry_days = 7
```

> **Catatan:** Struktur `[credentials]` mengikuti format `streamlit-authenticator`.
> Lihat [dokumentasi resminya](https://github.com/mkhorasani/Streamlit-Authenticator)
> untuk skema `usernames`, `name`, `email`, dan `password` (hashed).

---

### Menjalankan Aplikasi

```bash
streamlit run app.py
```

Akses di browser: `http://localhost:8501`

---

## Desain & Brand

T.U.N.T.A.S mengikuti panduan visual korporat **ID FOOD**.

| Token | Nilai | Penggunaan |
|---|---|---|
| `BLUE` | `#0054A6` | Primary — header, tombol utama, aksen navigasi |
| `GREEN` | `#00A651` | Success — status selesai, alert positif |
| `RED` | `#DC2626` | Danger — temuan kritis, deadline terlampaui |
| `AMBER` | `#D97706` | Warning — signifikansi tinggi, status parsial |

**Ikon:** Menggunakan Lucide icon set yang dirender sebagai **inline SVG** melalui `utils/icons.py`. Tidak ada dependensi `streamlit-lucide` — ikon diinjeksi langsung ke HTML via `st.markdown(unsafe_allow_html=True)` agar kompatibel di semua environment termasuk Streamlit Cloud.

**CSS Global:** Dikelola melalui `utils/styles.py` dengan fungsi `inject_global_css()` yang dipanggil di setiap halaman. Termasuk class `.tnt-card`, `.tnt-card-red`, `.tnt-card-green` untuk komponen card standar.

---

## Deploy ke Streamlit Cloud

```bash
git add .
git commit -m "feat: T.U.N.T.A.S v1.0 — initial release"
git push origin main
```

1. Buka [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Pilih repo dan set **Main file path**: `app.py`
3. Buka **Advanced settings → Secrets**
4. Paste seluruh isi `.streamlit/secrets.toml` ke kolom secrets
5. Klik **Deploy**

> ⚠️ Pastikan `.streamlit/secrets.toml` sudah masuk ke `.gitignore` sebelum push.

---

## Kredit

**Pengembang:** Muhammad Hamzah Nashirudin
S1 Manajemen · Universitas Negeri Surabaya (UNESA)
Program Magang SPI PT. PG Candi Baru 2026

**Pembimbing Lapangan:** Bapak Arif Wicaksono Roosyanto
**Dosen Pembimbing:** Ibu Dr. Cici Widowati

---

*T.U.N.T.A.S v1.0 · SPI PT. PG Candi Baru · 2026*
