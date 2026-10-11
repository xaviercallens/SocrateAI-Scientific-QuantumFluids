"""Analysis of the L3 runs against L3_PREREG.md. Writes results_L3/l3_summary.json and prints the tables."""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES3 = os.path.join(os.path.dirname(HERE), "results_L3")
SHAPES6 = ["square", "hexagon", "disc", "rect2", "lshape", "annulus"]
KERN = ["ungated:0.5", "gated:0.5:1.5"]
rng = np.random.default_rng(12345)


def load(prefix):
    out = []
    for f in sorted(glob.glob(f"{RES3}/{prefix}_*.json")):
        d = json.load(open(f)); out.append(d)
    return out


def g1():
    cases = load("g1")
    res = {}
    for w in (0.5, 0.75, 1.0, 1.25):
        cs = [c for c in cases if c["summary"]["w"] == w]
        n = sum(c["summary"]["nstart"] for c in cs)
        esc = sum(c["summary"]["n_escaped"] for c in cs)
        acc = sum(c["summary"]["n_accepted"] for c in cs)
        cell = {f"{c['summary']['shape']}|{c['summary']['spec']}": c["summary"]["n_escaped"] / c["summary"]["nstart"] for c in cs}
        st = [s for c in cs for s in c["starts"] if s.get("accepted")]
        d_band = np.array([s["n_def_band"] for s in st]); d_all = np.array([s["n_non6"] for s in st])
        n_band = np.array([s["n_band"] for s in st]); nf = np.array([s["nf"] for s in st])
        def R(ix):
            return (d_band[ix].sum() / max(d_all[ix].sum(), 1)) / (n_band[ix].sum() / nf[ix].sum())
        r = dict(ncases=len(cs), n_starts=n, n_escaped=esc, f_esc=esc / max(n, 1), n_accepted=acc,
                 f_esc_worst_cell=max(cell.values()) if cell else None, cells_over_25=[k for k, v in cell.items() if v > 0.25],
                 confines=bool(n and esc / n <= 0.05 and all(v <= 0.25 for v in cell.values())))
        if len(st):
            ix = np.arange(len(st))
            Rv = R(ix)
            bs = [R(rng.integers(0, len(st), len(st))) for _ in range(2000)]
            r.update(R=float(Rv), R_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                     defect_share_wall=float(d_band.sum() / max(d_all.sum(), 1)), node_share_wall=float(n_band.sum() / nf.sum()),
                     mean_n_non6=float(d_all.mean()), concentration_appears=bool(Rv >= 1.5 and np.percentile(bs, 2.5) > 1.0))
            per = {}
            for sh in SHAPES6:
                for sp in KERN:
                    cc = [c for c in cs if c["summary"]["shape"] == sh and c["summary"]["spec"] == sp]
                    s2 = [s for c in cc for s in c["starts"] if s.get("accepted")]
                    if s2:
                        db = sum(s["n_def_band"] for s in s2); da = sum(s["n_non6"] for s in s2)
                        per[f"{sh}|{sp}"] = dict(n=len(s2), mean_n_non6=float(np.mean([s["n_non6"] for s in s2])),
                                                 defect_share_wall=db / da if da else None,
                                                 esc=sum(c["summary"]["n_escaped"] for c in cc), nstart=sum(c["summary"]["nstart"] for c in cc))
            r["per_cell"] = per
        res[str(w)] = r
    # paired w dependence: n_non6 at w vs w=0.5 (same start, same shape/kernel)
    pair = {}
    key = lambda c: (c["summary"]["shape"], c["summary"]["spec"])
    by = {(key(c), c["summary"]["w"]): c for c in cases}
    for w in (0.75, 1.0, 1.25):
        diffs = []
        for (k, ww), c in by.items():
            if ww != w or (k, 0.5) not in by:
                continue
            a = {s["start"]: s for s in c["starts"] if s.get("accepted")}
            b = {s["start"]: s for s in by[(k, 0.5)]["starts"] if s.get("accepted")}
            diffs += [a[i]["n_non6"] - b[i]["n_non6"] for i in a if i in b]
        if diffs:
            diffs = np.array(diffs, float)
            pair[str(w)] = dict(n=len(diffs), mean=float(diffs.mean()), se=float(diffs.std(ddof=1) / np.sqrt(len(diffs))))
    res["paired_vs_w0.5"] = pair
    return res


def g2():
    cases = load("g2")
    out = {}
    for sp in KERN:
        rows = {}
        for sh in SHAPES6:
            cc = [c for c in cases if c["summary"]["shape"] == sh and c["summary"]["spec"] == sp]
            if not cc:
                continue
            st = cc[0]["starts"]
            ok = [s for s in st if s.get("fixed_accepted") and s.get("slid_accepted") and "fixed" in s and "slid" in s]
            def stats(sel):
                if len(sel) < 2:
                    return None
                d = np.array([s["fixed"]["n_non6"] - s["slid"]["n_non6"] for s in sel], float)
                return dict(n=len(sel), mean_delta=float(d.mean()), se=float(d.std(ddof=1) / np.sqrt(len(d))), n_changed=int((d != 0).sum()),
                            passes=bool(d.mean() >= 2.0))
            conv = [s for s in ok if s.get("lbfgs_converged")]
            row = dict(nstart=len(st), n_pairs=len(ok), all=stats(ok), converged_only=stats(conv),
                       n_lbfgs_not_converged=sum(1 for s in st if "lbfgs_converged" in s and not s["lbfgs_converged"]),
                       n_errors=sum(1 for s in st if "error" in s),
                       mean_dE=float(np.mean([s["E_fixed"] - s["E_slid"] for s in ok])) if ok else None,
                       mean_dQ=float(np.mean([s["slid"]["Q"] - s["fixed"]["Q"] for s in ok])) if ok else None,
                       n_Q_changed=sum(1 for s in ok if s["slid"]["Q"] != s["fixed"]["Q"]),
                       euler_fail=sum(1 for s in ok if not (s["fixed"]["euler_ok"] and s["slid"]["euler_ok"])),
                       nonconf=sum(1 for s in ok if not (s["fixed"]["conforming"] and s["slid"]["conforming"])),
                       mean_n_non6_fixed=float(np.mean([s["fixed"]["n_non6"] for s in ok])) if ok else None,
                       mean_n_non6_slid=float(np.mean([s["slid"]["n_non6"] for s in ok])) if ok else None,
                       wall_disp_max_mean=float(np.mean([s["wall_disp_max"] for s in ok])) if ok else None,
                       mean_n_eval=float(np.mean([s["n_eval"] for s in ok])) if ok else None)
            rows[sh] = row
        npass = sum(1 for r in rows.values() if r["all"] and r["all"]["passes"])
        out[sp] = dict(shapes=rows, n_shapes_pass=npass, gate_pass=bool(npass >= 3), n_shapes=len(rows))
    out["gate_overall_both_kernels"] = bool(all(out[sp]["gate_pass"] for sp in KERN if sp in out) and all(sp in out for sp in KERN))
    return out


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    summ = {}
    if which in ("g1", "all"):
        summ["g1"] = g1()
    if which in ("g2", "all"):
        summ["g2"] = g2()
    json.dump(summ, open(f"{RES3}/l3_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1)[:12000])
