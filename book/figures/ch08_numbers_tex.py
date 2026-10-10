"""Chapter 8: every number quoted in chapters/ch08.tex is a macro \\ceightV{key} defined in figures/ch08_numbers.tex, which this
script writes from figures/ch08_numbers.json (the output of ch08_zerosound.py, ch08_window.py, ch08_timedomain.py,
ch08_fermisurface.py, ch08_vlasov.py, ch08_wheel_check.py, ch08_solver_sweep.py).  An undefined key is a LaTeX error.
Run from book/figures:   ../../.venv/bin/python ch08_numbers_tex.py"""
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = json.loads((HERE / "ch08_numbers.json").read_text())
Z, W, TD, FS, V = N["zerosound"], N["window"], N["timedomain"], N["fermisurface"], N["vlasov"]
SW = N["cvode_output_spacing_sweep"]["results"]
STALE, FRESH = N["python_module_stale_venv"], N["python_module_5db8041"]
out = {}


def fx(x, nd=3): return f"{x:.{nd}f}"
def sci(x, nd=1):
    if x == 0: return "0"
    e = int(math.floor(math.log10(abs(x)))); m = x / 10 ** e
    if round(m, nd) >= 10: m /= 10; e += 1
    return rf"\ensuremath{{{m:.{nd}f}\times10^{{{e}}}}}"
def pc(x, nd=2): return rf"{x * 100:.{nd}f}\,\%"
def put(k, v): out[k] = v


def tag(F):
    s = f"{abs(F):g}".replace(".", "p")
    return ("m" if F < 0 else "") + s


# ------------------------------------------------------------------------------------------------------ roots, weights (Table 1)
for F in (0.1, 0.5, 1.0, 4.0, 12.0, 40.0):
    r = Z["roots_2d"][str(F)]; t = tag(F)
    put(f"s0_{t}", fx(r["s0"], 4)); put(f"qc_{t}", fx(r["q_c_over_kF"], 3)); put(f"W_{t}", fx(r["pole_weight_W"], 4))
    put(f"frac_{t}", fx(r["pole_fraction"], 4)); put(f"fracpc_{t}", pc(r["pole_fraction"], 1)); put(f"amp_{t}", fx(r["uniform_IC_pole_amplitude_2R"], 4))
    put(f"cont_{t}", fx(r["uniform_IC_continuum_weight"], 4)); put(f"s1_{t}", fx(r["first_sound"], 4)); put(f"s0m1_{t}", fx(r["s0"] - 1, 4))
for F in (0.5, 1.0, 4.0, 12.0):
    put(f"s3_{tag(F)}", fx(Z["roots_3d"][str(F)], 4))
put("s3m1_0p5", fx(Z["roots_3d"]["0.5"] - 1, 4)); put("s3m1_1", fx(Z["roots_3d"]["1.0"] - 1, 4))
put("Fstar", fx(W["F_star_s0_equals_2"]["F"], 3))
F90 = (math.sqrt(10) - 1) / 2; put("Fninety", fx(F90, 3))
A = Z["asymptotics"]
put("asymSmall1e3", fx(A["s0_minus1_over_Fsq_over_2"][1], 4)); put("asymLarge1e3", fx(A["s0_over_sqrtFover2"][0], 4)); put("asymLargeThree1e3", fx(A["s3_over_sqrtFover3"][0], 4))
put("asymThreeSmall", fx(A["s3_minus1_over_2exp_m2_m2overF"][1], 8))
put("partialFracErr", sci(A["s0_sq_partial_fractions_max_abs_err"], 1))
# CVODE continuation
for d in (2, 3):
    c = Z[f"cvode_continuation_{d}d"]
    put(f"contErr{d}", sci(c["max_rel_err_s"], 1)); put(f"contRes{d}", sci(c["max_residual_original_equation"], 1))
    put(f"contSteps{d}", c["driver_stats"].split("steps=")[1].split()[0])
put("contPoints", str(Z["cvode_continuation_2d"]["n_points"])); put("contRtol", sci(Z["cvode_continuation_2d"]["rtol"], 0))
S = Z["sum_rule_2d"]
put("sumDev", sci(S["max_abs_deviation"], 1)); put("sumRel", sci(S["S_cont_closed_form_vs_definition_max_rel"], 1))
for row in S["rows"]:
    if row["F"] in (0.5, 1.0, 4.0):
        put(f"sumCont_{tag(row['F'])}", fx(row["continuum"], 6)); put(f"sumPole_{tag(row['F'])}", fx(row["pole"], 6))

# ------------------------------------------------------------------------------------------------------ time domain
U, K, FT, SV = TD["uniform_IC"], TD["kick_IC"], TD["pole_fits"], TD["solver_verification"]
for F in (-0.5, 0.0, 0.5, 1.0, 4.0, 12.0):
    t = tag(F); put(f"errU_{t}", sci(U[str(F)]["max_abs_err"], 1)); put(f"edrift_{t}", sci(U[str(F)]["max_rel_energy_drift"], 1))
    put(f"stepsU_{t}", f"{U[str(F)]['steps']:,}".replace(",", r"\,")); put(f"rhsU_{t}", f"{U[str(F)]['rhs_evals']:,}".replace(",", r"\,")); put(f"wallU_{t}", fx(U[str(F)]["wall_s"], 1))
for F in (-0.5, 0.5, 1.0, 4.0, 12.0):
    put(f"errK_{tag(F)}", sci(K[str(F)]["max_abs_err"], 1))
for F in (0.5, 1.0, 4.0, 12.0):
    t = tag(F); put(f"fitW_{t}", sci(FT[str(F)]["rel_dev_omega"], 1)); put(f"fitA_{t}", sci(FT[str(F)]["rel_dev_amp"], 1))
put("omegaFit4", fx(FT["4.0"]["omega_fit"], 9)); put("ampFit4", fx(FT["4.0"]["amp_fit"], 6))
put("omegaFit12", fx(FT["12.0"]["omega_fit"], 8)); put("omegaFit05", fx(FT["0.5"]["omega_fit"], 9)); put("sZeroHalf", fx(Z["roots_2d"]["0.5"]["s0"], 9))
E = TD["envelope_exponents"]["per_F"]
for F in (-0.5, 0.0, 1.0, 4.0):
    put(f"expo_{tag(F)}", fx(E[str(F)]["slope_t10_to_60"], 3))
for m_, rt in (("bdf", "1e-06"), ("adams", "1e-06"), ("bdf", "1e-08"), ("adams", "1e-08"), ("bdf", "1e-10"), ("adams", "1e-10")):
    r = SV[f"{m_}_{rt}"]; put(f"tol_{m_}_{rt[-2:]}", sci(r["max_abs_err_vs_J0"], 1)); put(f"tolsteps_{m_}_{rt[-2:]}", f"{r['steps']:,}".replace(",", r"\,"))
put("adamsF4", fx(SV["F4_adams_rtol1e-8"]["max_abs_err_vs_semianalytic"], 2))
put("nNinetySix", sci(SV["F4_N96_vs_N64_max_abs_diff"], 1)); put("wallNinetySix", fx(SV["F4_N96_wall_s"], 0)); put("wallSixtyFour", fx(SV["F4_N64_wall_s"], 1))
put("normDrift", sci(TD["norm_conservation_F0"]["max_abs_norm2_minus_1"], 1)); put("mSqEnd", fx(TD["norm_conservation_F0"]["m2_at_t60"], 4))
G = TD["unstable_F_minus2"]
put("growthPred", fx(G["predicted_growth_rate"], 6)); put("growthFit", fx(G["fitted_growth_rates"]["10-14"], 6)); put("growthEdrift", sci(G["max_rel_energy_dev"], 1))
# machine caveat: the same problem and tolerances took different wall times at different loads
put("wallZeroA", fx(U["0.0"]["wall_s"], 1)); put("wallZeroB", fx(SV["bdf_1e-08"]["wall_s"], 1))
# Fermi-surface reconstruction
put("reconF0", sci(FS["reconstruction_vs_nodes_F0"]["max_abs_diff"], 1)); put("reconF4", sci(FS["reconstruction_vs_nodes_F4"]["max_abs_diff"], 1))
put("nuMaxFour12", fx(FS["max_abs_nu_F4"]["12"], 2)); put("nuMinFour24", fx(FS["min_abs_nu_F4"]["24"], 2))

# ------------------------------------------------------------------------------------------------------ solver notes (module and sweep)
def fmt_status(d): return sci(d["abs_err_m"], 1) if d["status"] == "ok" else "failed"
for nm, M in (("stale", STALE), ("fresh", FRESH)):
    for m_ in ("bdf", "adams"):
        for rt in ("1e-06", "1e-08", "1e-10"):
            put(f"mod_{nm}_{m_}_{rt[-2:]}", fmt_status(M["A"][f"{m_}_rtol{float(rt):g}"]))
        put(f"modB_{nm}_{m_}", fmt_status(M["B"][f"{m_}_rtol1e-08"]))
put("modStaleDate", STALE["module_file_date"].split()[0]); put("modFreshCommit", FRESH["commit"][:7])
put("sweepAdamsBad", sci(SW["analytic_jacobian_adams"]["0.1"]["max_abs_err"], 1)); put("sweepAdamsBadFD", sci(SW["differenced_jacobian_adams"]["0.1"]["max_abs_err"], 1))
good = [v["max_abs_err"] for dt, v in SW["analytic_jacobian_adams"].items() if dt != "0.1"] + [v["max_abs_err"] for dt, v in SW["differenced_jacobian_adams"].items() if dt != "0.1"]
put("sweepAdamsGoodMax", sci(max(good), 1)); put("sweepAdamsGoodMin", sci(min(good), 1))
put("sweepBdfMax", sci(max(v["max_abs_err"] for k, row in SW.items() if "bdf" in k for v in row.values()), 1))
put("sweepBdfMin", sci(min(v["max_abs_err"] for k, row in SW.items() if "bdf" in k for v in row.values()), 1))

# ------------------------------------------------------------------------------------------------------ Vlasov
for k in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
    m = V["maxwell"][str(k)]; t = tag(k)
    put(f"vmW_{t}", fx(m["theory_omega"], 4)); put(f"vmG_{t}", fx(-m["theory_gamma"], 4)); put(f"vmWs_{t}", fx(m["fit_nv512"]["omega"], 4)); put(f"vmGs_{t}", fx(-m["fit_nv512"]["gamma"], 4))
    put(f"vmRelG_{t}", pc(m["rel_diff_gamma"], 2)); put(f"vmRelW_{t}", pc(m["rel_diff_omega"], 3))
put("vmConvMax", sci(max(v["max_abs_gamma_change_nv128_256_vs_512"] for v in V["maxwell"].values()), 1))
put("vmCertRe", fx(V["maxwell_certified_root_k0.5"]["this_calculation"][0], 9)); put("vmCertIm", fx(-V["maxwell_certified_root_k0.5"]["this_calculation"][1], 9))
put("vmProgRe", fx(V["maxwell_certified_root_k0.5"]["programme_value"][0], 9)); put("vmProgIm", fx(-V["maxwell_certified_root_k0.5"]["programme_value"][1], 9))
for k in (0.3, 0.5, 0.8):
    f = V["fermi"][str(k)]; t = tag(k)
    put(f"vfW_{t}", fx(f["theory_omega"], 4)); put(f"vfWs_{t}", fx(f["fit_nv512"]["omega"], 4)); put(f"vfWb_{t}", fx(f["waterbag_omega"], 4))
    put(f"vfG_{t}", sci(abs(f["theory_gamma"]), 1)); put(f"vfGs_{t}", sci(abs(f["fit_nv512"]["gamma"]), 1)); put(f"vfRelW_{t}", pc(f["rel_diff_omega"], 3))
    put(f"vfRes_{t}", sci(f["fit_nv512"]["rms_over_max"], 1))
    put(f"vfRelG_{t}", pc(abs(f["fit_nv512"]["gamma"] / f["theory_gamma"] - 1), 2))
put("vfWeakG_03", sci(abs(V["fermi_weak_damping_formula_check"]["0.3"]["weak"]), 1))
put("vfG_0p3", sci(abs(V["fermi_weak_damping_formula_check"]["0.3"]["weak"]), 1))      # at k = 0.3 the weak-damping formula is the reliable theory value (the continued root is noise-limited)
cc = V["maxwell_certified_root_k0.5"]
put("vmCertDiff", sci(max(abs(cc["this_calculation"][0] - cc["programme_value"][0]), abs(cc["this_calculation"][1] - cc["programme_value"][1])), 1))
fs_ = V["free_streaming"]
put("fsMax", sci(fs_["max_abs_dev"], 1)); put("fsFloor", sci(fs_["floor_at_t40"], 1)); put("fsRecur", fx(fs_["recurrence_time"], 0))
C = V["conservation_k0.5_nv512"]
put("consMassM", sci(abs(C["maxwell"]["mass_rel_drift_at_t40"]), 1)); put("consEnM", sci(C["maxwell"]["energy_max_rel_dev"], 1)); put("consEnF", sci(C["fermi"]["energy_max_rel_dev"], 1))
put("fermiA", fx(V["background"]["normalisation_A"], 6))
put("vmLost03", pc(1 - math.exp(V["maxwell"]["0.3"]["theory_gamma"] * 40.0), 0))
# the rate returned by the Rust peak-spacing estimator for the degenerate run at k = 0.5, n_v = 512 (the one that came out positive)
for line in V["rust_peak_fit_tables"]["fermi"].splitlines()[1:]:
    kk_, nv_, rate_ = line.split(",")[:3]
    if kk_ == "0.5" and nv_ == "512": put("peakFitFermi05", sci(float(rate_), 1))
put("epsFS", fx(FS["epsilon"], 2))
put("fsumA", fx(K["-0.5"]["fsum_rule_slope_at_0"], 4)); put("fsumB", fx(K["12.0"]["fsum_rule_slope_at_0"], 4))
put("ratioNinetySix", fx(SV["F4_N96_wall_s"] / SV["F4_N64_wall_s"], 1))
# Lean: compile result of book/lean/Ch08_ZeroSound2D.lean (written by hand from the compile log into ch08_lean.json)
LJ = HERE / "ch08_lean.json"
if LJ.exists():
    L = json.loads(LJ.read_text()); put("leanAxioms", L["axioms_text"]); put("leanSeconds", str(L.get("cpu_seconds_user", "")))
else:
    put("leanAxioms", "[compile pending]"); put("leanSeconds", "")

# the exact STATS line printed by the driver for the F = 4 run quoted in the rustbox of the chapter
STJ = json.loads(Path("/mnt/data/xdev-cache/book_ch08/kinetic/stats.json").read_text())
(HERE / "ch08_statsline.txt").write_text(STJ["uni_p4"]["raw"] + "\n")
put("stepsN96", f"{STJ['uni_p4_N96']['steps']:,}".replace(",", r"\,")); put("stepsN64", f"{STJ['uni_p4']['steps']:,}".replace(",", r"\,"))

lines = ["% generated by figures/ch08_numbers_tex.py from figures/ch08_numbers.json -- do not edit"]
for k, v in out.items():
    lines.append(rf"\expandafter\def\csname ceight@{k}\endcsname{{{v}}}")
(HERE / "ch08_numbers.tex").write_text("\n".join(lines) + "\n")
print(len(out), "macros written to", HERE / "ch08_numbers.tex")
