#!/bin/bash
# ============================================================
# git_setup.sh — Panduan Git: T.U.N.T.A.S Version
# SPI PT. PG Candi Baru - Audit Management System
# ============================================================
# Cara pakai: 
# 1. Simpan di folder project
# 2. Jalankan: bash git_setup.sh
# ============================================================

echo "========================================================"
echo " 🚀 GIT SETUP: T.U.N.T.A.S → GITHUB"
echo "========================================================"

# --- LANGKAH 1: Identitas ---
echo -e "\n[1] Konfigurasi Identitas Git"
git config --global user.name "mhamzahnashirudin"
git config --global user.email "mhamzahnashirudin@gmail.com"
git config --global init.defaultBranch main
echo "✅ Identitas disetel ke: mhamzahnashirudin"

# --- LANGKAH 2: Inisialisasi ---
echo -e "\n[2] Inisialisasi Repo Lokal"
if [ ! -d ".git" ]; then
    git init
    echo "✅ Repo Git dibuat."
else
    echo "ℹ️ Repo Git sudah ada."
fi

# --- LANGKAH 3: Keamanan (Sangat Penting!) ---
echo -e "\n[3] Verifikasi .gitignore"
if [ ! -f ".gitignore" ]; then
    echo ".streamlit/secrets.toml" > .gitignore
    echo "venv/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo ".DS_Store" >> .gitignore
    echo "✅ .gitignore dibuat (Melindungi Secrets & venv)."
else
    if grep -q "secrets.toml" .gitignore; then
        echo "✅ secrets.toml sudah aman di .gitignore."
    else
        echo ".streamlit/secrets.toml" >> .gitignore
        echo "⚠️ secrets.toml ditambahkan ke .gitignore."
    fi
fi

# --- LANGKAH 4: Staging & Status ---
echo -e "\n[4] Staging Files"
git add .
echo "Berikut adalah file yang akan di-commit (PASTIKAN TIDAK ADA secrets.toml):"
git status | grep "new file" | head -n 10
echo "... (dan file lainnya)"

# --- LANGKAH 5: Commit ---
echo -e "\n[5] Membuat Commit Pertama"
git commit -m "feat: T.U.N.T.A.S v1.0 — SPI PT. PG Candi Baru

- Authentication system dengan streamlit-authenticator
- Dashboard interaktif menggunakan Plotly Express
- Integrasi Database Supabase (Cloud PostgreSQL)
- Optimasi RAM dengan gc.collect() ganda (Atas & Bawah)
- Struktur modular: utils/styles.py, utils/icons.py, utils/quotes.py"

# --- LANGKAH 6: Koneksi GitHub ---
echo -e "\n[6] Menghubungkan ke GitHub"
echo "Silakan buat repository di https://github.com/new dengan nama: tuntas-spi"
read -p "Masukkan URL Repository GitHub Anda (contoh: https://github.com/USERNAME/tuntas-spi.git): " repo_url

if [ ! -z "$repo_url" ]; then
    # Hapus remote lama jika ada, lalu tambah yang baru
    git remote remove origin 2>/dev/null
    git remote add origin $repo_url
    git branch -M main
    
    echo -e "\n[7] Pushing ke GitHub..."
    git push -u origin main
    echo "✅ SELESAI! Kode T.U.N.T.A.S sudah online."
else
    echo "❌ URL kosong. Push dibatalkan. Silakan jalankan 'git push' manual nanti."
fi

echo -e "\n========================================================"
echo " 💡 TIPS SEHARI-HARI (Workflow T.U.N.T.A.S)"
echo "========================================================"
echo " Jika ada perubahan kode baru:"
echo " 1. git add . "
echo " 2. git commit -m 'update: deskripsi perubahan' "
echo " 3. git push "
echo "--------------------------------------------------------"
echo " 🚀 TUNTASKAN HARI INI, TANPA BEBAN UNTUK ESOK!"
echo "========================================================"
