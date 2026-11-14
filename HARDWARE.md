# Hardware and memory reference

## Experimental equipment

| Configuration | Processor | Installed RAM | Software and execution |
|---|---|---|---|
| Main benchmark server | Intel Xeon Platinum 8378A, 3.00 GHz | 512 GB | Ubuntu 22.04 LTS; Python 3.9.19; Gurobi 12.0.3; four solver threads per instance |
| Second computer | Intel Core i9-14900KF | 128 GB | Gurobi 12.0.3; four solver threads per instance |

The second-computer comparison used RTS-24 and IEEE-118, N=150/300, T=24, epsilon=0.03, theta=0.06, and five paired seeds. It covered 40 optimization runs per computer. This is a separate hardware comparison, not a claim that every full-grid configuration was rerun on the second computer.

The main mixed-integer benchmark setting was a 0.1% relative MIP gap. Gurobi feasibility and optimality tolerances were 1e-6; iterative ramp screening used 1e-4 MW. The general instance time limit was four hours. The T=3 ExactLHS comparison has its own 600-second initial limit and selected one-hour retries, as described in the reproduction guide.

## Memory recorded in the archived experiments

The following entries are the **largest recorded process-memory values across 40 cases** at each network and N: four parameter pairs and ten seeds, with T=24. They are not medians and do not describe simultaneous workers.

| Network | Training scenarios N | FICA (GiB) | Direct EIFICA (GiB) | Iterative EIFICA (GiB) |
|---|---:|---:|---:|---:|
| RTS-24 | 50 | 1.04 | 1.00 | 1.12 |
| RTS-24 | 150 | 37.67 | 2.15 | 2.47 |
| RTS-24 | 300 | 89.35 | 15.68 | 16.32 |
| IEEE-118 | 50 | 2.17 | 2.08 | 2.46 |
| IEEE-118 | 150 | 50.04 | 4.68 | 5.97 |
| IEEE-118 | 300 | 108.92 | 26.59 | 29.04 |

The RTS-24 CVaR comparison uses the same four parameter pairs and ten seeds:

| Training scenarios N | Largest recorded process memory (GiB) |
|---|---:|
| 50 | 38.36 |
| 80 | 73.70 |

These values come from the public per-case CSVs. The recorded metric is the maximum **sampled resident set size**, or RSS, during a run. It measures resident process memory, not total installed RAM or an operating-system high-water counter. The original `peak_rss_mb` field contains MiB; divide by 1024 for GiB. One GiB equals 2^30 bytes. Sampled maxima are observed measurements, not guaranteed upper bounds for another machine or configuration.

Run `python summarize_resources.py` to regenerate [resource_memory_summary.csv](figure_table_data/resource_memory_summary.csv), which includes both the median and largest sampled maximum for every group above. The main-grid inputs are the same archived records used for Figs. 3–8; the CVaR inputs are the 80 records supporting revised Table 1.

## Choosing a reproduction workload

- **Regenerating tables and plotting saved results:** use the extraction and visualization commands in [ENVIRONMENT.md](ENVIRONMENT.md). They do not construct optimization models and do not require the benchmark server or a Gurobi license. The optimization-memory table above does not describe plotting memory.
- **Starting new optimization runs:** start with one N=50 instance and four solver threads, then inspect its memory use before increasing N. CVaR is already memory-intensive at N=50, so it should not be used as a lightweight installation check.
- **Larger instances:** provide available RAM above the listed process-memory maximum, with additional space for the operating system, input data, and other applications. For example, a FICA IEEE-118 run at N=300 has an archived value of 108.92 GiB; a machine with 64 GB RAM is insufficient for that recorded workload.
- **Parallel runs:** four solver threads belong to one optimization instance. Running four instances concurrently creates four separate models and memory allocations. Start with one worker; budget RAM for the combined processes before enabling parallel cases. The driver configuration and the core solver must both be available before launching a new experiment.

A Gurobi installation must also have a license that permits the model size. The full-size runs require the separately supplied core solver and instance files; the saved-result reproduction scripts can be run directly from the public repository.
