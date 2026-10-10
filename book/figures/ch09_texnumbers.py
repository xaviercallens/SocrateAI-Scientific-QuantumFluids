#!/usr/bin/env python3
"""Chapter 9: turn figures/ch09_numbers.json into TeX macros (figures/ch09_numbers.tex), so that every number typeset in chapters/ch09.tex is the
number in the JSON, formatted here and nowhere else.  A macro holds MATH-MODE material without the dollar signs: write $\\cnineForceTen$ in the text.
    .venv/bin/python -I book/figures/ch09_texnumbers.py
"""
import json, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
R = json.load(open(HERE / "ch09_numbers.json"))
M = {}

def sci(x, sig=2):
    """a x 10^b with `sig` significant digits"""
    if x == 0: return "0"
    e = int(math.floor(math.log10(abs(x)))); m = x / 10 ** e
    m = round(m, sig - 1)
    if abs(m) >= 10: m /= 10; e += 1
    s = f"{m:.{sig - 1}f}"
    return f"{s}\\times10^{{{e}}}"
def fix(x, nd=2): return f"{x:.{nd}f}"
def pct(x, nd=2): return f"{100 * x:.{nd}f}"
def put(name, val): M[name] = val
def sciS(x, sig=2): return sci(x, sig)

F = R["force"]; W = {(w["lo"], w["hi"]): w for w in F["windows"]}
# ------------------------------------------------------------------ force
put("ForceTc", sci(F["max_dF_t_le_0p3"])); put("ForceLtOne", sci(W[(0, 1)]["max_dF"])); put("ForceFive", sci(W[(1, 5)]["max_dF"])); put("ForceTen", sci(W[(5, 10)]["max_dF"]))
put("ForceTwenty", sci(W[(10, 20)]["max_dF"])); put("ForceThirty", sci(W[(20, 30)]["max_dF"])); put("ForceForty", sci(W[(30, 40)]["max_dF"])); put("ForceFifty", sci(W[(40, 50)]["max_dF"]))
put("ForceMax", fix(F["max_abs_F_ref_0_50"], 2)); put("ForceMaxT", fix(F["t_of_max"], 1)); put("ForceMaxTen", fix(F["max_abs_F_ref_t_le_10"], 2))
put("ForceOverallPct", fix(100 * F["rel_overall"], 2)); put("ForceOverall", sci(F["max_dF_overall"], 3)); put("ForceRelTen", sci(F["rel_t_le_10_window_max"], 1)); put("ForceRelTenTwo", sci(F["rel_t_le_10_window_max"], 2)); put("ForceRelTc", sci(F["rel_t_le_0p3_window_max"], 1))
put("ForceGrowth", fix(F["growth_factor_window5_10_to_10_20"], 0)); put("PlateauMean", sci(F["dF_plateau_mean_t26_50"], 2)); put("PlateauMin", sci(F["dF_plateau_min"], 2)); put("PlateauMax", sci(F["dF_plateau_max"], 2))
put("ZeroCross", fix(F["t_zero_crossing_of_dF"], 1)); put("PlateauFracAtBirth", fix(100 * F["dF_fraction_of_plateau_at_t24"], 0)); put("DragAtBirth", fix(F["D_at_24"], 1))
dd = dict(zip(F["dF_at"]["t"], F["dF_at"]["dF"]))
put("dFatFourteen", sci(dd[14], 2)); put("dFatTwenty", sci(dd[20], 2)); put("dFatTwentyFour", sci(dd[24], 2)); put("dFatTwentyEight", sci(dd[28], 2)); put("dFatFifty", sci(dd[50], 2))
tsf = F["time_shift_fit"]
put("ShiftTwenty", fix(-tsf[1]["shift"], 2)); put("ShiftThirty", fix(-tsf[2]["shift"], 2)); put("ShiftForty", fix(-tsf[3]["shift"], 2)); put("ShiftResTwenty", fix(100 * tsf[1]["rms_residual_over_rms_dF"], 0)); put("ShiftResThirty", fix(100 * tsf[2]["rms_residual_over_rms_dF"], 0)); put("ShiftResForty", fix(100 * tsf[3]["rms_residual_over_rms_dF"], 0))
# ------------------------------------------------------------------ lift
L = R["lift"]
put("LiftMax", sci(L["max_abs_Fy_ref_to_t100"], 2)); put("LiftRatio", sci(L["ratio_to_max_drag"], 1)); put("LiftRelMin", fix(100 * min(L["rel_diff"]), 1)); put("LiftRelMax", fix(100 * max(L["rel_diff"]), 1)); put("LiftZero", sci(L["Fy_ref_t0"], 1))
# ------------------------------------------------------------------ psi
P = {int(r["t"]): r for r in R["psi"]}
for t, nm in ((10, "Ten"), (20, "Twenty"), (30, "Thirty"), (40, "Forty"), (50, "Fifty")):
    put("Psi" + nm, sci(P[t]["psi_rel_L2"])); put("PsiGauge" + nm, sci(P[t]["psi_rel_L2_global_phase_removed"])); put("Dens" + nm, sci(P[t]["density_rel_L2"]))
    put("NearShare" + nm, fix(100 * P[t]["density_diff_share_within_40xi_of_obstacle"], 0))
put("DensRmsMin", sci(R["psi_density_diff_rms_range"][0], 1)); put("DensRmsMax", sci(R["psi_density_diff_rms_range"][1], 1))
put("MaxDpsiFifty", fix(P[50]["max_abs_dpsi"], 3)); put("MaxDnFifty", fix(P[50]["density_diff_max"], 4)); put("GlobalPhaseFifty", sci(abs(P[50]["global_phase"]), 2))
PQ = R["paper_quoted_not_reproduced"]
put("PaperVc", fix(PQ["v_c_over_c"], 2)); put("PaperVth", fix(PQ["v_th_over_c"], 2)); put("PaperRes", fix(PQ["Re_s_threshold"], 0))
put("PaperTLo", str(PQ["time_window_tau"][0])); put("PaperTHi", str(PQ["time_window_tau"][1]))
put("PaperWx", str(PQ["fringe_region_in_paper"]["w_x_xi"])); put("PaperWy", str(PQ["fringe_region_in_paper"]["w_y_xi"])); put("PaperD", str(PQ["fringe_region_in_paper"]["d_xi"]))
Pr = R["production_run"]
put("ProdSteps", str(Pr["steps"])); put("ProdWall", str(Pr["wall_s"])); put("ProdWallMin", fix(Pr["wall_minutes"], 0))
Dm = R["damping"]
put("GammaCentre", sci(Dm["gamma_centre_of_obstacle"], 2)); put("GammaDisc", sci(Dm["gamma_max_within_1_over_e2_radius"], 2))
# ------------------------------------------------------------------ initial field
I = R["initial_field"]
put("GammaOne", sci(I["gamma_after_one_step"], 3)); put("StopThr", sci(I["stop_threshold"], 1)); put("Eps", sci(I["epsilon"], 1)); put("InitDouble", sci(I["rel_L2_double_precision_to_deposited"], 2)); put("InitNoise", sci(I["noise_rms_relative"], 2))
put("InitDiffPct", fix(100 * I["n_elements_differing_after_rounding"] / I["n_elements"], 1)); put("InitDiffN", f"{I['n_elements_differing_after_rounding']:,}".replace(",", "\\,")); put("InitN", f"{I['n_elements']:,}".replace(",", "\\,"))
put("InitRounded", sci(I["rel_L2_to_deposited_with_noise"], 1))
# ------------------------------------------------------------------ ramp
Rm = R["ramp"]
put("Overshoot", fix(Rm["overshoot_dt0p01"], 5)); put("OvershootHalf", fix(Rm["overshoot_dt0p005"], 6)); put("SumV", fix(Rm["sum_v_dt_step_end"], 5)); put("IntV", fix(Rm["integral_v_dt"], 4))
put("RampOffset", sci(Rm["stage_times_dt0p01_dF_t0p1"], 2)); put("RampOffsetHalf", sci(Rm["step_end_dt0p005_dF_t0p1"], 3)); put("Sens", fix(Rm["sensitivity_dF_per_displacement_stage"], 2)); put("SensB", fix(Rm["sensitivity_dF_per_displacement_dt0p005"], 4))
put("SensA", fix(Rm["sensitivity_dF_per_displacement_stage"], 4)); put("OwnTemporal", sci(Rm["own_temporal_error_stage_dt0p01_vs_0p005_max_t_le_5"], 2)); put("StageMin", sci(Rm["stage_times_dF_min_t1_5"], 2)); put("StageMax", sci(Rm["stage_times_dF_max_t1_5"], 2))
# ------------------------------------------------------------------ census
C = R["census"]
put("EqualCounts", str(C["equal_counts_of_10"]))
rows = []
tt = C["times"]; labels = ["reference detector, deposited file", "same detector, our snapshots", "exact census, ours", "exact census, deposited fields"]
def cell(v): return "--" if v is None else str(v)
rowsA = [C["reference_rule_in_file"], C["ours_with_reference_rule"], C["ours_exact_census"], [C["reference_exact_census"].get(str(float(t))) for t in tt]]
census_rows = "\n".join(f"{lab} & " + " & ".join(cell(v) for v in row) + r" \\" for lab, row in zip(labels, rowsA))
put("CensusHeader", " & ".join(f"{t:g}" for t in tt)); M["__census_rows"] = census_rows
mt = C["match_ours_vs_reference"]
put("MatchThirty", f"{mt['30.0']['identical']}"); put("MatchForty", f"{mt['40.0']['identical']}"); put("MatchFiftyIdent", f"{mt['50.0']['identical']}"); put("MatchFiftyClose", f"{mt['50.0']['within_one_cell']}")
put("MatchTotalIdent", str(sum(mt[k]["identical"] for k in mt))); put("MatchTotal", str(sum(mt[k]["identical"] + mt[k]["within_one_cell"] for k in mt)))
W2 = R["winding_checks"]
put("WindN", str(W2["snapshots_checked"])); put("WindDev", sci(W2["max_abs_q_minus_round"], 1)); put("EdgeMax", fix(W2["max_edge_step_over_pi"], 4)); put("EdgeMargin", fix(100 * (1 - W2["max_edge_step_over_pi"]), 2))
Ru = R["rule"]
put("LoopDiffMax", fix(Ru["max_loop_integral_difference_over_pi"], 2)); put("LoopDiffThirty", fix(max(Ru["loop_integral_difference_same_vortex_ours_vs_ref"]["30.0"]), 2))
mg = Ru["marginal_candidate_t45_ours"]; put("MarginalInt", fix(mg["integral_over_pi"], 3)); put("MarginalX", fix(mg["x"], 1)); put("MarginalY", fix(-mg["y"], 1) if mg["y"] < 0 else fix(mg["y"], 1))
put("MarginalAbove", fix(100 * (mg["integral_over_pi"] / 0.9 - 1), 1))
S = R["symmetry"]
put("AsymZero", sci(S["asym_ref"][0], 2)); put("AsymRefFifty", sci(S["asym_ref"][-1], 2)); put("AsymOursFifty", sci(S["asym_ours"][-1], 2)); put("AsymOursFive", sci(S["asym_ours"][0], 2)); put("AsymRefTen", sci(S["asym_ref"][1], 2)); put("AsymOursTen", sci(S["asym_ours"][1], 2))
# ------------------------------------------------------------------ supersonic region
Su = R["supersonic"]
for key, nm in (("ours_5", "OursFive"), ("ours_10", "OursTen"), ("ours_15", "OursFifteen"), ("ours_20", "OursTwenty"), ("ref_10", "RefTen"), ("ref_20", "RefTwenty")):
    put("SupArea" + nm, fix(Su[key]["area"], 0)); put("SupM" + nm, fix(Su[key]["Mmax"], 2)); put("SupWidth" + nm, fix(Su[key]["width_y"], 1))
put("SupAreaOursTwentyP", fix(Su["ours_20"]["area"], 1)); put("SupAreaRefTwentyP", fix(Su["ref_20"]["area"], 1))
put("SupXminOursTwenty", fix(Su["ours_20"]["x_min"], 1)); put("SupXmaxOursTwenty", fix(Su["ours_20"]["x_max"], 1)); put("SupYhalfOursTwenty", fix(Su["ours_20"]["y_max"], 0)); put("SupXMmax", fix(Su["ours_20"]["x_Mmax"], 0))
A = R["axis_t20_ours"]
put("AxisNcentre", fix(A["n_center"], 2)); put("AxisUcentre", fix(abs(A["u_center"]), 2)); put("AxisMcentre", fix(A["M_center"], 2)); put("AxisJcentre", fix(A["j_center"], 2)); put("AxisJratio", fix(100 * A["j_center_over_upstream"], 0))
put("AxisNmin", fix(A["axis_min_density"], 3)); put("AxisSpeedMax", fix(A["speed_max"], 2)); put("AxisMaxM", fix(A["axis_max_M"], 1)); put("AxisXmin", fix(A["x_axis_min_density"], 0))
put("AxisSupLo", fix(A["axis_supersonic_x_range"][0], 1)); put("AxisSupHi", fix(A["axis_supersonic_x_range"][1], 1))
T = R["sonic_threshold"]; Tb = T["by_snapshot"]
put("UcFar", fix(T["u_c_far_field"], 3)); put("UcCentre", fix(T["u_c_centre"], 3)); put("SqrtOneMinusV", fix(T["sqrt_1_minus_V0"], 2)); put("BernB", fix(T["B"], 4))
for key, nm in (("ours_5", "OursFive"), ("ours_10", "OursTen"), ("ours_15", "OursFifteen"), ("ours_20", "OursTwenty")):
    put("ThrArea" + nm, fix(Tb[key]["area_threshold_region"], 0)); put("ThrIn" + nm, fix(100 * Tb[key]["fraction_of_mach_region_inside"], 0)); put("MachAreaNear" + nm, fix(Tb[key]["area_mach_region"], 0))
put("ThrExcess" + "OursTwenty", fix(100 * (Tb["ours_20"]["area_threshold_region"] / Tb["ours_20"]["area_mach_region"] - 1), 0)); put("ThrExcessOursFive", fix(100 * (Tb["ours_5"]["area_threshold_region"] / Tb["ours_5"]["area_mach_region"] - 1), 0))
put("NBernCentre", fix(Tb["ours_20"]["n_bernoulli_centre"], 3)); put("NMeasCentre", fix(Tb["ours_20"]["n_centre"], 3))
# ------------------------------------------------------------------ birth
Bi = R["birth"]
put("BirthBefore", fix(Bi["t_last_without"], 1)); put("BirthAfter", fix(Bi["t_first_with"], 1)); put("BirthNmin", sci(Bi["n_min_before"], 1)); put("BirthNminAfter", sci(Bi["n_min_at"], 2))
pl = Bi["first_charges"]["plaquettes"]
put("BirthX", fix(pl[0]["x"], 2)); put("BirthY", fix(abs(pl[0]["y"]), 2)); put("BirthDist", fix(100 - pl[0]["x"], 2)); put("BirthSep", fix(abs(pl[0]["y"] - pl[1]["y"]), 1))
put("BirthSepLate", fix(Bi["pair_by_time"]["24.9"]["separation"], 1)); put("BirthEdge", fix(Bi["max_edge_step_over_pi_at_birth"], 3)); put("ContRel", sci(Bi["numpy_continuation_vs_rust_t25_rel_L2"], 2))
nm = dict((round(a, 2), b) for a, b in Bi["n_min_series"]); put("NminTwenty", fix(nm[20.0], 3)); put("NminTwentyThree", sci(nm[23.3], 2))
es = dict((round(a, 2), b) for a, b in Bi["max_edge_step_series"]); put("EdgeTwentyFour", fix(es[24.0], 2)); put("EdgeTwentyFourTwo", fix(es[24.2], 2))
sb = Bi["supersonic_axis_range_by_time"]
put("BirthSupLo", fix(sb["24.3"]["axis_supersonic_x"][0], 1)); put("BirthSupHi", fix(sb["24.3"]["axis_supersonic_x"][1], 1))
Be = R["bernoulli"]
put("BernCorr", fix(Be["corr_R_vs_minus_dtheta_dt"], 5)); put("BernOneMinus", sci(1 - Be["corr_R_vs_minus_dtheta_dt"], 1)); put("BernMaxDiff", sci(Be["max_abs_difference"], 2)); put("BernRms", fix(Be["rms_R"], 2))
put("BernRspan", fix(Be["axis_R_span"], 1)); put("BernRlo", fix(Be["axis_R_range"][0], 2)); put("BernRhi", fix(Be["axis_R_range"][1], 2)); put("BernQsmall", fix(Be["axis_Q_abs_max_away_from_core"], 3)); put("BernQmin", fix(Be["axis_Q_min"], 2)); put("BernQx", fix(Be["x_axis_Q_min"], 1))
# ------------------------------------------------------------------ Lean numbers
Ln = R["lean_numbers"]
put("SonicS", fix(Ln["sonic_density_s"], 3)); put("Vc", fix(Ln["V_c_at_v0p55"], 3)); put("VzeroOverVc", fix(Ln["V0_over_Vc"], 1)); put("JatVc", fix(Ln["j_where_Vc_equals_V0"], 3)); put("SatVc", fix(Ln["s_where_Vc_equals_V0"], 3)); put("VcApprox", fix(Ln["Vc_small_barrier_approx_2over3_1minusj_sq"], 3))
put("CoreSound", fix(Ln["sound_speed_in_obstacle_core_TF"], 2)); put("CoreDensity", fix(Ln["TF_depleted_density_core"], 1))
# ------------------------------------------------------------------ fresh run
Fr = R["fresh_run"]
if Fr:
    put("FreshMax", sci(Fr["max_abs_dF_t_le_1"], 3)); put("FreshRel", sci(Fr["rel_to_max_F_in_window"], 2)); put("FreshCpu", fix(Fr["user_cpu_s"], 0)); put("FreshWall", str(Fr["program_wall_s"])); put("FreshLoadA", fix(Fr["load_average_start_end"][0], 1)); put("FreshLoadB", fix(Fr["load_average_start_end"][1], 1))
    put("FreshPerStep", fix(Fr["user_cpu_s"] / Fr["steps"], 2)); put("FreshLtOne", sci(Fr["max_abs_dF_t_lt_1"], 2)); put("FreshTc", sci(Fr["max_abs_dF_t_le_0p3"], 3))

out = ["% generated by book/figures/ch09_texnumbers.py from ch09_numbers.json -- do not edit.  Each macro is math-mode material: write $\\cnineForceTen$.",
       "% macros are prefixed cnine to stay clear of the other chapters' names."]
for k, v in M.items():
    if k.startswith("__"): continue
    out.append(f"\\newcommand{{\\cnine{k}}}{{{v}}}")
out.append("\\newcommand{\\cnineCensusRows}{%\n" + M["__census_rows"] + "%\n}")
(HERE / "ch09_numbers.tex").write_text("\n".join(out) + "\n")
print("wrote", HERE / "ch09_numbers.tex", len(M) - 1, "macros")
