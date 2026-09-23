#!/usr/bin/env python3
"""Throwaway prototype: PDF extraction (PyMuPDF vs pdfplumber) + manual TSR check.

Standalone. No imports from production code (backend/app, frontend, etc.).
Conceptually built BEFORE production system (Bab III 3.4).

Usage:
    python experiment_extraction_tsr.py --pdf-dir /path/to/sample/pdfs
    python experiment_extraction_tsr.py --pdf-dir /path/to/pdfs --output hasil_eksperimen.md

Deps (see requirements.txt): pymupdf, pdfplumber, fuzzywuzzy (+ python-Levenshtein).
"""

import argparse
import difflib
import os
import re
import sys
import time

THRESHOLD = 85


def mask_pii(text):
    """Replace email and phone patterns. Never print real PII."""
    masked = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[EMAIL]", text)
    masked = re.sub(r"(\+62|\+1|08)[\d\s\-\(\)]{7,16}", "[NO_HP]", masked)
    # generic long digit runs (likely phone/ID) -> mask, keep short years
    masked = re.sub(r"\b\d{9,16}\b", "[NO_HP]", masked)
    return masked


def extract_pymupdf(path):
    import fitz

    t0 = time.perf_counter()
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text("text") or ""
    dt_ms = (time.perf_counter() - t0) * 1000.0
    return text, dt_ms


def extract_pdfplumber(path):
    import pdfplumber

    t0 = time.perf_counter()
    chunks = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            chunks.append(page.extract_text() or "")
    dt_ms = (time.perf_counter() - t0) * 1000.0
    return "\n".join(chunks), dt_ms


def run_experiment_a(pdf_dir):
    files = sorted(
        f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")
    )
    # Anonymize: never expose original filenames (may contain real names).
    # Output uses DOC-NN ids in sorted order; mapping is not stored.
    rows = []
    for i, fname in enumerate(files, start=1):
        file_id = "DOC-%02d.pdf" % i
        path = os.path.join(pdf_dir, fname)
        for lib, fn in (("pymupdf", extract_pymupdf), ("pdfplumber", extract_pdfplumber)):
            try:
                text, ms = fn(path)
                n_chars = len(text)
                n_words = len(text.split())
                is_empty = (n_chars == 0)
                snippet = mask_pii(text[:500].replace("\n", " "))[:150]
                rows.append(
                    {
                        "file": file_id,
                        "lib": lib,
                        "ms": ms,
                        "chars": n_chars,
                        "words": n_words,
                        "empty": is_empty,
                        "snippet": snippet,
                        "error": "",
                    }
                )
            except Exception as exc:  # prototype: keep runnable, record failure
                rows.append(
                    {
                        "file": file_id,
                        "lib": lib,
                        "ms": 0.0,
                        "chars": 0,
                        "words": 0,
                        "empty": True,
                        "snippet": "",
                        "error": type(exc).__name__,
                    }
                )
    return rows


def tsr_manual(a, b):
    """TSR = (2M / T) x 100.

    Steps per spec: split into tokens, sort alphabetically,
    rejoin, then M = total length of sequential matching blocks
    via difflib.SequenceMatcher, T = combined length.
    """
    ta = sorted(a.lower().split())
    tb = sorted(b.lower().split())
    sa = " ".join(ta)
    sb = " ".join(tb)
    matcher = difflib.SequenceMatcher(None, sa, sb)
    m = sum(block.size for block in matcher.get_matching_blocks())
    t = len(sa) + len(sb)
    score = (2 * m / t * 100.0) if t > 0 else 0.0
    return sa, sb, m, t, score


PAIRS = [
    ("water", "wayer"),  # Bab II example, expect 80
    ("Web Frontend", "Frontend Web"),
    ("Python", "Python"),
    ("SQL", "MySQL"),
    ("Data Analysis", "Data Analytics"),
    ("REST API", "RESTful APIs"),
    ("Time Management", "State Management"),
]


def run_experiment_b():
    from fuzzywuzzy import fuzz

    rows = []
    for a, b in PAIRS:
        sa, sb, m, t, manual = tsr_manual(a, b)
        lib_score = fuzz.token_sort_ratio(a, b)
        same = int(round(manual)) == int(lib_score)
        passed = lib_score >= THRESHOLD
        rows.append(
            {
                "a": a,
                "b": b,
                "sorted_a": sa,
                "sorted_b": sb,
                "M": m,
                "T": t,
                "manual": manual,
                "lib": lib_score,
                "same": same,
                "passed": passed,
            }
        )
    return rows


def print_table_a(rows):
    print("\n=== Eksperimen A: Ekstraksi PDF (PyMuPDF vs pdfplumber) ===")
    print(f"{'file':28s} {'lib':10s} {'ms':>9s} {'chars':>7s} {'words':>7s} {'empty':>6s} snippet(150)")
    print("-" * 120)
    for r in rows:
        print(
            f"{r['file'][:28]:28s} {r['lib']:10s} {r['ms']:9.1f} "
            f"{r['chars']:7d} {r['words']:7d} {str(r['empty']):>6s} {r['snippet']}"
        )


def print_table_b(rows):
    print("\n=== Eksperimen B: Token Sort Ratio manual vs FuzzyWuzzy ===")
    print(f"{'A vs B':34s} {'M':>4s} {'T':>5s} {'manual':>8s} {'lib':>5s} {'sama':>5s} {'lolos>=85':>9s}")
    print("-" * 100)
    for r in rows:
        pair = f"{r['a']} vs {r['b']}"[:34]
        print(
            f"{pair:34s} {r['M']:4d} {r['T']:5d} {r['manual']:8.2f} "
            f"{r['lib']:5d} {str(r['same']):>5s} {str(r['passed']):>9s}"
        )


def summarize_a(rows):
    out = {}
    for lib in ("pymupdf", "pdfplumber"):
        sub = [r for r in rows if r["lib"] == lib]
        if not sub:
            out[lib] = {"avg_ms": 0.0, "avg_chars": 0.0, "n_empty": 0, "n": 0}
            continue
        out[lib] = {
            "avg_ms": sum(r["ms"] for r in sub) / len(sub),
            "avg_chars": sum(r["chars"] for r in sub) / len(sub),
            "n_empty": sum(1 for r in sub if r["empty"]),
            "n": len(sub),
        }
    return out


def write_markdown(path, rows_a, rows_b, summary):
    n_same = sum(1 for r in rows_b if r["same"])
    faster = min(summary, key=lambda k: summary[k]["avg_ms"]) if rows_a else "-"
    fuller = max(summary, key=lambda k: summary[k]["avg_chars"]) if rows_a else "-"
    consistent = "konsisten" if rows_b and n_same == len(rows_b) else "sebagian berbeda"

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Hasil Eksperimen Prototipe (Throwaway)\n\n")
        f.write("> Prototipe pra-produksi. File PDF sampel milik penguji, bukan data riil.\n")
        f.write("> Cuplikan teks disamarkan ([EMAIL]/[NO_HP]).\n\n")
        f.write("## Eksperimen A — Ekstraksi PDF\n\n")
        f.write("| file | pustaka | waktu_ms | karakter | kata | kosong | cuplikan_150 |\n")
        f.write("|---|---|---:|---:|---:|:---:|---|\n")
        for r in rows_a:
            snip = r["snippet"].replace("|", "/").replace("\n", " ")
            f.write(
                f"| {r['file']} | {r['lib']} | {r['ms']:.1f} | "
                f"{r['chars']} | {r['words']} | {r['empty']} | {snip} |\n"
            )
        f.write("\n**Ringkasan:**\n\n")
        for lib, s in summary.items():
            f.write(
                f"- {lib}: rata-rata {s['avg_ms']:.1f} ms/file, "
                f"rata-rata {s['avg_chars']:.0f} karakter/file, "
                f"kosong/gagal {s['n_empty']}/{s['n']}.\n"
            )
        f.write("\n## Eksperimen B — Token Sort Ratio\n\n")
        f.write("| A | B | M | T | TSR_manual | token_sort_ratio | sama | lolos_85 |\n")
        f.write("|---|---|---:|---:|---:|---:|:---:|:---:|\n")
        for r in rows_b:
            f.write(
                f"| {r['a']} | {r['b']} | {r['M']} | {r['T']} | "
                f"{r['manual']:.2f} | {r['lib']} | {r['same']} | {r['passed']} |\n"
            )
        f.write("\n## Kesimpulan singkat\n\n")
        f.write(
            f"Pustaka tercepat rata-rata: {faster}; cakupan teks terbanyak rata-rata: {fuller}. "
            f"Formula TSR manual {consistent} dengan pustaka "
            f"({n_same}/{len(rows_b)} pasangan sama setelah pembulatan); "
            f"perbedaan sisa berasal dari normalisasi bawaan pustaka "
            f"(lowercase/pembersihan non-alfanumerik) yang tidak ditiru manual.\n"
        )
    return faster, fuller, consistent


def main():
    ap = argparse.ArgumentParser(description="Prototype experiment: PDF extraction + TSR")
    ap.add_argument("--pdf-dir", required=True, help="folder berisi PDF sampel uji coba")
    ap.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hasil_eksperimen.md"),
        help="path file markdown keluaran",
    )
    args = ap.parse_args()

    if not os.path.isdir(args.pdf_dir):
        print(f"ERROR: --pdf-dir tidak ditemukan: {args.pdf_dir}", file=sys.stderr)
        sys.exit(2)

    rows_a = run_experiment_a(args.pdf_dir)
    rows_b = run_experiment_b()

    print_table_a(rows_a)
    print_table_b(rows_b)

    summary = summarize_a(rows_a)
    print("\n--- Ringkasan A ---")
    for lib, s in summary.items():
        print(f"{lib}: avg {s['avg_ms']:.1f} ms, avg {s['avg_chars']:.0f} chars, kosong {s['n_empty']}/{s['n']}")
    print(f"\nB: {sum(1 for r in rows_b if r['same'])}/{len(rows_b)} pasangan manual==pustaka (setelah dibulatkan).")

    write_markdown(args.output, rows_a, rows_b, summary)
    print(f"\nHasil disimpan: {args.output}")


if __name__ == "__main__":
    main()
