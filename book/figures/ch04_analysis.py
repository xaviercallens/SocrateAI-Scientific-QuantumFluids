"""Chapter 4 -- post-processing of the solver output.  Reads ch04_cvode_raw.json / ch04_cvode_results.npz (written by
ch04_cvode_compute.py), the exact-rational series of ch04_series_ext.py and the two ancillary tables of arXiv:2012.09067, and writes
  ch04_numbers.json   -- EVERY number quoted in the chapter text (the single source),
  ch04_analysis.npz   -- arrays used by the figure scripts.
Run from book/figures:  ../../.venv/bin/python ch04_analysis.py"""
import json
from pathlib import Path
import numpy as np
import mpmath as mp
import ch04_common as cc
import ch04_series_ext as se

HERE = Path(__file__).resolve().parent
raw = json.load(open(HERE/"ch04_cvode_raw.json")); R = np.load(HERE/"ch04_cvode_results.npz"); XC = json.load(open(HERE/"ch04_crosschecks.json"))
mp.mp.dps = 40
N = {}

# ---------------------------------------------------------------------------------------------- constants and closed forms
co = cc.coeffs_SI(); A = co["A"]
N["constants"] = dict(c_m_per_s=cc.c, V_cm3_per_mol=cc.Vm*1e6, theta_K_A=cc.THETA, alpha_A_powers=cc.ALPHA,
                      k_T_per_K_inv_A=1.0/cc.THETA)
N["coefficients"] = {n: dict(power=cc.POWERS[n], value=co[n], printed=cc.PRINTED[n], rel_diff_to_printed=co[n]/cc.PRINTED[n] - 1) for n in co}
N["coefficients_max_rel_diff_to_printed"] = max(abs(v["rel_diff_to_printed"]) for v in N["coefficients"].values())

# ---------------------------------------------------------------------------------------------- exact rational series (independent of Lean)
out, g = se.cv_coeffs(60)
ps = sorted(out)
cp = {p: float(out[p]) for p in ps}
N["exact_rational"] = dict(
    g_n={str(n): str(g[n]) for n in range(2, 12)},
    c_p={str(p): cp[p] for p in range(3, 21) if p in cp},
    ratio_to_A={str(p): cp[p]/cp[3] for p in range(3, 21) if p in cp},
    max_rel_diff_to_closed_forms=max(abs(cp[cc.POWERS[n]]/co[n] - 1) for n in co),
    T4_coefficient=float(out.get(4, 0)))
# nearest critical value of u(k) = k (1 + a2 k^2 + a3 k^3 + a4 k^4)
a2, a3, a4 = cc.ALPHA["a2"], cc.ALPHA["a3"], cc.ALPHA["a4"]
rts = np.roots([5*a4, 4*a3, 3*a2, 0, 1])
uc = np.array([r*(1 + a2*r**2 + a3*r**3 + a4*r**4) for r in rts])
iu = int(np.argmin(abs(uc)))
Rc = float(abs(uc[iu]))
N["critical_point"] = dict(k_c=[float(rts[iu].real), float(abs(rts[iu].imag))], u_c=[float(uc[iu].real), float(abs(uc[iu].imag))],
                           abs_u_c_per_A=Rc, hbar_c_u_c_over_kB_K=Rc*cc.THETA, inverse_K_inv=1.0/(Rc*cc.THETA),
                           all_abs_u_c=sorted(float(abs(x)) for x in uc))
root = {p: (abs(cp[p])/float(mp.factorial(p)))**(1.0/p) for p in ps if p >= 5}
N["root_test"] = dict(p20=root[20], p30=root[30], p40=root[40], p50=root[50], p60=root[60], predicted=1.0/(Rc*cc.THETA))

# ---------------------------------------------------------------------------------------------- (A) Bose integrals
A_runs = raw["A"]["runs"]
N["solver_module"] = raw["module"]
N["bose_cvode"] = dict(method=raw["method"], module=raw["rusty_sundials"], XEND=raw["A"]["XEND"],
    closed_form_vs_factorial_zeta=raw["A"]["closed_form_vs_factorial_zeta"],
    runs=[dict(rtol=r["rtol"], max_rel_err=max(r["rel_err_vs_lean_closed_form"].values()), rel_err=r["rel_err_vs_lean_closed_form"],
               rhs_calls=r["rhs_calls"], seconds=r["seconds"], load_avg_start=r["load_avg_start"], load_avg_end=r["load_avg_end"]) for r in A_runs],
    scipy_quad_max_rel_err=max(raw["A"]["scipy_quad_rel_err"].values()), scipy_quad_rel_err=raw["A"]["scipy_quad_rel_err"])

# ---------------------------------------------------------------------------------------------- (B) model dispersion
T_all = R["T_all"]; T_log = R["T_log"]; T_lin = R["T_lin"]
nlog = len(T_log)
B_runs = raw["B"]["runs"]
for r_ in B_runs:
    r_["abs_err_vs_mp"] = XC["B"]["abs_err_vs_mp"][{1e-8: "1e-08", 1e-10: "1e-10", 1e-12: "1e-12"}[r_["rtol"]]]
raw["B"]["mp_ref"] = XC["B"]["mp_ref"]; raw["B"]["ref_T"] = XC["B"]["ref_T"]
raw["B"]["raw_unsubtracted_1e12"]["abs_err_vs_mp"] = XC["B"]["abs_err_unsubtracted_vs_mp"]
N["model_cvode"] = dict(KMAX=raw["B"]["KMAX"], mp_ref=raw["B"]["mp_ref"],
    runs=[dict(rtol=r["rtol"], rhs_calls=r["rhs_calls"], seconds=r["seconds"], load_avg_start=r["load_avg_start"], load_avg_end=r["load_avg_end"],
               abs_err_vs_mp=r["abs_err_vs_mp"], max_abs_err_vs_mp=max(r["abs_err_vs_mp"].values())) for r in B_runs],
    unsubtracted=dict(rhs_calls=raw["B"]["raw_unsubtracted_1e12"]["rhs_calls"], abs_err_vs_mp=raw["B"]["raw_unsubtracted_1e12"]["abs_err_vs_mp"],
                      max_abs_err_vs_mp=max(raw["B"]["raw_unsubtracted_1e12"]["abs_err_vs_mp"].values())))
_r12 = [r for r in B_runs if r["rtol"] == 1e-12][0]
N["model_cvode"]["abs_err_subtracted_at_0p1"] = _r12["abs_err_vs_mp"]["0.1"]
N["model_cvode"]["abs_err_unsubtracted_at_0p1"] = raw["B"]["raw_unsubtracted_1e12"]["abs_err_vs_mp"]["0.1"]
N["model_cvode"]["n_T_all"] = int(len(T_all)); N["model_cvode"]["n_T_log"] = int(len(T_log)); N["model_cvode"]["n_T_lin"] = int(len(T_lin))
N["model_cvode"]["gain_at_0p1"] = raw["B"]["raw_unsubtracted_1e12"]["abs_err_vs_mp"]["0.1"]/_r12["abs_err_vs_mp"]["0.1"]
N["model_cvode"]["abs_err_1e8"] = dict(subtracted=XC["B"]["abs_err_vs_mp"]["1e-08"], unsubtracted=XC["B"]["abs_err_unsubtracted_1e8_vs_mp"])
N["model_cvode"]["gain_1e8"] = {T_: XC["B"]["abs_err_unsubtracted_1e8_vs_mp"][T_]/XC["B"]["abs_err_vs_mp"]["1e-08"][T_] for T_ in XC["B"]["ref_T"].__class__(map(str, XC["B"]["ref_T"]))}
y1 = np.array(R["yB"])                       # Debye-subtracted integral at rtol 1e-12, normalised by A T^3
Y = 1.0 + y1                                 # C_V^model(T)/(A T^3)
T = T_all
def series_ratio(Tv, pmax):                  # sum_{q <= pmax} c_q T^(q-3)/A  (normalised partial sum)
    return sum(cp[q]*Tv**(q - 3) for q in ps if q <= pmax)/cp[3]
truncs = [3, 5, 6, 7, 8, 9]
names = {3: "A", 5: "AC", 6: "ACD", 7: "ACDE", 8: "ACDEK", 9: "ACDEKL"}
nxt = {3: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}
resid = {p: np.abs(Y[:nlog] - series_ratio(T_log, p)) for p in truncs}
pred = {p: np.abs(cp[nxt[p]]*T_log**(nxt[p] - 3)/cp[3]) for p in truncs}
r12_ = [r for r in B_runs if r["rtol"] == 1e-12][0]
floor_T = np.array(raw["B"]["ref_T"], dtype=float); floor_err = np.array([r12_["abs_err_vs_mp"][str(T_)] for T_ in raw["B"]["ref_T"]])
floor = float(floor_err.max())
floor_of_T = lambda Tv: np.exp(np.interp(np.log(Tv), np.log(floor_T), np.log(np.maximum(floor_err, 1e-17))))
lad = {}
for p in truncs:
    sel = (resid[p] > 1e3*floor_of_T(T_log)) & (T_log <= 0.06) & (T_log >= 0.005)
    if sel.sum() >= 3:
        sl = np.polyfit(np.log(T_log[sel]), np.log(resid[p][sel]), 1)[0]
        ratio = resid[p][sel]/pred[p][sel]
        lad[names[p]] = dict(fitted_slope=float(sl), expected_slope=nxt[p] - 3, n_points=int(sel.sum()), T_range=[float(T_log[sel].min()), float(T_log[sel].max())],
                             ratio_to_next_term_lowestT=float(ratio[0]), ratio_to_next_term_highestT=float(ratio[-1]))
    else:
        lad[names[p]] = dict(n_points=int(sel.sum()), note="residual at or below the solver floor")
N["ladder"] = dict(solver_floor_abs=floor, solver_floor_abs_at_0p1=float(floor_of_T(0.1)), solver_floor_abs_at_0p005=float(floor_of_T(0.005)), lines=lad)
at = lambda arr, Tv: float(np.interp(np.log(Tv), np.log(T_log), arr))
N["ladder"]["residual_at"] = {names[p]: {str(Tv): at(resid[p], Tv) for Tv in (0.02, 0.05, 0.1, 0.2, 0.3, 0.5)} for p in truncs}
# coefficient recovery   c_hat_p(T) = (C_V - sum_{q<p} c_q T^q)/T^p
rec = {}
for p in truncs[1:]:
    est = (A*T_log**3*Y[:nlog] - sum(cp[q]*T_log**q for q in ps if q < p))/T_log**p
    rel = np.abs(est/cp[p] - 1)
    imin = int(np.argmin(rel))
    rec[str(p)] = dict(best_rel_err=float(rel[imin]), at_T=float(T_log[imin]), rel_err_at_0p02=at(rel, 0.02), rel_err_at_0p05=at(rel, 0.05), rel_err_at_0p1=at(rel, 0.1))
N["coefficient_recovery"] = rec

# what the Lean negative controls would do to a NUMERICAL test (change of C_V/(A T^3) at T)
a2_, a3_, a4_ = cc.ALPHA["a2"], cc.ALPHA["a3"], cc.ALPHA["a4"]
Lb = 55*a2_**3 - 30*a2_*a4_ - 15*a3_**2; Lb54 = 54*a2_**3 - 30*a2_*a4_ - 15*a3_**2
ctl = dict(D_15121=dict(rel_change_of_coefficient=15121/15120 - 1, p=6, c=cp[6]),
           K_8a2a3=dict(rel_change_of_coefficient=8/9 - 1, p=8, c=cp[8]),
           L_54=dict(rel_change_of_coefficient=Lb54/Lb - 1, p=9, c=cp[9]))
for nm, d_ in ctl.items():
    d_["effect_on_CV_over_AT3"] = {str(Tv): d_["rel_change_of_coefficient"]*d_["c"]*Tv**(d_["p"] - 3)/cp[3] for Tv in (0.05, 0.1, 0.2)}
ctl["next_term_c10_over_AT3"] = {str(Tv): cp[10]*Tv**7/cp[3] for Tv in (0.05, 0.1, 0.2)}
ctl["solver_floor_abs"] = floor
N["negative_controls_numerical"] = ctl

# ---------------------------------------------------------------------------------------------- (C) measured table
tab = cc.load_paper_cv()
Tc = R["T_lin"]
C_tot, C_ph = np.array(R["C_tot"]), np.array(R["C_ph"])
paper_tot = np.array([tab["tot"][np.argmin(abs(tab["T"] - t))] for t in Tc]); paper_ph = np.array([tab["ph"][np.argmin(abs(tab["T"] - t))] for t in Tc])
paper_rot = np.array([tab["rot"][np.argmin(abs(tab["T"] - t))] for t in Tc]); paper_err = np.array([tab["err"][np.argmin(abs(tab["T"] - t))] for t in Tc])
d_tot = C_tot/paper_tot - 1; d_ph = C_ph/paper_ph - 1
quad_tot, quad_ph = np.array(XC["C"]["quad_tot"]), np.array(XC["C"]["quad_ph"])
N["measured_cvode"] = dict(kM=float(R["kM"]), KEND=float(R["KEND"]), method=str(raw["method"]),
    rhs_calls_ph=raw["C"]["runs"]["1e-08"]["info_ph"]["rhs_calls"], rhs_calls_rot=raw["C"]["runs"]["1e-08"]["info_tot"]["rhs_calls"],
    seconds=raw["C"]["runs"]["1e-08"]["info_ph"]["seconds"] + raw["C"]["runs"]["1e-08"]["info_tot"]["seconds"],
    load_avg_end=raw["C"]["runs"]["1e-08"]["info_tot"]["load_avg_end"],
    vs_scipy_quad_max_rel=float(np.max(np.abs(C_tot/quad_tot - 1))), vs_scipy_quad_ph_max_rel=float(np.max(np.abs(C_ph/quad_ph - 1))),
    rtol_1e6_vs_1e8_max_rel=float(np.max(np.abs(np.array(R["C_tot_1e6"])/C_tot - 1))),
    vs_paper_total=dict(max_abs_rel=float(np.max(np.abs(d_tot))), median_abs_rel=float(np.median(np.abs(d_tot))), at_T_of_max=float(Tc[np.argmax(np.abs(d_tot))]),
                        n_temperatures=int(len(Tc)), rel_at={str(t): float(d) for t, d in zip(Tc, d_tot) if t in (0.1, 0.2, 0.5, 1.0, 1.3)}),
    vs_paper_phonon=dict(max_abs_rel=float(np.max(np.abs(d_ph))), median_abs_rel=float(np.median(np.abs(d_ph)))),
    paper_table_at={str(t): dict(tot=float(paper_tot[i]), ph=float(paper_ph[i]), rot=float(paper_rot[i])) for i, t in enumerate(Tc) if t in (0.1, 0.2, 0.5, 1.0)},
    paper_cv_over_T3={str(t): float(paper_tot[i]/t**3) for i, t in enumerate(Tc) if t in (0.1, 0.2, 0.3, 0.5)},
    paper_ph_over_T3={str(t): float(paper_ph[i]/t**3) for i, t in enumerate(Tc) if t in (0.1, 0.2, 0.3, 0.5, 1.0, 1.3)},
    ratio_Cv_0p2_over_0p1=float(paper_tot[list(Tc).index(0.2)]/paper_tot[list(Tc).index(0.1)]))
# phonon = roton crossing in my integration
rot = C_tot - C_ph
icr = int(np.argmax(rot > C_ph)) if np.any(rot > C_ph) else None
if icr:
    a_, b_ = icr - 1, icr
    f = lambda i: np.log(rot[i]/C_ph[i])
    Tx = float(np.exp(np.log(Tc[a_]) + (0 - f(a_))*(np.log(Tc[b_]) - np.log(Tc[a_]))/(f(b_) - f(a_))))
    N["measured_cvode"]["T_phonon_equals_roton_interp"] = Tx

# error budget: series (six terms) vs exact polynomial model vs measured phonon part
Ypoly = Y[nlog:]                              # on T_lin
C_poly = A*Tc**3*Ypoly
C_ser6 = np.array([sum(cp[q]*t**q for q in (3, 5, 6, 7, 8, 9)) for t in Tc])
e_trunc = C_ser6/C_poly - 1; e_model = C_poly/C_ph - 1; e_tot = C_ser6/C_ph - 1
rel_err_paper = paper_err/paper_tot
sel_t = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
N["budget"] = {str(t): dict(series6_over_poly_minus1=float(e_trunc[list(Tc).index(t)]), poly_over_measured_ph_minus1=float(e_model[list(Tc).index(t)]),
                            series6_over_measured_ph_minus1=float(e_tot[list(Tc).index(t)]),
                            paper_stated_rel_uncertainty=(None if np.isnan(rel_err_paper[list(Tc).index(t)]) else float(rel_err_paper[list(Tc).index(t)])))
               for t in sel_t}
# first T (on the 0.05 grid) where the six-term series deviates from the exact polynomial model by more than 1 %, 0.1 %
for thr, key in ((1e-2, "first_T_series6_vs_poly_exceeds_1pct"), (1e-3, "first_T_series6_vs_poly_exceeds_0p1pct"), (1e-2, "first_T_series6_vs_measured_ph_exceeds_1pct")):
    arr = np.abs(e_trunc) if "poly" in key else np.abs(e_tot)
    i = int(np.argmax(arr > thr)) if np.any(arr > thr) else None
    N["budget"][key] = (float(Tc[i]) if i is not None else None)
# paper's stated uncertainty (err column) at the temperatures where it is given
N["paper_uncertainty_table"] = {str(t): float(r) for t, r in zip(Tc, rel_err_paper) if not np.isnan(r)}

# ---------------------------------------------------------------------------------------------- asymptotic series: partial sums vs exact
asym = {}
pmax = 40
for t in (0.2, 0.3, 0.5, 0.8):
    i = list(Tc).index(t)
    exact = Ypoly[i]
    sums = np.array([series_ratio(t, p) for p in range(3, pmax + 1)])
    err = np.abs(sums/exact - 1)
    k = int(np.argmin(err))
    terms = {p_: abs(cp[p_])*t**(p_ - 3)/cp[3] for p_ in ps if 5 <= p_ <= pmax}
    sm = min(terms, key=terms.get)
    asym[str(t)] = dict(best_order=int(k + 3), best_rel_err=float(err[k]), err_at_order_9=float(err[9 - 3]), err_at_order_10=float(err[10 - 3]),
                        smallest_term_order=int(sm), smallest_term=float(terms[sm]))
# optimal truncation from the term envelope: p*(T) = order at which max(|t_p|,|t_p+1|,|t_p+2|) is smallest; predicted p* ~ hbar c |u_c|/(k_B T);
# its size fitted to  a - b/T + s ln T  (the prefactor is a power of T), predicted b = hbar c |u_c|/k_B
ps5 = [q_ for q_ in ps if q_ >= 5]
def envelope_min(t):
    tt = np.array([abs(cp[q_])*t**(q_ - 3)/cp[3] for q_ in ps5])
    env = np.maximum.reduce([tt[:-2], tt[1:-1], tt[2:]])
    i = int(np.argmin(env)); return float(env[i]), int(ps5[i + 1])
Tenv = np.arange(0.08, 0.6001, 0.02)
envs = np.array([envelope_min(t)[0] for t in Tenv])
Xf = np.vstack([np.ones_like(Tenv), -1.0/Tenv, np.log(Tenv)]).T
cf, *_ = np.linalg.lstsq(Xf, np.log(envs), rcond=None)
asym["envelope_fit"] = dict(T_range=[float(Tenv[0]), float(Tenv[-1])], a=float(cf[0]), b_K=float(cf[1]), s=float(cf[2]), predicted_b_K=float(Rc*cc.THETA))
asym["pstar"] = {str(t): dict(pstar=envelope_min(t)[1], predicted=float(Rc*cc.THETA/t), envelope=envelope_min(t)[0]) for t in (0.1, 0.15, 0.2, 0.3, 0.4, 0.5)}
N["asymptotic"] = asym
N["asymptotic"]["note"] = "orders p are powers of T; the order-4 coefficient is zero"

# ---------------------------------------------------------------------------------------------- merge with the figure-script numbers
for fname, key in (("ch04_numbers_dispersion.json", "dispersion"), ("ch04_numbers_heatmap.json", "heatmap"),
                   ("ch04_solver_probe_fixed.json", "solver_probe_fixed"), ("ch04_solver_probe_venv.json", "solver_probe_stale_venv"),
                   ("ch04_lean_runs.json", "lean_runs")):
    f = HERE/fname
    if f.exists():
        N[key] = json.load(open(f))

# ---------------------------------------------------------------------------------------------- numbers quoted from Lean sources / one-off runs
import re
_src = (cc.REPO/"lean_src"/"PhononSeries.lean").read_text()
_cert = {}
for _m in re.finditer(r"theorem\s+(\w+)(.*?)(?=\ntheorem|\n/--|\Z)", _src, re.S):
    _lc = re.search(r"linear_combination\s*\((.*?)\)\s*\*\s*h", _m.group(2), re.S)
    if _lc:      # number of monomials of the certificate polynomial multiplying the hypothesis h (top-level + and - signs)
        _e = _lc.group(1); _d = 0; _n = 1
        for _i, _ch in enumerate(_e):
            if _ch in "([{": _d += 1
            elif _ch in ")]}": _d -= 1
            elif _d == 0 and _ch in "+-" and _i > 0 and _e[_i - 1] == " ": _n += 1
        _cert[_m.group(1)] = _n
N["lean_certificate_monomials"] = dict(source="lean_src/PhononSeries.lean", per_theorem=_cert)
N["text_constants"] = dict(
    sympy_seconds=32.4, sympy_seconds_note="wall time (`time`) of one run of exploration/godfrin/derive_cv_series.py on 2026-10-10, shared machine (load 8-35); output kept in facts/ch04_lean_logs/sympy_derivation_output.txt",
    lean_toolchain="4.34.0-rc2", lean_toolchain_note="from facts/lean_audit.md and `lean --version` of the Lake tree used",
    rs_commit_short=str(raw["module"]["commit"])[:7])
(HERE/"ch04_numbers.json").write_text(json.dumps(N, indent=1))
np.savez(HERE/"ch04_analysis.npz", T_log=T_log, T_lin=Tc, Y_log=Y[:nlog], Y_lin=Ypoly, resid=np.array([resid[p] for p in truncs]), pred=np.array([pred[p] for p in truncs]),
         truncs=np.array(truncs), C_ph=C_ph, C_tot=C_tot, C_poly=C_poly, C_ser6=C_ser6, paper_tot=paper_tot, paper_ph=paper_ph, paper_err=paper_err,
         e_trunc=e_trunc, e_model=e_model, e_tot=e_tot, cp_p=np.array(ps), cp_v=np.array([cp[p] for p in ps]), floor=floor, floor_T=floor_T, floor_err=floor_err)
print(json.dumps(N, indent=1)[:6000])
