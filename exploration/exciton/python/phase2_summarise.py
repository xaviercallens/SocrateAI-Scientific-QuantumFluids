#!/usr/bin/env python3
"""Evaluate the Phase 2 gates (docs/designs/EXCITON_FLUID_PHASE2_PREREG.md) from the mean-field run record.

    python3 phase2_summarise.py <mf_report.json> <reference.json> <out.json>

Gates, as registered:
  P2-a  kernel B, 50 random starts: converged flow, max|n-n0|/n0 <= 1e-8 and |omega-omega0|/|omega0| <= 1e-10
  P2-b  kernel B, solver linearisation vs Bogoliubov: |omega-omega_ref|/omega_ref <= 1e-6, |Re lambda| <= 1e-8 (255 modes)
  P2-c  kernel C: (i) linearisation reproduces omega^2 (rel 1e-6 or abs 1e-9) with the same sign pattern;
        (ii) flow from uniform + 1e-3 noise: modulation >= 0.1 and omega below uniform by >= 1e-3 (relative)
  P2-d  planted bug (U(0) doubled) must violate P2-a on every start
"""
import json, math, sys
from pathlib import Path

rep = json.loads(Path(sys.argv[1]).read_text())
ref = json.loads(Path(sys.argv[2]).read_text())
out = {}

def eig2(M11, M12, M21, M22):
    """eigenvalues of the real 2x2 matrix -> list of complex numbers"""
    tr, det = M11 + M22, M11 * M22 - M12 * M21
    disc = tr * tr - 4 * det
    if disc >= 0:
        r = math.sqrt(disc)
        return [complex((tr + r) / 2, 0), complex((tr - r) / 2, 0)], tr, det
    r = math.sqrt(-disc)
    return [complex(tr / 2, r / 2), complex(tr / 2, -r / 2)], tr, det

# ---- P2-a
a = rep["P2a"]
dev = max(r["max_rel_dev"] for r in a)
om = max(r["omega_rel_err"] for r in a)
out["P2a"] = {"n_runs": len(a), "n_converged": sum(1 for r in a if r["converged"]),
              "worst_density_dev": dev, "worst_omega_rel_err": om,
              "pass": len(a) == 50 and all(r["converged"] for r in a) and dev <= 1e-8 and om <= 1e-10}

# ---- P2-b and P2-c(i)
def lin_gate(name, rows, key_ref):
    worst_rel_om, worst_re, worst_om2 = 0.0, 0.0, 0.0
    sign_mismatch = 0
    n_unstable_solver = 0
    n_unstable_formula = 0
    for r in rows:
        k = f'{r["i"]},{r["j"]}'
        om2_ref = ref[key_ref]["omega2"][k]
        ev, tr, det = eig2(r["M11"], r["M12"], r["M21"], r["M22"])
        om2_sol = det - (tr / 2) ** 2 * 0  # for tr ~ 0, omega^2 = det
        om2_sol = det
        scale = max(abs(om2_ref), 1e-9)
        worst_om2 = max(worst_om2, abs(om2_sol - om2_ref) / scale)
        worst_re = max(worst_re, abs(tr) / 2)
        if (om2_sol < 0) != (om2_ref < 0):
            sign_mismatch += 1
        n_unstable_solver += om2_sol < 0
        n_unstable_formula += om2_ref < 0
        if om2_ref > 0 and om2_sol > 0:
            worst_rel_om = max(worst_rel_om, abs(math.sqrt(om2_sol) - math.sqrt(om2_ref)) / math.sqrt(om2_ref))
    return {"n_modes": len(rows), "worst_omega_rel_err": worst_rel_om, "worst_omega2_rel_err": worst_om2,
            "worst_abs_real_part": worst_re, "sign_mismatches": sign_mismatch,
            "n_unstable_solver": n_unstable_solver, "n_unstable_formula": n_unstable_formula}

pb = lin_gate("B", rep["lin_B"], "B")
pb["pass"] = pb["n_modes"] == 255 and pb["worst_omega_rel_err"] <= 1e-6 and pb["worst_abs_real_part"] <= 1e-8 and pb["sign_mismatches"] == 0
out["P2b"] = pb
pc = lin_gate("C", rep["lin_C"], "C")
pc["pass_i"] = pc["n_modes"] == 255 and pc["worst_omega2_rel_err"] <= 1e-6 and pc["sign_mismatches"] == 0 and pc["n_unstable_formula"] > 0
fl = rep["P2c_flow"]
pc["flow"] = fl
pc["pass_ii"] = bool(fl["max_rel_modulation"] >= 0.1 and fl["rel_below"] >= 1e-3)
pc["pass"] = pc["pass_i"] and pc["pass_ii"]
out["P2c"] = pc

# ---- P2-d
bug = rep["P2d"]
out["P2d"] = {"n_runs": len(bug), "min_density_dev": min(r["max_rel_dev"] for r in bug),
              "pass": len(bug) > 0 and all(r["max_rel_dev"] > 1e-8 for r in bug)}
out["all_pass"] = all(out[k]["pass"] for k in ("P2a", "P2b", "P2c", "P2d"))
Path(sys.argv[3]).write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in out.items()}))
for k in ("P2a", "P2b", "P2c", "P2d"):
    print(k, {kk: vv for kk, vv in out[k].items() if kk != "flow"})
