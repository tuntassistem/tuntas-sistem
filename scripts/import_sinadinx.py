"""
scripts/import_sinadinx.py
===========================
Script Python untuk mengimpor data ekspor CSV dari sistem SINAdin
(ERP PT. PG Candi Baru) ke dalam database AuditFlow di Supabase.

Cara penggunaan:
  1. Export data dari SINAdin ke format CSV (UTF-8)
  2. Set environment variable SUPABASE_URL dan SUPABASE_SERVICE_KEY
  3. Jalankan: python scripts/import_sinadinx.py --file export_temuan.csv --mode temuan

Mode yang tersedia:
  --mode temuan   : Import data temuan audit dari SINAdin
  --mode unit     : Sinkronisasi master data unit kerja

Untuk video tutorial: demo singkat bahwa data dari SINAdin
bisa masuk ke AuditFlow tanpa perlu diketik ulang manual.
"""

import argparse
import os
import sys
import pandas as pd
from datetime import datetime, date

# ── Coba import supabase, tampilkan panduan jika belum terinstall ──────────────
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Library 'supabase' belum terinstall.")
    print("   Jalankan: pip install supabase")
    sys.exit(1)


# ── Konfigurasi dari environment variable ──────────────────────────────────────
SUPABASE_URL     = os.environ.get("SUPABASE_URL", "")
SUPABASE_SVC_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Untuk testing lokal, bisa juga hardcode di sini (JANGAN push ke GitHub):
# SUPABASE_URL     = "https://xxx.supabase.co"
# SUPABASE_SVC_KEY = "your-service-role-key"


def get_client() -> Client:
    """Inisialisasi koneksi Supabase dengan service_role key (full access)."""
    if not SUPABASE_URL or not SUPABASE_SVC_KEY:
        raise EnvironmentError(
            "Environment variable SUPABASE_URL dan SUPABASE_SERVICE_KEY "
            "harus di-set terlebih dahulu.\n"
            "Contoh:\n"
            "  export SUPABASE_URL='https://xxx.supabase.co'\n"
            "  export SUPABASE_SERVICE_KEY='your-service-role-key'"
        )
    return create_client(SUPABASE_URL, SUPABASE_SVC_KEY)


def clean(val) -> str | None:
    """Bersihkan nilai: hapus whitespace, kembalikan None jika kosong/NaN."""
    if pd.isna(val) or str(val).strip() in ("", "nan", "None", "-"):
        return None
    return str(val).strip()


# ── Mode 1: Import Temuan Audit ────────────────────────────────────────────────

def import_temuan(filepath: str, dry_run: bool = False):
    """
    Import data temuan audit dari file CSV ekspor SINAdin.

    Format CSV yang diharapkan (header baris pertama):
    kode_unit, nomor_temuan, judul_temuan, kondisi, kriteria, sebab,
    akibat, rekomendasi, tingkat_signifikansi, tgl_temuan, auditor_pic

    Kolom wajib: kode_unit, nomor_temuan, judul_temuan
    Kolom opsional: kondisi, kriteria, sebab, akibat, rekomendasi,
                    tingkat_signifikansi, tgl_temuan, auditor_pic

    Parameter:
        filepath  : Path ke file CSV
        dry_run   : Jika True, hanya validasi tanpa simpan ke database
    """
    print(f"\n{'='*60}")
    print(f"IMPORT TEMUAN AUDIT — AuditFlow")
    print(f"File    : {filepath}")
    print(f"Mode    : {'DRY RUN (tidak menyimpan)' if dry_run else 'LIVE (menyimpan ke database)'}")
    print(f"Waktu   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Baca file CSV
    try:
        df = pd.read_csv(filepath, encoding="utf-8", dtype=str)
        print(f"✅ File berhasil dibaca: {len(df)} baris data")
    except UnicodeDecodeError:
        # Coba encoding alternatif (Windows Excel sering pakai cp1252)
        df = pd.read_csv(filepath, encoding="cp1252", dtype=str)
        print(f"✅ File dibaca dengan encoding cp1252: {len(df)} baris")
    except FileNotFoundError:
        print(f"❌ File tidak ditemukan: {filepath}")
        return

    # Validasi kolom wajib
    required_cols = ["kode_unit", "nomor_temuan", "judul_temuan"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"❌ Kolom wajib tidak ditemukan: {missing}")
        print(f"   Kolom yang ada: {list(df.columns)}")
        return

    if dry_run:
        print("\n📋 Preview data (5 baris pertama):")
        print(df.head().to_string())
        print("\n✅ Dry run selesai. Tidak ada data yang disimpan.")
        return

    # Koneksi ke Supabase
    try:
        sb = get_client()
    except EnvironmentError as e:
        print(f"❌ {e}")
        return

    # Ambil pemetaan kode_unit → id dari database
    units_resp = sb.table("unit_kerja").select("id, kode_unit").execute()
    unit_map = {u["kode_unit"]: u["id"] for u in (units_resp.data or [])}
    print(f"📊 Master unit kerja ditemukan: {len(unit_map)} unit")

    # Tentukan nilai default untuk tingkat_signifikansi yang valid
    valid_signifikansi = {"KRITIS", "TINGGI", "SEDANG", "RENDAH"}

    sukses = gagal = duplikat = 0
    errors = []

    for idx, row in df.iterrows():
        baris = idx + 2  # Baris di CSV (dimulai dari 2 karena ada header)

        kode_unit = clean(row.get("kode_unit", ""))
        nomor     = clean(row.get("nomor_temuan", ""))
        judul     = clean(row.get("judul_temuan", ""))

        # Validasi field wajib per baris
        if not kode_unit:
            errors.append(f"Baris {baris}: kode_unit kosong — baris dilewati")
            gagal += 1
            continue

        if kode_unit not in unit_map:
            errors.append(f"Baris {baris}: unit '{kode_unit}' tidak ditemukan di database")
            gagal += 1
            continue

        if not nomor:
            errors.append(f"Baris {baris}: nomor_temuan kosong — baris dilewati")
            gagal += 1
            continue

        if not judul:
            errors.append(f"Baris {baris}: judul_temuan kosong — baris dilewati")
            gagal += 1
            continue

        # Validasi tingkat_signifikansi
        signifikansi_raw = clean(row.get("tingkat_signifikansi", "SEDANG"))
        signifikansi = signifikansi_raw.upper() if signifikansi_raw else "SEDANG"
        if signifikansi not in valid_signifikansi:
            signifikansi = "SEDANG"  # Fallback ke SEDANG jika tidak valid

        # Siapkan payload
        payload = {
            "unit_kerja_id":        unit_map[kode_unit],
            "nomor_temuan":         nomor.upper(),
            "judul_temuan":         judul,
            "kondisi":              clean(row.get("kondisi", "")),
            "kriteria":             clean(row.get("kriteria", "")),
            "sebab":                clean(row.get("sebab", "")),
            "akibat":               clean(row.get("akibat", "")),
            "rekomendasi":          clean(row.get("rekomendasi", "")),
            "tingkat_signifikansi": signifikansi,
            "tgl_temuan":           clean(row.get("tgl_temuan", "")) or date.today().isoformat(),
            "auditor_pic":          clean(row.get("auditor_pic", "")),
            "sumber_data":          "Import SINAdin",
            "status_temuan":        "OPEN",
        }

        try:
            sb.table("audit_findings").insert(payload).execute()
            sukses += 1
            print(f"  ✅ [{baris}] {nomor.upper()} — {judul[:50]}...")

        except Exception as e:
            error_msg = str(e)
            if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
                duplikat += 1
                print(f"  ⚠️  [{baris}] {nomor.upper()} sudah ada (duplikat, dilewati)")
            else:
                errors.append(f"Baris {baris}: {error_msg}")
                gagal += 1

    # ── Ringkasan Hasil ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"RINGKASAN HASIL IMPORT")
    print(f"{'='*60}")
    print(f"  ✅ Berhasil diimport : {sukses} baris")
    print(f"  ⚠️  Duplikat (skip)  : {duplikat} baris")
    print(f"  ❌ Gagal             : {gagal} baris")
    print(f"  📊 Total diproses    : {sukses + duplikat + gagal} baris")

    if errors:
        print(f"\n❗ Detail Error ({len(errors)} error):")
        for err in errors:
            print(f"   - {err}")

    print(f"\n🕐 Selesai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ── Mode 2: Sinkronisasi Unit Kerja ───────────────────────────────────────────

def sync_unit_kerja(filepath: str, dry_run: bool = False):
    """
    Sinkronisasi master data unit kerja dari file CSV SINAdin.

    Format CSV yang diharapkan:
    kode_unit, nama_unit, kepala_unit, kabag_induk, kategori_unit

    Menggunakan INSERT ... ON CONFLICT DO UPDATE (upsert)
    sehingga aman dijalankan berulang kali.
    """
    print(f"\n{'='*60}")
    print("SINKRONISASI MASTER UNIT KERJA")
    print(f"File: {filepath}")
    print("="*60)

    try:
        df = pd.read_csv(filepath, encoding="utf-8", dtype=str)
        print(f"✅ File dibaca: {len(df)} baris")
    except Exception as e:
        print(f"❌ Gagal membaca file: {e}")
        return

    if dry_run:
        print("📋 Preview (5 baris pertama):")
        print(df.head().to_string())
        print("\n✅ Dry run selesai.")
        return

    valid_kabag = {
        "Keuangan, IT & Manajemen Risiko", "SDM & Umum",
        "Tanaman", "Instalasi", "Pabrikasi", "Quality Assurance"
    }

    try:
        sb = get_client()
    except EnvironmentError as e:
        print(f"❌ {e}")
        return

    sukses = gagal = 0
    for idx, row in df.iterrows():
        kode = clean(row.get("kode_unit", ""))
        nama = clean(row.get("nama_unit", ""))
        if not kode or not nama:
            gagal += 1
            continue

        kabag_raw = clean(row.get("kabag_induk", ""))
        if kabag_raw not in valid_kabag:
            print(f"  ⚠️  Baris {idx+2}: kabag_induk '{kabag_raw}' tidak valid, dilewati")
            gagal += 1
            continue

        payload = {
            "kode_unit":    kode.upper(),
            "nama_unit":    nama,
            "kepala_unit":  clean(row.get("kepala_unit", "")),
            "kabag_induk":  kabag_raw,
            "kategori_unit": clean(row.get("kategori_unit", "")) or None,
            "aktif":        True,
        }

        try:
            sb.table("unit_kerja").upsert(payload, on_conflict="kode_unit").execute()
            sukses += 1
            print(f"  ✅ {kode.upper()} — {nama}")
        except Exception as e:
            print(f"  ❌ Baris {idx+2}: {e}")
            gagal += 1

    print(f"\n✅ Berhasil: {sukses} | ❌ Gagal: {gagal}")


# ── CONTOH FORMAT CSV (untuk dokumentasi / test) ───────────────────────────────

CONTOH_CSV_TEMUAN = """kode_unit,nomor_temuan,judul_temuan,kondisi,kriteria,sebab,akibat,rekomendasi,tingkat_signifikansi,tgl_temuan,auditor_pic
KEU-01,TEM-SPI-2026-006,Pencatatan biaya overhead tidak sesuai PSAK 14,"Ditemukan 3 item biaya overhead dibebankan ke HPP tidak sesuai PSAK 14","PSAK 14 mensyaratkan biaya overhead dibebankan berdasarkan kapasitas normal","Staf akuntansi belum terlatih PSAK 14 terbaru","Potensi salah saji HPP dan laba kotor","Pelatihan PSAK 14 dan review bulanan",SEDANG,2026-04-01,Hamzah N.
PAB-03,TEM-SPI-2026-007,Suhu masakan tidak terpantau real-time,"Sensor suhu masakan hanya dicatat manual 2x sehari","SOP mensyaratkan monitoring suhu setiap 30 menit","Sensor digital belum terpasang di semua unit masakan","Penurunan kualitas gula, kristal tidak seragam","Pasang sensor digital terintegrasi SINAdin",TINGGI,2026-04-02,Hamzah N.
"""

CONTOH_CSV_UNIT = """kode_unit,nama_unit,kepala_unit,kabag_induk,kategori_unit
NEW-01,Unit Baru Test,Budi Test,Pabrikasi,Pabrikasi
"""


def generate_sample_csv():
    """Generate file CSV contoh untuk testing import."""
    print("\n📄 Membuat file contoh CSV...")

    with open("contoh_import_temuan.csv", "w", encoding="utf-8") as f:
        f.write(CONTOH_CSV_TEMUAN)
    print("✅ contoh_import_temuan.csv berhasil dibuat")

    with open("contoh_import_unit.csv", "w", encoding="utf-8") as f:
        f.write(CONTOH_CSV_UNIT)
    print("✅ contoh_import_unit.csv berhasil dibuat")
    print("\nUji coba dengan: python scripts/import_sinadinx.py --file contoh_import_temuan.csv --mode temuan --dry-run")


# ── Main Entry Point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AuditFlow — Import CSV SINAdin ke Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  # Preview tanpa menyimpan (dry run):
  python scripts/import_sinadinx.py --file data.csv --mode temuan --dry-run

  # Import data temuan:
  python scripts/import_sinadinx.py --file export_maret2026.csv --mode temuan

  # Sinkronisasi unit kerja:
  python scripts/import_sinadinx.py --file unit_kerja.csv --mode unit

  # Buat file CSV contoh:
  python scripts/import_sinadinx.py --sample
        """
    )
    parser.add_argument("--file",    help="Path ke file CSV yang akan diimport")
    parser.add_argument("--mode",    choices=["temuan", "unit"], default="temuan",
                        help="Mode import: 'temuan' atau 'unit' (default: temuan)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validasi saja, tidak menyimpan ke database")
    parser.add_argument("--sample",  action="store_true",
                        help="Generate file CSV contoh untuk testing")

    args = parser.parse_args()

    if args.sample:
        generate_sample_csv()
        return

    if not args.file:
        parser.print_help()
        print("\n❌ Error: --file wajib diisi (kecuali menggunakan --sample)")
        sys.exit(1)

    if args.mode == "temuan":
        import_temuan(args.file, dry_run=args.dry_run)
    elif args.mode == "unit":
        sync_unit_kerja(args.file, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
