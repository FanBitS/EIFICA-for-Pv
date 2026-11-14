#!/usr/bin/env python3
"""Render the saved N=300 dispatch in the original Figure 2 plotting style."""
from pathlib import Path
import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parents[1] / 'figure_table_data' / 'fig2'
OUTPUT = Path(__file__).resolve().parents[1] / 'figure' / 'test'
plt.style.use('default')
plt.rcParams.update({
    'font.size':16, 'font.family':'serif',
    'font.serif':['STIXGeneral','Times New Roman','serif'],
    'legend.fontsize':12, 'xtick.labelsize':16, 'ytick.labelsize':16,
    'axes.linewidth':0.8,'grid.linewidth':0.8,'lines.linewidth':2.5,
    'mathtext.fontset':'stix',
})

def plot_paper(num_gen, gen_power_all, gen_alpha_all, gen_cap_individual, gen_pmin_individual, WT_pred,
                  WT_error_scenarios_test, method, epsilon, theta, network_name, T, gen_cost,
                  Solar_pred=None, Solar_error_scenarios_test=None, gen_ramp_rate=None):
    alpha_std = np.std(gen_alpha_all, axis=0)
    plot_gen_index = np.argsort(alpha_std)[-2:][::-1]
    print(f"\n=== Plotting Generators with Highest AGC Variation ===")
    print(f"Selected: Gen {plot_gen_index[0]} (std={alpha_std[plot_gen_index[0]]:.6f}), Gen {plot_gen_index[1]} (std={alpha_std[plot_gen_index[1]]:.6f})")

    num_plot_sce = 1
    scenario_set = np.array([0])

    print(f"\n=== Saved Selected Trajectory ===")
    sce_i = scenario_set[0]
    print(f"Saved trajectory row: {sce_i}")

    wt_error = WT_error_scenarios_test.sum(axis=-1)[sce_i]
    print(f"WT error in this scenario: mean={wt_error.mean():.4f}, std={wt_error.std():.4f}, range=[{wt_error.min():.4f}, {wt_error.max():.4f}]")

    total_error = wt_error
    if Solar_error_scenarios_test is not None:
        solar_error = Solar_error_scenarios_test.sum(axis=-1)[sce_i]
        print(f"Solar error in this scenario: mean={solar_error.mean():.4f}, std={solar_error.std():.4f}, range=[{solar_error.min():.4f}, {solar_error.max():.4f}]")
        total_error = total_error + solar_error
    print(f"Total RE error in this scenario: mean={total_error.mean():.4f}, std={total_error.std():.4f}, range=[{total_error.min():.4f}, {total_error.max():.4f}]")


    alpha_abs_sum = np.abs(gen_alpha_all).sum(axis=0)
    alpha_std_all = np.std(gen_alpha_all, axis=0)
    non_zero_gens = np.where(alpha_abs_sum > 1e-6)[0]

    top_std_gens = np.argsort(alpha_std_all)[-10:][::-1]


    num_rows = 0
    if Solar_pred is not None:
        num_rows += 1
    num_rows += len(plot_gen_index) * 3

    fig, axs = plt.subplots(num_rows, num_plot_sce, figsize=(10*num_plot_sce, 2.52 * num_rows))
    if num_plot_sce <= 1:
        axs = axs[..., None]

    title_kw = dict(fontsize=20, fontweight='bold', fontstyle='italic')
    label_kw = dict(fontsize=16, fontweight='bold', fontstyle='italic')
    legend_kw = dict(prop={'family': 'STIXGeneral', 'size': 12,
                           'weight': 'bold', 'style': 'italic'})

    def style_dispatch_axis(ax, grid_alpha=0.3):
        ax.tick_params(axis='both', which='major', labelsize=16, width=0.8)
        plt.setp(ax.get_xticklabels(), fontweight='bold')
        plt.setp(ax.get_yticklabels(), fontweight='bold')
        ax.grid(True, linestyle='--', alpha=grid_alpha, linewidth=0.8)

    row_idx = 0


    if Solar_pred is not None and Solar_error_scenarios_test is not None:
        for i in range(num_plot_sce):
            sce_i = scenario_set[i]
            ax_s = axs[row_idx, i]
            x = np.arange(T)
            ax_s.step(x, Solar_pred.sum(axis=-1), label='forecast', where='post', linewidth=2.5)
            ax_s.step(x, Solar_pred.sum(axis=-1) + Solar_error_scenarios_test.sum(axis=-1)[sce_i],
                      label='actual', where='post', linewidth=2.5)
            ax_s.set_title(f'Solar Farm', **title_kw)
            ax_s.set_ylabel('Solar (MW)', **label_kw)
            ax_s.set_xlim(-0.5, T-0.5)
            ax_s.set_xticks(np.arange(T))
            ax_s.set_xticklabels(np.arange(T))
            style_dispatch_axis(ax_s)
            ax_s.legend(**legend_kw)
        row_idx += 1
    gen_start_row = row_idx
    for i in range(num_plot_sce):
        sce_i = scenario_set[i]
        for ig, g in enumerate(plot_gen_index):
            ax = axs[gen_start_row + ig*3, i]
            x = np.arange(T)
            ax.step(x, gen_power_all[:, g], label='Scheduled', where='post', linewidth=2.5)
            total_RE_error_test = WT_error_scenarios_test.sum(axis=-1)[sce_i]
            if Solar_error_scenarios_test is not None:
                total_RE_error_test = total_RE_error_test + Solar_error_scenarios_test.sum(axis=-1)[sce_i]
            ax.step(x, gen_power_all[:, g] - gen_alpha_all[:, g] * total_RE_error_test,
                    label='actual', where='post', linewidth=2.5)
            ax.set_title(f'Gen {g}, Cost {gen_cost[g]:.2f} USD/MWh', **title_kw)
            ax.set_ylabel(f'Gen (MW)', **label_kw)
            ax.axhline(gen_pmin_individual[g], color='black', linestyle='--', linewidth=2.0)
            ax.axhline(gen_cap_individual[g], color='black', linestyle='--', linewidth=2.0)
            ax.set_xlim(-0.5, T-0.5)
            ax.set_xticks(np.arange(T))
            ax.set_xticklabels(np.arange(T))
            style_dispatch_axis(ax)
            ax.legend(**legend_kw)

    for i in range(num_plot_sce):
        sce_i = scenario_set[i]
        for ig, g in enumerate(plot_gen_index):
            ax = axs[gen_start_row + ig*3 + 1, i]
            x = np.arange(T) + 0.5
            ax.bar(x, gen_alpha_all[:, g], width=0.8, label='AGC', color='violet', align='center')
            ax.set_title(f'Gen {g} AGC Factor', **title_kw)
            ax.set_ylabel('AGC Factor', **label_kw)
            ax.set_ylim(-1, 1)
            ax.set_xlim(-0.5, T-0.5)
            ax.set_xticks(np.arange(T))
            ax.set_xticklabels(np.arange(T))
            style_dispatch_axis(ax, grid_alpha=0.5)
            ax.legend(**legend_kw)

    for i in range(num_plot_sce):
        sce_i = scenario_set[i]
        total_RE_error_test = WT_error_scenarios_test.sum(axis=-1)[sce_i]
        if Solar_error_scenarios_test is not None:
            total_RE_error_test = total_RE_error_test + Solar_error_scenarios_test.sum(axis=-1)[sce_i]

        for ig, g in enumerate(plot_gen_index):
            ax = axs[gen_start_row + ig*3 + 2, i]

            first_stage_ramp = np.diff(gen_power_all[:, g])

            actual_power = gen_power_all[:, g] - gen_alpha_all[:, g] * total_RE_error_test
            second_stage_ramp = np.diff(actual_power)

            x = np.arange(1, T) + 0.5

            width = 0.35
            ax.bar(x - width/2, first_stage_ramp, width, label='Scheduled', color='steelblue', alpha=0.7)
            ax.bar(x + width/2, second_stage_ramp, width, label='Actual', color='darkorange', alpha=0.7)

            ramp_limit = gen_ramp_rate[g] if gen_ramp_rate is not None else gen_cap_individual[g]
            ax.axhline(ramp_limit, color='red', linestyle='--', linewidth=2.0,
                       label=f'Limit (\u00b1{ramp_limit:.1f} MW)')
            ax.axhline(-ramp_limit, color='red', linestyle='--', linewidth=2.0)

            ax.set_ylim(-ramp_limit * 1.2, ramp_limit * 1.2)

            ax.set_title(f'Gen {g} Ramping', **title_kw)
            ax.set_ylabel('Ramp (MW/h)', **label_kw)
            ax.set_xlim(-0.5, T-0.5)
            ax.set_xticks(np.arange(0, T))
            ax.set_xticklabels(np.arange(0, T))
            if gen_start_row + ig*3 + 2 == num_rows - 1:
                ax.set_xlabel('Hour', **label_kw)
            style_dispatch_axis(ax, grid_alpha=0.5)
            ax.legend(loc='upper left', bbox_to_anchor=(0.0, 0.85), **legend_kw)

    plt.subplots_adjust(left=0.08, right=0.95, top=0.97, bottom=0.03, hspace=0.35, wspace=0.3)
    save_dir = str(OUTPUT)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_name = os.path.join(save_dir, 'Fig2.pdf')
    plt.savefig(save_name, dpi=300)
    plt.close(fig)

if __name__ == '__main__':
    data = np.load(HERE/'plot_data.npz')
    metadata = json.loads((HERE/'provenance.json').read_text())
    assert np.array_equal(np.argsort(np.std(data['gen_alpha_all'],axis=0))[-2:][::-1],data['selected_generators'])
    actual_power=data['gen_power_all']-data['gen_alpha_all']*data['total_error'][:,None]
    selected=data['selected_generators']
    actual_ramps=np.diff(actual_power[:,selected],axis=0)
    limits=data['gen_ramp_rate'][selected]
    assert np.all(np.abs(actual_ramps)<=1.2*limits), 'Original ramp y limits would clip the candidate trajectory'
    plot_paper(38,data['gen_power_all'],data['gen_alpha_all'],data['gen_cap_individual'],
               data['gen_pmin_individual'],np.zeros((24,1)),np.zeros((1,24,1)),
               'EIFICA',.03,.06,'case24_ieee_rts',24,data['gen_cost'],
               Solar_pred=data['solar_forecast'][:,None],
               Solar_error_scenarios_test=(data['solar_actual']-data['solar_forecast'])[None,:,None],
               gen_ramp_rate=data['gen_ramp_rate'])
    print('Saved:',OUTPUT/'Fig2.pdf')
    print('Original evaluation scenario index:',metadata['scenario_index_zero_based'])
