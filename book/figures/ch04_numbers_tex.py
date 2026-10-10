"""Chapter 4: write figures/ch04_numbers.tex from figures/ch04_numbers.json (+ the Lean/sympy logs recorded in ch04_lean_runs.json).
Every number that appears in chapters/ch04.tex is a macro \\cfv{key} defined here; an undefined key is a LaTeX error, so the text can only
quote numbers that were computed.  Run from book/figures:  ../../.venv/bin/python ch04_numbers_tex.py"""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
N = json.load(open(HERE/"ch04_numbers.json"))
L = json.load(open(HERE/"ch04_lean_runs.json")) if (HERE/"ch04_lean_runs.json").exists() else {}
K = {}

def sci(x, sig=3, texmath=False):
    """x -> a.bc \\times 10^{e} (math content)"""
    if x == 0: return "0"
    e = int(np.floor(np.log10(abs(x)))); m = x/10**e
    s = f"{m:.{sig-1}f}"
    if s.startswith("10"): s = f"{1.0:.{sig-1}f}"; e += 1
    return f"{s}\\times10^{{{e}}}" if e != 0 else s

def fix(x, nd):
    s = f"{x:.{nd}f}"
    return s

def sig(x, n):
    """n significant figures, plain decimal when the exponent is moderate, otherwise scientific"""
    if x == 0: return "0"
    e = int(np.floor(np.log10(abs(x))))
    if -4 <= e <= 4:
        nd = max(n - 1 - e, 0)
        return f"{x:.{nd}f}"
    return sci(x, n)

def put(key, tex): K[key] = tex
def num(key, x, n=3): put(key, f"\\ensuremath{{{sig(x, n)}}}")
def sci_(key, x, n=3): put(key, f"\\ensuremath{{{sci(x, n)}}}")

# ----------------------------------------------------------------------------------------------- constants and coefficients
C0 = N["constants"]
put("c", f"{C0['c_m_per_s']:.1f}"); put("V", f"{C0['V_cm3_per_mol']:.4f}")
num("theta", C0["theta_K_A"], 4); num("kT", C0["k_T_per_K_inv_A"], 3)
for k_, v in C0["alpha_A_powers"].items():
    if k_ in ("a2", "a3", "a4"): put(k_, f"{v:.2f}")
for name, d in N["coefficients"].items():
    num(f"{name}-val", d["value"], 5 if abs(d["value"]) < 0.1 or True else 4); put(f"{name}-pr", f"\\ensuremath{{{d['printed']}}}")
put("coef-maxdiff", f"{100*N['coefficients_max_rel_diff_to_printed']:.2f}")
ER = N["exact_rational"]
put("rat-maxdiff", f"\\ensuremath{{{sci(max(ER['max_rel_diff_to_closed_forms'], 1e-16), 1)}}}")
sci_("c10", ER["c_p"]["10"], 4); sci_("c11", ER["c_p"]["11"], 4)
# ----------------------------------------------------------------------------------------------- paper table, measured dispersion
MC = N["measured_cvode"]
put("cv-0.1", f"{sci(MC['paper_table_at']['0.1']['tot'], 4)}"); put("cv-0.2", f"{sci(MC['paper_table_at']['0.2']['tot'], 4)}")
put("cv-ratio", f"{MC['ratio_Cv_0p2_over_0p1']:.2f}"); put("cv-ratio-dev", f"{100*(8 - MC['ratio_Cv_0p2_over_0p1'])/8:.1f}")
put("cvT3-0.1", f"{MC['paper_cv_over_T3']['0.1']:.4f}"); put("cvT3-0.5", f"{MC['paper_cv_over_T3']['0.5']:.4f}")
put("cvT3-ph-0.5", f"{MC['paper_ph_over_T3']['0.5']:.4f}"); put("cvT3-ph-0.1", f"{MC['paper_ph_over_T3']['0.1']:.4f}")
put("repro-max", f"\\ensuremath{{{sci(MC['vs_paper_total']['max_abs_rel'], 2)}}}"); put("repro-median", f"\\ensuremath{{{sci(MC['vs_paper_total']['median_abs_rel'], 2)}}}")
put("repro-T-of-max", f"{MC['vs_paper_total']['at_T_of_max']:.2f}")
put("repro-ph-max", f"\\ensuremath{{{sci(MC['vs_paper_phonon']['max_abs_rel'], 2)}}}")
put("repro-vs-quad", f"\\ensuremath{{{sci(max(MC['vs_scipy_quad_max_rel'], 1e-16), 1)}}}")
put("repro-calls", f"{MC['rhs_calls_ph'] + MC['rhs_calls_rot']:,}".replace(",", "\\,"))
put("repro-seconds", f"{MC['seconds']:.0f}"); put("repro-load", f"{MC['load_avg_end']:.0f}")
put("n-T", str(MC['vs_paper_total']['n_temperatures']))
if "T_phonon_equals_roton_interp" in MC: put("T-cross", f"{MC['T_phonon_equals_roton_interp']:.2f}")
D0 = N.get("dispersion", {})
if D0:
    put("n-rows", str(D0["n_points_total"])); put("n-err-rows", str(D0["n_rows_with_uncertainty"])); put("n-gaps", str(D0["n_grid_steps_not_0p002"])); put("grid-until", f"{D0['grid_uniform_until_k']:.2f}"); put("grid-coarse", f"{D0['coarse_step']:.2f}"); put("maxon-k", f"{D0['maxon_k']:.3f}"); put("roton-k", f"{D0['roton_k']:.2f}")
    put("roton-K", f"{D0['roton_K']:.1f}"); put("rms-ueV", f"{1e3*D0['rms_residual_window_meV']:.2f}"); put("maxdev-ueV", f"{1e3*D0['max_abs_residual_window_meV']:.1f}")
    put("poly-dev-1", f"{100*D0['rel_dev_poly_at_1p0']:.1f}"); put("maxon-K", f"{D0['maxon_K']:.1f}")
H0 = N.get("heatmap", {})
if H0:
    for T_ in ("0.1", "0.3", "0.5", "1.0"):
        put(f"med-k-{T_}", f"{H0['median_k'][T_]:.3f}"); put(f"q90-k-{T_}", f"{H0['q90_k'][T_]:.3f}")
    put("lambda-0.1", f"{2*np.pi/H0['median_k']['0.1']:.0f}")
    for T_ in ("0.3", "0.5", "0.7", "1.0", "1.3"):
        put(f"share05-{T_}", f"{H0['share_above_0p5_percent'][T_]:.1f}")
    put("share05-0.3", f"{H0['share_above_0p5_percent']['0.3']:.2g}")
    put("share025-0.5", f"{H0['share_above_0p25_percent']['0.5']:.1f}")
# ----------------------------------------------------------------------------------------------- solver runs
B = N["bose_cvode"]
for r in B["runs"]:
    tag = f"{r['rtol']:.0e}".replace("e-0", "e-").replace("e-", "m")
    sci_(f"bose-err-{tag}", r["max_rel_err"], 2); put(f"bose-calls-{tag}", f"{r['rhs_calls']:,}".replace(",", "\\,"))
sci_("bose-quad", max(B["scipy_quad_max_rel_err"], 1e-16), 1)
rat_ = [r["max_rel_err"]/r["rtol"] for r in B["runs"]]
put("bose-ratio-min", f"{min(rat_):.1f}"); put("bose-ratio-max", f"{max(rat_):.0f}")
put("bose-XEND", f"{B['XEND']:.0f}")
M = N["model_cvode"]
r12 = [r for r in M["runs"] if r["rtol"] == 1e-12][0]
sci_("model-abserr", r12["max_abs_err_vs_mp"], 1); put("model-calls", f"{r12['rhs_calls']:,}".replace(",", "\\,"))
put("model-seconds", f"{r12['seconds']:.0f}")
put("nT-all", str(M["n_T_all"])); put("nT-log", str(M["n_T_log"] - 1)); put("nT-lin", str(M["n_T_lin"])); put("model-load", f"{r12['load_avg_end']:.0f}")
sci_("model-raw-abserr", M["unsubtracted"]["max_abs_err_vs_mp"], 1)
sci_("model-abserr-0.1", M["abs_err_subtracted_at_0p1"], 1); sci_("model-raw-abserr-0.1", M["abs_err_unsubtracted_at_0p1"], 1); put("model-gain", f"{M['gain_at_0p1']:.0f}")
LD = N["ladder"]
for nm, d in LD["lines"].items():
    if "fitted_slope" in d:
        put(f"slope-{nm}", f"{d['fitted_slope']:.2f}"); put(f"slope-exp-{nm}", str(d["expected_slope"]))
        put(f"ratio-{nm}", f"{d['ratio_to_next_term_lowestT']:.3f}"); put(f"Trange-lo-{nm}", f"{d['T_range'][0]:.3g}"); put(f"Trange-hi-{nm}", f"{d['T_range'][1]:.3g}")
sci_("floor", max(LD["solver_floor_abs"], 1e-16), 1); sci_("floor-0.1", max(LD["solver_floor_abs_at_0p1"], 1e-16), 1)
fl = N["model_cvode"]["abs_err_1e8"]
for T_ in ("0.005", "0.1"):
    sci_(f"sub8-{T_}", fl["subtracted"][T_], 1); sci_(f"raw8-{T_}", fl["unsubtracted"][T_], 1)
r12_ = [r for r in M["runs"] if r["rtol"] == 1e-12][0]
sci_("floor-0.02", r12_["abs_err_vs_mp"]["0.02"], 1)
put("slope-maxdev", f"{max(abs(d['fitted_slope'] - d['expected_slope']) for d in LD['lines'].values() if 'fitted_slope' in d):.2f}")
REC = N["coefficient_recovery"]
for p_, nm in (("5", "C"), ("6", "D"), ("7", "E"), ("8", "K"), ("9", "L")):
    put(f"rec-0.02-{nm}", f"{100*REC[p_]['rel_err_at_0p02']:.2g}"); put(f"rec-0.05-{nm}", f"{100*REC[p_]['rel_err_at_0p05']:.2g}")
NC = N["negative_controls_numerical"]
sci_("ctl-D-0.1", abs(NC["D_15121"]["effect_on_CV_over_AT3"]["0.1"]), 2); sci_("ctl-L-0.1", abs(NC["L_54"]["effect_on_CV_over_AT3"]["0.1"]), 2)
sci_("ctl-K-0.1", abs(NC["K_8a2a3"]["effect_on_CV_over_AT3"]["0.1"]), 2); sci_("ctl-next-0.1", abs(NC["next_term_c10_over_AT3"]["0.1"]), 2)
sci_("ctl-D-0.05", abs(NC["D_15121"]["effect_on_CV_over_AT3"]["0.05"]), 2); sci_("ctl-next-0.05", abs(NC["next_term_c10_over_AT3"]["0.05"]), 2)
sci_("ctl-K-0.05", abs(NC["K_8a2a3"]["effect_on_CV_over_AT3"]["0.05"]), 2)
put("ctl-D-rel", f"\\ensuremath{{{sci(abs(NC['D_15121']['rel_change_of_coefficient']), 2)}}}"); put("ctl-L-rel", f"{100*abs(NC['L_54']['rel_change_of_coefficient']):.1f}")
put("ctl-K-rel", f"{100*abs(NC['K_8a2a3']['rel_change_of_coefficient']):.0f}")
put("ctl-D-ratio", f"{abs(NC['next_term_c10_over_AT3']['0.1'])/abs(NC['D_15121']['effect_on_CV_over_AT3']['0.1']):.0f}")
put("ctl-L-ratio", f"{abs(NC['next_term_c10_over_AT3']['0.1'])/abs(NC['L_54']['effect_on_CV_over_AT3']['0.1']):.0f}")
put("ctl-K-ratio", f"{abs(NC['K_8a2a3']['effect_on_CV_over_AT3']['0.1'])/abs(NC['next_term_c10_over_AT3']['0.1']):.1f}")
# ----------------------------------------------------------------------------------------------- budget and asymptotics
BU = N["budget"]
for T_ in ("0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "1.0"):
    b = BU[T_]
    sci_(f"bud-trunc-{T_}", abs(b["series6_over_poly_minus1"]), 2); sci_(f"bud-model-{T_}", abs(b["poly_over_measured_ph_minus1"]), 2); sci_(f"bud-tot-{T_}", abs(b["series6_over_measured_ph_minus1"]), 2)
    put(f"bud-trunc-pct-{T_}", f"{100*abs(b['series6_over_poly_minus1']):.2g}"); put(f"bud-model-pct-{T_}", f"{100*abs(b['poly_over_measured_ph_minus1']):.2g}")
    put(f"bud-tot-pct-{T_}", f"{100*abs(b['series6_over_measured_ph_minus1']):.2g}")
for key in ("first_T_series6_vs_poly_exceeds_1pct", "first_T_series6_vs_poly_exceeds_0p1pct", "first_T_series6_vs_measured_ph_exceeds_1pct"):
    if BU.get(key) is not None: put("bud-" + key, f"{BU[key]:.2f}")
PU = N["paper_uncertainty_table"]
for T_ in ("0.1", "0.2", "0.3", "0.5", "0.7"):
    if T_ in PU: put(f"paper-unc-{T_}", f"{100*PU[T_]:.2g}")
CP = N["critical_point"]
num("uc-abs", CP["abs_u_c_per_A"], 3); num("uc-K", CP["hbar_c_u_c_over_kB_K"], 3); num("uc-inv", CP["inverse_K_inv"], 3)
mm = lambda x: "\\ensuremath{" + f"{x:.3f}" + "}"
put("uc-k-re", mm(CP["k_c"][0])); put("uc-k-im", mm(CP["k_c"][1])); put("uc-u-re", mm(CP["u_c"][0])); put("uc-u-im", mm(CP["u_c"][1]))
for p_ in ("5", "6", "7", "8", "9", "10", "11", "12", "13", "14"):
    x_ = ER["ratio_to_A"][p_]
    put(f"rA-{p_}", "\\ensuremath{" + (f"{x_:.2f}" if abs(x_) < 10 else f"{x_:.0f}") + "}")
RT = N["root_test"]
for k_ in ("p20", "p30", "p40", "p50", "p60"): num(f"root-{k_}", RT[k_], 3)
AS = N["asymptotic"]
for T_ in ("0.2", "0.3", "0.5", "0.8"):
    a = AS[T_]; put(f"best-order-{T_}", str(a["best_order"])); sci_(f"best-err-{T_}", a["best_rel_err"], 2); put(f"smallest-order-{T_}", str(a["smallest_term_order"]))
    sci_(f"err9-{T_}", a["err_at_order_9"], 2)
ef = AS["envelope_fit"]; num("fit-b", ef["b_K"], 3); num("fit-b-pred", ef["predicted_b_K"], 3); put("fit-s", "\\ensuremath{" + f"{ef['s']:.1f}" + "}")
put("fit-T-lo", f"{ef['T_range'][0]:.2f}"); put("fit-T-hi", f"{ef['T_range'][1]:.1f}")
for T_, d_ in AS["pstar"].items():
    put(f"pstar-{T_}", str(d_["pstar"])); put(f"pstar-pred-{T_}", f"{d_['predicted']:.0f}")
# ----------------------------------------------------------------------------------------------- solver module and probes
if "solver_probe_fixed" in N and "solver_probe_stale_venv" in N:
    Pn = N["solver_probe_fixed"]; Po = N["solver_probe_stale_venv"]
    def pick(P, method, problem, rtol): return [r for r in P["runs"] if r["method"] == method and r["problem"] == problem and r["rtol"] == rtol][0]
    ac = pick(Po, "adams", "cos", 1e-6); ab = pick(Po, "adams", "bose3", 1e-6); bb = pick(Po, "bdf", "bose3", 1e-6)
    put("probe-cap", f"{Po['cap_calls']:,}".replace(",", "\\,"))
    put("old-adams-cos-t", f"{ac.get('last_t', 70):.0f}" if ac["status"] != "ok" else "70")
    if ab["rel_err"] is not None:
        sci_("old-adams-bose-err", ab["rel_err"], 2); put("old-adams-bose-calls", f"{ab['rhs_calls']:,}".replace(",", "\\,")); put("old-adams-bose-ratio", f"{ab['rel_err']/ab['rtol']:.0f}")
    sci_("old-bdf-bose-err", bb["rel_err"], 2); put("old-bdf-bose-calls", f"{bb['rhs_calls']:,}")
    put("old-bdf-landing-err", str(Po["landing"]["bdf"]["n_solver_errors"])); put("old-adams-landing-cap", str(Po["landing"]["adams"]["n_over_cap"]))
    put("probe-landing-n", str(Po["landing"]["bdf"]["n_endpoints"]))
    dn = pick(Pn, "adams", "decay", 1e-8); bn = pick(Pn, "adams", "bose3", 1e-6)
    put("new-adams-decay-calls", str(dn["rhs_calls"])); put("new-adams-bose-calls", str(bn["rhs_calls"])); sci_("new-adams-bose-err", bn["rel_err"], 2)
    put("new-landing-err", str(Pn["landing"]["adams"]["n_solver_errors"] + Pn["landing"]["bdf"]["n_solver_errors"] + Pn["landing"]["adams"]["n_over_cap"] + Pn["landing"]["bdf"]["n_over_cap"]))
    put("rs-commit-short", N["text_constants"]["rs_commit_short"]); put("rs-sha-short", Pn["sha256"][:12])
# ----------------------------------------------------------------------------------------------- Lean / sympy run records
# fixed facts read from files (see facts/ch04_report.md)
CM = N["lean_certificate_monomials"]["per_theorem"]
put("cert-kSq0", str(CM["kSq0_eq"])); assert CM["kSq0_eq"] == CM["density_of_states"]
_k = [CM[f"kPow{i}_eq"] for i in range(2, 8)]
put("cert-list", ", ".join(str(x) for x in _k[:-1]) + " and " + str(_k[-1]))
put("sympy-seconds", f"{N['text_constants']['sympy_seconds']:.0f}")
put("lean-toolchain", N["text_constants"]["lean_toolchain"])
out = ["% generated by figures/ch04_numbers_tex.py from figures/ch04_numbers.json -- do not edit",
       "\\makeatletter",
       "\\providecommand{\\cfv}[1]{\\ifcsname cfv@#1\\endcsname\\csname cfv@#1\\endcsname\\else\\PackageError{ch04}{Undefined number key #1}{Run ch04_numbers_tex.py}\\fi}"]
for k_, v in sorted(K.items()):
    out.append("\\expandafter\\gdef\\csname cfv@%s\\endcsname{%s}" % (k_, v))
out.append("\\makeatother")
(HERE/"ch04_numbers.tex").write_text("\n".join(out) + "\n")
print(len(K), "keys written")
