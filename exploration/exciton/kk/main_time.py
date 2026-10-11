import time, json, numpy as np
from kk_eval import modal, images
sets = [(1, 1.5, 0.3, -0.4), (0.5, 0.5, 0.1, -0.2), (1, 3, 0.9, -2.0), (2, 0.4, 1.5, -0.2)]
rng = np.random.default_rng(7)
out = []
def tm(f, reps=3):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); best = min(best, time.perf_counter() - t)
    return best
for (h1, h2, ze, zh) in sets:
    l = h1 + h2; d = min(h1, h2)
    r = rng.uniform(0.3*d, 6*l, 10000)
    mo = modal(r, h1, h2, ze, zh)
    # naive plain truncation: smallest N reaching 1e-12 on these points (vs modal as reference)
    N = 50
    while N <= 3200:
        e = np.abs(images(r[:20], h1, h2, ze, zh, N=N, tail=False)/mo[:20] - 1).max()
        if e <= 1e-12: break
        N *= 2
    t_naive = tm(lambda: images(r[:100], h1, h2, ze, zh, N=min(N,3200), tail=False), 1) * 100 if N <= 3200 else float('nan')
    # fair baseline: images with EM tail, N=60 (valid only where cancellation permits)
    e_em = np.abs(images(r, h1, h2, ze, zh, N=60)/mo - 1)
    frac_em_ok = float(np.mean(e_em <= 1e-12))
    t_em = tm(lambda: images(r, h1, h2, ze, zh, N=60))
    t_mo = tm(lambda: modal(r, h1, h2, ze, zh))
    row = dict(naive_reached_1e12=bool(N<=3200), set=[h1, h2, ze, zh], N_naive=N, t_naive=t_naive, t_images_EM=t_em, frac_images_EM_ok=frac_em_ok, t_modal=t_mo)
    print(row, flush=True); out.append(row)
json.dump(out, open("timing.json", "w"), indent=1)
