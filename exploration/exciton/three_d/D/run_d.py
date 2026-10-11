#!/usr/bin/env python3
"""Experiment D (three_d/PREREG.md): hybrid (CM relax + 20 Lloyd) vs CVT alone, E3 protocol (dimlift/mesh3d.py reused unchanged).
Usage: run_d.py <out.jsonl> <parity 0|1|all>   Seeds 0..29, N=216, X0 = default_rng(31337+s).random((216,3)) as in E3."""
import json, os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "dimlift"))
import numpy as np
import mesh3d as M

N = 216
out, par = sys.argv[1], sys.argv[2]
done = set()
if os.path.exists(out):
    for l in open(out):
        r = json.loads(l); done.add((r["seed"], r["method"]))
with open(out, "a") as fo:
    def emit(s, name, X, **kw):
        if (s, name) in done: return
        fo.write(json.dumps(dict(seed=s, N=N, method=name, **M.tet_quality(X), **kw)) + "\n"); fo.flush()
    for s in range(30):
        if par != "all" and s % 2 != int(par): continue
        t0 = time.time()
        X0 = np.random.default_rng(31337 + s).random((N, 3))
        Xc, E = M.relax_cm(X0)
        Xh = M.lloyd(Xc, np.random.default_rng([31337 + s, 1]), iters=20)
        emit(s, "hybrid", Xh, E_cm=float(E), lloyd_iters=20)
        emit(s, "cm_only", Xc, E_cm=float(E))
        rng = np.random.default_rng([31337 + s, 2]); X = X0
        done_it = 0
        for tgt in (20, 40, 80):
            X = M.lloyd(X, rng, iters=tgt - done_it); done_it = tgt
            emit(s, f"cvt{tgt}", X, lloyd_iters=tgt)
        print(s, round(time.time() - t0, 1), flush=True)
