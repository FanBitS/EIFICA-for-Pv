"""Extract the original manuscript's main figure grid and Table 1 source rows."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "master_summary_20260708_110917.csv"
OUT = ROOT / "figure_table_data"
OUT.mkdir(exist_ok=True)

with SOURCE.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames
    rows = list(reader)

assert fields is not None

main = [row for row in rows if row["method"] in {"FICA", "EIFICA"}]
assert len(main) == 1680
assert {int(row["seed"]) for row in main} == set(range(10))

table1 = [
    row for row in rows
    if row["network"] == "case24_ieee_rts"
    and row["method"] in {"CVAR", "EIFICA"}
    and row["N_WDR"] in {"50", "80"}
    and int(row["seed"]) in range(5)
]
assert len(table1) == 120
assert sum(row["method"] == "CVAR" for row in table1) == 40
assert sum(row["method"] == "EIFICA" and row["eifica_mode"] == "one-shot" for row in table1) == 40
assert sum(row["method"] == "EIFICA" and row["eifica_mode"] == "iterative" for row in table1) == 40

for name, selected in (
    ("figures_3_to_8_main_grid_10seeds.csv", main),
    ("table_1_rts24_5seeds.csv", table1),
):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)
    print(f"{path.relative_to(ROOT)}: {len(selected)} rows")
