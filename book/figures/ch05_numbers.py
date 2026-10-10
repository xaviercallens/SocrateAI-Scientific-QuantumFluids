"""Chapter 5: assemble figures/ch05_numbers.json and the LaTeX macro files that chapters/ch05.tex reads.

Every number in the text is a macro \\cfiveV{key} defined in figures/ch05_numbers.tex (an undefined key is a LaTeX error, so the
text can only quote numbers that were computed).  Inputs, all produced by scripts in this directory:
    ch05_helium.py            table-derived numbers (the published SVP dispersion table of Godfrin et al. 2021, ancillary file)
    ch05_run_log.json         broadband runs R1-R4 of ch05_dispersion_run.py (Rust engine qf_pgpe)
    ch05_solver_numbers.json  statistics computed by ch05_solver_fig.py from ch05_results.npz
    ch05_rings_numbers.json   ring-wave experiment (ch05_rings.py)
    ch05_cvode_new.json / ch05_cvode_old.json   the CVODE referee (ch05_cvode.py, two builds of the Python module)
    ../lean/Ch05_BogoliubovDispersion.compile.log   the Lean compile log (axioms)
Run from book/figures:  ../../.venv/bin/python ch05_numbers.py
"""
import json, re, sys
from pathlib import Path
import numpy as np
import ch05_helium as H
from ch05_common import bog

HERE = Path(__file__).resolve().parent
N = {}          # json
K = {}          # macros

def _value(tex):
    """numeric value of a macro body if it is a plain number or  a x 10^e  (else None)"""
    t = re.sub(r"\\ensuremath\{(.*)\}$", r"\1", str(tex)).replace("\\,", "")
    try:
        return float(t)
    except ValueError:
        pass
    m = re.fullmatch(r"([0-9.]+)\\times10\^\{(-?[0-9]+)\}", t)
    return float(m.group(1)) * 10 ** int(m.group(2)) if m else None

def put(key, tex, raw=None):
    K[key] = tex
    N[key] = dict(tex=tex, value=raw if raw is not None else _value(tex))

def f(x, nd):                       # fixed decimals
    return f"{x:.{nd}f}"

def sig(x, n):
    if x == 0:
        return "0"
    e = int(np.floor(np.log10(abs(x))))
    return f"{x:.{max(n - 1 - e, 0)}f}"

def sci(x, nd=1):                   # 2.6e-5 -> $2.6\times10^{-5}$ (as math)
    if x == 0:
        return "0"
    e = int(np.floor(np.log10(abs(x)))); m = x / 10 ** e
    s = f"{m:.{nd}f}"
    if s.startswith("10"):
        s = f"{1.0:.{nd}f}"; e += 1
    return f"\\ensuremath{{{s}\\times10^{{{e}}}}}"

def ppm(x, nd=2):
    return f"{1e6 * x:.{nd}f}"

# --------------------------------------------------------------------------------------------------- helium table
F = H.features()
put("tableRows", f"{F['table_rows']:,}".replace(",", "\\,"), F["table_rows"]); put("nErrRows", str(F["rows_with_error"]))
put("kmax", f(F["k_max"], 1)); put("c", f(F["c_ms"], 1)); put("kDense", f(float(H.load_table()[0][np.where(np.round(np.diff(H.load_table()[0]), 4) != 0.002)[0][0]]), 2))
put("maxonKshort", f(F["maxon_grid_k"], 1)); put("maxonE", f(F["maxon_grid_e_meV"], 2))                       # the table's own maximum (1.1914 meV at 1.114)
put("rotonE", f(F["roton_grid_e_meV"], 3)); put("rotonGapK", f(F["roton_grid_gap_K"], 2)); put("rotonKshort", f(F["roton_grid_k"], 2))   # the table's own minimum (0.7413 meV at 1.920)
put("rotonMass", f(F["roton_mass_over_m4"], 3))
put("landauV", f(F["landau_velocity_ms"], 1)); put("landauK", f(F["landau_k_A_inv"], 2)); put("landauOverC", f(F["landau_over_c"], 3))
put("landauQuad", f(F["landau_quadratic_roton_ms"], 1)); put("landauQuadPct", f(100 * abs(F["landau_quadratic_roton_ms"] / F["landau_velocity_ms"] - 1), 2))
put("phaseMaxPct", f(100 * (F["phase_velocity_max_over_c"] - 1), 1))
vph_max_ms = F["phase_velocity_max_over_c"] * F["c_ms"]
put("vphLow", f(F["vph_at_k_0p01_ms"], 1)); put("phaseMaxPctAlt", f(100 * (vph_max_ms / F["vph_at_k_0p01_ms"] - 1), 1)); put("phaseMaxK", f(F["phase_velocity_max_at_k"], 2))
put("kGroup", f(F["k_group_series"], 3)); put("kSym", f(F["k_sym_series"], 3)); put("kPhase", f(F["k_phase_series"], 3))
put("kSymTable", f(F["k_sym_table_crossings"][0], 3))
put("shiftG", f(F["k_group_shift_max"], 3)); put("shiftP", f(F["k_phase_shift_max"], 3))
put("symMax", f(F["sym_excess_max_ueV"], 1)); put("symMaxK", f(F["sym_excess_max_at_k"], 2))
put("seriesDevMax", f(F["series_minus_table_max_ueV_025_05"], 1))
put("kstar", f(F["kstar_A_inv"], 2)); put("alphaBog", f(F["alpha2_bogoliubov_barem_A2"], 3)); put("alphaRatio", f(F["alpha2_ratio"], 0))
put("h2m4", f(F["hbar2_over_2m4_meV_A2"], 3))
# quantities quoted from the arXiv version of the paper (read in data/external/godfrin_papers/.../2020-Dispersion-paper-v6d.tex)
N["paper_quotes_used_literally"] = {"Delta_R_calibration_meV": "0.7418 +- 0.001 (Stirling, triple axis; used to calibrate the energy scale)", "c_ultrasound_ms": "238.3 +- 0.1",
    "alpha2_Rugar_Foster_A2": "1.55 +- 0.01 (alpha1 = 0)", "series_SVP_A": "alpha2 = 1.55, alpha3 = -4.04, alpha4 = 2.30 (valid k < 0.5 A^-1)",
    "normal_dispersion_pressure_bar": "about 20 (20.4 in the DMBT-corrected analysis)", "table_composition": "k < 0.15 ultrasound; 0.15-0.3 combined; > 0.3 neutron",
    "exercise1_roton": "Delta = 0.7418 meV, k_R = 1.918 A^-1, mu_R = 0.141 (paper's Table III)", "relative_energy_systematic": 2.1e-3,
    "source": "arXiv:2012.09067v1 (read from data/external/godfrin_papers/.../2020-Dispersion-paper-v6d.tex)"}
N["from_paper_text"] = dict(resolution_fwhm_meV_at_Ei_3p52=0.07, more_than_pixels_per_bin=70, detector_pixels="384 tubes x 241 pixels",
                            source="arXiv:2012.09067v1, Sections 'The time of flight spectrometer IN5' and 'Detailed pixel-by-pixel analysis'")
put("resFWHM", "0.07"); put("nPixBin", "70")
k_, e_, de_ = H.load_table()
j03 = int(np.argmin(np.abs(k_ - 0.3)))
fin = np.where(np.isfinite(de_))[0]; jerr = fin[np.argmin(np.abs(k_[fin] - 0.3))]          # nearest row that carries an uncertainty (k = 0.298)
put("err03ueV", f(1e3 * de_[jerr], 1)); put("bend03ueV", f(1e3 * (e_[j03] - H.HBARC * k_[j03]), 0))
N["err_row_used"] = dict(k=float(k_[jerr]), err_meV=float(de_[jerr]))
# helium phase velocity at the roton in the universal plot
put("rotonYat", f(F["roton_grid_e_meV"] / (H.HBARC * F["roton_grid_k"]), 2))
# group velocity landmarks of the table (local linear fit, window +-0.06 A^-1)
k, e, de = H.load_table()
vg = H.group_velocity(k, e, win=0.06) / H.C_SVP
s = (k >= 0.1) & (k <= 0.8); i = np.nanargmax(np.where(s, vg, -9))
put("vgMax", f(vg[i], 2)); put("vgMaxPct", f(100 * (vg[i] - 1), 1)); put("vgMaxK", f(k[i], 2))
j = np.where((k > k[i]) & (k < 1.0) & (vg < 1))[0][0]; put("vgCrossK", f(k[j], 2))
idx = np.where((k > 0.9) & (k < 1.4))[0]; z = idx[np.where(np.diff(np.sign(vg[idx])) != 0)[0]]; put("vgZeroK", f(k[z[0]], 2))
s3 = (k > 1.1) & (k < 1.9); i3 = np.nanargmin(np.where(s3, vg, 9)); put("vgMin", f(vg[i3], 2)); put("vgMinK", f(k[i3], 2))
N["group_velocity_landmarks"] = dict(max=float(vg[i]), max_k=float(k[i]), crosses_c_k=float(k[j]), zero_k=float(k[z[0]]), min=float(vg[i3]), min_k=float(k[i3]))
# exercise 1: Landau closed form with the printed parameters (Delta_R = 0.7418 meV, k_R = 1.918, mu_R = 0.141)
a = H.HBAR2_2M4 / 0.141; kL = np.sqrt(1.918 ** 2 + 0.7418 / a)
put("exLandau", f(2 * a * (kL - 1.918) * H.MS_PER_MEVA, 1))
# exercise 3: a non-local interaction with a mean-field roton:  n V(k) = 1 - 3 k^2 exp(-k^2),  hbar = m = 1
kk = np.linspace(1e-3, 6, 600000)
om2 = (kk ** 2 / 2) * (kk ** 2 / 2 + 2 * (1 - 3 * kk ** 2 * np.exp(-kk ** 2)))
assert (om2 > 0).all()
om = np.sqrt(om2); d = np.sign(np.diff(om)); ch = np.where(np.diff(d) != 0)[0] + 1
imax, imin = ch[0], ch[1]
put("mfMaxK", f(kk[imax], 2)); put("mfMaxW", f(om[imax], 3)); put("mfMinK", f(kk[imin], 2)); put("mfMinW", f(om[imin], 3))
il = np.argmin(om / kk); put("mfLandau", f(om[il] / kk[il], 3)); put("mfLandauK", f(kk[il], 2))
N["mean_field_roton_example"] = dict(maxon_k=float(kk[imax]), maxon_w=float(om[imax]), roton_k=float(kk[imin]), roton_w=float(om[imin]),
                                     landau=float(om[il] / kk[il]), landau_k=float(kk[il]), all_omega2_positive=True)

# --------------------------------------------------------------------------------------------------- pressure series
LP = H.landau_vs_pressure()
N["landau_vs_pressure"] = LP
put("pLandau0", f(LP[0]["landau_ms"], 1)); put("pLandau24", f(LP[-1]["landau_ms"], 1))
put("pRatio0", f(LP[0]["landau_over_c"], 3)); put("pRatio24", f(LP[-1]["landau_over_c"], 3))
put("pC24", f(LP[-1]["c_ultrasound_ms"], 0)); put("pCrise", f(100 * (LP[-1]["c_ultrasound_ms"] / LP[0]["c_ultrasound_ms"] - 1), 0))
put("pRoton24", f(LP[-1]["roton_E_meV"], 3)); put("pKR24", f(LP[-1]["roton_k"], 2)); put("pP24", f(LP[-1]["P_bar"], 2))
put("pKmaxRange", f(min(r["k_range_max"] for r in LP), 1))
tp = ["\\begin{table}[tp]\\centering\\small",
      "\\begin{tabular}{rrrrrr}\\toprule",
      "$P$ (bar) & $c$ (m/s) & $\\Delta_{\\rm R}$ (meV) & $k_{\\rm R}$ ($\\text{\\AA}^{-1}$) & $v_{\\rm L}$ (m/s) & $v_{\\rm L}/c$ \\\\\\midrule"]
for r in LP:
    tp.append(f"{r['P_bar']:.2f} & {r['c_ultrasound_ms']:.1f} & {r['roton_E_meV']:.4f} & {r['roton_k']:.3f} & {r['landau_ms']:.1f} & {r['landau_over_c']:.3f} \\\\")
tp += ["\\bottomrule\\end{tabular}",
       "\\caption{\\textbf{The Landau velocity against pressure}, from the seven-pressure table that accompanies the paper (neutron data from $0.15\\ \\text{\\AA}^{-1}$ to about $\\cfiveV{pKmaxRange}\\ \\text{\\AA}^{-1}$). $c$ is the ultrasonic sound velocity quoted in the paper; $\\Delta_{\\rm R}$ and $k_{\\rm R}$ are the minimum of the tabulated curve; $v_{\\rm L}=\\min_{k>1\\,\\text{\\AA}^{-1}}\\varepsilon/\\hbar k$ always lies inside the tabulated range. The sound speed rises by $\\cfiveV{pCrise}$ per cent over this pressure range while the Landau velocity falls.}\\label{ch05:tab-pressure}",
       "\\end{table}"]
(HERE / "ch05_pressure_table.tex").write_text("% generated by ch05_numbers.py from the 7-pressure ancillary table\n" + "\n".join(tp) + "\n")

# --------------------------------------------------------------------------------------------------- solver runs
L = json.load(open(HERE / "ch05_run_log.json"))
S = json.load(open(HERE / "ch05_solver_numbers.json"))
R1, R2 = L["R1"], L["R2"]
put("nModesMain", str(R1["n_modes_fitted"])); put("nmodesRetained", str(R1["n_modes_fitted"] + 1)); put("nModesG2", str(R2["n_modes_fitted"]))
put("Tmain", f"{R1['T']:.0f}"); put("nGolden", "28")
put("secRun", f(R1["seconds_run"], 0)); put("secFit", f(R1["seconds_fit"], 0))
put("medMain", ppm(R1["median_abs_dev"], 2)); put("p99Main", ppm(R1["p99_abs_dev"], 1)); put("maxMain", ppm(R1["max_abs_dev"], 0))
put("medG2", ppm(R2["median_abs_dev"], 2)); put("medSplit", ppm(R1["median_split"], 1))
put("medLowK", ppm(S["R1"]["median_abs_dev_k_lt_0p4"], 1)); put("medHighK", ppm(S["R1"]["median_abs_dev_k_ge_2p5"], 2))
B = S["band"]
put("nBand", str(B["n_k_ge_0p5"])); put("zMin", f(B["z_min_k_ge_0p5"], 3)); put("zMax", f(B["z_max_k_ge_0p5"], 3)); put("zDev", f(B["max_abs_z_minus_exact_k_ge_0p5"], 3))
D = S["dt_ladder"]
put("ladA", sci(D["median"][0], 1)); put("ladB", sci(D["median"][1], 1)); put("ladC", sci(D["median"][2], 1))
put("ratioA", f(D["ratio_004_over_002"], 1)); put("ratioB", f(D["ratio_002_over_001"], 1))
put("ladVsFit", f(R1["median_abs_dev"] / D["median"][1], 0))
C = S["collapse"]
put("collapseA", sci(C["max_abs_y_over_universal_minus_1_g1"], 1)); put("collapseB", sci(C["max_abs_y_over_universal_minus_1_g2"], 1))
lab = L["R1_lab_frame"]
put("labK", f(lab["k"], 3)); put("labOmega", f(lab["omega_bog"], 4))
put("labPeakA", f(lab["lab_frame_peaks_rad_per_t"][0], 4)); put("labPeakB", f(lab["lab_frame_peaks_rad_per_t"][1], 4))
put("labExpA", f(lab["expected_minus_mu_pm_omega"][0], 4)); put("labExpB", f(lab["expected_minus_mu_pm_omega"][1], 4))
A = L["R4"]
put("ampK1", f(A["m2_eps0.01"]["k"], 3)); put("ampK2", f(A["m8_eps0.01"]["k"], 3))
put("ampS1", sci(A["m8_eps0.01"]["rel_shift"], 1)); put("ampS2", sci(A["m8_eps0.1"]["rel_shift"], 1)); put("ampS3", sci(A["m8_eps0.3"]["rel_shift"], 1))
put("ampS3pct", f(-100 * A["m8_eps0.3"]["rel_shift"], 1)); put("ampR1", f(A["m2_eps0.1"]["rel_resid"], 2))
put("unkMain", f"{2 * (R1['n_modes_fitted'] + 1):,}".replace(",", "\\,"), 2 * (R1["n_modes_fitted"] + 1))
put("relSys", "2.1\\times10^{-3}", 2.1e-3)
put("phaseMaxRatio", f(F["phase_velocity_max_over_c"], 3))
# rings
Rg = json.load(open(HERE / "ch05_rings_numbers.json"))
put("vgKcut", f(Rg["vg_at_kcut"], 2))
put("ringRmin", f(Rg["r_min"], 0)); put("ringRmax", f(Rg["r_max"], 0)); put("ringKmin", f(Rg["k_min"], 1)); put("ringKmax", f(Rg["k_max"], 1))
put("ringMed", f(100 * Rg["median_abs_rel_dev"], 1)); put("ringMax", f(100 * Rg["max_abs_rel_dev"], 0))

# --------------------------------------------------------------------------------------------------- CVODE referee
tab = []
try:
    new = json.load(open(HERE / "ch05_cvode_new.json")); old = json.load(open(HERE / "ch05_cvode_old.json"))
except FileNotFoundError:
    new = old = None
# a JSON marked dry_run (tiny configurations, written only to test the layout of the tables) must never reach the chapter
if new is not None and (new.get("dry_run") or old.get("dry_run")) and "--allow-dry-run" not in sys.argv:
    print("WARNING: ch05_cvode_*.json is a DRY RUN; its numbers are ignored (pass --allow-dry-run to test the layout)", file=sys.stderr)
    new = old = None
if new is not None:
    M = new["main"]
    put("cvN", str(M["N"])); put("cvModes", str(M["n_modes"])); put("cvUnknowns", str(M["n_unknowns"])); put("cvT", f"{M['T']:.0f}")
    put("cvRustSec", f(M["seconds_rust_rk4"], 1)); put("cvRk4Dt", sci(M["rk4_dt_vs_dt4_max"], 1))
    put("cvEta", "10^{-4}")
    for r_ in M["ladder"]:
        put("cvErr" + str(int(round(-np.log10(r_["rtol"])))), sci(r_["omega_max_rel_vs_fine_rk4"], 1))
    put("cvBogMax", sci(M["rk4_vs_bogoliubov_max"], 1))
    _kk = np.array(M["distinct_k"]); _per = M["T"] * bog(_kk, M["g"]) / (2 * np.pi)
    put("cvPerMin", f(_per.min(), 1)); put("cvPerMax", f(_per.max(), 1))
    put("cvFineErr", sci(M["rk4_dt_vs_dt4_max"] / (4 ** 4 - 1), 1))
    last = M["ladder"][-1]
    put("cvBestTol", f"\\ensuremath{{10^{{{int(round(np.log10(last['rtol'])))}}}}}"); put("cvBestErr", sci(last["omega_max_rel_vs_fine_rk4"], 1)); put("cvBestTraj", sci(last["trajectory_max_rel"], 1))
    def row(r):
        return (f"\\ensuremath{{10^{{{int(round(np.log10(r['rtol'])))}}}}} & {r['rhs_calls']:,} & {r['seconds']:.1f} & {sci(r['omega_max_rel_vs_fine_rk4'], 1)} & {sci(r['trajectory_max_rel'], 1)} \\\\"
                ).replace(",", "\\,")
    t1 = ["\\begin{table}[t]\\centering\\small",
          "\\begin{tabular}{rrrrr}\\toprule",
          "tolerance (rtol) & right-hand sides & wall (s) & $\\max|\\Delta\\omega|/\\omega$ & $\\max|\\Delta s|/|s|$ \\\\\\midrule"]
    t1 += [row(r) for r in M["ladder"]]
    t1 += ["\\bottomrule\\end{tabular}",
           "\\caption{\\textbf{CVODE against the Rust engine.} The same random pulse ($\\eta=10^{-4}$) on a box of \\cfiveV{cvN}$^2$ grid points with \\cfiveV{cvModes} retained modes ($\\cfiveV{cvUnknowns}$ real unknowns), integrated to $T=\\cfiveV{cvT}$ by CVODE's Adams method (atol $=10^{-3}\\,$rtol) through the Python interface and by the engine ($\\Delta t=0.01$ and a four times smaller step as reference).",
           "Columns: right-hand-side evaluations, wall time on the shared machine, the largest relative difference between the frequencies read from the CVODE record and from the fine-step engine record, and the largest difference between the two mode records, relative to the rms amplitude of each mode.",
           "The engine's own frequencies differ from its four-times-finer run by at most \\cfiveV{cvRk4Dt}, and the engine took \\cfiveV{cvRustSec} s for this record.",
           "Both records go through the same fit; the frequencies of this short record, in which the modes complete between \\cfiveV{cvPerMin} and \\cfiveV{cvPerMax} periods, differ from Bogoliubov's formula by up to \\cfiveV{cvBogMax}, which cancels in the difference between the two records.}\\label{ch05:tab-cvode}",
           "\\end{table}"]
    # old vs fixed build, same small box
    So, Sn = old["small"]["ladder"], new["small"]["ladder"]
    t2 = ["\\begin{table}[t]\\centering\\small",
          "\\begin{tabular}{rrrrr}\\toprule",
          "tolerance (rtol) & \\multicolumn{2}{c}{older build} & \\multicolumn{2}{c}{current build}\\\\",
          " & right-hand sides & $\\max|\\Delta\\omega|/\\omega$ & right-hand sides & $\\max|\\Delta\\omega|/\\omega$ \\\\\\midrule"]
    for a_, b_ in zip(So, Sn):
        t2.append((f"\\ensuremath{{10^{{{int(round(np.log10(a_['rtol'])))}}}}} & {a_['rhs_calls']:,} & {sci(a_['omega_max_rel_vs_fine_rk4'], 1)} & {b_['rhs_calls']:,} & {sci(b_['omega_max_rel_vs_fine_rk4'], 1)} \\\\").replace(",", "\\,"))
    t2 += ["\\bottomrule\\end{tabular}",
           f"\\caption{{\\textbf{{The same experiment on two builds of the Python module.}} A box of ${new['small']['N']}^2$ grid points (${new['small']['n_modes']}$ modes, ${new['small']['n_unknowns']}$ unknowns), $T={new['small']['T']:.0f}$, the same pulse. The older build is the module of the project's virtual environment (installed on \\cfiveV{{cvOldDate}}); the current one was built from the rusty-SUNDIALS tree (commit 5db8041) that contains the fix of the Adams order.}}\\label{{ch05:tab-cvode-builds}}",
           "\\end{table}"]
    (HERE / "ch05_cvode_table.tex").write_text("% generated by ch05_numbers.py from ch05_cvode_new.json / ch05_cvode_old.json\n" + "\n".join(t2) + "\n\n" + "\n".join(t1) + "\n")
    sc = new["scaling"]
    put("cvScale8", f"{sc[0]['ladder'][0]['rhs_calls']:,}".replace(",", "\\,")); put("cvScale16", f"{sc[1]['ladder'][0]['rhs_calls']:,}".replace(",", "\\,")); put("cvScale32", f"{sc[2]['ladder'][0]['rhs_calls']:,}".replace(",", "\\,"))
    put("cvScaleSec8", f(sc[0]["ladder"][0]["seconds"], 1)); put("cvScaleSec16", f(sc[1]["ladder"][0]["seconds"], 1)); put("cvScaleSec32", f(sc[2]["ladder"][0]["seconds"], 1))
    put("cvScaleUnk8", str(sc[0]["n_unknowns"])); put("cvScaleUnk16", str(sc[1]["n_unknowns"]))
    put("cvScaleUnk32", str(sc[2]["n_unknowns"])); put("unkRatio", f(2 * (R1["n_modes_fitted"] + 1) / sc[2]["n_unknowns"], 0))
    put("cvSmallN", str(new["small"]["N"]))
    put("cvGrowOldA", f(So[1]["rhs_calls"] / So[0]["rhs_calls"], 0)); put("cvGrowOldB", f(So[2]["rhs_calls"] / So[1]["rhs_calls"], 0))
    put("cvOldFallA", f(So[0]["omega_max_rel_vs_fine_rk4"] / So[1]["omega_max_rel_vs_fine_rk4"], 0)); put("cvOldFallB", f(So[1]["omega_max_rel_vs_fine_rk4"] / So[2]["omega_max_rel_vs_fine_rk4"], 0))
    import datetime, os
    old_so = old["small"]["rusty_sundials_file"]
    old_so_dir = os.path.dirname(old_so)
    so_files = [os.path.join(old_so_dir, x) for x in os.listdir(old_so_dir) if x.endswith(".so")] if os.path.isdir(old_so_dir) else []
    old_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(so_files[0])) if so_files else None
    put("cvOldDate", old_mtime.strftime("%-d September %Y") if old_mtime and old_mtime.month == 9 else "??")
    for (a_, b_, nm_) in zip(So, Sn, ("4", "6", "8")):
        put("cvRatio" + nm_, f(a_["rhs_calls"] / b_["rhs_calls"], 0))
        if nm_ == "6":
            put("cvOldErr6", sci(a_["omega_max_rel_vs_fine_rk4"], 1)); put("cvNewErr6", sci(b_["omega_max_rel_vs_fine_rk4"], 1))
    import hashlib
    def sha(path):
        try:
            return hashlib.sha256(open(path, "rb").read()).hexdigest()
        except OSError:
            return None
    N["cvode"] = dict(new=new, old=old,
                      module_new_file=new["main"]["rusty_sundials_file"], module_old_file=old["small"]["rusty_sundials_file"],
                      module_new_sha256=sha(new["main"]["rusty_sundials_file"]), module_old_sha256=sha(so_files[0]) if so_files else None,
                      module_old_so=so_files[0] if so_files else None, module_old_mtime=str(old_mtime),
                      editor_build_sha256=sha("/mnt/data/xdev-cache/rs_py_5db8041/rusty_sundials.so"),
                      note="new build = rusty-SUNDIALS commit 5db8041 (byte-identical to /mnt/data/xdev-cache/rs_py_5db8041); old = the stale module of the project venv, run on purpose for the old/new comparison")
else:
    for key in ("cvPerMin", "cvPerMax", "cvErr4", "cvErr6", "cvErr8", "cvErr10", "cvBogMax", "cvFineErr", "cvOldFallA", "cvOldFallB", "unkRatio", "cvScaleUnk8", "cvScaleUnk16", "cvSmallN", "cvGrowOldA", "cvGrowOldB", "cvOldDate", "cvOldErr6", "cvNewErr6", "cvBestTol", "cvBestErr", "cvBestTraj", "cvRatio4", "cvRatio6", "cvRatio8", "cvN", "cvModes", "cvUnknowns", "cvT", "cvRustSec", "cvRk4Dt", "cvScale8", "cvScale16", "cvScale32", "cvScaleSec8", "cvScaleSec16", "cvScaleSec32", "cvScaleUnk32"):
        put(key, "??")
    (HERE / "ch05_cvode_table.tex").write_text("% placeholder: ch05_cvode_*.json not yet available\n")

# --------------------------------------------------------------------------------------------------- Lean
lean_log = HERE.parent / "lean" / "Ch05_BogoliubovDispersion.compile.log"
txt = lean_log.read_text() if lean_log.exists() else ""
n_ax = len(re.findall(r"depends on axioms", txt))
std = all(("sorryAx" not in blk) for blk in txt.split("depends on axioms")[1:])
put("nAxiomLines", str(n_ax)); N["lean"] = dict(axiom_lines=n_ax, no_sorry=bool(std), log=str(lean_log.name))

# --------------------------------------------------------------------------------------------------- write
N["meta"] = dict(note="numbers quoted by chapters/ch05.tex; macros in ch05_numbers.tex", machine="shared 8-core machine, load average 10-36 during runs")
N["helium_features"] = F
(HERE / "ch05_numbers.json").write_text(json.dumps(N, indent=1, default=float))
lines = ["% generated by ch05_numbers.py -- do not edit"]
for key, tex in K.items():
    lines.append(f"\\expandafter\\def\\csname cfive@{key}\\endcsname{{{tex}}}")
(HERE / "ch05_numbers.tex").write_text("\n".join(lines) + "\n")
print(len(K), "macros written;", "CVODE results present" if new is not None else "CVODE results MISSING")
