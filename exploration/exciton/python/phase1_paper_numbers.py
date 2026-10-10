#!/usr/bin/env python3
"""Generate paper/exciton_numbers.tex (macros) and paper/exciton_cases_table.tex from the Phase 1 result files, so that
every number in the note comes from a file.

    python3 exploration/exciton/python/phase1_paper_numbers.py
"""
import json, math, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "exploration/exciton/results/phase1"
OUT = ROOT / "paper"

def sci(x, digits=2):
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    if abs(round(m, digits) - 10) < 1e-12:
        m, e = 1.0, e + 1
    return f"${m:.{digits}f}\\times10^{{{e}}}$"

def load(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else None

mac = {}
def D(name, value):
    mac[name] = value

s0 = load(RES / "s0_report.json")
if s0:
    D("SzeroAdamsRhs", str(s0["adams_rtol1e-10"]["rhs"]))
    D("SzeroAdamsErr", sci(s0["adams_rtol1e-10"]["err"]))
    D("SzeroBdfErr", sci(s0["bdf_rtol1e-8"]["err"]))
ka = load(RES / "ka_report.json")
if ka:
    D("KAaRel", sci(ka["KA1a"]["rows"][-1]["rel_err"]))
    D("KAbRel", sci(max(r["rel_err"] for r in ka["KA1b"]["rows"])))
    D("KAcRel", sci(max(r["rel_err"] for r in ka["KA1c"]["rows"])))
    D("KAtwoRel", sci(ka["KA2"]["rel_err"]))
    D("KAfourRel", sci(max(r["rel_err"] for r in ka["KA4"]["rows"])))
    D("KAthreeHess", sci(max(r["hess_fd_rel"] for r in ka["KA3_rust_side"]["rows"])))
ka2 = load(RES / "ka_report_A2.json")
if ka2:
    D("KAcAtwoRel", sci(max(r["rel_err"] for r in ka2["KA1c"]["rows"])))
npt = RES / "ka3_numpy_report.txt"
if npt.exists():
    m = re.search(r'\{"KA3_numpy_side".*\}', npt.read_text())
    if m:
        d = json.loads(m.group(0))["KA3_numpy_side"]
        D("KAthreeE", sci(d["worst_energy_rel"]))
        D("KAthreeF", sci(d["worst_force_rel"]))
ff = load(RES / "ff_report.json")
if ff:
    D("FFworstRel", sci(max(b["worst_rel_err"] for b in ff["FF2a"]["blocks"])))
    D("FFBcmT", f'{ff["FF2b"]["B_c_numeric_T"]*1e3:.1f}')
    D("FFBcRel", sci(ff["FF2b"]["rel_err_vs_reference"]))
    D("FFspinNum", f'{ff["FF2c"]["field_leaves_IIA_T"]:.3f}')
    D("FFspinCF", f'{ff["FF2c"]["closed_form_spinodal_T"]:.4f}')
    D("FFstarts", str(sum(b["n_IIA"] + b["n_IIB"] + b["n_other_single_or_empty"] + b["n_unconverged"] for b in ff["FF2a"]["blocks"])))
ref = load(RES / "reference.json")
if ref:
    tab = ref["sandwich_K6_eH_over_elat"]
    for k, key in zip("ABCDEF", ["0.001", "0.01", "0.1", "0.3", "1.0", "3.0"]):
        D("Sand" + k, f"{tab[key]:#.3g}")
    tn = ref["sandwich_K6_d2nm"]
    for k, key in zip("ABCD", ["0.1", "0.3", "0.5", "0.75"]):
        D("SandN" + k, f"{tn[key]['ratio']:#.3g}")
p2 = load(ROOT / "exploration/exciton/results/phase2/summary.json")
if p2:
    D("PtwoAdev", sci(p2["P2a"]["worst_density_dev"]))
    D("PtwoAom", sci(p2["P2a"]["worst_omega_rel_err"]))
    D("PtwoBom", sci(p2["P2b"]["worst_omega_rel_err"]))
    D("PtwoBomTwo", sci(p2["P2b"]["worst_omega2_rel_err"]))
    D("PtwoBre", sci(p2["P2b"]["worst_abs_real_part"]))
    D("PtwoCom", sci(p2["P2c"]["worst_omega2_rel_err"]))
    D("PtwoCn", str(p2["P2c"]["n_unstable_solver"]))
D("LEANNEW", "Lean 4.34.1 with Mathlib tag v4.34.1 (commit d13f23b7)")

# ---- N-particle summary (written by phase1_summarise.py) and exploratory polish
summ = load(RES / "summary.json")
polish = {}
for fn in ("polish_exploratory_1.jsonl", "polish_exploratory_2.jsonl"):
    f = RES / fn
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line.startswith("{"):
                d = json.loads(line)
                polish[d["case"]] = d
rows_tex = []

def fmt_sci(x):
    if x == 0:
        return "$0$"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    return f"${m:.1f}\\times10^{{{e}}}$"

if summ:
    gates = summ["gates"]
    D("NRuns", str(gates["n_runs"]))
    D("NRunsCM", str(sum(c["n_runs"] for c in summ["cases"] if c["kernel"] != "N1")))
    D("NRunsN", str(sum(c["n_runs"] for c in summ["cases"] if c["kernel"] == "N1")))
    D("NCases", str(gates["n_cases"]))
    D("NNotConv", str(gates["n_not_converged"]))
    D("NLtwoViol", str(gates["L2_total_violations"]))
    cm = [c for c in summ["cases"] if c["kernel"] != "N1"]
    comm = [c for c in cm if c["torus"] != "T36s"]
    frus = [c for c in cm if c["torus"] == "T36s"]
    D("NCommTotal", str(len(comm)))
    D("NCommAttained", str(sum(1 for c in comm if c.get("EX1b_attained"))))
    D("NMinRatio", fmt_sci(min(c["min_ratio_minus_1"] for c in cm)))
    D("NFrusMin", fmt_sci(min(c["min_ratio_minus_1"] for c in frus)))
    D("NFrusMax", fmt_sci(max(c["min_ratio_minus_1"] for c in frus)))
    n1 = [c for c in summ["cases"] if c["kernel"] == "N1"]
    D("NNoneBest", f'{min(c["min_ratio"] for c in n1):.3f}')
    D("NNoneWorst", f'{max(c["min_ratio"] for c in n1):.3f}')
    order = ["K1", "K2", "K3", "K4", "K5", "K6", "N1"]
    cases = sorted(summ["cases"], key=lambda r: (order.index(r["kernel"]), r["rho"], r["torus"]))
    for r in cases:
        mr1 = r["min_ratio_minus_1"]
        ex1a = r.get("EX1a_pass")
        att = r.get("EX1b_attained")
        fr = r.get("EX1c_frustration")
        col_a = "--" if ex1a is None else ("pass" if ex1a else "FAIL")
        if att is not None:
            col_b = "yes" if att else "\\textbf{no}"
        elif fr is not None:
            col_b = f"+{fmt_sci(fr)[1:-1]}".join(["$", "$"])
        else:
            col_b = "--"
        if r["kernel"] == "N1":
            col_a = "ratio " + f'{r["min_ratio"]:.3f}'
        pol = polish.get(r["case"])
        col_p = "--" if pol is None else fmt_sci(pol["ratio_after_minus_1"])
        rows_tex.append(
            f"{r['kernel']} & {r['rho']:g} & {r['torus']} & {r['n_runs']} & {r['n_converged']} & "
            f"{fmt_sci(mr1)} & {('--' if r['kernel'] == 'N1' else r['n_within_attain_tol'])} & {col_a} & {col_b} & {col_p}")
# rows are separated by \\ and the last one has none: the main document writes it after \input (a trailing \\ before
# \bottomrule is followed by the file-end hook of recent LaTeX kernels and gives "Misplaced \noalign")
(OUT / "exciton_cases_table.tex").write_text("\\\\\n".join(rows_tex) + "\n" if rows_tex else "\\multicolumn{10}{c}{(no runs yet)}\n")

lines = ["% generated by exploration/exciton/python/phase1_paper_numbers.py -- do not edit"]
for k, v in mac.items():
    lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
# macros that need a default so the document compiles before everything exists
for k, v in {"NPARTABSTRACT": "", "VERIFYSTATUS": ""}.items():
    if k not in mac:
        lines.append(f"\\providecommand{{\\{k}}}{{{v}}}")
(OUT / "exciton_numbers.tex").write_text("\n".join(lines) + "\n")
print("macros:", len(mac), " case rows:", len(rows_tex))
