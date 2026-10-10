"""Chapter 6 -- collect every number that the text of chapters/ch06.tex quotes from a computation, write figures/ch06_numbers.json, and inject the
corresponding \\newcommand block (and the ladder table) into chapters/ch06.tex between the markers

    % BEGIN ch06 numbers ... % END ch06 numbers        and        % BEGIN ch06 table ... % END ch06 table

Inputs (all written by scripts of this directory): ch06_constants.json, ch06_loglaw_numbers.json, ch06_pgpe_numbers.json, ch06_cert_numbers.json,
ch06_flow_numbers.json, ch06_backward.json, ch06_field_info.json, ch06_cvode_probe_venv.json, ch06_cvode_probe_5db8041.json.
Every macro has: the TeX text that appears in the chapter, the underlying value(s), and the file/key it comes from.
Run:  .venv/bin/python figures/ch06_numbers.py          (add --check to verify that the chapter uses exactly the macros defined here)"""
import json, math, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEX = HERE.parent / "chapters" / "ch06.tex"
L = lambda name: json.loads((HERE / name).read_text())
C, LOG, PG, CERT, FLOW, BACK, FIELD, PVENV, PNEW = (L(n) for n in ("ch06_constants.json", "ch06_loglaw_numbers.json", "ch06_pgpe_numbers.json", "ch06_cert_numbers.json",
                                                                  "ch06_flow_numbers.json", "ch06_backward.json", "ch06_field_info.json", "ch06_cvode_probe_venv.json", "ch06_cvode_probe_5db8041.json"))
N = {}


def put(name, tex, value, source):
    N[name] = dict(tex=tex, value=value, source=source)


def sci(x, digits=1):
    """3.3 x 10^-4 as TeX (to be used inside math mode)."""
    m, e = f"{x:.{digits}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def thousands(n):
    return f"{int(n):,}".replace(",", "\\,")


# ---------------------------------------------------------------------------------------------------- constants
put("cnJump", f"{C['universal_jump_cgs_g_cm2_K'] * 1e9:.2f}", C["universal_jump_cgs_g_cm2_K"], "ch06_constants.json universal_jump_cgs_g_cm2_K (x 1e-9 g cm^-2 K^-1)")
put("cnFc", f"{C['f_at_pi_over_2']:.3f}", C["f_at_pi_over_2"], "ch06_constants.json f_at_pi_over_2")
put("cnLnThreeEighty", f"{C['ln380']:.2f}", C["ln380"], "ch06_constants.json ln380")
put("cnTwoPiLnTwo", f"{C['two_pi_ln2']:.3f}", C["two_pi_ln2"], "ch06_constants.json two_pi_ln2")
# ---------------------------------------------------------------------------------------------------- pair energy (qf-pgpe)
f64, f128 = LOG["L64"]["fits"]["dmin8.0"], LOG["L128"]["fits"]["dmin8.0"]
put("cnCdiff", f"{LOG['C_difference']['dmin8.0']:.3f}", LOG["C_difference"]["dmin8.0"], "ch06_loglaw_numbers.json C_difference.dmin8.0")
put("cnCdiffA", f"{LOG['C_difference']['dmin4.0']:.3f}", LOG["C_difference"]["dmin4.0"], "ch06_loglaw_numbers.json C_difference.dmin4.0")
put("cnCdiffB", f"{LOG['C_difference']['dmin6.0']:.3f}", LOG["C_difference"]["dmin6.0"], "ch06_loglaw_numbers.json C_difference.dmin6.0")
put("cnDloSixtyfour", f"{round(f64['d_range'][0])}", f64["d_range"][0], "ch06_loglaw_numbers.json L64.fits.dmin8.0.d_range")
put("cnDhiSixtyfour", f"{round(f64['d_range'][1])}", f64["d_range"][1], "same")
put("cnElowSixtyfour", f"{f64['dE_range'][0]:.1f}", f64["dE_range"][0], "ch06_loglaw_numbers.json L64.fits.dmin8.0.dE_range")
put("cnEhighSixtyfour", f"{f64['dE_range'][1]:.1f}", f64["dE_range"][1], "same")
put("cnRmsSixtyfour", f"{f64['rms']:.3f}", f64["rms"], "ch06_loglaw_numbers.json L64.fits.dmin8.0.rms")
put("cnMaxSixtyfour", f"{f64['max_abs']:.3f}", f64["max_abs"], "ch06_loglaw_numbers.json L64.fits.dmin8.0.max_abs")
put("cnDloHundred", f"{round(f128['d_range'][0])}", f128["d_range"][0], "ch06_loglaw_numbers.json L128.fits.dmin8.0.d_range")
put("cnDhiHundred", f"{round(f128['d_range'][1])}", f128["d_range"][1], "same")
put("cnElowHundred", f"{f128['dE_range'][0]:.1f}", f128["dE_range"][0], "ch06_loglaw_numbers.json L128.fits.dmin8.0.dE_range")
put("cnEhighHundred", f"{f128['dE_range'][1]:.1f}", f128["dE_range"][1], "same")
put("cnRmsHundred", f"{f128['rms']:.3f}", f128["rms"], "ch06_loglaw_numbers.json L128.fits.dmin8.0.rms")
put("cnMaxHundred", f"{f128['max_abs']:.3f}", f128["max_abs"], "ch06_loglaw_numbers.json L128.fits.dmin8.0.max_abs")
put("cnSlopeSixtyfour", f"{LOG['L64']['slopes']['d4_8']['slope_over_2pi']:.2f}", LOG["L64"]["slopes"]["d4_8"]["slope_over_2pi"], "ch06_loglaw_numbers.json L64.slopes.d4_8.slope_over_2pi")
put("cnSlopeHundred", f"{LOG['L128']['slopes']['d4_8']['slope_over_2pi']:.2f}", LOG["L128"]["slopes"]["d4_8"]["slope_over_2pi"], "ch06_loglaw_numbers.json L128.slopes.d4_8.slope_over_2pi")
# ---------------------------------------------------------------------------------------------------- classical field (programme runs, recomputed)
cr64, cr32 = PG["L64"]["crossing"], PG["L32"]["crossing"]
put("cnTbktSixtyfour", f"{cr64['T_BKT']:.3f}", cr64["T_BKT"], "ch06_pgpe_numbers.json L64.crossing.T_BKT")
put("cnEtaCrossSixtyfour", f"{cr64['eta']:.3f}", cr64["eta"], "ch06_pgpe_numbers.json L64.crossing.eta")
put("cnNsOverNCross", f"{4 * cr64['T_BKT'] / (2 * math.pi):.2f}", 4 * cr64["T_BKT"] / (2 * math.pi), "n_s/n = 4 T_BKT/(2 pi) at the crossing (n_s lambda^2 = 4, lambda^2 = 2 pi/T, n = 1)")
lo, hi = PG["L64"]["per_seed_T_BKT_range"]
put("cnTbktSeedLo", f"{lo:.3f}", lo, "ch06_pgpe_numbers.json L64.per_seed_T_BKT_range"); put("cnTbktSeedHi", f"{hi:.3f}", hi, "same")
ks = {r["name"]: r["K"] for r in PG["L64"]["per_run"] if abs(r["e"] - 1.25) < 1e-9}
kA, kB = ks["II_e0.90_s11_t4000_e1.25"], ks["II_e0.90_s12_t4000_e1.25"]
put("cnKseedA", f"{kA:.2f}", kA, "ch06_pgpe_numbers.json L64.per_run II_e0.90_s11_t4000_e1.25 K"); put("cnKseedB", f"{kB:.2f}", kB, "ch06_pgpe_numbers.json L64.per_run II_e0.90_s12_t4000_e1.25 K")
put("cnTbktThirtytwo", f"{cr32['T_BKT']:.3f}", cr32["T_BKT"], "ch06_pgpe_numbers.json L32.crossing.T_BKT")
lo, hi = PG["L32"]["per_seed_T_BKT_range"]
put("cnTbktSeedLoThirtytwo", f"{lo:.3f}", lo, "ch06_pgpe_numbers.json L32.per_seed_T_BKT_range"); put("cnTbktSeedHiThirtytwo", f"{hi:.3f}", hi, "same")
put("cnSlopeCrossSixtyfour", f"{cr64['slope']:.0f}", cr64["slope"], "ch06_pgpe_numbers.json L64.crossing.slope"); put("cnSlopeCrossThirtytwo", f"{cr32['slope']:.0f}", cr32["slope"], "ch06_pgpe_numbers.json L32.crossing.slope")
ek64 = [r["eta_K"] for r in PG["L64"]["rows"] if r["K"] > 4]; ek32 = [r["eta_K"] for r in PG["L32"]["rows"] if r["K"] > 4]
put("cnEtaKlo", f"{min(ek64):.2f}", min(ek64), "ch06_pgpe_numbers.json L64.rows eta_K for K > 4 (min)"); put("cnEtaKhi", f"{max(ek64):.2f}", max(ek64), "same (max)")
put("cnEtaKloThirtytwo", f"{min(ek32):.2f}", min(ek32), "ch06_pgpe_numbers.json L32.rows eta_K for K > 4 (min)"); put("cnEtaKhiThirtytwo", f"{max(ek32):.2f}", max(ek32), "same (max)")
nl = 2 * math.pi / cr64["T_BKT"]
put("cnNlambda", f"{nl:.2f}", nl, "2 pi / T_BKT(64)"); put("cnNlambdaExcess", f"{100 * (nl / C['ln380'] - 1):.0f}", 100 * (nl / C["ln380"] - 1), "100 (n lambda^2 / ln 380 - 1)")
put("cnPairLo", f"{FIELD['1.00']['mean_pair']:.1f}", FIELD["1.00"]["mean_pair"], "ch06_field_info.json 1.00 mean_pair")
put("cnPairMid", f"{FIELD['1.25']['mean_pair']:.1f}", FIELD["1.25"]["mean_pair"], "ch06_field_info.json 1.25 mean_pair")
put("cnPairHi", f"{FIELD['1.40']['mean_pair']:.1f}", FIELD["1.40"]["mean_pair"], "ch06_field_info.json 1.40 mean_pair")
put("cnNvMid", f"{FIELD['1.25']['n_v']}", FIELD["1.25"]["n_v"], "ch06_field_info.json 1.25 n_v")
# ---------------------------------------------------------------------------------------------------- certificates
S = CERT["fields_summary"]
put("cnNconfigs", f"{S['n']}", S["n"], "ch06_cert_numbers.json fields_summary.n"); put("cnPremiseOk", f"{S['P_premise_ok']}", S["P_premise_ok"], "ch06_cert_numbers.json fields_summary.P_premise_ok")
put("cnTauLoFields", f"{S['tau_k1_min']:.2f}", S["tau_k1_min"], "fields_summary.tau_k1_min"); put("cnTauHiFields", f"{S['tau_k1_max']:.2f}", S["tau_k1_max"], "fields_summary.tau_k1_max")
taus = [r["tau_k1_mean"] for r in CERT["L192"].values()]
put("cnTauLoRuns", f"{min(taus):.2f}", min(taus), "ch06_cert_numbers.json L192 tau_k1_mean (min)"); put("cnTauHiRuns", f"{max(taus):.2f}", max(taus), "same (max)")
put("cnRemMed", f"{S['P_rel_remainder_median']:.2f}", S["P_rel_remainder_median"], "fields_summary.P_rel_remainder_median"); put("cnRemMedPct", f"{100 * S['P_rel_remainder_median']:.0f}", 100 * S["P_rel_remainder_median"], "same x 100")
put("cnBoundMed", f"{S['P_rel_bound_median']:.2f}", S["P_rel_bound_median"], "fields_summary.P_rel_bound_median")
d4 = [r["ratio"] for r in CERT["L192"].values()]
put("cnDfourLo", f"{min(d4):.2f}", min(d4), "ch06_cert_numbers.json L192 ratio (min)"); put("cnDfourHi", f"{max(d4):.2f}", max(d4), "same (max)")
# ---------------------------------------------------------------------------------------------------- CVODE flow
put("cnNtraj", f"{FLOW['n_traj']}", FLOW["n_traj"], "ch06_flow_numbers.json n_traj"); put("cnNhyp", f"{FLOW['n_hyp']}", FLOW["n_hyp"], "n_hyp")
put("cnNbelow", f"{FLOW['n_below_sep_start_u_lt_uc']}", FLOW["n_below_sep_start_u_lt_uc"], "n_below_sep_start_u_lt_uc")
put("cnNbetween", f"{FLOW['between']['n']}", FLOW["between"]["n"], "between.n"); put("cnNbetweenTrapped", f"{FLOW['between']['trapped_by_cvode']}", FLOW["between"]["trapped_by_cvode"], "between.trapped_by_cvode")
assert FLOW["n_hyp_trapped"] == FLOW["n_hyp"] == FLOW["n_hyp_monotone"] == FLOW["n_hyp_ysq"] and FLOW["n_below_sep_crossed"] == FLOW["n_below_sep_start_u_lt_uc"]
put("cnMaxUstarErr", sci(FLOW["max_ustar_error_hyp"]), FLOW["max_ustar_error_hyp"], "ch06_flow_numbers.json max_ustar_error_hyp")
slow = [r for r in FLOW["family"] if r["hypothesis"] and r["Hmargin"] <= 4e-3]; fast = [r for r in FLOW["family"] if r["hypothesis"] and r["Hmargin"] > 4e-3]
assert len(slow) == 3 and all(abs(r["u_end"] - r["u_star"]) > 1e-7 for r in slow) and all(abs(r["u_end"] - r["u_star"]) < 3e-9 for r in fast)
put("cnUstarErrTypical", sci(max(abs(r["u_end"] - r["u_star"]) for r in fast)), max(abs(r["u_end"] - r["u_star"]) for r in fast), "family: max |u_end - u*| over the 17 trapped starts with H-margin > 4e-3")
tol = FLOW["tolerance"]
put("cnDriftAdamsA", sci(tol["adams_0.0001"]["max_drift"]), tol["adams_0.0001"]["max_drift"], "tolerance.adams_0.0001.max_drift"); put("cnDriftAdamsD", sci(tol["adams_1e-10"]["max_drift"]), tol["adams_1e-10"]["max_drift"], "tolerance.adams_1e-10.max_drift")
put("cnDriftBdfA", sci(tol["bdf_0.0001"]["max_drift"]), tol["bdf_0.0001"]["max_drift"], "tolerance.bdf_0.0001.max_drift"); put("cnDriftBdfD", sci(tol["bdf_1e-10"]["max_drift"]), tol["bdf_1e-10"]["max_drift"], "tolerance.bdf_1e-10.max_drift")
ctl = FLOW["control_wrong_coeff_drift"]
put("cnCtlLo", sci(min(ctl)), min(ctl), "control_wrong_coeff_drift (min)"); put("cnCtlHi", f"{max(ctl):.2f}", max(ctl), "control_wrong_coeff_drift (max)")
put("cnCtlRatioLo", sci(min(ctl) / tol["adams_1e-10"]["max_drift"], 0), min(ctl) / tol["adams_1e-10"]["max_drift"], "min(control)/adams_1e-10 drift")
put("cnCtlRatioHi", sci(max(ctl) / tol["adams_1e-10"]["max_drift"]), max(ctl) / tol["adams_1e-10"]["max_drift"], "max(control)/adams_1e-10 drift")
esc = FLOW["escape"]
put("cnEscN", f"{len(esc)}", len(esc), "escape rows"); assert FLOW["escape_all_within_bound"]
put("cnEscRatioLo", f"{min(e['ratio_bound'] for e in esc):.2f}", min(e["ratio_bound"] for e in esc), "escape ratio_bound (min)"); put("cnEscRatioHi", f"{max(e['ratio_bound'] for e in esc):.2f}", max(e["ratio_bound"] for e in esc), "(max)")
put("cnEscRelErr", sci(FLOW["escape_max_rel_err"]), FLOW["escape_max_rel_err"], "escape_max_rel_err")
J = FLOW["jump"]
put("cnKzeroC", f"{J['K0c']:.4f}", J["K0c"], "jump.K0c"); put("cnUzeroC", f"{J['u0c']:.3f}", J["u0c"], "jump.u0c")
put("cnKRgrid", f"{J['KR_at_that_point']:.3f}", J["KR_at_that_point"], "jump.KR_at_that_point (K0 = %.3f)" % J["K0_min_superfluid_grid"]); put("cnNslGrid", f"{2 * math.pi * J['KR_at_that_point']:.2f}", 2 * math.pi * J["KR_at_that_point"], "2 pi KR_at_that_point")
i8 = min(range(len(J["K0_cv"])), key=lambda i: abs(J["K0_cv"][i] - 0.8)); j8 = min(range(len(J["K0"])), key=lambda i: abs(J["K0"][i] - 0.8))
assert abs(J["KR_cv"][i8] - J["KR_inv"][j8]) < 1e-3
put("cnKRcv", f"{J['KR_cv'][i8]:.3f}", J["KR_cv"][i8], "jump.KR_cv at K0 = 0.8 (and KR_inv)")
FB = FLOW["finite_box"]["runs"]
for tag, key in zip("ABCD", ("16", "64", "256", "4096")):
    sh = 100 * ((1 / FB[key]["K0_cross"]) / J["u0c"] - 1)
    put(f"cnShift{tag}", f"{sh:.1f}\\%", sh, f"finite_box.runs[{key}].K0_cross vs jump.u0c")
cr = {c["l"]: c for c in FLOW["critical"]}
put("cnCritA", f"{cr[10]['excess_times_l']:.2f}", cr[10]["excess_times_l"], "critical l=10 (n_s lambda^2 - 4) l"); put("cnCritB", f"{cr[100]['excess_times_l']:.2f}", cr[100]["excess_times_l"], "critical l=100")
put("cnCritC", f"{cr[10000]['excess_times_l']:.4f}", cr[10000]["excess_times_l"], "critical l=10000"); put("cnCritDrift", sci(max(c["Hdrift"] for c in FLOW["critical"])), max(c["Hdrift"] for c in FLOW["critical"]), "critical Hdrift (max)")
pred = lambda l: 2 - (2 / 3) * math.log(l) / l          # Exercise 2: l (n_s lambda^2 - 4) = 2 - (2/3) ln(l)/l + O(1/l)
put("cnCritDevB", f"{abs(cr[100]['excess_times_l'] - pred(100)):.4f}", abs(cr[100]["excess_times_l"] - pred(100)), "|critical l=100 - (2 - (2/3) ln l / l)|")
put("cnCritDevC", sci(abs(cr[10000]["excess_times_l"] - pred(10000)), 0), abs(cr[10000]["excess_times_l"] - pred(10000)), "|critical l=10000 - (2 - (2/3) ln l / l)|")
es = {e["eps"]: e for e in FLOW["essential"]["rows"]}
put("cnEssRatioA", f"{es[0.1]['ratio']:.2f}", es[0.1]["ratio"], "essential eps=1e-1 ratio"); put("cnEssRatioB", f"{es[0.001]['ratio']:.2f}", es[0.001]["ratio"], "essential eps=1e-3 ratio")
put("cnEssRatioC", f"{es[1e-06]['ratio']:.3f}", es[1e-06]["ratio"], "essential eps=1e-6 ratio")
put("cnEssOffset", f"{-es[1e-06]['l_minus_asym']:.2f}", es[1e-06]["l_minus_asym"], "essential eps=1e-6 l_minus_asym (negated)")
put("cnEssRel", sci(abs(es[1e-06]["l_cvode"] - es[1e-06]["l_quad"]) / es[1e-06]["l_quad"]), abs(es[1e-06]["l_cvode"] - es[1e-06]["l_quad"]) / es[1e-06]["l_quad"], "essential eps=1e-6 |l_cvode - l_quad| / l_quad")
sh = FLOW["finite_box"]["shift_32_to_64_percent"]; shf = 100 * (cr32["T_BKT"] / cr64["T_BKT"] - 1)
put("cnShiftToy", f"{sh:.0f}", sh, "ch06_flow_numbers.json finite_box.shift_32_to_64_percent (crossing in u0 ~ T, L/a = 32 vs 64)")
put("cnShiftField", f"{shf:.0f}", shf, "100 (T_BKT(32)/T_BKT(64) - 1) from ch06_pgpe_numbers.json")
# ---------------------------------------------------------------------------------------------------- environment and probes
E = FLOW["environment"]
put("cnCommitShort", f"\\texttt{{{E['commit'][:7]}}}", E["commit"], "ch06_flow_numbers.json environment.commit")
put("cnShaShort", f"\\texttt{{{E['sha256'][:12]}}}", E["sha256"], "ch06_flow_numbers.json environment.sha256")
pnew = {p["label"][:2]: p for p in PNEW["probes"]}; pold = {p["label"][:2]: p for p in PVENV["probes"]}
assert PNEW["sha256"] == E["sha256"] and PVENV["sha256"] != E["sha256"]
put("cnPoneNew", f"{pnew['P1']['rhs_calls']}", pnew["P1"]["rhs_calls"], "ch06_cvode_probe_5db8041.json P1"); put("cnPoneOld", thousands(pold["P1"]["rhs_calls"]), pold["P1"]["rhs_calls"], "ch06_cvode_probe_venv.json P1")
put("cnPoneOldErr", sci(pold["P1"]["relerr"], 1), pold["P1"]["relerr"], "ch06_cvode_probe_venv.json P1 relerr"); put("cnPoneNewErr", sci(pnew["P1"]["relerr"], 1), pnew["P1"]["relerr"], "ch06_cvode_probe_5db8041.json P1 relerr")
put("cnPthreeOld", thousands(pold["P3"]["rhs_calls"]), pold["P3"]["rhs_calls"], "venv P3"); put("cnPthreeNew", f"{pnew['P3']['rhs_calls']}", pnew["P3"]["rhs_calls"], "5db8041 P3")
put("cnPfourOld", thousands(pold["P4"]["rhs_calls"]), pold["P4"]["rhs_calls"], "venv P4"); put("cnPfourNew", f"{pnew['P4']['rhs_calls']}", pnew["P4"]["rhs_calls"], "5db8041 P4")
# ---------------------------------------------------------------------------------------------------- backward flow
bt, bb = BACK["cases"][0], BACK["cases"][1]
put("cnBackU", f"{bt['u0']:.1f}", bt["u0"], "ch06_backward.json cases[0].u0"); put("cnBackY", f"{bt['y0']:.3f}", bt["y0"], "cases[0].y0")
put("cnBackL", f"{bt['l_minus_quadrature']:.3f}", bt["l_minus_quadrature"], "cases[0].l_minus_quadrature"); put("cnBackLb", f"{bb['l_minus_quadrature']:.3f}", bb["l_minus_quadrature"], "cases[1].l_minus_quadrature")
put("cnBackCvodeU", f"{bt['cvode_at_lm_plus_002']['u']:.2f}", bt["cvode_at_lm_plus_002"]["u"], "cases[0].cvode_at_lm_plus_002.u"); put("cnBackCvodeY", f"{bt['cvode_at_lm_plus_002']['y']:.2f}", bt["cvode_at_lm_plus_002"]["y"], "cases[0].cvode_at_lm_plus_002.y")

# ---------------------------------------------------------------------------------------------------- the ladder table
rows = []
for r in PG["L64"]["rows"]:
    rows.append(f"{r['e']:.2f} & {r['T']:.3f} & {r['ns_over_n']:.3f} & {r['K']:.2f} & {r['eta']:.3f} & {r['eta_K']:.2f} & {r['n_v']:.0f}\\\\")
table = "\n".join(rows)

# ---------------------------------------------------------------------------------------------------- write
out = dict(chapter=6, note="Every macro \\cn... of chapters/ch06.tex: TeX text, value, source. Produced by figures/ch06_numbers.py from the JSON files of this directory.",
           environment=E, environment_qf_pgpe=LOG["environment"], numbers=N, ladder_L64=PG["L64"]["rows"], ladder_L32=PG["L32"]["rows"],
           key_results=dict(
               T_BKT_L64=cr64, T_BKT_L32=cr32, per_seed_T_BKT=dict(L64=PG["L64"]["per_seed_crossings"], L32=PG["L32"]["per_seed_crossings"]),
               pair_energy_fits=dict(L64=LOG["L64"]["fits"], L128=LOG["L128"]["fits"], C_difference=LOG["C_difference"], two_pi_ln2=LOG["two_pi_ln2"]),
               matching_bound=dict(violations=S["violations_total"], n_fields=S["n"], n_L192_snapshots=sum(r["n_snap"] for r in CERT["L192"].values()),
                                   violations_L192=sum(r["violations"] for r in CERT["L192"].values())),
               flow=dict(n_traj=FLOW["n_traj"], n_hyp=FLOW["n_hyp"], tolerance=tol, control=ctl, escape=esc, jump=dict(K0c=J["K0c"], u0c=J["u0c"], KR_at_grid=J["KR_at_that_point"]),
                         critical=FLOW["critical"], essential=FLOW["essential"]["rows"]),
               universal_jump=dict(cgs_g_cm2_K=C["universal_jump_cgs_g_cm2_K"], SI=C["universal_jump_SI_kg_m2_K"], m_He4_amu=C["m_He4_amu"]),
               cvode_probe=dict(venv=PVENV["probes"], stable_5db8041=PNEW["probes"])))
(HERE / "ch06_numbers.json").write_text(json.dumps(out, indent=1, default=float))

block = "% BEGIN ch06 numbers\n" + "\n".join(f"\\newcommand{{\\{k}}}{{{v['tex']}}}" for k, v in sorted(N.items())) + "\n% END ch06 numbers"
tex = TEX.read_text()
tex = re.sub(r"% BEGIN ch06 numbers.*?% END ch06 numbers", lambda m: block, tex, flags=re.S)
tex = re.sub(r"% BEGIN ch06 table.*?% END ch06 table", lambda m: "% BEGIN ch06 table\n" + table + "\n% END ch06 table", tex, flags=re.S)
TEX.write_text(tex)
used = set(re.findall(r"\\(cn[A-Za-z]+)", tex.split("% END ch06 numbers")[1]))
missing = sorted(used - set(N)); unused = sorted(set(N) - used)
print(len(N), "macros defined;", len(used), "used in the chapter")
print("USED BUT NOT DEFINED:", missing)
print("DEFINED BUT UNUSED:", unused)
