# Prototipe Throwaway (Bab III Subbab 3.4)

Folder ini adalah **prototipe throwaway**: dibuat SEBELUM sistem produksi
untuk menguji bagian berisiko tinggi, lalu dibuang. Isinya **bukan basis
kode produksi** dan tidak boleh diimpor oleh `backend/app`, `frontend`, dll.

## Isi folder

```text
prototype/
├── mockup/
│   └── index.html                  # wireframe statis (HTML+CSS+JS, tanpa backend)
├── experiment/
│   ├── experiment_extraction_tsr.py # skrip mandiri ekstraksi PDF + TSR manual
│   ├── requirements.txt             # pymupdf, pdfplumber, fuzzywuzzy, python-Levenshtein
│   └── hasil_eksperimen.md          # keluaran skrip (dibuat saat dijalankan)
└── README.md                        # file ini
```

Folder ini mandiri: bisa disalin ke repo publik tersendiri
(`git init` di dalam `prototype/`) untuk tautan lampiran sidang.

## 1. Mockup wireframe

File: `mockup/index.html` — satu file, tanpa framework, tanpa request server.

Cara menjalankan:

```bash
# opsi A: buka langsung (double-click)
mockup/index.html

# opsi B: server statis lokal (tanpa backend)
cd prototype/mockup
python3 -m http.server 8080
# buka http://localhost:8080/index.html
```

Isi: 5 tab (Login, Dashboard Supervisor, Form MPR dengan tag keywords,
Dashboard HRD, Alur Persetujuan). Semua data dummy; tombol Setujui/Tolak
hanya mengubah tampilan (tanpa penyimpanan). Setiap halaman berlabel
"PROTOTIPE - WIREFRAME".

## 2. Skrip eksperimen Python

File: `experiment/experiment_extraction_tsr.py` — mandiri, tidak mengimpor
kode produksi.

```bash
cd prototype/experiment
pip install -r requirements.txt
python experiment_extraction_tsr.py --pdf-dir /path/ke/folder-cv-uji-coba
# keluaran: tabel di terminal + hasil_eksperimen.md
```

- Eksperimen A membandingkan PyMuPDF vs pdfplumber per file PDF
  (waktu ms, jumlah karakter/kata, flag kosong, 150 karakter pertama
  yang disamarkan `[EMAIL]`/`[NO_HP]`).
- Eksperimen B menguji fungsi `tsr_manual(a, b)` = `(2M/T) x 100`
  (token → sort alfabetis → gabung → `difflib.SequenceMatcher`)
  melawan `fuzz.token_sort_ratio`, plus flag lolos ambang 85.

## Status throwaway

- Mockup hanya acuan visual untuk konfirmasi layout/alur dengan calon pengguna.
- Skrip hanya pembuktian kelayakan (feasibility) ekstraksi dan formula TSR.
- Keduanya **tidak dipakai sebagai kode produksi** dan sengaja tidak
  mengikuti struktur `backend/`/`frontend/`.
