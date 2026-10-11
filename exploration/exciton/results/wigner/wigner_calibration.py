"""Calibration on the bare 1/r^3 dipole against S1 (290(30)) and S3 (324, 196-484). Registered criteria A and B."""
import json, numpy as np, wigner_lib as w
res = {}
# c in gamma_h = c (n r0^2)^(-1/8); evaluate at several (nu, Lambda) with n r0^2 = nu Lambda^2 as the P3 check
rows = []
for nu, Lam in [(1.0, 1.0), (10.0, 1.0), (1.0, 10.0), (0.1, 30.0), (100.0, 0.5)]:
    g = w.gamma_R(nu, "dip", Lam=Lam)
    n_r0 = nu*Lam**2
    rows.append(dict(nu=nu, Lam=Lam, n_r0sq=n_r0, gamma=g, c=g*n_r0**0.125))
res["P3_rows"] = rows
cs = np.array([r["c"] for r in rows])
res["c"] = float(cs.mean()); res["P3_spread_rel"] = float((cs.max()-cs.min())/cs.mean())
res["P3_pass"] = bool(res["P3_spread_rel"] < 1e-3)
c = res["c"]
# numerical convergence of c (not registered criteria, bookkeeping)
conv = {}
for lab, kw in {"N16_32": dict(Nq=16), "N32_64_Rc40": dict(Nq=32), "N48_96": dict(Nq=48), "N32_64_Rc60": dict(Nq=32, Rc_over_a=60.0), "N32_64_Rc25": dict(Nq=32, Rc_over_a=25.0)}.items():
    conv[lab] = float(w.gamma_R(1.0, "dip", **kw))
res["convergence_c"] = conv
nc = lambda gc: float((c/gc)**8)
res["criterion_A"] = dict(gamma_c=0.23, gamma_c_err=0.006, n_c=nc(0.23), n_c_lo=nc(0.236), n_c_hi=nc(0.224),
                          ratio_to_290=nc(0.23)/290, ratio_to_324=nc(0.23)/324)
gB = c*290.0**-0.125
res["criterion_B"] = dict(gamma_c=gB, gamma_c_from_n=[c*260.0**-0.125, c*320.0**-0.125], anchor_S1=[260, 290, 320], anchor_S3=[196, 324, 484],
                          gamma_c_S3=[c*196.0**-0.125, c*324.0**-0.125, c*484.0**-0.125])
res["gamma_h_at_290"] = gB
res["gamma_h_at_324"] = c*324.0**-0.125
res["sensitivity"] = {str(g): dict(n_c=nc(g), ratio_to_290=nc(g)/290) for g in [0.10, 0.15, 0.20, 0.23, 0.25]}
# measured/harmonic gamma at the QMC density
res["QMC_gamma_over_harmonic_at_290"] = 0.230/gB
res["P1_direction_pass"] = bool(nc(0.23) < 290)
res["P2_usable_pass"] = bool(0.5 <= nc(0.23)/290 <= 2.0)
json.dump(res, open("calibration.json", "w"), indent=1)
print(json.dumps(res, indent=1))
