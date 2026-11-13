"""Draw the revised Fig. 9 objective-bound comparison from its 120-case CSV.

Six shared-axis panels, zero baseline, colored boxes, red seed points, and
zoom insets retain the six-panel layout used in the reviewer response.
Black intervals on main panels identify nine one-hour ExactLHS time limits.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

plt.style.use('default')
plt.rcParams.update({
    'font.size': 16, 'font.family': 'serif',
    'font.serif': ['STIXGeneral', 'Times New Roman', 'serif'],
    'mathtext.fontset': 'stix', 'axes.linewidth': .8,
    'grid.linewidth': .8, 'xtick.direction': 'out', 'ytick.direction': 'out',
})
here = Path(__file__).resolve().parent
rows = list(csv.DictReader((here.parent / 'figure_table_data' / 'fig9_exactlhs_120_cases.csv').open(newline='')))
assert len(rows) == 120 and sum(r['status'] == '60min_time_limit' for r in rows) == 9
out_pdf = here / 'figures' / 'Fig9.pdf'
ns, sfs, epss = [30, 60, 90, 120], [1., 1.5, 2.], [.03, .06]
seeds = [0, 100, 200, 300, 400]
colors = ['#E68685', '#9986B1', '#F3983C', '#6DAB81']
upper_all = max(float(r['difference_upper_pct']) for r in rows)
ytop = upper_all + .11

def draw(ax, panel, zoom=False):
    for k, n in enumerate(ns):
        group = sorted((r for r in panel if int(r['N']) == n), key=lambda r: int(r['seed']))
        assert [int(r['seed']) for r in group] == seeds
        vals = [float(r['observed_difference_pct']) for r in group]
        box = ax.boxplot(vals, positions=[k], widths=.6, patch_artist=True,
                         showfliers=False,
                         medianprops={'color': '#303030', 'linewidth': 2},
                         whiskerprops={'color': '#666666', 'linewidth': 1.4},
                         capprops={'color': '#666666', 'linewidth': 1.4})
        box['boxes'][0].set(facecolor=colors[k], edgecolor='#555555', alpha=.82)
        for h, r in enumerate(group):
            x = k + (h-2)*.09
            low = float(r['difference_lower_pct'])
            high = float(r['difference_upper_pct'])
            if not zoom and r['status'] == '60min_time_limit':
                ax.plot([x, x], [low, high], color='#202020', lw=2, zorder=5)
                for y in [low, high]:
                    ax.plot([x-.035, x+.035], [y, y], color='#202020', lw=2, zorder=5)
            limited = r['status'] == '60min_time_limit'
            ax.plot(x, low, 'D' if limited else 'o', markersize=5 if zoom else 6,
                    markerfacecolor='#c52227' if limited else 'white',
                    markeredgecolor='#202020' if limited else '#c52227',
                    markeredgewidth=1.2 if limited else 1.5, zorder=6)
    ax.set_xlim(-.55, 3.55)
    ax.set_xticks(range(4), [str(n) for n in ns])
    ax.grid(True, ls='--', lw=.8, alpha=.4)
    ax.set_axisbelow(True)
    for name in ('top', 'right'):
        ax.spines[name].set_visible(False)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

fig, axes = plt.subplots(3, 2, figsize=(10, 11.49), sharex=True, sharey=True)
for i, sf in enumerate(sfs):
    for j, eps in enumerate(epss):
        ax = axes[i, j]
        panel = [r for r in rows if float(r['sf']) == sf and float(r['epsilon']) == eps]
        draw(ax, panel)
        ax.axhline(0, color='#2F4B7C', lw=2, zorder=1)
        ax.set_ylim(-.04, ytop)
        ax.yaxis.set_major_locator(MaxNLocator(6))
        ax.set_title(rf'$\boldsymbol{{SF}}={sf:g},\ \boldsymbol{{\epsilon}}={eps:.2f}$',
                     fontsize=20, fontweight='bold', fontstyle='italic', pad=7)
        ax.set_ylabel('Obj. Diff. (%)' if j == 0 else '',
                      fontsize=16, fontweight='bold', fontstyle='italic')
        ax.set_xlabel(r'$\boldsymbol{N}$ (Sample Size)' if i == 2 else '',
                      fontsize=16, fontweight='bold', fontstyle='italic')
        ax.tick_params(labelsize=16, width=.8, labelbottom=True)
        pmin = min(float(r['observed_difference_pct']) for r in panel)
        pmax = max(float(r['observed_difference_pct']) for r in panel)
        zpad = max((pmax-pmin)*.35, .006)
        y0 = .15 if (pmin+pmax)/2 > (-.04+ytop)/2 else .55
        # Keep every recorded one-hour interval unobscured in the main panel.
        if (sf, eps) == (1.0, .06):
            inset_x, inset_width = .12, .43
        elif (sf, eps) == (2.0, .03):
            inset_x, inset_width = .20, .55
        else:
            inset_x, inset_width = .42, .55
        if (i, j) in {(0, 1), (2, 0)}:
            inset_y, inset_height = y0 + .075, .365
        elif (i, j) == (1, 0):
            inset_y, inset_height = .11, .28
        else:
            inset_y, inset_height = y0, .40
        inset = ax.inset_axes([inset_x, inset_y, inset_width, inset_height])
        draw(inset, panel, zoom=True)
        inset.set_ylim(pmin-zpad, pmax+zpad)
        inset.yaxis.set_major_locator(MaxNLocator(4))
        inset.tick_params(labelsize=11, width=.8)
        for label in inset.get_xticklabels() + inset.get_yticklabels():
            label.set_fontweight('bold')
        for spine in inset.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('#888888')
        ax.indicate_inset_zoom(inset, edgecolor='#888888', alpha=.7, linewidth=1)
fig.subplots_adjust(left=.10, right=.98, top=.97, bottom=.065, wspace=.08, hspace=.30)
fig.savefig(out_pdf, dpi=300, bbox_inches='tight')
print(out_pdf)
