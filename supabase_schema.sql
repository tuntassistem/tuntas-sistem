-- ============================================================
-- T.U.N.T.A.S — Supabase Schema
-- SPI PT. PG Candi Baru | 2026
--
-- Jalankan seluruh file ini di:
--   Supabase Dashboard → SQL Editor → New Query → Run
--
-- Tabel:
--   1. unit_kerja     — master 25 unit kerja
--   2. audit_findings — temuan audit (standar 5C IIA)
--   3. action_plans   — tindak lanjut & verifikasi
-- ============================================================


-- ──────────────────────────────────────────────────────────────────────────────
-- TABEL 1: unit_kerja
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE unit_kerja (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    kode_unit     VARCHAR(10)  NOT NULL UNIQUE,
    nama_unit     VARCHAR(100) NOT NULL,
    kepala_unit   VARCHAR(100),
    kabag_induk   VARCHAR(60)  NOT NULL
        CHECK (kabag_induk IN (
            'Keuangan, IT & Manajemen Risiko',
            'SDM & Umum',
            'Tanaman',
            'Instalasi',
            'Pabrikasi',
            'Quality Assurance'
        )),
    kategori_unit VARCHAR(50)
        CHECK (kategori_unit IN (
            'Keuangan & Akuntansi', 'IT & Sistem', 'Manajemen Risiko', 'Gudang',
            'SDM', 'Umum & HSE', 'Pengadaan', 'Pemasaran',
            'Tanaman & Kebun', 'Tebang Angkut',
            'Instalasi Mesin', 'Kelistrikan', 'Workshop',
            'Pabrikasi', 'Laboratorium & QC',
            'Quality Assurance', 'Pengawasan Internal'
        )),
    aktif         BOOLEAN      DEFAULT TRUE,
    created_at    TIMESTAMPTZ  DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  DEFAULT NOW()
);

-- Seed: 25 unit kerja sesuai struktur organisasi PG Candi Baru
INSERT INTO unit_kerja (kode_unit, nama_unit, kabag_induk, kategori_unit) VALUES
    ('KEU-01', 'Akuntansi & Anggaran',             'Keuangan, IT & Manajemen Risiko', 'Keuangan & Akuntansi'),
    ('KEU-02', 'Keuangan, ATR & Manajemen Risiko', 'Keuangan, IT & Manajemen Risiko', 'Manajemen Risiko'),
    ('KEU-03', 'IT & Timbangan',                   'Keuangan, IT & Manajemen Risiko', 'IT & Sistem'),
    ('KEU-04', 'Gudang Material & Gudang Hasil',   'Keuangan, IT & Manajemen Risiko', 'Gudang'),
    ('SDM-01', 'SDM',                              'SDM & Umum',    'SDM'),
    ('SDM-02', 'Umum & HSE',                       'SDM & Umum',    'Umum & HSE'),
    ('SDM-03', 'Pengadaan',                        'SDM & Umum',    'Pengadaan'),
    ('SDM-04', 'Pemasaran & Pengembangan Usaha',   'SDM & Umum',    'Pemasaran'),
    ('TAN-01', 'SKK I (SKW I - V)',                'Tanaman',       'Tanaman & Kebun'),
    ('TAN-02', 'SKK II (SKW VI - VIII)',           'Tanaman',       'Tanaman & Kebun'),
    ('TAN-03', 'Tebang Angkut & Mekanisasi',       'Tanaman',       'Tebang Angkut'),
    ('TAN-04', 'Railban & Remise',                 'Tanaman',       'Tebang Angkut'),
    ('INS-01', 'St. Gilingan (Instalasi)',         'Instalasi',     'Instalasi Mesin'),
    ('INS-02', 'St. Ketel (Instalasi)',            'Instalasi',     'Instalasi Mesin'),
    ('INS-03', 'Besali / Workshop',                'Instalasi',     'Workshop'),
    ('INS-04', 'Listrik & Instrument',             'Instalasi',     'Kelistrikan'),
    ('PAB-01', 'St. Pemurnian',                    'Pabrikasi',     'Pabrikasi'),
    ('PAB-02', 'St. Penguapan',                    'Pabrikasi',     'Pabrikasi'),
    ('PAB-03', 'St. Masakan & Pendingin',          'Pabrikasi',     'Pabrikasi'),
    ('PAB-04', 'St. Puteran & Penyelesaian',       'Pabrikasi',     'Pabrikasi'),
    ('QA-01',  'PQA & CS',                         'Quality Assurance', 'Quality Assurance'),
    ('QA-02',  'IQA (Internal Quality Audit)',     'Quality Assurance', 'Quality Assurance'),
    ('QA-03',  'Document Controller',              'Quality Assurance', 'Quality Assurance'),
    ('QA-04',  'Laboratorium & QC',                'Quality Assurance', 'Laboratorium & QC'),
    ('SPI-01', 'Satuan Pengawas Internal',         'Keuangan, IT & Manajemen Risiko', 'Pengawasan Internal');


-- ──────────────────────────────────────────────────────────────────────────────
-- TABEL 2: audit_findings
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE audit_findings (
    id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    unit_kerja_id         UUID NOT NULL REFERENCES unit_kerja(id) ON DELETE RESTRICT,
    nomor_temuan          VARCHAR(30)  NOT NULL UNIQUE,
    judul_temuan          VARCHAR(300) NOT NULL,
    -- Elemen 5C standar IIA
    kondisi               TEXT,
    kriteria              TEXT,
    sebab                 TEXT,
    akibat                TEXT,
    rekomendasi           TEXT,
    -- Klasifikasi
    tingkat_signifikansi  VARCHAR(10) DEFAULT 'SEDANG'
        CHECK (tingkat_signifikansi IN ('KRITIS', 'TINGGI', 'SEDANG', 'RENDAH')),
    kategori_temuan       VARCHAR(30)
        CHECK (kategori_temuan IN (
            'Kelemahan Kontrol', 'Ketidakpatuhan', 'Inefisiensi',
            'Risiko Keuangan', 'Risiko Operasional', 'Risiko IT'
        )),
    sumber_data           VARCHAR(20) DEFAULT 'Manual'
        CHECK (sumber_data IN ('Manual', 'Import CSV')),
    -- Timeline
    tgl_temuan            DATE NOT NULL DEFAULT CURRENT_DATE,
    auditor_pic           VARCHAR(100),
    -- Respons auditee
    tanggapan_auditee     TEXT,
    tgl_tanggapan         DATE,
    -- Status
    status_temuan         VARCHAR(15) DEFAULT 'OPEN'
        CHECK (status_temuan IN ('OPEN', 'IN_PROGRESS', 'VERIFIED', 'CLOSED')),
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_findings_unit   ON audit_findings(unit_kerja_id);
CREATE INDEX idx_findings_status ON audit_findings(status_temuan);
CREATE INDEX idx_findings_signif ON audit_findings(tingkat_signifikansi);
CREATE INDEX idx_findings_tgl    ON audit_findings(tgl_temuan);


-- ──────────────────────────────────────────────────────────────────────────────
-- TABEL 3: action_plans
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE action_plans (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    finding_id          UUID NOT NULL REFERENCES audit_findings(id) ON DELETE CASCADE,
    urutan_tl           SMALLINT    DEFAULT 1,
    rencana_aksi        TEXT        NOT NULL,
    pic_pelaksana       VARCHAR(100) NOT NULL,
    jabatan_pic         VARCHAR(100),
    tgl_target          DATE        NOT NULL,
    tgl_realisasi       DATE,
    status_tl           VARCHAR(20) DEFAULT 'OPEN'
        CHECK (status_tl IN (
            'OPEN', 'ON_PROGRESS', 'SELESAI_PARSIAL', 'CLOSED', 'MELEWATI_TARGET'
        )),
    persentase_kemajuan SMALLINT DEFAULT 0
        CHECK (persentase_kemajuan BETWEEN 0 AND 100),
    bukti_dokumen       TEXT,
    catatan_verifikasi  TEXT,
    tgl_verifikasi      DATE,
    verifikator         VARCHAR(100),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ap_finding ON action_plans(finding_id);
CREATE INDEX idx_ap_status  ON action_plans(status_tl);
CREATE INDEX idx_ap_target  ON action_plans(tgl_target);


-- ──────────────────────────────────────────────────────────────────────────────
-- TRIGGER: updated_at otomatis diperbarui saat UPDATE
-- ──────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_findings_updated
    BEFORE UPDATE ON audit_findings
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_ap_updated
    BEFORE UPDATE ON action_plans
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ──────────────────────────────────────────────────────────────────────────────
-- ROW LEVEL SECURITY (RLS)
-- ──────────────────────────────────────────────────────────────────────────────
ALTER TABLE unit_kerja     ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_plans   ENABLE ROW LEVEL SECURITY;

-- Prototipe: semua user authenticated bisa baca
CREATE POLICY "read_all" ON unit_kerja     FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "read_all" ON audit_findings FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "read_all" ON action_plans   FOR SELECT TO anon, authenticated USING (true);
-- Write hanya lewat service_role (dikontrol dari backend Streamlit)
