"""gamma_h(nu, Lambda=1, D/d) for gated kernels, ungated bilayer, and the 1/r^3 control. Registered grids."""
import json, sys, numpy as np, wigner_lib as w
nus = np.logspace(np.log10(0.05), np.log10(200.0), 33)
Ds = [1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0, "inf"]
out = dict(nus=nus.tolist(), Ds=[str(d) for d in Ds], gamma1={})
for D in Ds:
    row = []
    for nu in nus:
        if D == "inf":
            g = w.gamma_R(nu, "ungated")
        else:
            g = w.gamma_R(nu, "gated", h=D/2.0)
        row.append(float(g))
        print(D, round(nu, 4), g, flush=True)
    out["gamma1"][str(D)] = row
out["gamma1"]["dip"] = [float(w.gamma_R(nu, "dip")) for nu in nus]
json.dump(out, open("gated_scan.json", "w"), indent=1)
print("DONE")
