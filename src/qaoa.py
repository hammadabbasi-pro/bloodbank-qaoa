"""qaoa.py - hand-built QAOA circuit, optimiser loop and exact statevector simulation."""
import time
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector

def ising_terms(op):
    """Split a diagonal SparsePauliOp into single-Z terms {i: h} and ZZ terms {(i,j): J}."""
    n = op.num_qubits
    h, J = {}, {}
    for pauli, coeff in zip(op.paulis, op.coeffs):
        idx = [i for i in range(n) if pauli.z[i]]
        c = float(np.real(coeff))
        if len(idx) == 1:
            h[idx[0]] = h.get(idx[0], 0.0) + c
        elif len(idx) == 2:
            J[tuple(idx)] = J.get(tuple(idx), 0.0) + c
    return h, J

def build_qaoa_circuit(n, h, J, p):
    """|+>^n, then p rounds of: cost layer exp(-i*gamma*H_C) and mixer layer exp(-i*beta*sum X)."""
    gam, bet = ParameterVector("gamma", p), ParameterVector("beta", p)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(p):
        for i, c in h.items():
            qc.rz(2 * gam[layer] * c, i)
        for (i, j), c in J.items():
            qc.rzz(2 * gam[layer] * c, i, j)
        for q in range(n):
            qc.rx(2 * bet[layer], q)
    return qc

def run_qaoa(op, diag, p=2, restarts=4, maxiter=250, seed=0):
    """Minimise <H_C> over (beta, gamma). `diag` = cost of every bitstring, so <H_C> = sum_i prob_i * diag_i."""
    n = op.num_qubits
    scale = np.max(np.abs(op.coeffs))            # normalise coefficients so the angles stay O(1)
    h, J = ising_terms(op / scale)
    qc = build_qaoa_circuit(n, h, J, p)
    n_eval = [0]

    def energy(theta):
        n_eval[0] += 1
        return float(np.dot(Statevector(qc.assign_parameters(theta)).probabilities(), diag))

    rng = np.random.default_rng(seed)
    best, t0 = None, time.perf_counter()
    for _ in range(restarts):
        # qc.parameters is sorted by name: beta[0..p-1] first, then gamma[0..p-1]
        x0 = np.concatenate([rng.uniform(0, np.pi / 2, p), rng.uniform(0, np.pi, p)])
        res = minimize(energy, x0, method="COBYLA", options={"maxiter": maxiter})
        if best is None or res.fun < best.fun:
            best = res
    probs = Statevector(qc.assign_parameters(best.x)).probabilities()
    return {"energy": best.fun, "probs": probs, "theta": best.x, "evals": n_eval[0],
            "time": time.perf_counter() - t0, "depth": qc.decompose().depth()}
