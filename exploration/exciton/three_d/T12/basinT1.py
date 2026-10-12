"""T1 basin diagnostic (unregistered, 2026-10-12, after run 2): can the surrogate + Experiment B minimiser return to a KNOWN
formally self-dual configuration? Start from diamond (D3+, N = 2) and from SC as a 2-point supercell, perturb positions
and cell by eps in {1e-3, 1e-2, 5e-2, 1e-1, 2e-1} (5 draws each), minimise the same surrogate as run 3, and report the
registered shell mismatch. Output: T1_basin.jsonl."""
import os, sys, json
os.environ.setdefault('OMP_NUM_THREADS', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'AB'))
import numpy as np
from opt import minimize_structure
from selfdual import mismatch, SelfDualObjective, is_lattice

a = 2.0  # diamond: primitive FCC cell of cube side a has volume a^3/4 = 2 for its 2 points -> unit density
DIA = (np.array([[0, a / 2, a / 2], [a / 2, 0, a / 2], [a / 2, a / 2, 0]]), np.array([[0, 0, 0], [0.25, 0.25, 0.25]]))
SC2 = (np.diag([2.0, 1.0, 1.0]), np.array([[0, 0, 0], [0.5, 0, 0]]))
obj = SelfDualObjective()
rng = np.random.default_rng(4242)
with open(os.path.join(HERE, 'T1_basin.jsonl'), 'w') as f:
    for name, (A0, S0) in (('diamond', DIA), ('SC_2pt', SC2)):
        assert abs(abs(np.linalg.det(A0)) - 2) < 1e-12
        m0 = mismatch((A0, S0))[0]
        for eps in (1e-3, 1e-2, 5e-2, 1e-1, 2e-1):
            for k in range(5):
                A = A0 + eps * rng.normal(size=(3, 3)); A *= (2 / abs(np.linalg.det(A))) ** (1 / 3)
                S = (S0 + eps * rng.normal(size=S0.shape)) % 1.0
                M, A1, S1, nfev = minimize_structure(obj, A, S, gtol=1e-13)
                mm = mismatch((A1, S1))[0]
                r = dict(start=name, mismatch_exact=m0, eps=eps, draw=k, M=M, shell_mismatch=mm, accepted=bool(mm < 1e-10),
                         is_lattice=bool(is_lattice(A1, S1)), nfev=nfev)
                f.write(json.dumps(r) + '\n'); f.flush(); print(r, flush=True)
