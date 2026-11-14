"""Extract the ten-seed figure grid and both current manuscript tables."""

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figure_table_data'


def read(name):
    with (ROOT / name).open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write(name, fields, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(f'{name}: {len(rows)} rows')


def case_key(row):
    return float(row['epsilon']), float(row['theta']), int(row['N_WDR']), int(row['seed'])


fields, rows = read('master_summary_20260708_110917.csv')
main = [row for row in rows if row['method'] in {'FICA', 'EIFICA'}]
assert len(main) == 1680
assert {int(row['seed']) for row in main} == set(range(10))
write('figures_3_to_8_main_grid_10seeds.csv', fields, main)

eifica = [row.copy() for row in main if row['network'] == 'case24_ieee_rts'
          and row['method'] == 'EIFICA' and int(row['N_WDR']) in {50, 80}]
_, cvar = read('figure_table_data/table1_cvar_80_cases.csv')
assert len(cvar) == 80
assert len({(float(r['epsilon']), float(r['theta']), int(r['N']), int(r['seed'])) for r in cvar}) == 80
original = {case_key(r): r for r in rows if r['method'] == 'CVAR' and int(r['seed']) < 5}
for row in cvar:
    key = float(row['epsilon']), float(row['theta']), int(row['N']), int(row['seed'])
    if key in original:
        old = original[key]
        for new_field, old_field in [('cost', 'min_cost'), ('reliability', 'reliability_pct'),
                                     ('time', 't_solve_s'), ('rss_mib', 'peak_rss_mb')]:
            assert abs(float(row[new_field]) - float(old[old_field])) < 1e-7
    eifica.append(dict.fromkeys(fields, '') | {
        'network': 'case24_ieee_rts', 'method': 'CVAR', 'eifica_mode': 'iterative',
        'epsilon': row['epsilon'], 'theta': row['theta'], 'N_WDR': row['N'],
        'seed': row['seed'], 'num_gen': '38', 'num_Solar': '5', 'T': '24',
        'min_cost': row['cost'], 'reliability_pct': row['reliability'],
        't_solve_s': row['time'], 'peak_rss_mb': row['rss_mib'],
        'source_dir': row['source']})
assert len(eifica) == 240
assert len({(r['method'], r['eifica_mode'], *case_key(r)) for r in eifica}) == 240
write('table_1_rts24_10seeds.csv', fields, sorted(eifica, key=lambda r: (*case_key(r), r['method'], r['eifica_mode'])))

groups = defaultdict(list)
for row in eifica:
    name = 'CVaR' if row['method'] == 'CVAR' else ('Direct EIFICA' if row['eifica_mode'] == 'one-shot' else 'Iterative EIFICA')
    groups[(float(row['epsilon']), float(row['theta']), int(row['N_WDR']), name)].append(row)
summary = []
order = {'CVaR': 0, 'Direct EIFICA': 1, 'Iterative EIFICA': 2}
for (eps, theta, n, name), group in sorted(groups.items(), key=lambda x: (*x[0][:3], order[x[0][3]])):
    assert len(group) == 10 and {int(r['seed']) for r in group} == set(range(10))
    rss_mib = median(float(r['peak_rss_mb']) for r in group)
    summary.append(dict(epsilon=eps, theta=theta, N=n, method=name, seeds=10,
        scheduled_cost_usd=median(float(r['min_cost']) for r in group),
        joint_satisfaction_pct=median(float(r['reliability_pct']) for r in group),
        runtime_s=median(float(r['t_solve_s']) for r in group),
        sampled_max_rss_GB=rss_mib * 1048576 / 1e9, sampled_max_rss_GiB=rss_mib / 1024))
write('Table1.csv', list(summary[0]), summary)

_, days = read('figure_table_data/table2_historical_validation_days.csv')
groups = defaultdict(list)
for row in days:
    groups[(int(row['N']), float(row['theta']))].append(row)
validation = []
for (n, theta), group in sorted(groups.items()):
    assert len(group) == 45 and len({r['date'] for r in group}) == 45
    validation.append(dict(N=n, epsilon=.08, theta=theta, days=45,
        passing_days=sum(r['operating_pass'] == 'True' for r in group),
        mean_scheduled_cost_usd=mean(float(r['objective_usd']) for r in group if r['status'] == 'audited'),
        selected=n == 250 and theta == .03, exploratory_extension=n in {300, 350}))
assert len(validation) == 15
write('Table2.csv', list(validation[0]), validation)
