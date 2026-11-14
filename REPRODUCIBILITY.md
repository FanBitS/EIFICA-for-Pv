# Reproduction guide

This guide follows the current manuscript numbering. Table 1 uses ten matched seeds for all three methods. Table 2 reports historical validation. Save the full repository commit ID with reproduced results.

Install the packages and configure the working directory as described in [ENVIRONMENT.md](ENVIRONMENT.md).

## Rebuild the table data

From the repository root, run:

```bash
python extract_figure_table_data.py
python extract_exactlhs_table_data.py
```

The first script uses only the Python standard library and creates:

| Output | Definition |
|---|---|
| `figure_table_data/figures_3_to_8_main_grid_10seeds.csv` | 1,680 FICA/EIFICA records on two networks, training seeds 0–9 |
| `figure_table_data/table_1_rts24_10seeds.csv` | 240 RTS-24 records: four parameter pairs × two sample sizes × ten seeds × three methods |
| `figure_table_data/Table1.csv` | 24 rows of ten-seed medians for scheduled cost, measured joint satisfaction, time, and sampled maximum process RSS |
| `figure_table_data/Table2.csv` | 15 historical validation settings, each evaluated on the same 45 days |

### Table 1

CVaR source records are in `figure_table_data/table1_cvar_80_cases.csv`. These combine 40 original cases with 40 added cases at seeds 5–9. The direct and iterative EIFICA records come from `master_summary_20260708_110917.csv`, restricted to RTS-24 and N=50/80. Each parameter/sample-size/method group contains seeds 0–9 exactly once. The extraction script checks the original CVaR records against the original summary.

Each seed uses 5,000 generated evaluation scenarios. Joint satisfaction is recorded as a percentage. Cost is scheduled generation cost in USD. Runtime is the archived elapsed-time field. The original `peak_rss_mb` field contains MiB; Table 1 converts it to GiB by dividing by 1024. `Table1.csv` also includes decimal GB for explicit unit conversion.

The original summary files are retained as historical inputs. Their CVaR rows alone are not the complete ten-seed comparison; use the extraction script above for current Table 1.

### Table 2

The source is `figure_table_data/table2_historical_validation_days.csv`, containing 675 daily records: five N values × three radii × 45 validation days. Epsilon is 0.08. The original selection grid uses N=100/200/250; N=300/350 are later exploratory extensions. The selected setting remains N=250 and theta=0.03.

A day passes when its solve is optimal, iteration stops without additions, and generator limits, both ramp directions, DC line limits, and PV bounds all satisfy the 1e-4 MW threshold throughout the day. Every planned day remains in the denominator. Mean scheduled cost uses the records with completed optimal audits, as in the archived validation summaries. The CSV retains per-family maximum residuals, the separate power-balance residual, and the original broader audit flag; `operating_pass` applies the operating-limit definition used in the manuscript table.

Validation covers 1 April–15 May 2026. Training uses 363 complete days from 2025. N and theta remain fixed for the independent 45-day test from 1 August–14 September 2026. Table 2 contains validation results, not test results.

The second extraction script creates `figure_table_data/exactlhs_one_hour_retries.csv` from the 120-case Fig. 9 archive. Those ten retry records support the ExactLHS comparison and are not current Table 2.

## Reproduce the figures

| Figure | Input | Command or notebook | Output |
|---|---|---|---|
| Fig. 1 | `data/ods032.csv` | `solar_error_generalization.ipynb` | `solar_error_gen_figure/Fig1.pdf` |
| Fig. 2 | `figure_table_data/fig2/plot_data.npz` and `provenance.json` | `python result_vis/plot_fig2.py` | `figure/test/Fig2.pdf` |
| Fig. 3, RTS-24 reliability | Ten-seed main-grid CSV | RTS-24 reliability cell in `result_vis/EIFICA_result_vis.ipynb` | `result_vis/figures/Fig3.pdf` |
| Fig. 4, IEEE-118 reliability | Same CSV | IEEE-118 reliability cell in the same notebook | `result_vis/figures/Fig4.pdf` |
| Fig. 5, RTS-24 runtime | Same CSV | RTS-24 runtime cell in the same notebook | `result_vis/figures/Fig5.pdf` |
| Fig. 6, IEEE-118 runtime | Same CSV | IEEE-118 runtime cell in the same notebook | `result_vis/figures/Fig6.pdf` |
| Fig. 7, RTS-24 time and memory | Same CSV | RTS-24 time-memory cell in the same notebook | `result_vis/figures/Fig7.pdf` |
| Fig. 8, IEEE-118 memory | Same CSV | IEEE-118 memory cell in the same notebook | `result_vis/figures/Fig8.pdf` |
| Fig. 9, ExactLHS bounds | `figure_table_data/fig9_exactlhs_120_cases.csv` | `python result_vis/plot_fig9.py` | `result_vis/figures/Fig9.pdf` |

Run the main visualization notebook from `result_vis/`. Its summary output is `result_vis/summary_table.csv`; the historical five-seed summary has a separate `_5seed` filename. The plots retain their existing styles. Figure scripts write PDF outputs only. Python plotting requires NumPy and Matplotlib; notebooks additionally require their imported scientific packages.

Fig. 2 uses iterative EIFICA on RTS-24 at N=300, epsilon=0.03, theta=0.06, and T=24, with training seed 0. Sampling seed 10 selects evaluation scenario 245, using zero-based indexing, from 5,000 generated scenarios. The saved plot arrays contain this selected trajectory; row 0 in that file is therefore original scenario 245. Gen 7 and Gen 13 are selected by the original AGC-variation rule. The script plots the saved dispatch without importing the optimizer. Computing a new schedule requires the core solver.

Fig. 9 uses all 120 fixed-five-seed paired cases. Nine final one-hour time-limit cases have objective-difference intervals calculated from the ExactLHS incumbent and solver lower bound. The original `Solar_c24_optgap/optimality_gap_T3_fixed.csv` is a different 240-pair archive and is not the input to revised Fig. 9.

## Preprocessing, seeds, and optimization access

- `solar_error_generalization.py` and `solar_error_generalization.ipynb` implement historical-error preprocessing, KDE fitting, and copula-based scenario construction from the included PV data. Scenario generation specifies seed 0 and saves its arrays under `data/`.
- `paper_eval.py` describes the main experiment grid. Its original default is five seeds; the current figure and Table 1 CSVs explicitly contain seeds 0–9. Use the seeds recorded in each applicable dataset.
- `exp_optimality_run.py` describes the original T=3 ExactLHS grid, with seeds 0, 100, ..., 900, a requested 0.1% MIP gap, and a 600-second time limit. The revised 120-case archive separately records later one-hour retries.
- Full optimizer constraints and Big-M construction are in `solar_all_method.py`, which is not included in the public files. Editors and reviewers may contact **f13265151226@163.com** to arrange confidential access to the core solver, complete benchmark implementation, and instance settings. New optimization runs also require a Gurobi license.
