# Blood Bank Allocation with QAOA (Qiskit Fall Fest 2026, Healthcare)

**Team:** Shor thing | **Repo:** [\[GITHUB URL\]](https://github.com/hammadabbasi-pro/bloodbank-qaoa)

A non-profit blood bank allocates scarce, perishable red-cell units to urgent requests from partner
centres. We formulate it as a QUBO (15 qubits), solve it with QAOA on a Qiskit statevector simulator,
and compare against brute force, MILP and greedy baselines. Synthetic data only. No quantum speedup is claimed.

## Setup
- Python 3.10+ (tested on 3.12.3)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Pinned: qiskit 2.6.2, qiskit-optimization 0.7.0, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2

## Run
```bash
python tests/test_consistency.py                          # sanity checks -> "all tests passed"
python src/main.py                                        # full experiment, ~1.5 min on a laptop
python src/main.py --layers 1 2 --restarts 2 --no-plots  # quick demo, ~15 s
```
Options: `--seed N`, `--layers 1 2 3`, `--restarts K`, `--shots S`.

## Expected output
- Console: 15 qubits (10 decision + 5 slack), QAOA statistics per layer count, comparison table,
  optimal allocation (brute force) and best QAOA allocation.
- Files: `results/results_table.md`, `results/results.json`, `results/qaoa_vs_p.png`.
- Brute force, MILP and greedy values are deterministic. QAOA numbers are seeded but may differ slightly across machines and library versions.

## Files
| Path | Purpose |
|---|---|
| `src/instance.py` | synthetic lots, requests, distances, objective weights |
| `src/model.py` | QuadraticProgram -> QUBO -> Ising, decoding, feasibility |
| `src/qaoa.py` | QAOA circuit, COBYLA loop, statevector simulation |
| `src/classical.py` | brute force, greedy, MILP baselines |
| `src/main.py` | runs everything, prints and saves results |
| `tests/test_consistency.py` | Ising vs QUBO vs brute-force checks |
| `docs/report.docx` | project report (regenerate with `node docs/make_report.js`) |
| `docs/architecture.png` | architecture diagram (`python docs/make_diagram.py`) |
| `docs/video_script.md` | 3-minute pitch script |
| `CREDITS.md` | credits and references |

## Limitations
Simulator only, 15 qubits, synthetic data, hand-tuned weights; classical methods solve this instance in milliseconds. See the report.
