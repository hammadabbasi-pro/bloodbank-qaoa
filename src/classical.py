"""classical.py - exact / classical baselines: brute force, greedy, MILP."""
import itertools, time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from instance import LOTS, REQUESTS, compatible_options, assignment_cost
from model import is_feasible, objective

def brute_force():
    """Enumerate every assignment (each request -> unserved or one compatible lot)."""
    t0 = time.perf_counter()
    options = [[None] + compatible_options(r) for r in range(len(REQUESTS))]
    best, best_val, n = None, np.inf, 0
    for combo in itertools.product(*options):
        n += 1
        chosen = {r: [l] for r, l in enumerate(combo) if l is not None}
        if is_feasible(chosen):
            v = objective(chosen)
            if v < best_val - 1e-12:
                best, best_val = chosen, v
    return best, best_val, time.perf_counter() - t0, n

def greedy():
    """Serve requests by urgency (then size); give each the cheapest compatible lot with stock left."""
    t0 = time.perf_counter()
    left = [lot.stock for lot in LOTS]
    chosen = {}
    for r in sorted(range(len(REQUESTS)), key=lambda r: (-REQUESTS[r].urgency, -REQUESTS[r].units)):
        cands = [l for l in compatible_options(r) if left[l] >= REQUESTS[r].units]
        if cands:
            l = min(cands, key=lambda l: assignment_cost(r, l))
            chosen[r] = [l]
            left[l] -= REQUESTS[r].units
    return chosen, objective(chosen), time.perf_counter() - t0

def ilp(pairs):
    """Exact MILP with hard constraints (scipy.optimize.milp / HiGHS)."""
    t0 = time.perf_counter()
    c = np.array([assignment_cost(r, l) for r, l in pairs])
    A, ub = [], []
    for r in range(len(REQUESTS)):                       # at most one lot per request
        A.append([1.0 if rr == r else 0.0 for rr, _ in pairs]); ub.append(1)
    for l, lot in enumerate(LOTS):                       # lot capacity
        A.append([REQUESTS[rr].units if ll == l else 0.0 for rr, ll in pairs]); ub.append(lot.stock)
    res = milp(c, constraints=LinearConstraint(np.array(A), -np.inf, np.array(ub)),
               integrality=np.ones(len(pairs)), bounds=Bounds(0, 1))
    chosen = {r: [l] for k, (r, l) in enumerate(pairs) if res.x[k] > 0.5}
    return chosen, objective(chosen), time.perf_counter() - t0
