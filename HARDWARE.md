# Hardware and memory reference

## Experimental equipment

| Configuration | Processor | Installed RAM | Software and execution |
|---|---|---|---|
| Main benchmark server | Intel Xeon Platinum 8378A, 3.00 GHz | 512 GB | Ubuntu 22.04 LTS; Python 3.9.19; Gurobi 12.0.3; four solver threads per instance |
| Second computer | Intel Core i9-14900KF | 128 GB | Gurobi 12.0.3; four solver threads per instance |

The second-computer comparison used RTS-24 and IEEE-118, N=150/300, T=24, epsilon=0.03, theta=0.06, and five paired seeds. It covered 40 optimization runs per computer.

The main mixed-integer benchmark setting was a 0.1% relative MIP gap. Gurobi feasibility and optimality tolerances were 1e-6; iterative ramp screening used 1e-4 MW. The general instance time limit was four hours. The T=3 ExactLHS comparison uses a one-hour time limit.

## Memory recorded in the archived experiments

Each entry is the **largest sampled process RSS across 40 individual runs** at the stated network and N. Each group covers four parameter pairs, ten seeds, and T=24.

| Network | Training scenarios N | FICA (GB) | Direct EIFICA (GB) | Iterative EIFICA (GB) |
|---|---:|---:|---:|---:|
| RTS-24 | 50 | 1.12 | 1.07 | 1.20 |
| RTS-24 | 150 | 40.45 | 2.31 | 2.65 |
| RTS-24 | 300 | 95.94 | 16.84 | 17.52 |
| IEEE-118 | 50 | 2.33 | 2.23 | 2.65 |
| IEEE-118 | 150 | 53.73 | 5.02 | 6.41 |
| IEEE-118 | 300 | 116.95 | 28.55 | 31.18 |

The RTS-24 CVaR comparison uses the same four parameter pairs and ten seeds:

| Training scenarios N | Largest recorded process memory (GB) |
|---|---:|
| 50 | 41.19 |
| 80 | 79.13 |

The public per-case CSVs record the maximum sampled resident set size, or RSS, of each process during a run. The original `peak_rss_mb` field contains MiB. Multiply by 2^20 and divide by 10^9 to obtain GB, where one GB equals 10^9 bytes.

Run `python summarize_resources.py` to regenerate [resource_memory_summary.csv](figure_table_data/resource_memory_summary.csv), which includes both the median and largest sampled maximum for every group above. The main-grid inputs are the same archived records used for Figs. 3–8; the CVaR inputs are the 80 records supporting revised Table 1.

## Running on your machine

- **Saved-result reproduction:** run the table extraction and plotting commands in [ENVIRONMENT.md](ENVIRONMENT.md) using the included data. These commands read the archived arrays and CSV records.
- **New optimization runs:** start with one N=50 instance and four solver threads. Check its memory use before increasing N. Use the method-specific memory figures above when selecting the workload.
- **Memory budget:** reserve RAM for the optimization process, operating system, input data, and other applications. The largest listed IEEE-118 FICA measurement at N=300 is 116.95 GB.
- **Concurrency:** each instance uses four solver threads. Concurrent instances allocate separate models, so budget for their combined memory use. Start with one worker and increase concurrency according to available RAM.

New optimization runs use the separately supplied core solver and instance files, together with a Gurobi license that supports the model size.
