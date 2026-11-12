# 3-minute video script (about 400 spoken words, about 2:50 at a steady pace). Replace [NAMES].

**0:00-0:25 Problem**
"Hi, we're [NAMES]. Blood can't be manufactured, and it expires. A non-profit blood bank has limited units in different storage lots, and urgent requests arrive from hospitals and clinics. Who gets which units? We want to serve the most critical patients first, use soon-to-expire stock before it's wasted, keep deliveries short, and avoid spending scarce O-negative blood on patients who could take another group. These goals compete with each other."

**0:25-1:00 Approach** (show docs/architecture.png)
"We turn each possible assignment of a request to a compatible lot into one yes-or-no variable. The cost rewards urgent patients, and penalizes expiry waste, distance, and spending O-negative on other groups. The rules, one lot per request and never exceeding stock, become penalty terms. That makes the whole problem a QUBO, and then an Ising Hamiltonian with fifteen qubits. We solve it with QAOA in Qiskit, tuning the circuit angles with the COBYLA optimizer on a simulator, then sample the result and keep the best feasible allocation."

**1:00-1:55 Demo** (screen: terminal)
"Here's the code running. First, a test confirms the quantum Hamiltonian matches the classical cost, and that the exact minimum equals the brute-force answer. Now the main script. It builds the problem, runs the classical baselines, then QAOA with one, two and three layers. And here's the allocation: critical requests are served, the Maternity Ward gets the A-positive unit that expires in two days, the Trauma Centre gets the O-negative units, and the routine clinic waits because stock ran out. QAOA's best sampled allocation matches the exact optimum."

**1:55-2:25 Results** (screen: results table and results/qaoa_vs_p.png)
"Brute force and MILP find the optimum in milliseconds. A simple urgency-first greedy method is worse, because it wastes an expiring unit. QAOA also finds the optimum, but the honest measure is probability. The optimal answer is only about 0.04 to 0.1 percent likely, yet that is roughly thirteen to forty times better than random guessing. So the quantum state is measurably biased toward good solutions, but it is far slower than the classical solvers."

**2:25-2:48 Limitations**
"Our limitations are clear. It's a tiny synthetic instance, a noise-free simulation, and hand-tuned weights. Random sampling also finds the optimum at this size, and deeper circuits did not clearly help. We claim no quantum speedup, and real use would need clinician-validated priorities."

**2:48-3:00 Impact**
"If quantum hardware matures, larger, multi-period blood allocation could become a natural fit. For now, we've built a transparent, reproducible testbed. Thank you."
