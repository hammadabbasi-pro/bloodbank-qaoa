// Builds docs/report.docx from results/results.json + results_table.md. Run: node docs/make_report.js
const fs = require("fs");
const path = require("path");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, HeadingLevel,
        AlignmentType, WidthType, ShadingType, BorderStyle, LevelFormat } = D;
const root = path.resolve(__dirname, "..");
const res = JSON.parse(fs.readFileSync(path.join(root, "results", "results.json")));
const tableMd = fs.readFileSync(path.join(root, "results", "results_table.md"), "utf8").trim().split("\n").slice(2)
  .map(l => l.split("|").slice(1, -1).map(s => s.trim()));
const W = 9026; // A4 with 1-inch margins, in DXA
const b = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const borders = { top: b, bottom: b, left: b, right: b };

const P = (t, o = {}) => new Paragraph({ spacing: { after: 120 }, ...o, children: [new TextRun({ text: t, ...(o.run || {}) })] });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const BUL = t => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 }, children: [new TextRun(t)] });
const NUM = t => new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60 }, children: [new TextRun(t)] });
function table(headers, rows, widths) {
  const cell = (t, w, hdr) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: hdr ? { fill: "D9E2F3", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: [new TextRun({ text: String(t), bold: hdr, size: 19 })] })] });
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true)) }),
           ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i], false)) }))] });
}
const img = (file, w, h) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 120 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(root, file)), transformation: { width: w, height: h } })] });

const q = res.qaoa;
const diagRows = Object.keys(q).map(k => [k, q[k].depth, q[k].p_opt.toExponential(2), q[k].enrichment.toFixed(1) + "x",
  q[k].p_feas.toFixed(2), q[k].quality_vs_random.toFixed(2), q[k].time.toFixed(1)]);

const kids = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Urgency-Aware Blood Allocation with QAOA")] }),
  P("Qiskit Fall Fest 2026 Hackathon | Domain 3: Healthcare", { run: { bold: true } }),
  P("Team: [TEAM NAME]   |   Members: [NAMES]   |   Repository: [GITHUB URL]"),
  P("Summary. We model the allocation of scarce, perishable blood units from a non-profit blood bank to urgent requests " +
    "as a QUBO with 15 qubits and solve it with QAOA on a noise-free Qiskit statevector simulator. QAOA finds the exact optimum " +
    "after sampling and feasibility filtering, but classical methods solve this instance in milliseconds. We therefore make no speedup claim. " +
    "The quantum result is measured by how much probability QAOA places on the optimal allocation compared with uniform random sampling."),

  H1("1. Introduction"),
  P("Blood cannot be manufactured and red cells expire after roughly six weeks. A blood bank must decide, repeatedly, who receives which units. " +
    "Serving the most critical patients, avoiding expiry waste, keeping deliveries short and protecting scarce O-negative stock are competing goals " +
    "under a hard limit on units. This project formulates a small version of that decision as a binary optimization problem and studies it with QAOA."),

  H1("2. Problem and stakeholders"),
  P("A non-profit blood bank holds stock in storage lots (blood group, units, days to expiry) and receives requests from partner centres " +
    "(blood group, units, urgency). The bank decides which request is served from which lot."),
  BUL("Patients: critical cases are served first."),
  BUL("Clinicians: they receive compatible blood quickly."),
  BUL("Blood bank administrators: fewer expired units and less wasted donor effort."),
  BUL("Donors: their donations are used rather than discarded."),
  P("Not covered: real donor logistics, antibody screening and clinical sign-off."),

  H1("3. Formulation"),
  H2("3.1 Decision variables"),
  P("x(r,l) is 1 if request r is served entirely from lot l, otherwise 0. Variables exist only for lots that are ABO/Rh compatible and hold enough stock, giving 10 binary variables."),
  H2("3.2 Objective"),
  P("Minimise the sum of c(r,l)*x(r,l), where c(r,l) = -W_SERVE*urgency*units + W_EXPIRY*(days_left/max_days)*units + W_DIST*distance/max_distance " +
    "+ W_MISMATCH*units (if the lot's group differs from the requested group) + W_UNIVERSAL*units (extra, if O-negative is spent on a non-O-negative request). " +
    "The competing goals are combined as a weighted sum with hand-tuned weights."),
  table(["Weight", "Value", "Meaning"], [
    ["W_SERVE", "3.0", "reward per urgency x unit delivered"], ["W_EXPIRY", "1.5", "prefer stock that expires sooner"],
    ["W_DIST", "1.0", "normalised delivery distance"], ["W_MISMATCH", "0.3", "non-identical blood group"],
    ["W_UNIVERSAL", "1.5", "O-negative spent on a non-O-negative patient"]], [2200, 1200, 5626]),
  H2("3.3 Constraints"),
  BUL("At most one lot per request: a quadratic penalty on every pair of variables of the same request."),
  BUL("Lot capacity: the sum of units*x for a lot must not exceed its stock. The Qiskit converter adds slack bits (5 in total) and a penalty."),
  BUL("Compatibility and stock: enforced by pruning variables."),
  BUL("Fairness: handled implicitly through urgency weights. Explicit fairness rules are future work."),
  H2("3.4 Test instance (synthetic)"),
  table(["Lot", "Group", "Units", "Days to expiry"], [["Hub-O+", "O+", "3", "4"], ["North-O-", "O-", "2", "9"], ["East-A+", "A+", "1", "2"]], [3000, 1800, 1800, 2426]),
  P(""),
  table(["Request", "Needs", "Units", "Urgency (3 = critical)"], [
    ["City Hospital", "A+", "2", "3"], ["Rural Clinic", "O+", "1", "1"], ["Trauma Centre", "O-", "2", "3"],
    ["Oncology Day Care", "B+", "1", "2"], ["Maternity Ward", "A+", "1", "3"]], [3000, 1800, 1800, 2426]),
  P("Distances are synthetic. The East lot is far from the Maternity Ward, which creates a trap for greedy methods. Assumptions: a request is served in full from one lot or not at all; red cells only; simplified ABO/Rh table; single time period."),

  H1("4. Method"),
  NUM("Build a Qiskit QuadraticProgram from the instance."),
  NUM("Convert with QuadraticProgramToQubo (penalty = 1.5 x the largest single-assignment reward). This yields 15 qubits."),
  NUM("Convert the QUBO to an Ising Hamiltonian (SparsePauliOp of Z and ZZ terms)."),
  NUM("Build the QAOA circuit: Hadamard on all qubits, then p layers of RZ/RZZ cost rotations and RX mixer rotations."),
  NUM("Minimise the expected cost with COBYLA, using 4 random restarts. The expected cost is computed from the exact statevector probabilities."),
  NUM("Sample 4000 shots, decode each bitstring, discard infeasible allocations and keep the best feasible one."),
  P("A consistency test checks that the Ising operator reproduces the QUBO cost and that the exact QUBO minimum decodes to the brute-force optimum. " +
    "The quantum component does real work: the final allocation is drawn from the optimised quantum state, and we measure how strongly that state favours the optimum."),

  H1("5. Architecture"),
  img("docs/architecture.png", 600, 283),

  H1("6. Results"),
  H2("6.1 Comparison with classical and exact baselines"),
  table(["Method", "Objective", "Gap", "Feasible", "Time (s)", "Expiring units unused"], tableMd, [3000, 1100, 900, 1000, 1000, 2026]),
  P(""),
  P("Lower objective is better. Brute force enumerates 216 assignments and MILP uses SciPy/HiGHS; both give the exact optimum. " +
    "Greedy by urgency is the only method that loses quality: it assigns the last Hub unit to the Maternity Ward and leaves the unit that expires in two days unused."),
  H2("6.2 QAOA diagnostics"),
  table(["p", "Depth", "P(optimal)", "vs uniform", "P(feasible)", "Quality*", "Time (s)"], diagRows, [800, 1000, 1700, 1400, 1400, 1300, 1426]),
  P("*Quality: 0 = uniform random sampling, 1 = exact ground state. Uniform probability of the optimal bitstring is 1/32768 (3.05e-5).", { run: { size: 18 } }),
  img("results/qaoa_vs_p.png", 560, 214),
  P("Interpretation. QAOA concentrates probability on the optimal allocation at a rate well above uniform sampling, and sampling plus filtering recovers the exact optimum. " +
    "However, the optimal state has under 0.2% probability, uniform random sampling with 4000 shots also finds the optimum (only 1024 decision patterns exist), " +
    "and the classical solvers are orders of magnitude faster. Deeper circuits did not give a clear improvement from p=2 to p=3 in energy or quality, which points to optimiser limits."),

  H1("7. Limitations"),
  BUL("Scale: 15 qubits and 5 requests. Classical methods solve it instantly. Simulation cost doubles with each extra qubit and slack bits grow with capacity."),
  BUL("No quantum speedup is claimed or observed."),
  BUL("Noise-free simulation: real hardware would degrade QAOA at circuit depths of 74 to 103."),
  BUL("Low success probability: the final answer relies on sampling and a feasibility filter."),
  BUL("Optimiser sensitivity: COBYLA can reach local minima; results vary with seed."),
  BUL("Hand-tuned weights and penalties; capacity is a soft penalty in the QUBO. An ablation over weights was not completed."),
  BUL("Clinical validity: urgency scores and weights are illustrative. Real use needs clinician-validated priorities, fairness review and full ABO/Rh/antibody logic."),
  BUL("Data: synthetic only. No real donor, patient or hospital data."),
  BUL("Model simplifications: one lot per request, red cells only, single time period."),

  H1("8. Future work"),
  P("Constraint-preserving mixers, partial fulfilment, multi-period inventory with expiry, real-hardware runs with error mitigation, and clinician-validated priority weights."),

  H1("9. Reproducibility"),
  P("Repository: [GITHUB URL]. Python 3.10+ (tested on 3.12.3); qiskit 2.6.2, qiskit-optimization 0.7.0, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2."),
  P("Commands: pip install -r requirements.txt; python tests/test_consistency.py; python src/main.py (about 1.5 minutes)."),

  H1("10. Credits"),
  BUL("Qiskit and qiskit-optimization (Apache-2.0)."),
  BUL("E. Farhi, J. Goldstone, S. Gutmann, A Quantum Approximate Optimization Algorithm, arXiv:1411.4028 (2014)."),
  BUL("SciPy (COBYLA, milp/HiGHS)."),
  BUL("All project code was written by [TEAM NAME]. Instance data are synthetic."),
];

const doc = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: "Arial", size: 40, bold: true }, paragraph: { spacing: { before: 0, after: 160 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 30, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 300, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 25, bold: true, color: "2F5496" }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 1 } } ] },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] } ] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: kids }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(path.join(__dirname, "report.docx"), buf); console.log("report.docx written"); });
