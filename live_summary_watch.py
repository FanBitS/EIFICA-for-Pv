# -*- coding: utf-8 -*-
import argparse
import csv
import os
import time

from paper_eval import SUMMARY_FIELDS, _row_from_npy


def load_seen(csv_path):
    if not os.path.exists(csv_path):
        return set()
    seen = set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fn = row.get("file")
            if fn:
                seen.add(fn)
    return seen


def ensure_header(csv_path):
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        return
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=SUMMARY_FIELDS).writeheader()


def append_rows(csv_path, rows):
    if not rows:
        return
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        for row in rows:
            writer.writerow(row)


def scan_once(out_dir, csv_path, seen):
    rows = []
    for fn in sorted(os.listdir(out_dir)):
        if not (fn.startswith("result_") and fn.endswith(".npy")):
            continue
        if fn in seen:
            continue
        try:
            row = _row_from_npy(out_dir, fn)
        except Exception as exc:
            print(f"[live-summary] skip unreadable {fn}: {type(exc).__name__}: {exc}", flush=True)
            continue
        rows.append(row)
        seen.add(fn)
    append_rows(csv_path, rows)
    if rows:
        print(f"[live-summary] appended {len(rows)} row(s); total={len(seen)} -> {csv_path}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Append live paper_eval summary rows as .npy files complete.")
    parser.add_argument("out_dir", help="paper_eval output directory, e.g. Solar_c118_speed")
    parser.add_argument("--csv", default=None, help="CSV path; default: <out_dir>/live_summary.csv")
    parser.add_argument("--interval", type=float, default=30.0, help="scan interval seconds")
    args = parser.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    csv_path = os.path.abspath(args.csv or os.path.join(out_dir, "live_summary.csv"))
    os.makedirs(out_dir, exist_ok=True)
    ensure_header(csv_path)
    seen = load_seen(csv_path)
    print(f"[live-summary] watching {out_dir}", flush=True)
    print(f"[live-summary] csv {csv_path}; already_seen={len(seen)}", flush=True)

    while True:
        scan_once(out_dir, csv_path, seen)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
