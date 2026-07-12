import pandas as pd
import numpy as np
import time
import os
import sys
from solar_all_method import solve_PD_instance
from joblib import Parallel, delayed

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T          = 3
THETA      = 0.06
NUM_SOLAR  = 5
NETWORK    = "case24_ieee_rts"
TIME_LIMIT = int(os.environ.get("OPTGAP_TIME_LIMIT", "600"))
MIPGAP = {"ExactLHS": 0.001, "EIFICA": 0.001}

OUTDIR      = "Solar_c24_optgap"
LOGDIR      = os.path.join(OUTDIR, "logs")
OUTPUT_FILE = os.path.join(OUTDIR, "optimality_gap_T3_fixed.csv")
LOG_FILE    = os.path.join(LOGDIR, "main_experiment_T3_fixed.log")


class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def worker(sf, eps, n, seed, method, current_task, total_tasks, output_file):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] [{current_task}/{total_tasks}] STARTING {method}: SF={sf}, eps={eps}, N={n}, Seed={seed}")

    start_time = time.time()
    try:
        res = solve_PD_instance(
            method=method,
            N_WDR=n,
            epsilon=eps,
            load_scaling_factor=sf,
            seed=seed,
            show_plot=False,
            num_Solar=NUM_SOLAR,
            T=T,
            theta=THETA,
            network_name=NETWORK,
            time_limit=TIME_LIMIT,
            MIPGap=MIPGAP[method],
        )
        duration = time.time() - start_time
        result = {
            'method': method,
            'sf': sf,
            'epsilon': eps,
            'n_wdr': n,
            'seed': seed,
            'T': T,
            'theta': THETA,
            'obj': res['obj_value'],
            'solve_time': res['solve_time'],
            'total_duration': duration,
            'satisfied_rate': res['satisfied_rate'],
            'status': res['status'],
        }

        pd.DataFrame([result]).to_csv(output_file, mode='a',
                                      header=not os.path.exists(output_file), index=False)

        finish_time = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{finish_time}] [{current_task}/{total_tasks}] FINISHED {method} (Seed {seed}) in {duration:.2f}s. "
              f"Obj: {res['obj_value']:.2f}, Rate: {res['satisfied_rate']:.2%}, Status: {res['status']}")
        return result
    except Exception as e:
        error_time = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{error_time}] [{current_task}/{total_tasks}] !!! ERROR in {method} (Seed {seed}): {str(e)}")
        with open(os.path.join(LOGDIR, "error_details_T3.log"), "a", encoding="utf-8") as ef:
            ef.write(f"[{error_time}] SF={sf}, eps={eps}, N={n}, method={method}, seed={seed} -> {str(e)}\n")
        return None


def run_experiment():
    SF_list  = [1.0, 1.5, 2.0]
    EPS_list = [0.03, 0.06]
    N_list   = [30, 60, 90, 120]
    METHODS  = ['EIFICA', 'ExactLHS']
    NUM_RUNS = 10

    N_PARALLEL = 8

    os.makedirs(LOGDIR, exist_ok=True)

    sys.stdout = Logger(LOG_FILE)

    all_tasks = []
    for sf in SF_list:
        for eps in EPS_list:
            for n in N_list:
                for run in range(NUM_RUNS):
                    for method in METHODS:
                        all_tasks.append((sf, eps, n, run * 100, method))

    if os.path.exists(OUTPUT_FILE):
        existing_df = pd.read_csv(OUTPUT_FILE)
        print(f"Loaded {len(existing_df)} existing results.")
        tasks_to_run = []
        for task in all_tasks:
            sf, eps, n, seed, method = task
            mask = (existing_df['sf'] == sf) & (existing_df['epsilon'] == eps) & \
                   (existing_df['n_wdr'] == n) & (existing_df['seed'] == seed) & \
                   (existing_df['method'] == method)
            if not mask.any():
                tasks_to_run.append(task)
    else:
        tasks_to_run = all_tasks

    total_tasks = len(tasks_to_run)
    print(f"T={T}, theta={THETA}, MIPGap={MIPGAP}, time_limit={TIME_LIMIT}")
    print(f"Total remaining tasks to run: {total_tasks} (Parallel={N_PARALLEL})\n")

    Parallel(n_jobs=N_PARALLEL)(
        delayed(worker)(sf, eps, n, seed, method, i + 1, total_tasks, OUTPUT_FILE)
        for i, (sf, eps, n, seed, method) in enumerate(tasks_to_run)
    )

    print(f"\nBatch experiment complete at {time.ctime()}!")


if __name__ == "__main__":
    run_experiment()
