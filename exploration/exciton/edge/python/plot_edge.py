"""Figures of the edge study.  usage: plot_edge.py <summary.json> <out_prefix>"""
import sys, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PF = {"disk": 2 * np.sqrt(np.pi), "square": 4.0, "rect32": 4.083, "rect21": 4.243, "rect31": 4.619, "tri": 4.559, "hex": 3.722}
S = json.load(open(sys.argv[1])); out = sys.argv[2]
cs = S["cases"]
cols = {"disk": "#1f77b4", "hex": "#2ca02c", "square": "#d62728", "rect32": "#ff7f0e", "rect21": "#9467bd", "rect31": "#8c564b", "tri": "#e377c2", "trap": "#7f7f7f"}
kernels = sorted({c["kernel"] for c in cs})
fig, ax = plt.subplots(2, len(kernels), figsize=(5.0 * len(kernels), 8.0), squeeze=False)
for j, k in enumerate(kernels):
    for cid in sorted({c["container"] for c in cs if c["kernel"] == k}):
        pts = sorted([(np.sqrt(c["n"]), c["E_edge"], c["n"]) for c in cs if c["kernel"] == k and c["container"] == cid])
        x = [p[0] for p in pts]; y = [p[1] for p in pts]
        ax[0][j].plot(x, y, "o-", color=cols[cid], label=cid, ms=4)
        if cid != "trap":
            yp = [p[1] / (PF[cid] * np.sqrt(p[2] / 0.5)) for p in pts]
            ax[1][j].plot(x, yp, "o-", color=cols[cid], label=cid, ms=4)
    ax[0][j].set_title(f"kernel {k}: E_edge = E_p - N e_lat"); ax[0][j].set_xlabel("sqrt(N)"); ax[0][j].set_ylabel("E_edge (trap: E - E_LDA)")
    ax[1][j].set_title(f"kernel {k}: E_edge / perimeter"); ax[1][j].set_xlabel("sqrt(N)"); ax[1][j].set_ylabel("E_edge / P")
    ax[0][j].legend(fontsize=7, ncol=2)
for a in ax.ravel():
    a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(out + "_edge_energy.png", dpi=130)
