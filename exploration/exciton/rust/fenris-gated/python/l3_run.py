"""L3 production: `python3 l3_run.py g1|g2 [--workers 3] [--only substr]`. Pre-registration: ../L3_PREREG.md."""
import json, os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l3_lib import *

W_SCAN = [0.5, 0.75, 1.0, 1.25]
NSTART_G1, NSTART_G2 = 24, 30
LBFGS_MAXITER, LBFGS_MAXFUN = 40, 80


def g1_cases():
    out = []
    for si, sh in enumerate(SHAPES6):
        for ki, sp in enumerate(KERNELS):
            for w in W_SCAN:
                out.append(dict(group="g1", shape=sh, spec=sp, w=w, n_target=100, nstart=NSTART_G1, idx=400 + 2 * si + ki))
    return out


def g2_cases():
    out = []
    for si, sh in enumerate(SHAPES6):
        for ki, sp in enumerate(KERNELS):
            out.append(dict(group="g2", shape=sh, spec=sp, w=0.5, n_target=60, nstart=NSTART_G2, idx=500 + 2 * si + ki))
    return out


def cid(c):
    return f"{c['group']}_{c['shape']}_N{c['n_target']}_{c['spec'].replace(':', '-')}_w{c['w']}"


def starts_for(c, shape):
    seeds = [20261011 + 1000 * c["idx"] + s for s in range(c["nstart"])]
    return seeds, [shape.sample_rsa(shape.n_free, np.random.default_rng(sd)) for sd in seeds]


def run_g1(c):
    t0 = time.time()
    shape = make_shape(c["shape"], c["n_target"], c["w"])
    seeds, S = starts_for(c, shape)
    runs = fg_run(c["spec"], shape.boundary, S, cid(c))
    recs = []
    for s, r in enumerate(runs):
        if "error" in r:
            recs.append(dict(start=s, seed=seeds[s], error=r["error"])); continue
        P = r["P"]
        n_out = int((~shape.inside(P)).sum())
        rec = dict(start=s, seed=seeds[s], converged=r["converged"], hessian_pd=r["pd"], fmax_rel=r["fmax_rel"],
                   secs=r["secs"], E_free=r["energy"], n_outside=n_out, escaped=n_out > 0)
        rec["accepted"] = bool(n_out == 0 and r["fmax_rel"] <= 1e-6 and r["pd"])
        if n_out == 0 and r["fmax_rel"] <= 1e-6 and r["pd"]:
            rec.update(state_analysis(shape, shape.sites, P))
        recs.append(rec)
    summ = dict(case=cid(c), **{k: c[k] for k in ("shape", "spec", "w", "n_target", "nstart", "idx")}, N_free=shape.n_free,
                B_wall=len(shape.boundary), n_sites=len(shape.sites), perimeter=shape.perimeter,
                wall_spacing_actual=shape.perimeter / len(shape.boundary),
                n_escaped=sum(1 for r in recs if r.get("escaped")), n_accepted=sum(1 for r in recs if r.get("accepted")),
                secs_total=time.time() - t0)
    json.dump(dict(summary=summ, starts=recs), open(f"{RES3}/{cid(c)}.json", "w"), indent=1)
    return summ


def run_g2_start(args):
    pass


def run_g2(c):
    t0 = time.time()
    shape = make_shape(c["shape"], c["n_target"], c["w"])
    seeds, S = starts_for(c, shape)
    sw = SlidingWall(shape)
    free_mask = ~sw.corner
    site_idx = np.array([int(np.argmin(np.linalg.norm(shape.boundary - p, axis=1))) for p in shape.sites])
    nW = len(shape.boundary)
    recs = []
    for s, P0 in enumerate(S):
        rec = dict(start=s, seed=seeds[s])
        tag = f"{cid(c)}_s{s}"
        try:
            state = dict(P=P0.copy(), best=None, nev=0, hist=[])
            def evaluate(z):
                sv = sw.s0.copy(); sv[free_mask] = z
                Wp, T = sw.positions_tangents(sv)
                r = fg_run(c["spec"], Wp, [state["P"]], tag)[0]
                state["nev"] += 1
                if "error" in r:
                    return 1e30, np.zeros_like(z), None
                X = r["P"]
                E, gs = total_energy_and_wallgrad(c["spec"], X, Wp, T)
                rec_e = dict(E=E, fmax_rel=r["fmax_rel"], pd=r["pd"], conv=r["converged"], X=X, Wp=Wp,
                             gmax=float(np.abs(gs[free_mask]).max()))
                state["hist"].append((E, rec_e["gmax"]))
                if state["best"] is None or E < state["best"]["E"]:
                    state["best"] = rec_e
                    state["P"] = X.copy()
                return E, gs[free_mask], rec_e
            # iteration 0: fixed-wall minimum
            z0 = sw.s0[free_mask]
            E0, g0, r0 = evaluate(z0)
            base = r0
            res = minimize(lambda z: evaluate(z)[:2], z0, jac=True, method="L-BFGS-B",
                           options=dict(maxiter=LBFGS_MAXITER, maxfun=LBFGS_MAXFUN, gtol=1e-6, ftol=1e-15, maxcor=20))
            fin = state["best"]
            rec.update(E_fixed=base["E"], E_slid=fin["E"], n_eval=state["nev"], lbfgs_nit=int(res.nit),
                       lbfgs_converged=bool(res.success and fin["gmax"] <= 1e-5), gmax_final=fin["gmax"],
                       fixed_fmax_rel=base["fmax_rel"], fixed_pd=base["pd"], slid_fmax_rel=fin["fmax_rel"], slid_pd=fin["pd"],
                       max_slide=float(np.abs(np.mod(res.x - z0 + 0, 1e9)).max()) if False else None)
            for key, st in (("fixed", base), ("slid", fin)):
                n_out = int((~shape.inside(st["X"])).sum())
                rec[f"{key}_outside"] = n_out
                acc = bool(n_out == 0 and st["fmax_rel"] <= 1e-6 and st["pd"])
                rec[f"{key}_accepted"] = acc
                if n_out == 0:
                    try:
                        rec[key] = state_analysis(shape, st["Wp"][site_idx], st["X"])
                    except Exception as ex:
                        rec[f"{key}_analysis_error"] = str(ex)[:100]
            disp = np.linalg.norm(fin["Wp"] - base["Wp"], axis=1)
            rec["wall_disp_max"] = float(disp.max()); rec["wall_disp_mean"] = float(disp.mean())
        except Exception as ex:
            rec["error"] = str(ex)[:200]
        recs.append(rec)
        if s % 5 == 4:
            print(f"{cid(c)} start {s + 1}/{c['nstart']} {time.time() - t0:.0f}s", flush=True)
    summ = dict(case=cid(c), **{k: c[k] for k in ("shape", "spec", "w", "n_target", "nstart", "idx")}, N_free=shape.n_free,
                B_wall=nW, n_corner=int(sw.corner.sum()), secs_total=time.time() - t0)
    json.dump(dict(summary=summ, starts=recs), open(f"{RES3}/{cid(c)}.json", "w"), indent=1)
    return summ


if __name__ == "__main__":
    which = sys.argv[1]
    nw = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 3
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    cases = g1_cases() if which == "g1" else g2_cases()
    todo = [c for c in cases if (only is None or only in cid(c)) and not os.path.exists(f"{RES3}/{cid(c)}.json")]
    print(f"{len(todo)} cases to run of {len(cases)}", flush=True)
    fn = run_g1 if which == "g1" else run_g2
    from multiprocessing import Pool
    with Pool(nw) as pool:
        for s in pool.imap_unordered(fn, todo):
            print("DONE", s["case"], {k: s[k] for k in s if k.startswith("n_") or k == "secs_total"}, flush=True)
