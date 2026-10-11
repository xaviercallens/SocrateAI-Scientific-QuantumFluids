"""Piecewise-Chebyshev table of the smooth part W(r) of the gated kernel (built from the image series, mpmath)."""
import sys, time, numpy as np
from numpy.polynomial import chebyshev as C
from edge_kernel import W_image_mp, U_gated_K0, dU_gated_K0, U_ungated, dU_ungated

RMAX = 36.0; WIDTH = 0.5; DEG = 16


def build(D, d=1.0, path=None):
    nint = int(round(RMAX / WIDTH))
    k = np.arange(DEG + 1)
    xs = np.cos(np.pi * (k + 0.5) / (DEG + 1))     # Chebyshev nodes of the first kind (DEG+1 of them)
    coefs = np.zeros((nint, DEG + 1))
    for i in range(nint):
        a = i * WIDTH; b = a + WIDTH
        r = 0.5 * (a + b) + 0.5 * (b - a) * xs
        v = np.array([float(W_image_mp(float(ri), d, D)) for ri in r])
        coefs[i] = C.chebfit(xs, v, DEG)
    if path:
        with open(path, "w") as f:
            f.write(f"# W(r) piecewise Chebyshev: D={D!r} d={d!r} rmax={RMAX!r} width={WIDTH!r} deg={DEG}\n")
            f.write(f"{D!r} {d!r} {RMAX!r} {WIDTH!r} {DEG}\n")
            for row in coefs:
                f.write(" ".join(repr(float(c)) for c in row) + "\n")
    return coefs


def evalW(coefs, r):
    r = np.asarray(r, float)
    i = np.minimum((r / WIDTH).astype(int), coefs.shape[0] - 1)
    x = (r - (i + 0.5) * WIDTH) / (0.5 * WIDTH)
    return np.array([C.chebval(xx, coefs[ii]) for xx, ii in zip(x, i)]), np.array(
        [C.chebval(xx, C.chebder(coefs[ii])) / (0.5 * WIDTH) for xx, ii in zip(x, i)])


if __name__ == "__main__":
    out = sys.argv[1]
    for D in (3.0, 10.0):
        t0 = time.time()
        c = build(D, 1.0, f"{out}/table_D{int(D)}.txt")
        rng = np.random.default_rng(0)
        r = rng.uniform(0.2, 20, 400)
        W, dW = evalW(c, r)
        U = W + U_ungated(r, 1.0); dU = dW + dU_ungated(r, 1.0)
        Uk = U_gated_K0(r, 1.0, D); dUk = dU_gated_K0(r, 1.0, D)
        print(D, "time", round(time.time() - t0, 1), "max rel err U", np.max(np.abs(U - Uk) / np.abs(Uk)),
              "max abs err U", np.max(np.abs(U - Uk)), "max abs err dU", np.max(np.abs(dU - dUk)), "rel", np.max(np.abs(dU - dUk) / np.abs(dUk)))
