import json, numpy as np
from kk_eval import modal, images, reference
# Reference policy (deviation from PREREG, disclosed): mpmath (20 digits) at 10 points per set validates the float64
# modal sum, which is then the reference at the other points; mpmath at all 160 points was too slow.
sets = [(1, 1.5, 0.3, -0.4), (0.5, 0.5, 0.1, -0.2), (1, 3, 0.9, -2.0), (2, 0.4, 1.5, -0.2)]
res = []
for (h1, h2, ze, zh) in sets:
    l = h1 + h2
    r = l*np.logspace(-2, np.log10(20), 40)
    mo = modal(r, h1, h2, ze, zh)
    sub = np.arange(0, 40, 4)
    ref = np.array([float(v) for v in reference(r[sub], h1, h2, ze, zh, dps=20)])
    chk = np.abs(mo[sub]/ref - 1).max()
    im = images(r, h1, h2, ze, zh, N=60)
    e = np.abs(im/mo - 1)
    ok = e <= 1e-12
    print((h1, h2, ze, zh), "modal vs mpmath: %.2e | images+EM vs modal max %.2e | within 1e-12 for r/l in %s" %
          (chk, e.max(), "[%.3g, %.3g]" % ((r/l)[ok].min(), (r/l)[ok].max()) if ok.any() else "never"), flush=True)
    res.append(dict(set=[h1, h2, ze, zh], r_over_l=(r/l).tolist(), relerr_images_EM=e.tolist(), modal_vs_mp=float(chk)))
json.dump(res, open("accuracy.json", "w"))
