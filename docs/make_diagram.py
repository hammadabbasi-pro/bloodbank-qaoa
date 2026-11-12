"""Draws docs/architecture.png (matplotlib only). Run: python docs/make_diagram.py"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(11, 5.2)); ax.set_xlim(0, 11); ax.set_ylim(0, 5.2); ax.axis("off")
def box(x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fc=fc, ec="#333", lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.5)
def arrow(x1, y1, x2, y2, both=False):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="<->" if both else "->", lw=1.3, color="#333"))
Q, C, R = "#dbeafe", "#fde68a", "#bbf7d0"
box(0.2, 3.7, 2.0, 1.1, "Instance data\nlots, requests,\ndistances\n(instance.py)", "#f3f4f6")
box(2.7, 3.7, 2.0, 1.1, "QuadraticProgram\n10 binary variables\n+ capacity constraints\n(model.py)", "#f3f4f6")
box(5.2, 3.7, 2.0, 1.1, "QUBO\npenalties + 5 slack bits\n= 15 qubits", Q)
box(7.7, 3.7, 2.0, 1.1, "Ising Hamiltonian\nSparsePauliOp (Z, ZZ)", Q)
box(7.7, 2.0, 2.0, 1.1, "QAOA circuit\nH, then p x (RZ/RZZ + RX)\n(qaoa.py)", Q)
box(9.0, 0.3, 1.8, 1.0, "COBYLA optimiser\nminimise <H_C>", Q)
box(5.2, 2.0, 2.0, 1.1, "Statevector simulator\nsample 4000 shots", Q)
box(2.7, 2.0, 2.0, 1.1, "Decode + feasibility\nfilter -> best feasible\nallocation", Q)
box(0.2, 2.0, 2.0, 1.1, "Classical baselines\nbrute force, MILP,\ngreedy (classical.py)", C)
box(2.7, 0.3, 4.4, 1.0, "Comparison (main.py): objective, gap, feasibility,\ntime, expiring units left unused", R)
box(0.2, 0.3, 2.0, 1.0, "results/\ntable, JSON, plot", R)
arrow(2.2, 4.25, 2.7, 4.25); arrow(4.7, 4.25, 5.2, 4.25); arrow(7.2, 4.25, 7.7, 4.25)
arrow(8.7, 3.7, 8.7, 3.1)
arrow(9.4, 2.0, 9.9, 1.3, both=True)
arrow(7.7, 2.55, 7.2, 2.55); arrow(5.2, 2.55, 4.7, 2.55)
arrow(3.7, 2.0, 3.7, 1.3)
arrow(1.2, 2.0, 2.7, 0.9)
arrow(2.7, 0.8, 2.2, 0.8)
ax.text(5.5, 5.05, "Blood bank allocation with QAOA: architecture", ha="center", fontsize=11, weight="bold")
fig.savefig("docs/architecture.png", dpi=170, bbox_inches="tight")
