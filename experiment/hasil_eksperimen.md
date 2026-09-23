# Hasil Eksperimen Prototipe (Throwaway)

> Prototipe pra-produksi. File PDF sampel milik penguji, bukan data riil.
> Cuplikan teks disamarkan ([EMAIL]/[NO_HP]).

## Eksperimen A — Ekstraksi PDF

| file | pustaka | waktu_ms | karakter | kata | kosong | cuplikan_150 |
|---|---|---:|---:|---:|:---:|---|
| DOC-01.pdf | pymupdf | 18.3 | 1284 | 144 | False | PROTOTYPE SAMPLE 01, Backend Developer (fictional). Skills: Python, FastAPI, PostgreSQL. Experience: 3 years building REST APIs. Contact: [EMAIL], [NO |
| DOC-01.pdf | pdfplumber | 313.6 | 1283 | 144 | False | PROTOTYPE SAMPLE 01, Backend Developer (fictional). Skills: Python, FastAPI, PostgreSQL. Experience: 3 years building REST APIs. Contact: [EMAIL], [NO |
| DOC-02.pdf | pymupdf | 14.7 | 1236 | 132 | False | PROTOTYPE SAMPLE 02, Frontend Developer (fictional). Skills: JavaScript, React, CSS. Experience: 2 years building dashboards. Contact: [EMAIL], [NO_HP |
| DOC-02.pdf | pdfplumber | 228.0 | 1235 | 132 | False | PROTOTYPE SAMPLE 02, Frontend Developer (fictional). Skills: JavaScript, React, CSS. Experience: 2 years building dashboards. Contact: [EMAIL], [NO_HP |
| DOC-03.pdf | pymupdf | 13.7 | 1164 | 132 | False | PROTOTYPE SAMPLE 03, Data Analyst (fictional). Skills: SQL, Python, Data Analysis. Experience: 1 year reporting. Contact: [EMAIL], [NO_HP]. Education: |
| DOC-03.pdf | pdfplumber | 153.5 | 1163 | 132 | False | PROTOTYPE SAMPLE 03, Data Analyst (fictional). Skills: SQL, Python, Data Analysis. Experience: 1 year reporting. Contact: [EMAIL], [NO_HP]. Education: |
| DOC-04.pdf | pymupdf | 9.6 | 1128 | 126 | False | PROTOTYPE SAMPLE 04, QA Engineer (fictional). Skills: State Management, Time Management, REST API testing. Contact: [EMAIL], [NO_HP]. Education: BSc E |
| DOC-04.pdf | pdfplumber | 84.1 | 1127 | 126 | False | PROTOTYPE SAMPLE 04, QA Engineer (fictional). Skills: State Management, Time Management, REST API testing. Contact: [EMAIL], [NO_HP]. Education: BSc E |

**Ringkasan:**

- pymupdf: rata-rata 14.1 ms/file, rata-rata 1203 karakter/file, kosong/gagal 0/4.
- pdfplumber: rata-rata 194.8 ms/file, rata-rata 1202 karakter/file, kosong/gagal 0/4.

## Eksperimen B — Token Sort Ratio

| A | B | M | T | TSR_manual | token_sort_ratio | sama | lolos_85 |
|---|---|---:|---:|---:|---:|:---:|:---:|
| water | wayer | 4 | 10 | 80.00 | 80 | True | False |
| Web Frontend | Frontend Web | 12 | 24 | 100.00 | 100 | True | True |
| Python | Python | 6 | 12 | 100.00 | 100 | True | True |
| SQL | MySQL | 3 | 8 | 75.00 | 75 | True | False |
| Data Analysis | Data Analytics | 12 | 27 | 88.89 | 89 | True | True |
| REST API | RESTful APIs | 8 | 20 | 80.00 | 80 | True | False |
| Time Management | State Management | 13 | 31 | 83.87 | 84 | True | False |

## Kesimpulan singkat

Pustaka tercepat rata-rata: pymupdf; cakupan teks terbanyak rata-rata: pymupdf. Formula TSR manual konsisten dengan pustaka (7/7 pasangan sama setelah pembulatan); perbedaan sisa berasal dari normalisasi bawaan pustaka (lowercase/pembersihan non-alfanumerik) yang tidak ditiru manual.
