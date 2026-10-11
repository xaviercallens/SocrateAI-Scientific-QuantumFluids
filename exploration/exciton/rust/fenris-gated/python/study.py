"""Production runs and analysis of PREREG.md. Usage: python3 study.py [primary|size|sens|all] [--workers 2] [--only substr]"""
import json, os, subprocess, sys, time, hashlib
import numpy as np
from scipy.spatial import Delaunay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geometry as G
from gates import np_pair, SPECS, FG, SCR

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "results")
SENS_SPECS = ["ungated:1.0", "gated:1.0:3.0", "gated:1.0:10.0", "yukawa:3.0"]
NSTART = 24
TOL_SAME = [1e-7, 1e-6, 1e-4, 1e-3]


def case_list(which):
    cases = []
    if which in ("primary", "all"):
        for si, sh in enumerate(G.SHAPES):
            for ki, sp in enumerate(SPECS):
                cases.append(dict(idx=si * 4 + ki, shape=sh, n_target=200, spec=sp, group="primary"))
    if which in ("size", "all"):
        k = 0
        for sh in ("square", "hexagon", "disc"):
            for n in (100, 400, 600):
                for sp in SPECS:
                    cases.append(dict(idx=100 + k, shape=sh, n_target=n, spec=sp, group="size", nstart=20 if n >= 600 else NSTART)); k += 1
    if which in ("sens", "all"):
        k = 0
        for sh in ("square", "hexagon"):
            for sp in SENS_SPECS:
                cases.append(dict(idx=200 + k, shape=sh, n_target=200, spec=sp, group="sens")); k += 1
    return cases


def cid(c):
    return f"{c['group']}_{c['shape']}_N{c['n_target']}_{c['spec'].replace(':', '-')}"


def bulk_energy(spec, n_ref, fg=FG):
    a = np.sqrt(2.0 / (np.sqrt(3.0) * n_ref))
    out = subprocess.run([fg, "lattice", spec, repr(float(a))], capture_output=True, text=True).stdout
    return float(out), float(a)


def pair_matrix_energy(spec, A, B=None):
    """sum over pairs (A internal pairs if B is None, else all A x B) of the shifted-force kernel, numpy/scipy."""
    if B is None:
        iu = np.triu_indices(len(A), 1)
        r = np.linalg.norm(A[iu[0]] - A[iu[1]], axis=1)
    else:
        r = np.linalg.norm(A[:, None] - B[None], axis=2).ravel()
    return float(np_pair(spec, r)[0].sum())


def triangulate(shape, fixed, free):
    pts = np.vstack([fixed, free])
    tri = Delaunay(pts)
    S = tri.simplices
    cen = pts[S].mean(axis=1)
    keep = shape.inside(cen)
    S = S[keep]
    return pts, S


def analyse_state(shape, fixed, free):
    nb, nf = len(fixed), len(free)
    pts, S = triangulate(shape, fixed, free)
    edges = {}
    for t in S:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            e = (min(a, b), max(a, b)); edges[e] = edges.get(e, 0) + 1
    V = len(np.unique(S)); E = len(edges); F = len(S)
    bedges = {e for e, c in edges.items() if c == 1}
    over = [e for e, c in edges.items() if c > 2]
    expect = set()
    for r in np.unique(shape.ring_of):
        idx = np.where(shape.ring_of == r)[0]
        for i in range(len(idx)):
            a, b = idx[i], idx[(i + 1) % len(idx)]
            expect.add((min(a, b), max(a, b)))
    conforming = bool(bedges == expect and not over and V == nb + nf and (V - E + F) == shape.chi)
    deg = np.zeros(len(pts), int); ntri = np.zeros(len(pts), int)
    nbrs = [[] for _ in range(len(pts))]
    for a, b in edges:
        deg[a] += 1; deg[b] += 1; nbrs[a].append(b); nbrs[b].append(a)
    for t in S:
        for v in t: ntri[v] += 1
    c = deg[nb:]
    Q = int((6 - c).sum())
    rhs = 6 * shape.chi + int((ntri[:nb] - 3).sum())
    # psi6
    psi = np.zeros(nf, complex)
    for i in range(nf):
        j = nbrs[nb + i]
        if j:
            d = pts[j] - pts[nb + i]
            psi[i] = np.exp(6j * np.arctan2(d[:, 1], d[:, 0])).mean()
    return dict(c=c, Q=Q, rhs=rhs, euler_ok=bool(Q == rhs), conforming=conforming, V=V, E=E, F=F, Eb=len(bedges),
                psi=psi, edges=np.array(sorted(edges)), pts=pts)


def local_energy(spec, fixed, free):
    allp = np.vstack([fixed, free])
    nf = len(free)
    D = np.linalg.norm(free[:, None] - allp[None], axis=2)
    D[np.arange(nf), len(fixed) + np.arange(nf)] = np.inf
    u = np.where(np.isinf(D), 0.0, np_pair(spec, np.where(np.isinf(D), 1.0, D))[0])
    return 0.5 * u.sum(axis=1)


def parse_out(path, nf):
    lines = open(path).read().splitlines()
    out = []; k = 0
    while k < len(lines):
        h = lines[k].split()
        if h[2] == "error":
            out.append(dict(error=" ".join(h[3:]))); k += 1; continue
        P = np.array([[float(t) for t in l.split()] for l in lines[k + 1:k + 1 + nf]]); k += 1 + nf
        g = lambda key: h[h.index(key) + 1]
        out.append(dict(P=P, converged=int(g("converged")), fmax_rel=float(g("fmax_rel")), steps=int(g("cvode_steps")),
                        fallback=int(g("fallback")), secs=float(g("secs")), energy=float(g("energy")), ell=float(g("ell"))))
    return out


def run_case(c, fg=FG):
    name = cid(c)
    t0 = time.time()
    shape = G.fit_shape(c["shape"], c["n_target"])
    nf = shape.n_free
    nstart = c.get("nstart", NSTART)
    d = f"{SCR}/prod/{name}"; os.makedirs(d, exist_ok=True)
    np.savetxt(d + "/fixed.txt", shape.boundary, fmt="%.17g")
    seeds = [20261011 + 1000 * c["idx"] + s for s in range(nstart)]
    with open(d + "/starts.txt", "w") as f:
        f.write(f"{nstart} {nf}\n")
        for sd in seeds:
            P = shape.sample(nf, np.random.default_rng(sd))
            f.writelines(f"{x!r} {y!r}\n" for x, y in P)
    env = dict(os.environ, RAYON_NUM_THREADS="1")
    subprocess.run([fg, "run", c["spec"], d + "/fixed.txt", d + "/starts.txt", d + "/out.txt"], env=env, capture_output=True)
    runs = parse_out(d + "/out.txt", nf)
    fixed = shape.boundary
    e_bb = pair_matrix_energy(c["spec"], fixed)
    n_ref = (nf + 0.5 * shape.B) / shape.area
    e_bulk, a_ref = bulk_energy(c["spec"], n_ref, fg)
    n_tot = nf + shape.B
    per = []
    states = []
    for s, r in enumerate(runs):
        if "error" in r:
            per.append(dict(start=s, seed=seeds[s], error=r["error"])); continue
        P = r["P"]
        inside = bool(shape.inside(P).all())
        n_out = int((~shape.inside(P)).sum())
        rec = dict(start=s, seed=seeds[s], converged=r["converged"], fmax_rel=r["fmax_rel"], cvode_steps=r["steps"],
                   order1_fallback=r["fallback"], secs=r["secs"], ell=r["ell"], E_free=r["energy"], n_outside=n_out,
                   escaped=not inside)
        if inside and r["converged"]:
            a = analyse_state(shape, fixed, P)
            c6 = a["c"]
            wd = shape.wall_distance(P)
            rec.update(E_tot=r["energy"] + e_bb, E_per_node=(r["energy"] + e_bb) / n_tot,
                       dE=(r["energy"] + e_bb) - n_tot * e_bulk, euler_ok=a["euler_ok"], conforming=a["conforming"],
                       Q=a["Q"], rhs=a["rhs"], n5=int((c6 == 5).sum()), n7=int((c6 == 7).sum()),
                       n_other=int(((c6 != 5) & (c6 != 6) & (c6 != 7)).sum()),
                       n_defect_wall=int(((c6 != 6) & (wd < 1.5)).sum()), n_defect_near=int(((c6 != 6) & (wd >= 1.5) & (wd < 3)).sum()),
                       n_defect_deep=int(((c6 != 6) & (wd >= 3)).sum()), n_deep=int((wd >= 3).sum()),
                       psi6_abs_mean=float(np.abs(a["psi"]).mean()), psi6_global=float(np.abs(a["psi"].mean())),
                       V=a["V"], E=a["E"], F=a["F"], Eb=a["Eb"])
            states.append((s, P, a, wd))
        per.append(rec)
    good = [p for p in per if "E_tot" in p]
    summary = dict(case=name, group=c["group"], shape=c["shape"], spec=c["spec"], s=shape.s, B=shape.B, N_free=nf,
                   area=shape.area, perimeter=shape.perimeter, chi=shape.chi, n_ref=n_ref, a_ref=a_ref, e_bulk=e_bulk,
                   E_bb=e_bb, nstart=nstart, n_converged=sum(1 for p in per if p.get("converged") == 1),
                   n_escaped=sum(1 for p in per if p.get("escaped")), n_good=len(good), idx=c["idx"],
                   seeds=seeds)
    if good:
        E = np.array([p["E_tot"] for p in good])
        Eb = E.min()
        summary.update(E_best=float(Eb), E_per_node_best=float(Eb / n_tot), dE_best=float(Eb - n_tot * e_bulk),
                       dE_per_perimeter_best=float((Eb - n_tot * e_bulk) / shape.perimeter),
                       E_mean=float(E.mean()), E_std=float(E.std()), E_median=float(np.median(E)),
                       frac_best={str(t): float(np.mean(np.abs(E - Eb) <= t * abs(Eb))) for t in TOL_SAME},
                       n_distinct_1e7=int(1 + (np.diff(np.sort(E)) > 1e-7 * abs(Eb)).sum()),
                       euler_all_ok=bool(all(p["euler_ok"] for p in good)), n_nonconforming=sum(1 for p in good if not p["conforming"]),
                       n_euler_fail=sum(1 for p in good if not p["euler_ok"]))
        for key in ("n5", "n7", "n_other", "n_defect_wall", "n_defect_near", "n_defect_deep", "psi6_abs_mean", "psi6_global", "Q", "n_deep"):
            v = np.array([p[key] for p in good], float)
            summary[key + "_mean"] = float(v.mean()); summary[key + "_std"] = float(v.std())
            summary[key + "_best"] = float(good[int(np.argmin(E))][key])
        cc = np.concatenate([a["c"] for _, _, a, _ in states])
        summary["coordination_hist"] = {str(k): int((cc == k).sum()) for k in range(2, 11)}
        summary["coordination_hist_frac"] = {str(k): float((cc == k).mean()) for k in range(2, 11)}
        # psi6 vs wall distance
        bins = np.arange(0, 8.5, 0.5)
        wd_all = np.concatenate([w for *_, w in states]); ps_all = np.concatenate([np.abs(a["psi"]) for _, _, a, _ in states])
        prof = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (wd_all >= lo) & (wd_all < hi)
            prof.append([float(lo), float(hi), int(m.sum()), float(ps_all[m].mean()) if m.any() else None])
        summary["psi6_profile"] = prof
        # best state arrays, heat-maps
        ib = int(np.argmin([p["E_tot"] for p in good]))
        sb = good[ib]["start"]
        s_, P, a, wd = [t for t in states if t[0] == sb][0]
        eloc = local_energy(c["spec"], fixed, P)
        arr = dict(x=P[:, 0], y=P[:, 1], coordination=a["c"], psi6_abs=np.abs(a["psi"]), psi6_arg=np.angle(a["psi"]), e_local=eloc, wall_distance=wd)
        os.makedirs(f"{RES}/states", exist_ok=True)
        np.savez_compressed(f"{RES}/states/{name}_best.npz", **arr, fixed=fixed, edges=a["edges"], start=sb)
        lo, hi = shape.bbox()
        nb_x = max(2, int(np.ceil((hi[0] - lo[0]) / 0.5))); nb_y = max(2, int(np.ceil((hi[1] - lo[1]) / 0.5)))
        H = np.zeros((nb_x, nb_y))
        for _, P2, a2, _ in states:
            m = a2["c"] != 6
            h, xe, ye = np.histogram2d(P2[m, 0], P2[m, 1], bins=[nb_x, nb_y], range=[[lo[0], hi[0]], [lo[1], hi[1]]])
            H += h
        H /= len(states)
        np.savez_compressed(f"{RES}/states/{name}_defect_probability.npz", H=H, xedges=xe, yedges=ye)
        make_png(name, shape, fixed, P, a, eloc, H, xe, ye, summary, c)
    summary["secs_total"] = time.time() - t0
    json.dump(dict(summary=summary, starts=per), open(f"{RES}/case_{name}.json", "w"), indent=1)
    return summary


def make_png(name, shape, fixed, P, a, eloc, H, xe, ye, summ, c):
    os.makedirs(f"{RES}/png", exist_ok=True)
    fig, ax = plt.subplots(1, 3, figsize=(15, 5.2))
    pts, ed = a["pts"], a["edges"]
    for k, (title) in enumerate(["coordination (best-energy state)", "local energy per node", "defect probability (all starts)"]):
        ax[k].set_aspect("equal"); ax[k].set_title(title, fontsize=9)
    seg = np.array([[pts[i], pts[j]] for i, j in ed])
    from matplotlib.collections import LineCollection
    ax[0].add_collection(LineCollection(seg, colors="0.8", linewidths=0.5))
    col = {5: "#d62728", 6: "0.55", 7: "#1f77b4"}
    cc = np.array([col.get(int(k), "k") for k in a["c"]])
    ax[0].scatter(P[:, 0], P[:, 1], c=cc, s=14, zorder=3)
    ax[0].scatter(fixed[:, 0], fixed[:, 1], c="k", marker="s", s=6, zorder=3)
    sc = ax[1].scatter(P[:, 0], P[:, 1], c=eloc, s=22, cmap="viridis")
    ax[1].scatter(fixed[:, 0], fixed[:, 1], c="k", marker="s", s=6)
    plt.colorbar(sc, ax=ax[1], fraction=0.046)
    im = ax[2].imshow(H.T, origin="lower", extent=[xe[0], xe[-1], ye[0], ye[-1]], cmap="magma")
    ax[2].scatter(fixed[:, 0], fixed[:, 1], c="w", marker="s", s=4)
    plt.colorbar(im, ax=ax[2], fraction=0.046)
    fig.suptitle(f"{name}  N_free={summ['N_free']}  5/7: {int((a['c']==5).sum())}/{int((a['c']==7).sum())}  "
                 f"E/node={summ['E_per_node_best']:.4f} (bulk {summ['e_bulk']:.4f})  best-fraction={summ['frac_best']['1e-06']:.2f}", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{RES}/png/{name}.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "primary"
    nw = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 2
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    cases = [c for c in case_list(which) if only is None or only in cid(c)]
    done = []
    from multiprocessing import Pool
    todo = [c for c in cases if not os.path.exists(f"{RES}/case_{cid(c)}.json")]
    print(f"{len(todo)} cases to run of {len(cases)}", flush=True)
    with Pool(nw) as pool:
        for s in pool.imap_unordered(run_case, todo):
            print(f"{s['case']}: N_free={s['N_free']} good={s['n_good']}/{s['nstart']} escaped={s['n_escaped']} "
                  f"E/node={s.get('E_per_node_best')} 5/7={s.get('n5_mean')}/{s.get('n7_mean')} euler_ok={s.get('euler_all_ok')} "
                  f"secs={s['secs_total']:.0f}", flush=True)
