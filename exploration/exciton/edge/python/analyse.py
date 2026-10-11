"""Analysis of the edge study (PREREG.md sections 5-7).  usage: analyse.py <runs_dir> <out_dir>"""
import sys, os, json, glob, numpy as np
from scipy.spatial import Delaunay, ConvexHull
from edge_ref import LDA, polygon, pair, spacing, e_lat as e_lat_direct

RHO0 = 0.5
PF = {"disk": 2 * np.sqrt(np.pi), "square": 4.0, "rect32": 2 * (np.sqrt(1.5) + np.sqrt(1 / 1.5)),
      "rect21": 2 * (np.sqrt(2) + np.sqrt(0.5)), "rect31": 2 * (np.sqrt(3) + np.sqrt(1 / 3)),
      "tri": 3 * np.sqrt(4 / np.sqrt(3)), "hex": 6 * np.sqrt(2 / (3 * np.sqrt(3)))}
ASPECT = {"square": 1.0, "rect32": 1.5, "rect21": 2.0, "rect31": 3.0}


def bbox(cid, area):
    if cid == "disk":
        R = np.sqrt(area / np.pi); return 2 * R, 2 * R
    V = polygon(cid, area)
    return float(V[:, 0].max() - V[:, 0].min()), float(V[:, 1].max() - V[:, 1].min())


class ElatSpline:
    def __init__(self, kid):
        self.lda = LDA(kid); self.kid = kid
    def __call__(self, rho):
        f, _, _ = self.lda._d(rho)
        return f / rho


def lower_bound(kid, cid, n, elat, ws=np.geomspace(0.3, 150, 80)):
    """LB of PREREG section 5 (conditional on the periodic lattice theorem), maximised over w."""
    area = n / RHO0
    bx, by = bbox(cid, area)
    phi, _ = pair(kid)
    best = -np.inf
    M = 300 if kid in ("dip", "r3") else 40
    mm = np.arange(-M, M + 1)
    MX, MY = np.meshgrid(mm, mm)
    nz = ~((MX == 0) & (MY == 0))
    for w in ws:
        Lx, Ly = bx + w, by + w
        dx = np.maximum(0.0, np.abs(MX[nz]) * Lx - bx); dy = np.maximum(0.0, np.abs(MY[nz]) * Ly - by)
        dl = np.hypot(dx, dy)
        if kid in ("dip", "r3"):
            s = float(np.sum(phi(dl)))
            RM = M * min(Lx, Ly) - np.hypot(bx, by)
            if RM > 0 and kid == "dip":
                s += 2 * np.pi / (Lx * Ly) * 2 * (np.sqrt(RM * RM + 1) - RM)
        else:
            dl = dl[dl < 36.0]
            s = float(np.sum(phi(dl))) if len(dl) else 0.0
        lb = elat(n / (Lx * Ly)) - 0.5 * n * s
        best = max(best, lb)
    return best


def defects(x, kid_scale=None):
    x = np.asarray(x).reshape(-1, 2)
    tri = Delaunay(x)
    hl = ConvexHull(x)
    # boundary = on the convex hull *or within 0.25 of the median nearest-neighbour distance of a hull edge*
    # (Qhull drops collinear points on a straight wall from `vertices`)
    from scipy.spatial import cKDTree
    nn = np.median(cKDTree(x).query(x, k=2)[0][:, 1])
    dist_hull = np.min(-(x @ hl.equations[:, :2].T + hl.equations[:, 2]), axis=1)
    hull = set(np.where(dist_hull < 0.25 * nn)[0].tolist())
    edges = set()
    for s in tri.simplices:
        for a in range(3):
            i, j = sorted((int(s[a]), int(s[(a + 1) % 3])))
            edges.add((i, j))
    L = {e: float(np.hypot(*(x[e[0]] - x[e[1]]))) for e in edges}
    med = float(np.median(list(L.values())))
    nb = {i: [] for i in range(len(x))}
    for (i, j), l in L.items():
        if l <= 1.4 * med:
            nb[i].append(j); nb[j].append(i)
    interior = [i for i in range(len(x)) if i not in hull]
    z = {i: len(nb[i]) for i in interior}
    n5 = sum(1 for i in interior if z[i] == 5)
    n7 = sum(1 for i in interior if z[i] == 7)
    other = sum(1 for i in interior if z[i] != 6 and z[i] not in (5, 7))
    charge = sum(6 - z[i] for i in interior)
    # degeneracy flag: ratio of longest to shortest Delaunay edge in the star
    bad = 0
    for i in interior:
        ls = [L[tuple(sorted((i, j)))] for j in nb[i]] if nb[i] else [1.0]
        if max(ls) / min(ls) > 1.35:
            bad += 1
    return dict(n_interior=len(interior), n5=n5, n7=n7, other=other, charge=charge,
                frac_irregular=bad / max(1, len(interior)), n_hull=len(hull))


def main():
    runs, outd = sys.argv[1], sys.argv[2]
    extra_dirs = sys.argv[3:]
    os.makedirs(outd, exist_ok=True)
    trap = json.load(open(os.path.join(runs, "trap_k.json"))) if os.path.exists(os.path.join(runs, "trap_k.json")) else {}
    elat = {}; elat_val = {}
    cases = []
    for path in sorted(glob.glob(os.path.join(runs, "*.jsonl"))):
        recs = [json.loads(l) for l in open(path) if l.strip()]
        runs_ = [r for r in recs if r["rec"] == "run"]
        pol = [r for r in recs if r["rec"] == "polished"]
        if not pol:
            continue
        pol_main_best = min(r["e_total"] for r in pol)
        al_runs, al_best = [], None
        for ed in extra_dirs:
            ap = os.path.join(ed, os.path.basename(path))
            if os.path.exists(ap):
                arecs = [json.loads(l) for l in open(ap) if l.strip()]
                al_runs += [r for r in arecs if r["rec"] == "run"]
                apol = [r for r in arecs if r["rec"] == "polished"]
                if apol:
                    b_ = min(r["e_total"] for r in apol)
                    al_best = b_ if al_best is None else min(al_best, b_)
                pol = pol + apol
        case = runs_[0]["case"] if runs_ else pol[0]["case"]
        kid, cid, ns = case.split("_")
        n = int(ns[1:])
        if kid not in elat:
            elat[kid] = ElatSpline(kid)
            elat_val[kid] = float(__import__("edge_ref").e_lat(kid, RHO0))
        pol.sort(key=lambda r: r["e_total"])
        b = pol[0]
        e_best = b["e_total"]
        # all screened energies are >= polished-best up to screening accuracy; success = within 1e-5 relative
        succ = float(np.mean([r["e_total"] <= e_best * (1 + 1e-5) for r in runs_])) if runs_ else float("nan")
        succ_al = float(np.mean([r["e_total"] <= e_best * (1 + 1e-5) for r in al_runs])) if al_runs else None
        nonconv = sum(1 for r in runs_ if not r["converged"])
        l2 = sum(r["l2_viol"] for r in runs_)
        rec = dict(case=case, kernel=kid, container=cid, n=n, n_runs=len(runs_), e_total=e_best, e_int=b["e_int"],
                   e_wall=b["e_wall"], e_per_particle=e_best / n, max_viol=b["max_viol"], fmax=b["fmax"],
                   converged=b["converged"], lambda_min=b["lambda_min"], success_rate=succ, nonconverged_screen=nonconv,
                   l2_viol=l2, n_polished=len(pol), polished_energies=[r["e_total"] for r in pol],
                   best_kind=b["kind"], wall_s=sum(r["wall_s"] for r in runs_) + sum(r["wall_s"] for r in pol))
        rec["e_lat"] = elat_val[kid]
        rec["best_main_polished"] = pol_main_best
        rec["best_aligned_polished"] = al_best
        rec["success_rate_aligned"] = succ_al
        rec["aligned_improved"] = bool(al_best is not None and al_best < pol_main_best * (1 - 1e-9))
        rec["aligned_gain_rel"] = float((pol_main_best - al_best) / abs(pol_main_best)) if al_best is not None else None
        if cid == "trap":
            t = trap[f"{kid}_N{n}"]
            rec["k_trap"] = t["k"]; rec["e_lda"] = t["e_lda"]
            rec["E_edge"] = e_best - t["e_lda"]
            rec["E_int_nonneg"] = bool(b["e_int"] >= 0)
            rec["LB"] = None
        else:
            rec["E_edge"] = e_best - n * elat_val[kid]
            rec["LB"] = lower_bound(kid, cid, n, elat[kid])
        rec["E_edge_over_sqrtN"] = rec["E_edge"] / np.sqrt(n)
        # E-c: every screened and polished energy respects the bound
        allE = [r["e_total"] for r in runs_] + [r["e_total"] for r in al_runs] + [r["e_total"] for r in pol]
        # for hard walls the penalty energy includes e_wall >= 0 so e_total >= e_int; the bound is on the interaction energy
        eint_all = [r["e_int"] for r in pol]
        if cid != "trap":
            lbv = max(rec["LB"], 0.0)
            rec["ec_pass"] = bool(all(e / n >= lbv - 1e-10 for e in allE))
            rec["ec_margin"] = float(min(allE) / n - lbv)
            # planted-bug control: would the gate notice a halved / doubled energy?
            rec["ec_detects_halved"] = bool(min(allE) / 2 / n < lbv - 1e-10)
            rec["ec_detects_doubled"] = bool(2 * min(allE) / n < lbv - 1e-10)
        else:
            rec["ec_pass"] = bool(all(e >= 0 for e in eint_all))
            rec["ec_margin"] = float(min(eint_all) / n)
        rec["defects"] = defects(b["x"])
        rec["ee_stationary"] = bool(b["fmax"] < 1e-9 and b["lambda_min"] >= -1e-6)
        # best patch-start screened energy vs best overall
        pe = [r["e_total"] for r in runs_ if r["kind"] == "patch"]
        re_ = [r["e_total"] for r in runs_ if r["kind"] == "rand"]
        rec["best_patch_screen"] = min(pe) if pe else None
        rec["best_rand_screen"] = min(re_) if re_ else None
        rec["under_searched"] = bool(pe and re_ and (min(re_) - min(pe)) > 1e-6 * abs(min(pe)))
        cases.append(rec)
    # fits
    fits = []
    for kid in sorted({c["kernel"] for c in cases}):
        for cid in sorted({c["container"] for c in cases if c["kernel"] == kid}):
            cs = sorted([c for c in cases if c["kernel"] == kid and c["container"] == cid], key=lambda c: c["n"])
            if len(cs) < 3:
                fits.append(dict(kernel=kid, container=cid, ns=[c["n"] for c in cs], note="fewer than 3 N: no fit"))
                continue
            x = np.sqrt([c["n"] for c in cs]); y = np.array([c["E_edge"] for c in cs])
            A = np.c_[x, np.ones_like(x)]
            (g, c0), res, *_ = np.linalg.lstsq(A, y, rcond=None)
            resid = float(np.max(np.abs(y - (g * x + c0))))
            row = dict(kernel=kid, container=cid, ns=[c["n"] for c in cs], gamma=float(g), intercept=float(c0), max_resid=resid)
            if cid != "trap":
                row["gamma_P"] = float(g / (PF[cid] / np.sqrt(RHO0)))
            fits.append(row)
    # aspect ratio tables
    aspect = []
    for kid in sorted({c["kernel"] for c in cases}):
        for n in sorted({c["n"] for c in cases}):
            row = {}
            for cid in ("square", "rect32", "rect21", "rect31"):
                m = [c for c in cases if c["kernel"] == kid and c["container"] == cid and c["n"] == n]
                if m:
                    row[cid] = dict(aspect=ASPECT[cid], E_edge=m[0]["E_edge"], E_edge_over_P=m[0]["E_edge"] / (PF[cid] * np.sqrt(n / RHO0)))
            if len(row) >= 2:
                order = sorted(row, key=lambda c: ASPECT[c])
                ve = [row[c]["E_edge"] for c in order]; vp = [row[c]["E_edge_over_P"] for c in order]
                mono = lambda v: bool(all(np.diff(v) >= 0) or all(np.diff(v) <= 0))
                aspect.append(dict(kernel=kid, n=n, shapes=order, E_edge=ve, E_edge_over_P=vp,
                                   monotone_E_edge=mono(ve), monotone_E_edge_over_P=mono(vp)))
    json.dump(dict(cases=cases, fits=fits, aspect=aspect), open(os.path.join(outd, "summary.json"), "w"), indent=1, default=float)
    # text table
    with open(os.path.join(outd, "cases.md"), "w") as f:
        f.write("| kernel | shape | N | e = E_p/N | E_edge | E_edge/sqrtN | n5 | n7 | other | charge | irreg | lam_min | succ | polished | LB/N | EC | stat | best | al_gain |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for c in sorted(cases, key=lambda c: (c["kernel"], c["container"], c["n"])):
            d = c["defects"]
            lb = "-" if c["LB"] is None else f"{c['LB']:.3g}"
            f.write(f"| {c['kernel']} | {c['container']} | {c['n']} | {c['e_per_particle']:.6f} | {c['E_edge']:.4f} | {c['E_edge_over_sqrtN']:.4f} | {d['n5']} | {d['n7']} | {d['other']} | {d['charge']} | {d['frac_irregular']:.2f} | {c['lambda_min']:.1e} | {c['success_rate']:.2f} | {c['n_polished']} | {lb} | {'ok' if c['ec_pass'] else 'FAIL'} | {'ok' if c['ee_stationary'] else 'no'} | {c['best_kind']} | {('%.1e' % c['aligned_gain_rel']) if c['aligned_gain_rel'] is not None else '-'} |\n")
    hv = [c for c in cases if c.get("ec_detects_halved") is not None]
    print(f"E-c planted halved energy detected in {sum(c['ec_detects_halved'] for c in hv)}/{len(hv)} hard-wall cases")
    print(f"{len(cases)} cases; E-c pass all: {all(c['ec_pass'] for c in cases)}; stationary: {sum(c['ee_stationary'] for c in cases)}/{len(cases)}")


if __name__ == "__main__":
    main()
