# utils/quotes.py
import random

QUOTES_LIST = [
    # --- 1. ISLAMI (Prinsip Amanah & Kejujuran) ---
    '"Sampaikanlah kebenaran meski itu pahit." – HR. Ahmad',
    '"Amanah itu membawa rezeki, khianat itu membawa fakir." – HR. Ad-Dailami',
    '"Cukuplah seseorang dikatakan berdusta jika menceritakan semua yang didengar." – HR. Muslim',
    '"Bekerjalah seakan kamu hidup selamanya." – Ali bin Abi Thalib',
    '"Kejujuran itu menenangkan, kebohongan itu menggelisahkan." – HR. Tirmidzi',

    # --- 2. INDONESIA (Semangat Kerja & Integritas) ---
    '"Berani jujur itu hebat!" – Slogan KPK',
    '"Kurang cerdas bisa diperbaiki, kurang jujur sulit diperbaiki." – Bung Hatta',
    '"Tuhan tidak mengubah nasib suatu bangsa sebelum mereka mengubahnya sendiri." – Bung Karno',
    '"Integritas adalah napas seorang pemimpin." – Baharuddin Lopa',
    '"Bekerja bukan sekadar mencari nafkah, tapi ibadah." – Buya Hamka',

    # --- 3. ENGLISH (To the Point & Modern) ---
    '"Facts are stubborn things." – John Adams',
    '"Standardize then optimize." – Masaaki Imai',
    '"In God we trust, all others bring data." – W. Edwards Deming',
    '"Trust is built with consistency." – Lincoln Chafee',
    '"Don’t find fault, find a remedy." – Henry Ford',

    # --- 4. FILSAFAT (Dalam & Reflektif) ---
    '"Hidup yang tidak diuji tidak layak untuk dijalani." – Socrates',
    '"Kebenaran adalah anak waktu, bukan otoritas." – Francis Bacon',
    '"Kita adalah apa yang kita kerjakan berulang kali." – Aristoteles',
    '"Mengetahui diri sendiri adalah awal kebijaksanaan." – Socrates',
    '"Berpikir itu berat, karena itu sedikit orang yang melakukannya." – Carl Jung'

    # --- 5. FILSAFAT ISLAM (Logika & Kebijaksanaan) ---
    '"Keyakinan tidak bisa dikalahkan oleh keraguan." – Imam Syafi’i',
    '"Kebijaksanaan adalah barang hilang milik mukmin, ambillah di mana pun kau temukan." – Ibnu Rusyd',
    '"Penyakit ilmu adalah lupa, dan menyia-nyiakannya adalah bicara tanpa ahli." – Al-Ghazali',
    '"Kebenaran objektif itu ada, tugas kita adalah mendekatinya dengan akal." – Al-Kindi',
    '"Jangan biarkan emosi mematikan logika keadilanmu." – Ibnu Khaldun'
]

def get_random_quote():
    return random.choice(QUOTES_LIST)
#feat: T.U.N.T.A.S v1.0 — SPI PT. PG Candi Baru
