import time, json, numpy as np
from kk_eval import modal, images
sets = [(1, 1.5, 0.3, -0.4), (0.5, 0.5, 0.1, -0.2), (1, 3, 0.9, -2.0), (2, 0.4, 1.5, -0.2)]
rng = np.random.default_rng(7)
def tm(f, reps=5):
    b = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); b = min(b, time.perf_counter()-t)
    return b
def modal_binned(r, *a, nb=12):
    out = np.empty_like(r); edges = np.geomspace(r.min()*0.999, r.max()*1.001, nb+1)
    idx = np.digitize(r, edges)
    for k in np.unique(idx):
        m = idx == k; out[m] = modal(r[m], *a)
    return out
res = []
for (h1, h2, ze, zh) in sets:
    l = h1+h2; d = min(h1, h2)
    r = rng.uniform(0.3*d, 6*l, 10000)
    ref = modal(r, h1, h2, ze, zh)
    # minimal N for images+EM reaching 1e-12 on the part where it can (r <= l)
    near = r <= l
    Nmin = next((N for N in (2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64)
                 if np.abs(images(r[near], h1, h2, ze, zh, N=N)/ref[near]-1).max() <= 1e-12), None)
    # hybrid: images+EM(Nmin) for r<=l, binned modal for r>l
    def hybrid():
        o = np.empty_like(r)
        if Nmin: o[near] = images(r[near], h1, h2, ze, zh, N=Nmin)
        o[~near] = modal_binned(r[~near], h1, h2, ze, zh)
        return o
    h = hybrid(); err = np.abs(h/ref-1).max()
    t_h = tm(hybrid)
    t_em60 = tm(lambda: images(r, h1, h2, ze, zh, N=60))   # fair baseline: single method everywhere (accurate only r<=~l)
    t_mo_all = tm(lambda: modal_binned(r, h1, h2, ze, zh)) # modal everywhere, binned
    row = dict(set=[h1,h2,ze,zh], Nmin_EM=Nmin, hybrid_maxrelerr=float(err), t_hybrid=t_h, t_images_EM60_everywhere=t_em60, t_modal_binned_all=t_mo_all)
    print(row, flush=True); res.append(row)
json.dump(res, open("timing2.json","w"), indent=1)
