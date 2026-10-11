import numpy as np
from scipy.optimize import minimize
from lattsum import reduce_cell


def minimize_structure(kern, A0, S0, rounds=40, chunk=60, gtol=1e-9):
    """L-BFGS-B on (A0, S) with periodic re-reduction of the cell. Returns E, A, S, nfev."""
    N = len(S0)
    A = np.array(A0, float)
    S = np.array(S0, float)
    nfev = 0
    E = None
    for r in range(rounds):
        A, S = reduce_cell(A, S)
        S = S - np.floor(S)

        def fun(x):
            Aa = x[:9].reshape(3, 3)
            Ss = x[9:].reshape(N, 3)
            e, gA, gS = kern.eg(Aa, Ss)
            return e, np.concatenate([gA.ravel(), gS.ravel()])
        x0 = np.concatenate([A.ravel(), S.ravel()])
        res = minimize(fun, x0, jac=True, method='L-BFGS-B',
                       options=dict(maxiter=chunk, maxcor=30, ftol=1e-16, gtol=gtol, maxls=40))
        nfev += res.nfev
        A = res.x[:9].reshape(3, 3).copy()
        S = res.x[9:].reshape(N, 3).copy()
        Enew = res.fun
        if E is not None and abs(Enew - E) <= 1e-14 * abs(E):
            E = Enew
            break
        E = Enew
        if res.nit < chunk and res.success:
            # converged inside chunk; one more reduction pass is harmless but not needed
            A, S = reduce_cell(A, S)
            break
    # normalise to det = N
    s = (N / np.linalg.det(A)) ** (1 / 3)
    A = A * s
    A, S = reduce_cell(A, S)
    S = S - np.floor(S)
    E = kern.eg(A, S)[0]
    return E, A, S, nfev


def energy(kern, A0, S0):
    return kern.eg(np.asarray(A0, float), np.asarray(S0, float))[0]
