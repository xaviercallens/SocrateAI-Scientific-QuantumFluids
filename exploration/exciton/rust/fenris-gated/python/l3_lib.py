"""L3 library: generalised wall spacing and sliding-wall (arclength) parametrisation. See ../L3_PREREG.md."""
import copy, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geometry as G
from study import analyse_state, parse_out
from gates import np_pair

FG3 = "/mnt/data/xdev-cache/target_fenris_l3/release/fg"
TMP = "/mnt/data/xdev-cache/tmp/l3run"
RES3 = os.path.join(os.path.dirname(HERE), "results_L3")
os.makedirs(TMP, exist_ok=True); os.makedirs(RES3, exist_ok=True)

SHAPES6 = ["square", "hexagon", "disc", "rect2", "lshape", "annulus"]
KERNELS = ["ungated:0.5", "gated:0.5:1.5"]


def make_shape(name, n_target, w):
    """Shape with wall spacing w. n_free is that of the spacing-1 wall for every w; w = 0.5, 1.0 are exactly the
    registered L6 shapes (geometry.Shape)."""
    base = G.fit_shape(name, n_target, w=1.0)
    if abs(w - 0.5) < 1e-12 or abs(w - 1.0) < 1e-12:
        return G.Shape(name, base.s, w)
    sh = copy.copy(base)
    nodes, ring_of = [], []
    for k, r in enumerate(base.rings):
        if r["kind"] == "circle":
            n = max(3, int(round(2 * np.pi * r["R"] / w)))
            t = 2 * np.pi * np.arange(n) / n
            pts = np.c_[r["R"] * np.cos(t), r["R"] * np.sin(t)]
        else:
            poly = r["pts"]; m = len(poly); pts = []
            for i in range(m):
                p, q = poly[i], poly[(i + 1) % m]
                ne = max(1, int(round(np.linalg.norm(q - p) / w)))
                for j in range(ne):
                    pts.append(p + (q - p) * (j / ne))
            pts = np.array(pts)
        nodes.append(pts); ring_of += [k] * len(pts)
    sh.boundary = np.vstack(nodes)
    sh.sites = sh.boundary            # all wall nodes are triangulation sites for w not in {0.5}
    sh.ring_of = np.array(ring_of)
    sh.w = w
    return sh


def ring_sizes_and_nodes(shape):
    """Boundary nodes are stored ring after ring; recover per-ring node blocks."""
    counts = np.bincount(shape.ring_of_all) if hasattr(shape, "ring_of_all") else None
    mult = int(round(1.0 / shape.w)) if abs(shape.w - 0.5) < 1e-12 or abs(shape.w - 1.0) < 1e-12 else None
    sizes = []
    for r in shape.rings:
        if mult is not None:
            if r["kind"] == "circle":
                sizes.append(max(3, int(round(2 * np.pi * r["R"]))) * mult)
            else:
                poly = r["pts"]; m = len(poly)
                sizes.append(sum(max(1, int(round(np.linalg.norm(poly[(i + 1) % m] - poly[i])))) * mult for i in range(m)))
        else:
            raise ValueError("sliding is defined only for w in {0.5, 1.0}")
    return sizes


class SlidingWall:
    """Wall nodes parametrised by arclength s on their ring; polygon corners (nodes at vertices) do not slide."""
    def __init__(self, shape):
        self.shape = shape
        pts = shape.boundary
        self.sizes = ring_sizes_and_nodes(shape)
        assert sum(self.sizes) == len(pts)
        self.rings = []   # dict(kind, R / poly,cum, L)
        s0, corner, ring_id = [], [], []
        idx = 0
        for k, (r, sz) in enumerate(zip(shape.rings, self.sizes)):
            nodes = pts[idx:idx + sz]; idx += sz
            if r["kind"] == "circle":
                R = r["R"]
                th = np.mod(np.arctan2(nodes[:, 1], nodes[:, 0]), 2 * np.pi)
                self.rings.append(dict(kind="circle", R=R, L=2 * np.pi * R))
                s0.append(R * th); corner.append(np.zeros(sz, bool))
            else:
                poly = np.asarray(r["pts"], float)
                seg = np.roll(poly, -1, axis=0) - poly
                ln = np.linalg.norm(seg, axis=1)
                cum = np.concatenate([[0], np.cumsum(ln)])
                self.rings.append(dict(kind="poly", poly=poly, seg=seg, ln=ln, cum=cum, L=cum[-1]))
                s = np.empty(sz)
                for j, p in enumerate(nodes):
                    t = np.clip(((p - poly) * seg).sum(1) / (ln ** 2), 0, 1)
                    d = np.linalg.norm(p - (poly + t[:, None] * seg), axis=1)
                    i = int(np.argmin(d)); s[j] = cum[i] + t[i] * ln[i]
                    assert d[i] < 1e-9
                s0.append(s)
                c = np.array([np.min(np.linalg.norm(poly - p, axis=1)) < 1e-9 for p in nodes])
                corner.append(c)
            ring_id += [k] * sz
        self.s0 = np.concatenate(s0)
        self.corner = np.concatenate(corner)
        self.ring_id = np.array(ring_id)

    def positions_tangents(self, s):
        P = np.empty((len(s), 2)); T = np.empty((len(s), 2))
        for k, rg in enumerate(self.rings):
            m = self.ring_id == k
            sk = np.mod(s[m], rg["L"])
            if rg["kind"] == "circle":
                th = sk / rg["R"]
                P[m] = rg["R"] * np.c_[np.cos(th), np.sin(th)]
                T[m] = np.c_[-np.sin(th), np.cos(th)]
            else:
                i = np.clip(np.searchsorted(rg["cum"], sk, side="right") - 1, 0, len(rg["poly"]) - 1)
                t = (sk - rg["cum"][i]) / rg["ln"][i]
                P[m] = rg["poly"][i] + t[:, None] * rg["seg"][i]
                T[m] = rg["seg"][i] / rg["ln"][i][:, None]
        return P, T


def total_energy_and_wallgrad(spec, X, W, T):
    """E = free-free + free-wall + wall-wall (shifted-force kernel, numpy), and dE/ds for every wall node."""
    n = len(X)
    iu = np.triu_indices(n, 1)
    r = np.linalg.norm(X[iu[0]] - X[iu[1]], axis=1)
    e = np_pair_u(spec, r)[0].sum()
    dXW = W[None, :, :] - X[:, None, :]            # from free to wall
    rw = np.linalg.norm(dXW, axis=2)
    uw, duw = np_pair_u(spec, rw.ravel())[:2]
    e += uw.sum()
    gW = ((duw.reshape(rw.shape) / rw)[:, :, None] * dXW).sum(0)       # dE/dW from free nodes
    m = len(W)
    iu2 = np.triu_indices(m, 1)
    dWW = W[iu2[0]] - W[iu2[1]]
    rww = np.linalg.norm(dWW, axis=1)
    uww, duww = np_pair_u(spec, rww)[:2]
    e += uww.sum()
    gpair = (duww / rww)[:, None] * dWW
    np.add.at(gW, iu2[0], gpair); np.add.at(gW, iu2[1], -gpair)
    return float(e), (gW * T).sum(1)


def np_pair_u(spec, r):
    r = np.asarray(r, float)
    return np_pair(spec, r)


def fg_run(spec, fixed, starts_list, tag, ftol="1e-9", rtol="1e-2", atol="1e-5"):
    """starts_list: list of (nf,2) arrays; returns parse_out records."""
    d = f"{TMP}/{tag}"; os.makedirs(d, exist_ok=True)
    np.savetxt(d + "/fixed.txt", fixed, fmt="%.17g")
    nf = len(starts_list[0])
    with open(d + "/starts.txt", "w") as f:
        f.write(f"{len(starts_list)} {nf}\n")
        for P in starts_list:
            f.writelines(f"{x!r} {y!r}\n" for x, y in P)
    env = dict(os.environ, RAYON_NUM_THREADS="1")
    cp = subprocess.run([FG3, "run", spec, d + "/fixed.txt", d + "/starts.txt", d + "/out.txt", ftol, rtol, atol],
                        env=env, capture_output=True, text=True)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr[-400:])
    return parse_out(d + "/out.txt", nf)


def state_analysis(shape, sites, P):
    """Defect statistics of one state (free nodes P, triangulation sites)."""
    a = analyse_state(shape, sites, P)
    c = a["c"]
    wd = shape.wall_distance(P)
    band = wd < 1.5
    return dict(n_non6=int((c != 6).sum()), n5=int((c == 5).sum()), n7=int((c == 7).sum()), Q=int(a["Q"]),
                rhs=int(a["rhs"]), euler_ok=bool(a["euler_ok"]), conforming=bool(a["conforming"]),
                n_def_band=int(((c != 6) & band).sum()), n_band=int(band.sum()), nf=len(P))
