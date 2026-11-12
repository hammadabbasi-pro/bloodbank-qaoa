"""model.py - build the QuadraticProgram, convert to QUBO and Ising, decode bitstrings."""
import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
from instance import LOTS, REQUESTS, compatible_options, assignment_cost, W_SERVE

def build_problem():
    qp = QuadraticProgram("blood_allocation")
    pairs = []  # (request, lot) for every decision variable, in variable order
    for r in range(len(REQUESTS)):
        for l in compatible_options(r):
            qp.binary_var(f"x_{r}_{l}")
            pairs.append((r, l))
    # penalty must beat the biggest reward any single assignment can earn
    max_gain = max(W_SERVE * q.urgency * q.units for q in REQUESTS)
    penalty = 1.5 * max_gain
    linear = {f"x_{r}_{l}": assignment_cost(r, l) for r, l in pairs}
    quad = {}
    for i, (r1, l1) in enumerate(pairs):          # "at most one lot per request" as a quadratic penalty
        for (r2, l2) in pairs[i + 1:]:
            if r1 == r2:
                quad[(f"x_{r1}_{l1}", f"x_{r2}_{l2}")] = penalty
    qp.minimize(linear=linear, quadratic=quad)
    for l, lot in enumerate(LOTS):                # capacity: sum(units * x) <= stock  (needs slack bits)
        coeffs = {f"x_{r}_{ll}": REQUESTS[r].units for (r, ll) in pairs if ll == l}
        if coeffs:
            qp.linear_constraint(coeffs, "<=", lot.stock, f"cap_{lot.name}")
    return qp, pairs, penalty

def to_qubo(qp, penalty):
    return QuadraticProgramToQubo(penalty=penalty).convert(qp)

def qubo_diagonal(qubo):
    """Cost of every bitstring (index i, qubit k = bit k of i) = diagonal of the cost Hamiltonian."""
    n = qubo.get_num_vars()
    idx = np.arange(2 ** n)
    X = ((idx[:, None] >> np.arange(n)) & 1).astype(float)
    Q = qubo.objective.quadratic.to_array()
    c = qubo.objective.linear.to_array()
    return np.einsum("ij,jk,ik->i", X, Q, X) + X @ c + qubo.objective.constant

def decode(bits, pairs):
    """bits: sequence of 0/1 indexed by variable. Returns {request: [lots chosen]} for decision vars."""
    chosen = {}
    for k, (r, l) in enumerate(pairs):
        if bits[k]:
            chosen.setdefault(r, []).append(l)
    return chosen

def is_feasible(chosen):
    if any(len(v) > 1 for v in chosen.values()):
        return False
    used = {l: 0 for l in range(len(LOTS))}
    for r, ls in chosen.items():
        used[ls[0]] += REQUESTS[r].units
    return all(used[l] <= LOTS[l].stock for l in used)

def objective(chosen):
    return sum(assignment_cost(r, ls[0]) for r, ls in chosen.items())

def describe(chosen):
    rows = []
    for r, q in enumerate(REQUESTS):
        src = LOTS[chosen[r][0]].name if r in chosen else "UNSERVED"
        rows.append(f"{q.center} (needs {q.units}x{q.blood}, urgency {q.urgency}) <- {src}")
    return rows

def wasted_expiring_units(chosen, horizon=3):
    """Units in lots expiring within `horizon` days that are NOT allocated (potential waste)."""
    used = {l: 0 for l in range(len(LOTS))}
    for r, ls in chosen.items():
        used[ls[0]] += REQUESTS[r].units
    return sum(lot.stock - used[l] for l, lot in enumerate(LOTS) if lot.days_left <= horizon)
