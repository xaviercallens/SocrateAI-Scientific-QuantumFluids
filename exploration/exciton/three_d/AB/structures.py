"""Reference crystal structures: (A0 rows, fractional positions S, number of atoms, representable-in-N rule)."""
import numpy as np

FCC_A = np.array([[0, .5, .5], [.5, 0, .5], [.5, .5, 0]])
BCC_A = np.array([[-.5, .5, .5], [.5, -.5, .5], [.5, .5, -.5]])
HCP_A = np.array([[1, 0, 0], [-.5, np.sqrt(3) / 2, 0], [0, 0, np.sqrt(8 / 3)]])


def _fcc_translations():
    return np.array([[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0]])


def a15():
    p = [(0, 0, 0), (.5, .5, .5), (.25, 0, .5), (.75, 0, .5), (.5, .25, 0), (.5, .75, 0), (0, .5, .25), (0, .5, .75)]
    return np.eye(3), np.array(p, float)


def c15():
    """MgCu2 Laves, Fd-3m origin choice 1, conventional cubic cell, 24 atoms."""
    a8 = np.array([(0, 0, 0), (.25, .25, .25)])
    d16 = np.array([(5 / 8, 5 / 8, 5 / 8), (3 / 8, 7 / 8, 1 / 8), (7 / 8, 1 / 8, 3 / 8), (1 / 8, 3 / 8, 7 / 8)])
    base = np.vstack([a8, d16])
    pts = []
    for t in _fcc_translations():
        for b in base:
            pts.append((b + t) % 1.0)
    return np.eye(3), np.array(pts)


def references():
    """name -> (A0, S, natoms)."""
    R = {}
    R['FCC'] = (FCC_A.copy(), np.zeros((1, 3)))
    R['BCC'] = (BCC_A.copy(), np.zeros((1, 3)))
    R['HCP'] = (HCP_A.copy(), np.array([[0, 0, 0], [1 / 3, 2 / 3, .5]]))
    R['diamond'] = (FCC_A.copy(), np.array([[0, 0, 0], [.25, .25, .25]]))
    R['A15'] = a15()
    R['C15'] = c15()
    return {k: (v[0], v[1], len(v[1])) for k, v in R.items()}


# which references fit in an N-point cell (N multiple of the primitive atom count; C15 primitive = 6)
PRIM_COUNT = {'FCC': 1, 'BCC': 1, 'HCP': 2, 'diamond': 2, 'A15': 8, 'C15': 6}


def representable(name, N):
    return N % PRIM_COUNT[name] == 0
