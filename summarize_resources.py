"""Summarize archived per-process memory records for reproduction planning."""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'figure_table_data'
groups = defaultdict(list)

with (DATA / 'figures_3_to_8_main_grid_10seeds.csv').open(newline='') as handle:
    for row in csv.DictReader(handle):
        n = int(row['N_WDR'])
        if n not in {50, 150, 300}:
            continue
        method = row['method']
        if method == 'EIFICA':
            method = 'Direct EIFICA' if row['eifica_mode'] == 'one-shot' else 'Iterative EIFICA'
        network = 'RTS-24' if row['network'] == 'case24_ieee_rts' else 'IEEE-118'
        groups[(network, n, method)].append(float(row['peak_rss_mb']) / 1024)

with (DATA / 'table1_cvar_80_cases.csv').open(newline='') as handle:
    for row in csv.DictReader(handle):
        groups[('RTS-24', int(row['N']), 'CVaR')].append(float(row['rss_mib']) / 1024)

summary = []
for (network, n, method), values in sorted(groups.items()):
    assert len(values) == 40
    summary.append(dict(network=network, N=n, method=method, cases=len(values),
                        median_sampled_max_rss_GiB=median(values),
                        largest_sampled_max_rss_GiB=max(values)))

path = DATA / 'resource_memory_summary.csv'
with path.open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(summary)
print(f'{path.relative_to(ROOT)}: {len(summary)} groups, 40 cases per group')
