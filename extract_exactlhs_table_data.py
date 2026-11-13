"""Extract the manuscript's ExactLHS Table 2 from Fig. 9 case data."""

import csv
from collections import Counter
from pathlib import Path


root = Path(__file__).resolve().parent
data = root / "figure_table_data"
with (data / "fig9_exactlhs_120_cases.csv").open(newline="") as source:
    cases = list(csv.DictReader(source))

assert len(cases) == 120
hour_cases = sorted(
    (case for case in cases if case["final_stage"] == "60min"),
    key=lambda case: (float(case["sf"]), float(case["epsilon"]), int(case["N"]), int(case["seed"])),
)
assert Counter(case["status"] for case in hour_cases) == {
    "60min_time_limit": 9,
    "60min_tolerance": 1,
}
table_rows = []
for case in hour_cases:
    lower = float(case["exactlhs_lower_bound"])
    upper = float(case["exactlhs_incumbent"])
    table_rows.append({
        "sf": f'{float(case["sf"]):g}',
        "epsilon": f'{float(case["epsilon"]):.2f}',
        "N": case["N"],
        "seed": case["seed"],
        "status": "TL" if case["status"] == "60min_time_limit" else "Tol.",
        "L_usd": case["exactlhs_lower_bound"],
        "U_usd": case["exactlhs_incumbent"],
        "gap_pct": 100 * (upper - lower) / abs(upper),
        "difference_lower_pct": case["difference_lower_pct"],
        "difference_upper_pct": case["difference_upper_pct"],
    })

target_path = data / "table_2_exactlhs_10_retries.csv"
with target_path.open("w", newline="") as target:
    writer = csv.DictWriter(target, fieldnames=table_rows[0].keys())
    writer.writeheader()
    writer.writerows(table_rows)
print(f"{target_path}: {len(table_rows)} rows")
