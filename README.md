# 🚀 T.U.N.T.A.S 
### **Trackable Unit for Networked & Transparent Audit System**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![UNESA](https://img.shields.io/badge/University-UNESA-003366?style=for-the-badge&logo=unicef&logoColor=FFCC00)](https://www.unesa.ac.id)
[![Maintainer](https://img.shields.io/badge/Maintainer-SPI_PGCB-0054A6?style=for-the-badge)](https://www.pgcandibaru.com/)

---

## 🏛️ Tentang Proyek
**T.U.N.T.A.S** adalah platform manajemen audit digital terintegrasi yang dirancang khusus untuk **Satuan Pengawas Internal (SPI) PT. PG Candi Baru (ID FOOD)**. Sistem ini bertujuan untuk mengeliminasi inefisiensi pelaporan manual dan memastikan setiap temuan audit terpantau secara transparan hingga tahap penyelesaian (*Action Plans*).

> **Visi Sistem:** Mewujudkan akuntabilitas audit yang *real-time*, terukur, dan terdokumentasi secara digital untuk mendukung keberlanjutan industri gula nasional.

---

## ✨ Fitur Utama
* **📊 Dashboard Analytics:** Visualisasi KPI temuan audit, status penyelesaian, dan sebaran risiko per unit kerja secara interaktif.
* **📝 Form Input 5C:** Standardisasi input temuan berdasarkan kriteria *Condition, Cause, Consequences, Complexity,* dan *Control*.
* **🛠️ Action Plan Tracker:** Monitoring bertahap untuk rencana tindak lanjut (Action Plans) hingga tahap verifikasi akhir oleh auditor.
* **💾 Cloud Integration:** Sinkronisasi data langsung ke database PostgreSQL Cloud (Supabase).

---

## Struktur Folder

```
tuntas/
├── app.py                      # Beranda T.U.N.T.A.S
├── supabase_schema.sql         # Schema DB (jalankan di Supabase SQL Editor)
├── requirements.txt
├── .gitignore
│
├── .streamlit/
│   ├── config.toml             # Tema ID FOOD (primary #0054A6)
│   └── secrets.toml            # ⚠️ Buat manual, JANGAN commit!
│
├── pages/
│   ├── 1_Dashboard.py          # Visualisasi & KPI
│   ├── 2_Input_Audit.py        # Form input temuan 5C
│   └── 3_Action_Plans.py       # Monitoring & verifikasi tindak lanjut
│
└── utils/
    ├── __init__.py
    ├── supabase_client.py      # Data Access Layer (DAL)
    ├── export_utils.py         # Export CSV UTF-8 BOM
    ├── icons.py                # Lucide icon renderer (inline SVG)
    └── styles.py               # Design tokens & CSS global ID FOOD
```

---

## Instalasi

```bash
git clone https://github.com/tuntassistem/tuntas-sistem
cd tuntas-sistem

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Setup Supabase

1. Buat project di [supabase.com](https://supabase.com)
2. **SQL Editor → New Query** → paste isi `supabase_schema.sql` → **Run**
3. Buat `.streamlit/secrets.toml`:

```toml
[supabase]
url              = "https://YOUR_PROJECT_REF.supabase.co"
key              = "YOUR_ANON_PUBLIC_KEY"
service_role_key = "YOUR_SERVICE_ROLE_KEY"
```

```bash
streamlit run app.py
```

---

## Desain & Brand

| Elemen | Warna | Hex | Representasi |
|---|---|---|---|
| **ID FOOD Blue** | 🔵 | `#0054A6` | Stabilitas, Integritas, Profesionalisme |
| **ID FOOD Green** | 🟢 | `#00A651` | Pertumbuhan, Sustainabilitas |
| **Alert Red** | 🔴 | `#DC2626` | Risiko Kritis / Temuan Mayor |

**Ikon:** Lucide icon set via library `lucide` (Python) — dirender sebagai inline SVG melalui `utils/icons.py`. Tidak ada dependensi `streamlit-lucide` (paket tersebut tidak tersedia di PyPI).

---

## Deploy ke Streamlit Cloud

```bash
git add .
git commit -m "feat: T.U.N.T.A.S v1.0 — rebranding ID FOOD"
git push origin main
# share.streamlit.io → New app → Advanced settings → Secrets → paste secrets.toml
```

---

**Muhammad Hamzah Nashirudin** · S1 Manajemen UNESA · Magang SPI PT. PG Candi Baru 2026  
Pembimbing Lapangan: Bapak Arif Wicaksono Roosyanto · Dosen: Ibu Dr. Cici Widowati
