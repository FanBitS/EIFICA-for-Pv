# EIFICA-for-PV

Public data and figure files for the revised manuscript, **“Envelope Informed Fast Inner Convex Approximation for Distributionally Robust Day-Ahead AGC Scheduling under PV Uncertainty.”**

## Reproduce the manuscript figures and tables

The [reproduction guide](REPRODUCIBILITY.md) identifies the input data, script, saved output, and seed coverage for **Figs. 1–9 and Tables 1–2**. The figure and table source rows are in [`figure_table_data/`](figure_table_data/).

| Manuscript item | Source |
|---|---|
| Fig. 1 | [`solar_error_generalization.ipynb`](solar_error_generalization.ipynb) and [`data/ods032.csv`](data/ods032.csv) |
| Fig. 2 | [`figure/test/Fig2.pdf`](figure/test/Fig2.pdf); its optimization and plotting code requires the core solver |
| Figs. 3–8 | [`result_vis/EIFICA_result_vis.ipynb`](result_vis/EIFICA_result_vis.ipynb) and the [ten-seed CSV](figure_table_data/figures_3_to_8_main_grid_10seeds.csv) |
| Fig. 9 | [`result_vis/plot_fig9.py`](result_vis/plot_fig9.py) and the [120-case CSV](figure_table_data/fig9_exactlhs_120_cases.csv) |
| Table 1 | [Original five-seed CVaR comparison rows](figure_table_data/table_1_rts24_5seeds.csv) |
| Table 2 | [Ten one-hour ExactLHS retry rows](figure_table_data/table_2_exactlhs_10_retries.csv) |

The five-seed Table 1 and ten-seed Figs. 3–8 use different seed counts. The guide identifies their underlying records so that small-sample reliability values can be checked against the correct data.

## Code availability

This repository includes the experiment drivers, PV-error preprocessing, plotting code, saved results, and figure/table source data. **The core optimization solver, `solar_all_method.py`, is not public.** Running new optimization instances with [`paper_eval.py`](paper_eval.py) or [`exp_optimality_run.py`](exp_optimality_run.py) requires that solver and a Gurobi license. Editors and reviewers may request the complete code for confidential examination at **f13265151226@163.com**.

For a fixed version of these public files, use the [EPSR revision archive](https://github.com/FanBitS/EIFICA-for-Pv/tree/epsr-revision-2026-11-13-v2).
