import math
import pickle
from pathlib import Path

import matplotlib.pyplot as plt

DATASET_SIZES = [20, 50, 100, 200, 300, 400, 500, 1000, 5000]
RESULTS_PATH = Path("results/results.pkl")
OUT_PATH = Path("results/objective_comparison.png")
CONVERGENCE_OUT_PATH = Path("results/ga_convergence.png")
RUNTIME_OUT_PATH = Path("results/runtime_when_cplex_optimal.png")
SNAPSHOT_INTERVAL = 5000
CONVERGENCE_SIZE = 1000


def cplex_objective(entry):
    obj = entry.get("objective")
    if obj is None or (isinstance(obj, float) and math.isnan(obj)):
        return None
    return obj


def ga_objective(entry):
    pop = entry.get("population")
    if not pop:
        return None
    return pop[0][0]


def align(values, sizes):
    xs, ys = [], []
    for size, v in zip(sizes, values):
        if v is not None:
            xs.append(size)
            ys.append(v)
    return xs, ys


def main():
    with open(RESULTS_PATH, "rb") as f:
        results = pickle.load(f)

    cplex_vals = [cplex_objective(e) for e in results["cplex"]]
    ga_no_repair_vals = [ga_objective(e) for e in results["ga_no_repair"]]
    ga_repair_vals = [ga_objective(e) for e in results["ga_repair"]]

    n = max(len(cplex_vals), len(ga_no_repair_vals), len(ga_repair_vals))
    sizes = DATASET_SIZES[:n]

    fig, ax = plt.subplots(figsize=(9, 6))

    for label, vals, marker in [
        ("CPLEX", cplex_vals, "o"),
        ("GA (no repair)", ga_no_repair_vals, "s"),
        ("GA (repair)", ga_repair_vals, "^"),
    ]:
        xs, ys = align(vals, sizes)
        ax.plot(xs, ys, marker=marker, label=label)

    ax.set_xscale("log")
    ax.set_xticks(sizes)
    ax.set_xticklabels([str(s) for s in sizes])
    ax.minorticks_off()
    ax.set_xlabel("Dataset size (number of Nodes)")
    ax.set_ylabel("Final objective value")
    ax.set_title("Final objective value after 10 Minutes: CPLEX vs Genetic Algorithm Variants")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend()

    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=150)
    print(f"Saved plot to {OUT_PATH}")

    plot_convergence(results)
    plot_runtimes_when_cplex_optimal(results)

    plt.show()


def plot_convergence(results):
    variants = [
        ("ga_no_repair", "GA (no repair)"),
        ("ga_repair", "GA (repair)"),
    ]

    if CONVERGENCE_SIZE not in DATASET_SIZES:
        raise ValueError(f"CONVERGENCE_SIZE {CONVERGENCE_SIZE} not in DATASET_SIZES")
    size_idx = DATASET_SIZES.index(CONVERGENCE_SIZE)

    fig, ax = plt.subplots(figsize=(9, 6))

    for key, label in variants:
        runs = results[key]
        if size_idx >= len(runs):
            continue
        run = runs[size_idx]
        best = run.get("best_fitnesses") or []
        if not best:
            continue
        iters = [i * SNAPSHOT_INTERVAL for i in range(len(best))]
        ax.plot(iters, best, label=label, marker="o", markersize=3)

    ax.set_xlim(0, 550000)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best fitness in population")
    ax.set_title(f"GA convergence at n={CONVERGENCE_SIZE}: best fitness vs iteration")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(CONVERGENCE_OUT_PATH, dpi=150)
    print(f"Saved plot to {CONVERGENCE_OUT_PATH}")


def plot_runtimes_when_cplex_optimal(results):
    cplex_runs = results["cplex"]
    ga_nr_runs = results["ga_no_repair"]
    ga_r_runs = results["ga_repair"]

    sizes, cplex_t, ga_nr_t, ga_r_t = [], [], [], []
    ga_nr_optimal, ga_r_optimal = [], []
    tol = 1e-6
    for size, c, g1, g2 in zip(DATASET_SIZES, cplex_runs, ga_nr_runs, ga_r_runs):
        status = (c.get("status") or "").lower()
        if not status.startswith("integer optimal"):
            continue
        sizes.append(size)
        cplex_t.append(c.get("elapsed", 0.0))
        ga_nr_t.append(g1.get("elapsed", 0.0))
        ga_r_t.append(g2.get("elapsed", 0.0))

        cobj = c.get("objective")
        g1_best = g1["population"][0][0] if g1.get("population") else None
        g2_best = g2["population"][0][0] if g2.get("population") else None
        ga_nr_optimal.append(cobj is not None and g1_best is not None and g1_best >= cobj - tol)
        ga_r_optimal.append(cobj is not None and g2_best is not None and g2_best >= cobj - tol)

    if not sizes:
        print("No CPLEX-optimal runs found; skipping runtime bar chart.")
        return

    import numpy as np

    x = np.arange(len(sizes))
    width = 0.27

    fig, ax = plt.subplots(figsize=(9, 6))
    cplex_bars = ax.bar(x - width, cplex_t, width, label="CPLEX")
    ga_nr_bars = ax.bar(x, ga_nr_t, width, label="GA (no repair)")
    ga_r_bars = ax.bar(x + width, ga_r_t, width, label="GA (repair)")

    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in sizes])
    ax.set_xlabel("Dataset size (number of Nodes)")
    ax.set_ylabel("Run time (seconds)")
    ax.set_title("Run time on instances where CPLEX found the optimal solution\n(* = solver found the optimal solution)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.legend()

    def labels(values, optimal_flags):
        return [f"{v:.1f}*" if opt else f"{v:.1f}" for v, opt in zip(values, optimal_flags)]

    cplex_optimal = [True] * len(sizes)
    ax.bar_label(cplex_bars, labels=labels(cplex_t, cplex_optimal), padding=2, fontsize=8)
    ax.bar_label(ga_nr_bars, labels=labels(ga_nr_t, ga_nr_optimal), padding=2, fontsize=8)
    ax.bar_label(ga_r_bars, labels=labels(ga_r_t, ga_r_optimal), padding=2, fontsize=8)

    fig.tight_layout()
    fig.savefig(RUNTIME_OUT_PATH, dpi=150)
    print(f"Saved plot to {RUNTIME_OUT_PATH}")


if __name__ == "__main__":
    main()