"""Run: python -m pytest -q tests   (or: python tests/test_consistency.py)
Checks that the Ising operator, the QUBO diagonal and the classical optimum all agree."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import numpy as np
from qiskit.quantum_info import Statevector
from model import build_problem, to_qubo, qubo_diagonal, decode, is_feasible, objective
import classical

def _setup():
    qp, pairs, pen = build_problem()
    qubo = to_qubo(qp, pen)
    op, offset = qubo.to_ising()
    return qubo, op, offset, pairs, qubo_diagonal(qubo)

def test_ising_matches_diagonal():
    qubo, op, offset, pairs, diag = _setup()
    n = qubo.get_num_vars()
    for i in np.random.default_rng(1).integers(0, 2 ** n, 5):
        sv = Statevector.from_int(int(i), 2 ** n)
        assert abs(sv.expectation_value(op).real + offset - diag[i]) < 1e-8

def test_qubo_ground_state_is_classical_optimum():
    qubo, op, offset, pairs, diag = _setup()
    n = qubo.get_num_vars()
    best = decode([(int(np.argmin(diag)) >> k) & 1 for k in range(n)], pairs)
    _, bf_val, _, _ = classical.brute_force()
    assert is_feasible(best) and abs(objective(best) - bf_val) < 1e-9

if __name__ == "__main__":
    test_ising_matches_diagonal(); test_qubo_ground_state_is_classical_optimum(); print("all tests passed")
