# EIFICA-for-PV

Data and reproduction scripts for **“Envelope Informed Fast Inner Convex Approximation for Distributionally Robust Day-Ahead AGC Scheduling under PV Uncertainty.”**

## Setup

See [ENVIRONMENT.md](ENVIRONMENT.md) for the tested Python and package versions, a user-named environment, and execution commands. Saved-result plots do not require the optimization solver or a Gurobi license. See [HARDWARE.md](HARDWARE.md) for the two experimental computers, observed per-instance memory, and guidance on selecting a workload.

## Manuscript figures and tables

The [reproduction guide](REPRODUCIBILITY.md) identifies the inputs, scripts, saved outputs, and statistical definitions. Figure and table data are in [`figure_table_data/`](figure_table_data/).

| Item | Data and script |
|---|---|
| Fig. 1 | [`solar_error_generalization.ipynb`](solar_error_generalization.ipynb), using [`data/ods032.csv`](data/ods032.csv) |
| Fig. 2 | [`result_vis/plot_fig2.py`](result_vis/plot_fig2.py), using the [saved N=300 dispatch trajectory](figure_table_data/fig2/) |
| Figs. 3–8 | [`result_vis/EIFICA_result_vis.ipynb`](result_vis/EIFICA_result_vis.ipynb), using the [ten-seed main grid](figure_table_data/figures_3_to_8_main_grid_10seeds.csv) |
| Fig. 9 | [`result_vis/plot_fig9.py`](result_vis/plot_fig9.py), using the [120 paired ExactLHS cases](figure_table_data/fig9_exactlhs_120_cases.csv) |
| Table 1 | [Ten-seed summary](figure_table_data/Table1.csv) and [240 source records](figure_table_data/table_1_rts24_10seeds.csv) |
| Table 2 | [Historical validation summary](figure_table_data/Table2.csv) and [675 daily records](figure_table_data/table2_historical_validation_days.csv) |

Run `python extract_figure_table_data.py` to rebuild the main-grid CSV and both table summaries. Table 1 now uses the same ten seeds, 0–9, for CVaR and both EIFICA modes. Table 2 is the historical validation table. ExactLHS one-hour retries are retained as [supporting records](figure_table_data/exactlhs_one_hour_retries.csv).

## Code availability

The repository includes experiment drivers, PV-error preprocessing, plotting scripts, and saved results. Plotting Fig. 2 from its saved trajectory does not require the core solver. Running new optimization instances requires the core solver, `solar_all_method.py`, and a Gurobi license. The core solver and complete Big-M implementation are available to editors and reviewers for confidential examination by contacting **f13265151226@163.com**. The core algorithm code will be released publicly promptly upon acceptance.

For a fixed version, retain the full commit ID returned by `git rev-parse HEAD`. GitHub's commit history provides the corresponding immutable file view.
