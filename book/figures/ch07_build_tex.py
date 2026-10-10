#!/usr/bin/env python3
"""Build book/chapters/ch07.tex from the three template parts figures/ch07_template_p{1,2,3}.tex.

Markers (each on a line of its own) are replaced by the EXACT text of a source:
    @@LEAN{File.lean}{a-b}@@            lines a..b (1-based, inclusive) of lean_src/File.lean
    @@LEANBOOK{File.lean}{a-b}@@        lines a..b of book/lean/File.lean   (the book's own new module)
    @@BOOKBLOCK{path}{name1,name2}@@    the code between '# BOOK-BEGIN name' and '# BOOK-END name' in <path> (dedented); several blocks are joined by '# ...'
and @@KEY@@ tokens are replaced by numbers read from figures/ch07_numbers.json (formatted here), so that every number of the text that is not typed by hand
comes from a file written by a script of this chapter.  The script also writes the numbers it formats into ch07_numbers.json['text_numbers'] and checks that no
@@ token is left and that every line of every leanbox listing occurs in its Lean source."""
import json, re, sys, textwrap
from pathlib import Path
HERE = Path(__file__).resolve().parent; BOOK = HERE.parent; ROOT = BOOK.parent
NUMF = HERE / "ch07_numbers.json"
N = json.loads(NUMF.read_text())
TN = {}                                                                   # token -> string, also written to the JSON


def sci(x, d=1):
    """3.3e-7 -> 3.3\\times10^{-7}   (math-mode content, no dollar signs)"""
    if x == 0:
        return "0"
    e = int(np_floor_log10(abs(x))); m = x / 10 ** e
    if round(abs(m), d) >= 10:                                   # 9.99e-4 -> 1.0e-3, not 10.0e-4
        m /= 10; e += 1
    return f"{m:.{d}f}\\times10^{{{e}}}"


def scim(x, d=1):
    return "$" + sci(x, d) + "$"


def np_floor_log10(x):
    import math
    return math.floor(math.log10(x))


def f(x, d=3):
    return f"{x:.{d}f}"


def put(tok, s):
    TN[tok] = s


# ------------------------------------------------------------------ CVODE figure
fd = N["fig_dipole"]
put("SPIRAL_TURNS", f"{fd['spiral']['turns']:.1f}")
dip = [v for k, v in fd["max_rel_err_d2_rtol1e-8"].items() if k.startswith("dipole")]; cor = [v for k, v in fd["max_rel_err_d2_rtol1e-8"].items() if k.startswith("corotating")]
put("DIP_ERR_MIN", scim(min(dip))); put("DIP_ERR_MAX", scim(max(dip))); put("COR_ERR_MIN", scim(min(cor))); put("COR_ERR_MAX", scim(max(cor)))
put("CENTRE_ID_DEV", scim(max(fd["centre_identity_alphap0.0"]["max_abs_dev"], fd["centre_identity_alphap0.3"]["max_abs_dev"])))
put("CENTRE_ERR", scim(fd["centre_displacement_max_abs_err_alphap0.0"])); put("CENTRE_END", f"${fd['centre_displacement_end_alphap0.0']:.0f}$")
wp = fd["work_precision"]
def wpsel(m, mode): return [w for w in wp if w["method"] == m and w["mode"] == mode]
put("WP_A_RANGE", f"{min(w['rhs_calls'] for w in wpsel('adams', 'one call'))}--{max(w['rhs_calls'] for w in wpsel('adams', 'one call'))}")
put("WP_B_RANGE", f"{min(w['rhs_calls'] for w in wpsel('bdf', 'one call'))}--{max(w['rhs_calls'] for w in wpsel('bdf', 'one call'))}")
ratios = [c["rhs_calls"] / o["rhs_calls"] for m in ("bdf", "adams") for o, c in zip(wpsel(m, "one call"), wpsel(m, "60 outputs"))]
put("WP_CHAIN_MIN", f"{min(ratios):.0f}"); put("WP_CHAIN_MAX", f"{max(ratios):.0f}")
bch = {w["rtol"]: w["err"] for w in wpsel("bdf", "60 outputs")}
put("WP_BCH4", scim(bch[1e-4])); put("WP_BCH6", scim(bch[1e-6]))
put("CV_SECONDS", f"{fd['seconds']:.1f}"); put("CV_LOAD", "$" + "$--$".join(f"{x:.1f}" for x in sorted(fd["load_average_start_end"])) + "$")
put("FIXED_NFE", str(fd["cvode_env"]["adams_probe_rhs_calls"])); put("STALE_NFE", f"{N['cvode_stale_probe']['adams_probe_rhs_calls']:,}".replace(",", "\\,"))
# ------------------------------------------------------------------ imprint
fi = N["fig_imprint"]
put("IMP_ALPHA_OLD", f"{fi['old_alpha_apparent']:.4f}"); put("IMP_PEAK_OLD", f"${fi['old_peak_density_t0']:.3f}$"); put("IMP_PEAK_NEW", f"${fi['new_peak_density_t0']:.3f}$")
put("IMP_MOM_OLD_RATIO", f"${fi['old_momentum_t20'][1] / -fi['two_pi_n_d']:.2f}$"); put("IMP_MOM_NEW_RATIO", f"${fi['new_momentum_t20'][1] / -fi['two_pi_n_d']:.2f}$")
# ------------------------------------------------------------------ the fresh run and the archived ensemble
ff = N.get("fig_fields"); fr = N.get("fig_friction"); xc = N.get("estimator_crosscheck")
if ff and fr:
    ch = ff["chunks"]; loads = [c["load_start"] for c in ch] + [c["load_end"] for c in ch]
    te = [0.0] + [c_["t_end"] for c_ in ch]; steps = [round(y - x) for x, y in zip(te[:-1], te[1:])]
    put("RUN_NCHUNK", {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}.get(len(ch), str(len(ch)))); put("RUN_CHMIN", str(min(steps))); put("RUN_CHMAX", str(max(steps)))
    put("RUN_SECONDS", f"{ff['seconds']:.0f}"); put("RUN_TEND", f"{ff['t_end']:.0f}"); put("RUN_LOAD", f"${min(loads):.0f}$--${max(loads):.0f}$")
    put("FIELDS_NOTE", f"for {ff['t_end']:.0f} time units (one run, seed {ff['seed']}; relative energy drift {scim(ff['drift_E'])})")
    p1, p2 = ff["pair1"], ff["pair2"]
    put("RUN_LAPS", f"{(ff['laps_pair1'] + ff['laps_pair2']) / 2:.1f}")
    put("RUN_SPEEDS", f"${p1['centre_speed']:.3f}$ and ${p2['centre_speed']:.3f}$"); put("RUN_MODEL_SPEEDS", f"${p1['model_speed_torus']:.3f}$ and ${p2['model_speed_torus']:.3f}$")
    put("RUN_SPEED_RATIOS", f"${p1['speed_over_model']:.3f}$ and ${p2['speed_over_model']:.3f}$")
    put("RUN_PLANAR_LOW", f"{100 * (1 - p1['planar_speed_1_over_meand'] / p1['model_speed_torus']):.0f} and {100 * (1 - p2['planar_speed_1_over_meand'] / p2['model_speed_torus']):.0f}")
    d_first = (p1["d_first20"] + p2["d_first20"]) / 2; d_last = (p1["d_last20"] + p2["d_last20"]) / 2
    put("RUN_D0", f"{d_first:.1f}"); put("RUN_DEND", f"{d_last:.1f}")
    put("RUN_DMIN", f"{min(p1['d25_min'], p2['d25_min']):.1f}"); put("RUN_DMAX", f"{max(p1['d25_max'], p2['d25_max']):.1f}")
    put("RUN_DWANDER", f"up to ${max(p1['d25_max'] - p1['d25_min'], p2['d25_max'] - p2['d25_min']):.1f}$ in the $25$-unit means")
    put("RUN_A1", f"${p1['alpha_from_d2_slope']:+.4f}$"); put("RUN_A2", f"${p2['alpha_from_d2_slope']:+.4f}$")
    ended = ff["ended"]; pl = 1500
    put("RUN_ENDED_PHRASE", {"t_max": f"reached the planned $t={ff['t_end']:.0f}$ with all four vortices tracked throughout",
                            "stopped": f"was stopped at $t={ff['t_end']:.0f}$ of the ${pl}$ planned, with all four vortices tracked throughout, because the last chunk of the checkpointed run could not get a processor of the shared machine in the time available",
                            "annihilated": f"ended by the annihilation of a pair at $t={ff['t_end']:.0f}$", "track_lost": f"ended by the loss of a track at $t={ff['t_end']:.0f}$"}[ended])
    put("RUN_ALPHA_D2", f"{fr['fresh_run']['alpha_from_d2_slope_mean']:.4f}")
    put("RUN_RMS", f"{fr['energy_identity']['rms_residual']:.2f}"); put("RUN_DH", f"{abs(fr['energy_identity']['H_change']):.2f}"); put("RUN_AE", f"{fr['fresh_run']['rust_full']['alpha_energy']:.4f}"); put("RUN_AR", f"{fr['fresh_run']['rust_full']['alpha_regression']:.4f}"); put("RUN_Z", f"{fr['fresh_run']['z_vs_archived_same_duration']:.1f}"); put("RUN_AE_DIRECT", f"{fr['energy_identity']['alpha_E_direct']:.4f}")
    s4 = fr["fresh_run"]["rust_four_subtracks"]
    put("RUN_AE4", f"{s4['alpha_energy']:.4f}"); put("RUN_AE4_SE", f"{s4['alpha_energy_se']:.4f}"); put("RUN_AR4", f"{s4['alpha_regression']:.4f}"); put("RUN_AR4_SE", f"{s4['alpha_regression_se']:.4f}")
    mean, sd = fr["archived_T0115"]["single_run_alpha_energy_mean_sd"]; put("SINGLE_MEAN", f"{mean:.4f}"); put("SINGLE_SD", f"{sd:.4f}")
    z = abs(s4["alpha_energy"] - mean) / sd
    zr = fr["fresh_run"]["z_vs_archived_same_duration"]; rk = fr["fresh_run"]["rank_lowest_first_of_nine"]
    fe = fr["fresh_run"]["first_1000"]
    put("RUN_AE1000", f"{fe['alpha_energy']:.4f}"); put("RUN_AR1000", f"{fe['alpha_regression']:.4f}"); put("RUN_MOVE", f"${abs(fr['fresh_run']['rust_full']['alpha_energy'] - fe['alpha_energy']):.4f}$")
    dirn = "below" if zr < 0 else "above"
    put("RUN_VERDICT", (f"on the ensemble mean ({abs(zr):.2f} standard deviations away, number {rk} of the nine single runs counted from the lowest)" if abs(zr) < 0.5 else
                        f"{abs(zr):.1f} standard deviations {dirn} the ensemble mean, number {rk} of the nine single runs counted from the lowest" + (", the odd one out" if abs(zr) >= 2 else "")))
    put("SINGLE_CV", f"{100 * sd / mean:.0f}")
    put("RUN_SHRINK", f"{4 * 0.0062 * ff['t_end']:.0f}"); put("RUN_FALL", f"{(ff["d0"] ** 2 - 4 * 0.0062 * ff["t_end"]) ** 0.5:.1f}")
    put("RUN_OMA", f"${fr['fresh_run']['rust_full']['one_minus_alpha_prime']:.3f}\\pm{s4['one_minus_alpha_prime_se']:.3f}$")
    g2 = fr["archived_G2_pairs"]; ds = [x["d_start"] for x in g2]; de = [x["d_end_t1500"] for x in g2]
    put("G2_START", f"${min(ds):.1f}$--${max(ds):.1f}$"); put("G2_END", f"${min(de):.1f}$--${max(de):.1f}$")
    ens = fr["archived_T0115"]["ensemble"]
    put("ARCH_AE", f"{ens['alpha_energy']:.5f}"); put("ARCH_AE_SE", f"{ens['alpha_energy_se']:.5f}"); put("ARCH_AR", f"{ens['alpha_regression']:.5f}"); put("ARCH_AR_SE", f"{ens['alpha_regression_se']:.5f}")
    put("ARCH_OMA", f"{ens['one_minus_alpha_prime']:.4f}"); put("ARCH_OMA_SE", f"{ens['one_minus_alpha_prime_se']:.4f}")
if xc:
    c0 = xc["rust"]["msd_offset"]; put("XCHK_C0", f"{c0:.2f}"); put("RUN_JIT", f"${(c0 / 2) ** 0.5:.2f}$")
    put("XCHK_RELDIFF", sci(xc["max_rel_diff"], 0) if xc["max_rel_diff"] > 0 else "0"); put("XCHK_PY_S", f"{xc['python']['seconds']:.0f}"); put("XCHK_RS_S", f"{xc['rust']['seconds']:.1f}")
# ------------------------------------------------------------------ table of alpha at three temperatures
PE = json.loads((ROOT / "data/generated/pgpe/transport/production_estimates.json").read_text())
def e(k): return PE[k]
put("T0_AE", sci(e("T0")["alpha_energy"]))
put("T0_AR", sci(e("T0")["alpha_regression"]))
for key, tag in (("e0.60", "E060"), ("e0.70", "E070"), ("e0.80", "E080")):
    x = e(key)
    put(tag + "_T", f"{x['T']:.3f}" if key != "e0.70" else f"{x['T']:.3f}"); put(tag + "_RN", f"{x['rho_n']:.3f}"); put(tag + "_N", f"{x['n_runs']}")
    put(tag + "_AE", f"{x['alpha_energy']:.4f}" if x["alpha_energy"] < 0.1 else f"{x['alpha_energy']:.3f}"); put(tag + "_AE_SE", f"{x['alpha_energy_se']:.4f}")
    put(tag + "_AR", f"{x['alpha_regression']:.4f}"); put(tag + "_AR_SE", f"{x['alpha_regression_se']:.4f}")
    put(tag + "_RATIO", f"{x['alpha_d8'] / x['alpha_d12']:.2f}")
# ------------------------------------------------------------------ friction law, six arms
if fr:
    sa = fr["six_arms"]
    put("C_23", f"{sa['c_energy_by_cutoff']['2.09']['c']:.2f}"); put("C_23_SE", f"{sa['c_energy_by_cutoff']['2.09']['se']:.2f}")
    put("C_31", f"{sa['c_energy_by_cutoff']['3.14']['c']:.3f}"); put("C_31_SE", f"{sa['c_energy_by_cutoff']['3.14']['se']:.3f}")
    put("C_63", f"{sa['c_energy_by_cutoff']['6.28']['c']:.3f}"); put("C_63_SE", f"{sa['c_energy_by_cutoff']['6.28']['se']:.3f}")
    put("C_SPREAD", f"{sa['spread_c_energy']:.2f}"); put("BORN_CHI2", f"{sa['Born_rival']['chi2']:.0f}"); put("ONEC_CHI2", f"{sa['one_common_c_energy']['chi2']:.0f}")
    put("AT_E", f"{sa['alpha_over_T_energy']['a']:.4f}"); put("AT_E_SE", f"{sa['alpha_over_T_energy']['se']:.4f}"); put("AT_E_CHI2", f"{sa['alpha_over_T_energy']['chi2']:.2f}")
    put("AT_R", f"{sa['alpha_over_T_regression']['a']:.4f}"); put("AT_R_SE", f"{sa['alpha_over_T_regression']['se']:.4f}"); put("AT_R_CHI2", f"{sa['alpha_over_T_regression']['chi2']:.2f}")
bath = N["bath"]
put("MODES_PI", str([a["n_modes"] for a in bath["arms"] if a["label"].startswith("pi, T=0.115")][0]))
rows = []
for a in sorted(bath["arms"], key=lambda a: (a["kcut"], a["T"])):
    kc = {2.0944: r"2\pi/3", 3.1416: r"\pi", 6.2832: r"2\pi"}[round(a["kcut"], 4)]
    rows.append(rf"$k_c\xi={kc}$ & ${a['T']:.3f}$ & ${a['rho_n_measured']:.4f}$ & ${a['rho_n_landau_RJ']:.4f}$ & {scim(a['rho_n_landau_Bose'], 1)} & ${a['ratio_RJ_over_Bose']:.0f}$ \\")
put("BATH_ROWS", "\n".join(rows))
fr_ = [x["rho_n_landau_RJ"] / x["rho_n_measured"] for x in bath["arms"]]; rt_ = [x["ratio_RJ_over_Bose"] for x in bath["arms"]]
put("BATH_FRAC_MIN", f"{100 * min(fr_):.0f}"); put("BATH_FRAC_MAX", f"{100 * max(fr_):.0f}"); put("BATH_RATIO_MIN", f"{min(rt_):.0f}"); put("BATH_RATIO_MAX", f"{max(rt_):.0f}")
occ = {round(o["k"], 3): o for o in bath["occupations_T0p115"]}
put("OCC_RATIO_K1", scim(occ[1.0]["ratio"])); put("FRAC_EPS_LT_T", f"${100 * bath['fraction_RJ_landau_sum_eps_lt_T']:.2f}\\,\\%$"); put("FRAC_EPS_LT_3T", f"{100 * bath['fraction_RJ_landau_sum_eps_lt_3T']:.1f}\\,\\%")
psp = json.loads((ROOT / "data/generated/pgpe/transport/pair_speed_T0.json").read_text())
put("PS_D6", f"${psp['6.0']['one_minus_alpha_prime_T0']:.2f}$"); put("PS_D16", f"${psp['16.0']['one_minus_alpha_prime_T0']:.2f}$")
# ------------------------------------------------------------------ kicks, wind, bias
fk = N["fig_kicks"]; fw = N["fig_failures"]
for i, key in enumerate(("0.115", "0.220", "0.353"), 1):
    m = fk[f"msd_{key}"]; put(f"GAM{i}", f"{m['gamma_20_400']:.2f}\\pm{m['gamma_se']:.2f}")
for i, key in enumerate(("e0.60", "e0.70", "e0.80"), 1):
    put(f"RE{i}", f"{fk['einstein'][key]['R_E']:.1f}")
wv = fw["wind_vs_data_summary"]; put("WV_MIN", f"{wv['abs_end_minus_wind_min']:.1f}"); put("WV_MAX", f"{wv['abs_end_minus_wind_max']:.1f}"); put("WF_MIN", f"{wv['end_minus_free_min']:.1f}"); put("WF_MAX", f"{wv['end_minus_free_max']:.1f}")
wr = fw["wind_runs"]; r1 = wr["W1_e0.60_dipole_d12_s1.npz"]; r2 = wr["W1_e0.60_dipole_d12_s2.npz"]; W3 = fw["W3"]
put("W1_D0", f"{r1['d_first20']:.1f}"); put("W1_S1_MIN", f"{r1['d_at_1800']:.1f}"); put("W1_S1_LO", f"{r1['d_range_after_2000_smoothed'][0]:.1f}"); put("W1_S1_HI", f"{r1['d_range_after_2000_smoothed'][1]:.1f}")
put("W1_S2_MIN", f"{r2['d_min_smoothed']:.1f}"); put("W1_S2_END", f"{r2['d_end_last100']:.1f}")
w3 = [W3["W1_e0.60_dipole_d12_s1.npz"], W3["W1_e0.60_dipole_d12_s2.npz"]]
put("W3_S1", f"{w3[0]['slope_unsmoothed']:.2f}"); put("W3_S2", f"{w3[1]['slope_unsmoothed']:.2f}")
put("W3_SM", f"{w3[0]['slope']:.2f}" if abs(w3[0]['slope'] - w3[1]['slope']) < 0.01 else f"{w3[0]['slope']:.2f} and {w3[1]['slope']:.2f}")
rows = []
for key, lab in (("e0.60", "0.14"), ("e0.70", "0.27"), ("e0.80", "0.43")):
    x = fk["einstein"][key]; ex = int(np_floor_log10(x["eta"]))
    rows.append(f"${lab}$ & ${x['gamma']:.2f}$ & $({x['eta'] * 1e4:.1f}\\pm{x['eta_se'] * 1e4:.1f})\\times10^{{-4}}$ & ${x['K']:.1f}$ & ${x['R_E']:.1f}\\pm{x['R_E_se_from_eta_only']:.1f}$ & {'yes' if x['quoted'] else 'no'} \\\\")
put("EIN_ROWS", "\n".join(rows))
w = fw["wind"]
put("RN64", f"{w['rho_n64']:.3f}"); put("W64", f"{w['w64']:.3f}"); put("WD64", f"{w['w64_d0sq']:.1f}"); put("B64", f"{w['b64']:.1f}"); put("A64", f"{w['a64']:.1f}")
put("LAM64", sci(w["relaxation_rate_L64_linearised"])); put("TAU64", f"{round(w['relaxation_time_L64_linearised'], -2):.0f}"); put("WD8", f"{w['w8_d0sq']:.1f}")
put("RN96", f"{w['rho_n96']:.3f}"); put("WD96", f"{w['w96_d0sq']:.1f}"); put("C96", f"{w['C96']:.1f}")
br = fw["bias_rows"]; lines = []
for r in br:
    eta = "$0$" if r["eta"] == 0 else scim(r["eta"], 0)
    bias = "$0$" if r["eta"] == 0 else f"${100 * (r['aE'] / 0.02 - 1):.0f}\\,\\%$"
    lines.append(rf"{eta} & ${r['aE']:.4f}\pm{r['aE_sd']:.4f}$ & ${r['aR']:.4f}\pm{r['aR_sd']:.4f}$ & {bias} \\")
nz = [r for r in br if r["eta"] > 0]
def pc(x):
    t = f"{abs(x):.1f}"; return t[:-2] if t.endswith(".0") else t
put("BIAS_PCT", ", ".join(f"${pc(100 * (r['aE'] / 0.02 - 1))}$" for r in nz[:-1]) + f" and ${pc(100 * (nz[-1]['aE'] / 0.02 - 1))}\\%$")
put("BIAS_REG_PCT", f"${pc(min(100 * (r['aR'] / 0.02 - 1) for r in nz))}$ to ${pc(max(100 * (r['aR'] / 0.02 - 1) for r in nz))}\\%$" if False else "$" + "$ to $".join([pc(100 * (nz[0]['aR'] / 0.02 - 1)), pc(100 * (nz[-1]['aR'] / 0.02 - 1))]) + "\\%$")
put("BIAS_AE", ", ".join(f"${r['aE']:.4f}\\pm{r['aE_sd']:.4f}$" for r in nz)); put("BIAS_AR", ", ".join(f"${r['aR']:.4f}\\pm{r['aR_sd']:.4f}$" for r in nz))
put("BIAS_ROWS", "\n".join(lines)); put("BIAS_SEEDS", "8" if "g0_scan" in fw.get("bias_source", "") and "run for this chapter" in fw.get("bias_source", "") else "8--10")

# ------------------------------------------------------------------ assemble
def lines_of(path, spec):
    L = path.read_text().split("\n"); out = []
    for part in spec.split(","):
        a, b = part.split("-"); out += L[int(a) - 1:int(b)]
    return "\n".join(out)


def block_of(path, names):
    text = path.read_text().split("\n"); chunks = []
    for name in names.split(","):
        i0 = next(i for i, l in enumerate(text) if l.strip() == f"# BOOK-BEGIN {name}"); i1 = next(i for i, l in enumerate(text) if l.strip() == f"# BOOK-END {name}")
        chunks.append(textwrap.dedent("\n".join(text[i0 + 1:i1])))
    return "\n# ...\n".join(chunks)


src = "\n".join((HERE / f"ch07_template_p{i}.tex").read_text() for i in (1, 2, 3))
src = "\n".join(l for l in src.split("\n") if not l.startswith("% Chapter 7 -- template") and not l.startswith("% lines of lean_src") )
out = []
for line in src.split("\n"):
    m = re.fullmatch(r"@@LEAN\{([^}]*)\}\{([^}]*)\}@@", line.strip())
    if m:
        out.append(lines_of(ROOT / "lean_src" / m.group(1), m.group(2))); continue
    m = re.fullmatch(r"@@LEANBOOK\{([^}]*)\}\{([^}]*)\}@@", line.strip())
    if m:
        out.append(lines_of(BOOK / "lean" / m.group(1), m.group(2))); continue
    m = re.fullmatch(r"@@BOOKBLOCK\{([^}]*)\}\{([^}]*)\}@@", line.strip())
    if m:
        out.append(block_of(ROOT / m.group(1) if m.group(1).startswith("book/") else BOOK / m.group(1), m.group(2))); continue
    out.append(line)
tex = "\n".join(out)
missing = set()
def sub(m):
    k = m.group(1)
    if k in TN:
        return TN[k]
    missing.add(k); return ("\\textbf{[TBD:" + k.replace('_', '\\_') + "]}") if "--draft" in sys.argv else m.group(0)
tex = re.sub(r"@@([A-Z0-9_]+)@@", sub, tex)
(BOOK / "chapters").mkdir(exist_ok=True)
(BOOK / "chapters/ch07.tex").write_text(tex)
# derived checks of numbers typed by hand in the template (kept in the JSON for the report)
chk = {}
for key in ("e0.60", "e0.70", "e0.80"):
    x = PE[key]
    chk[key] = dict(T_over_TBKT=x["T"] / 0.821, alpha_E_over_rho_n=x["alpha_energy"] / x["rho_n"], regression_over_energy=x["alpha_regression"] / x["alpha_energy"], alpha_d8_over_d12=x["alpha_d8"] / x["alpha_d12"])
chk["rho_n_ratio_hot_over_cold"] = PE["e0.80"]["rho_n"] / PE["e0.60"]["rho_n"]
chk["alpha_over_rho_n_numbers_in_text"] = [0.23, 0.26, 0.22]
# record the formatted numbers
cur = json.loads(NUMF.read_text()); cur["text_numbers"] = {k: v for k, v in TN.items() if "\n" not in v}; cur["derived_checks"] = chk; NUMF.write_text(json.dumps(cur, indent=1, default=float))
print("wrote", BOOK / "chapters/ch07.tex", len(tex.split()), "words incl. markup")
if missing:
    print("UNRESOLVED TOKENS:", sorted(missing))
    if "--draft" not in sys.argv:
        sys.exit(1)

# ------------------------------------------------------------------ check: every line of every leanbox listing occurs in its Lean source
ok = True
for m in re.finditer(r"\\begin\{leanbox\}\{([^}]*)\}(.*?)\\end\{leanbox\}", tex, re.S):
    title = m.group(1).replace("\\_", "_").split(" ")[0]; body = m.group(2)
    srcf = ROOT / "lean_src" / f"{title}.lean"
    if not srcf.exists():
        srcf = BOOK / "lean" / f"{title}.lean"
    if not srcf.exists():
        print("leanbox", title, ": no source file found"); ok = False; continue
    stext = srcf.read_text(); code = re.search(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", body, re.S)
    for l in code.group(1).split("\n"):
        if l.strip() and l not in stext:
            print("NOT FOUND in", srcf.name, ":", l); ok = False
print("leanbox check:", "all listing lines occur in their sources" if ok else "PROBLEMS")
