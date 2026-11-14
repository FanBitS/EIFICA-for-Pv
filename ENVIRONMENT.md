# Environment and execution

The scripts were checked on Linux x86_64 with Python 3.9.19. Package versions below were read from the local environment used for the paper. They provide a reproduction baseline rather than a claim about every operating system or package combination.

## Create an environment

Choose any environment name by changing the value on the first line. Run from the repository root after cloning.

```bash
REPRO_ENV=my_reproduction_env
conda create -n "$REPRO_ENV" python=3.9.19 pip -y
conda activate "$REPRO_ENV"
python -m pip install -r requirements.txt
```

Alternatively, with Python 3.9 already installed, choose your own environment directory:

```bash
REPRO_ENV_DIR="$HOME/my_reproduction_env"
python3.9 -m venv "$REPRO_ENV_DIR"
source "$REPRO_ENV_DIR/bin/activate"
python -m pip install -r requirements.txt
```

`requirements.txt` specifies NumPy 1.26.4, pandas 2.2.2, SciPy 1.13.0, Matplotlib 3.8.4, and seaborn 0.13.2. No machine-specific environment name or absolute project path is required.

## Reproduce saved results

From the repository root:

```bash
python extract_figure_table_data.py
python extract_exactlhs_table_data.py
python result_vis/plot_fig2.py
python result_vis/plot_fig9.py
```

The extraction scripts require only the Python standard library. The plotting scripts use the installed scientific packages and a noninteractive backend, so no desktop display is needed. Outputs are listed in [REPRODUCIBILITY.md](REPRODUCIBILITY.md). These commands do not run an optimizer.

### Notebooks

To use the notebooks in an editor such as VS Code, install and register a kernel in your chosen environment:

```bash
python -m pip install -r requirements-notebooks.txt
REPRO_KERNEL=my_reproduction_kernel
python -m ipykernel install --user --name "$REPRO_KERNEL" --display-name "$REPRO_KERNEL"
```

The kernel name is also user-selected. Open the notebook in your notebook application and select this kernel. The editor's notebook support is separate from the Python packages installed here.

- Run `solar_error_generalization.ipynb` with the repository root as its working directory. This notebook fits the PV error model, generates the saved scenario arrays, and produces Fig. 1. Running it writes the generated arrays under `data/`.
- Run `result_vis/EIFICA_result_vis.ipynb` with `result_vis/` as its working directory. It reads the ten-seed main-grid CSV and produces Figs. 3–8 and the summary CSV.

`solar_error_generalization.py` is an alternative preprocessing entry point and is run from the repository root. Preprocessing recalculates the scenario pool; use the included result CSVs for the archived optimization outcomes.

## New optimization runs

Consult [HARDWARE.md](HARDWARE.md) before choosing N or the number of concurrent instances. It reports the experimental equipment and observed per-process memory.

After obtaining the core solver and instance files, install the additional packages:

```bash
python -m pip install -r requirements-solver.txt
```

The local optimization environment used pandapower 2.14.6, gurobipy 12.0.3, joblib 1.5.2, and psutil 7.0.0. The solver uses pandapower's internal network conversion routines, so retain the stated pandapower version when reproducing those runs. Gurobi requires a valid license with capacity for the intended model size. Installing `gurobipy` alone does not provide that capacity.

`paper_eval.py` and `exp_optimality_run.py` require the separately supplied `solar_all_method.py`. Editors and reviewers may contact **f13265151226@163.com** to arrange access. Place the supplied solver and associated instance files in the documented repository locations before launching a new optimization experiment. The original driver defaults and the archived ten-seed results have different seed coverage; consult the reproduction guide rather than launching the driver to recreate a table from saved results.

## Installation check

A fresh Python 3.9.19 virtual environment was used to install `requirements-notebooks.txt`. `python -m pip check` passed, and both extraction scripts plus the Fig. 2 and Fig. 9 plotting scripts completed successfully in that environment. New optimization experiments were not launched as part of this installation check.
