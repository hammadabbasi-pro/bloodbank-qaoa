"""main.py - run baselines + QAOA, print comparison, save results/ (table, json, plot)."""
import argparse, json, time
from pathlib import Path
import numpy as np
from model import (build_problem, to_qubo, qubo_diagonal, decode, is_feasible, objective,
                   describe, wasted_expiring_units)
import classical
from qaoa import run_qaoa

def bits_of(i, n):
    return [(i >> k) & 1 for k in range(n)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--layers", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("--shots", type=int, default=4000)
    ap.add_argument("--no-plots", action="store_true")
    a = ap.parse_args()
    out = Path(__file__).resolve().parent.parent / "results"
    out.mkdir(exist_ok=True)

    qp, pairs, penalty = build_problem()
    qubo = to_qubo(qp, penalty)
    op, offset = qubo.to_ising()
    n, n_dec = qubo.get_num_vars(), len(pairs)
    diag = qubo_diagonal(qubo)
    print(f"Decision variables: {n_dec} | slack bits: {n - n_dec} | qubits: {n} | Ising terms: {len(op)}")

    # ---- classical / exact baselines ----
    bf, bf_val, bf_t, bf_n = classical.brute_force()
    gr, gr_val, gr_t = classical.greedy()
    il, il_val, il_t = classical.ilp(pairs)
    ground = set(np.flatnonzero(np.isclose(diag, diag.min(), atol=1e-9)).tolist())
    g_chosen = decode(bits_of(int(np.argmin(diag)), n), pairs)   # exact QUBO minimum (what NumPyMinimumEigensolver would return)
    assert is_feasible(g_chosen) and abs(objective(g_chosen) - bf_val) < 1e-9, "QUBO penalties too weak!"
    uniform_mean = diag.mean()
    rows = [("Brute force (exact)", bf_val, True, bf_t, wasted_expiring_units(bf)),
            ("MILP / HiGHS (exact)", il_val, True, il_t, wasted_expiring_units(il)),
            ("Greedy by urgency", gr_val, True, gr_t, wasted_expiring_units(gr))]

    rng = np.random.default_rng(a.seed)
    qres = {}
    for p in a.layers:
        r = run_qaoa(op, diag, p=p, restarts=a.restarts, seed=a.seed)
        probs = r["probs"] / r["probs"].sum()
        samples = rng.choice(2 ** n, size=a.shots, p=probs)
        feas = [(objective(c), s) for s in samples
                for c in [decode(bits_of(s, n), pairs)] if is_feasible(c)]
        best_val, best_s = min(feas) if feas else (np.nan, None)
        p_opt = float(sum(probs[g] for g in ground))
        feas_mask = np.array([is_feasible(decode(bits_of(i, n), pairs)) for i in range(2 ** n)])
        p_feas = float(probs[feas_mask].sum())
        ratio = (uniform_mean - r["energy"]) / (uniform_mean - diag.min())
        chosen = decode(bits_of(best_s, n), pairs) if best_s is not None else {}
        qres[p] = dict(p=p, energy=r["energy"], quality_vs_random=ratio, p_opt=p_opt,
                       enrichment=p_opt / (len(ground) / 2 ** n), p_feas=p_feas, best_val=best_val,
                       time=r["time"], evals=r["evals"], depth=r["depth"],
                       found_opt=bool(abs(best_val - bf_val) < 1e-9), chosen=chosen)
        print(f"QAOA p={p}: <E>={r['energy']:.2f} quality-vs-random={ratio:.2f} P(opt)={p_opt:.4f} "
              f"(uniform={len(ground)/2**n:.5f}) P(feasible)={p_feas:.3f} best feasible sample={best_val:.2f} "
              f"time={r['time']:.1f}s depth={r['depth']}")
        rows.append((f"QAOA p={p} (best feasible of {a.shots} shots)", best_val, best_s is not None, r["time"],
                     wasted_expiring_units(chosen)))
    # uniform random sampling with the same shot budget
    samples = rng.integers(0, 2 ** n, size=a.shots)
    feas = [objective(c) for s in samples for c in [decode(bits_of(s, n), pairs)] if is_feasible(c)]
    rows.append((f"Uniform random ({a.shots} shots)", min(feas) if feas else np.nan, bool(feas), 0.0, None))

    # ---- report ----
    md = ["| Method | Objective (lower = better) | Gap to optimum | Feasible | Time (s) | Expiring units left unused |",
          "|---|---|---|---|---|---|"]
    for name, val, ok, t, w in rows:
        md.append(f"| {name} | {val:.2f} | {val - bf_val:.2f} | {'yes' if ok else 'no'} | {t:.3f} | {w if w is not None else '-'} |")
    (out / "results_table.md").write_text("\n".join(md))
    print("\n" + "\n".join(md))
    print(f"\nOptimal allocation (brute force over {bf_n} assignments):")
    for s in describe(bf): print("  ", s)
    pbest = min(qres, key=lambda k: qres[k]["energy"])
    print(f"\nQAOA (p={pbest}) best feasible sample:")
    for s in describe(qres[pbest]["chosen"]): print("  ", s)
    json.dump({"qubits": n, "brute_force": bf_val, "greedy": gr_val, "milp": il_val,
               "qaoa": {str(k): {kk: vv for kk, vv in v.items() if kk != "chosen"} for k, v in qres.items()}},
              open(out / "results.json", "w"), indent=2, default=float)
    if not a.no_plots:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        ps = sorted(qres)
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
        ax[0].plot(ps, [qres[p]["p_opt"] for p in ps], "o-", label="QAOA")
        ax[0].axhline(len(ground) / 2 ** n, ls="--", c="gray", label="uniform random")
        ax[0].set_yscale("log"); ax[0].set_xlabel("QAOA layers p"); ax[0].set_ylabel("P(optimal bitstring)"); ax[0].legend()
        ax[1].plot(ps, [qres[p]["quality_vs_random"] for p in ps], "s-")
        ax[1].set_xlabel("QAOA layers p"); ax[1].set_ylabel("quality (0 = random, 1 = optimal)"); ax[1].set_ylim(0, 1)
        fig.tight_layout(); fig.savefig(out / "qaoa_vs_p.png", dpi=150)

if __name__ == "__main__":
    main()
