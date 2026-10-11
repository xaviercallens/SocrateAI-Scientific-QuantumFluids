"""Container geometries for the L6 edge/frustration design study (boundary node spacing = 1).

A shape is a set of rings. `kind='poly'` rings carry polygon vertices; `kind='circle'` rings carry a radius.
Fixed boundary nodes are placed at spacing ~1 along every ring (polygon edges are divided into round(length)
segments, corners are always nodes; circles carry round(2 pi R) equally spaced nodes).
N_free = round(Area - B/2): every boundary node is shared half-and-half with the exterior, so the mean node
spacing sqrt(Area / (N_free + B/2)) is 1 by construction.
"""
import numpy as np
from matplotlib.path import Path

SQ3 = np.sqrt(3.0)


def _circle_poly(R, n=2000):
    t = 2 * np.pi * np.arange(n) / n
    return np.c_[R * np.cos(t), R * np.sin(t)]


def _shoelace(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _offset_polyline(path, hw):
    """Left and right mitred offsets of an orthogonal polyline."""
    path = np.asarray(path, float)
    seg = np.diff(path, axis=0)
    seg = seg / np.linalg.norm(seg, axis=1)[:, None]
    nrm = np.c_[-seg[:, 1], seg[:, 0]]  # left normals
    left, right = [], []
    for i, p in enumerate(path):
        if i == 0:
            n = nrm[0]; m = 1.0
        elif i == len(path) - 1:
            n = nrm[-1]; m = 1.0
        else:
            n1, n2 = nrm[i - 1], nrm[i]
            n = (n1 + n2); m = 1.0 + float(np.dot(n1, n2))
        left.append(p + hw * n / m)
        right.append(p - hw * n / m)
    return np.array(left), np.array(right)


def unit_rings(name, s):
    """Rings (list of dict) of shape `name` at scale parameter s."""
    if name.startswith("rect"):
        a = float(name[4:]) if len(name) > 4 else 1.0
        W, H = a * s, s
        return [dict(kind="poly", pts=np.array([[0, 0], [W, 0], [W, H], [0, H]], float), hole=False)]
    if name == "square":
        return unit_rings("rect1", s)
    if name == "hexagon":
        t = np.pi / 3 * np.arange(6)
        return [dict(kind="poly", pts=s * np.c_[np.cos(t), np.sin(t)], hole=False)]
    if name == "triangle":
        t = 2 * np.pi / 3 * np.arange(3) + np.pi / 2
        return [dict(kind="poly", pts=s / SQ3 * np.c_[np.cos(t), np.sin(t)], hole=False)]
    if name == "disc":
        return [dict(kind="circle", R=s, hole=False)]
    if name == "annulus":
        return [dict(kind="circle", R=s, hole=False), dict(kind="circle", R=0.5 * s, hole=True)]
    if name == "lshape":
        return [dict(kind="poly", pts=s * np.array([[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]], float), hole=False)]
    if name == "kagomecut":
        t = np.pi / 3 * np.arange(6)
        hexa = s * np.c_[np.cos(t), np.sin(t)]
        pts = []
        for i in range(6):
            v, u, w = hexa[i], hexa[i - 1], hexa[(i + 1) % 6]
            pts.append(v + (u - v) / 3.0)   # cut at one third of the side
            pts.append(v + (w - v) / 3.0)
        return [dict(kind="poly", pts=np.array(pts), hole=False)]
    if name == "maze":
        Lh, pitch = s, 6.0   # corridor width 3, wall thickness 3
        path = [(0, 0), (Lh, 0), (Lh, pitch), (0, pitch), (0, 2 * pitch), (Lh, 2 * pitch), (Lh, 3 * pitch), (0, 3 * pitch)]
        left, right = _offset_polyline(path, 1.5)
        return [dict(kind="poly", pts=np.vstack([left, right[::-1]]), hole=False)]
    raise ValueError(name)


class Shape:
    """w = wall node spacing. N_free and B_ref (= node count of the w = 1 wall, the 'lattice sites') are independent of w;
    for w = 1/m (m even) the extra nodes are midpoints and `sites` is the w = 1 subset used for the triangulation."""
    def __init__(self, name, s, w=1.0):
        self.name, self.s, self.w = name, s, w
        mult = int(round(1.0 / w))
        assert abs(mult * w - 1.0) < 1e-12 and (mult == 1 or mult % 2 == 0)
        self.rings = unit_rings(name, s)
        self.membership = []   # (Path, hole)
        self.edges = []        # all polygon edges (p, q) for wall distance
        nodes, ring_of, site = [], [], []
        self.area = 0.0
        for k, r in enumerate(self.rings):
            if r["kind"] == "circle":
                n = max(3, int(round(2 * np.pi * r["R"]))) * mult
                t = 2 * np.pi * np.arange(n) / n
                pts = np.c_[r["R"] * np.cos(t), r["R"] * np.sin(t)]
                poly = _circle_poly(r["R"], 2000)
            else:
                poly = r["pts"]
                pts = []
                m = len(poly)
                for i in range(m):
                    p, q = poly[i], poly[(i + 1) % m]
                    ne = max(1, int(round(np.linalg.norm(q - p)))) * mult
                    for j in range(ne):
                        pts.append(p + (q - p) * (j / ne))
                pts = np.array(pts)
            nodes.append(pts); ring_of += [k] * len(pts)
            if r["kind"] == "circle":
                site += [(i % mult == 0) for i in range(len(pts))]
            else:
                idx = 0
                for i in range(len(poly)):
                    ne = max(1, int(round(np.linalg.norm(poly[(i + 1) % len(poly)] - poly[i])))) * mult
                    site += [(j % mult == 0) for j in range(ne)]
            self.membership.append((Path(np.vstack([poly, poly[:1]]), closed=True), r["hole"]))
            self.area += (-1 if r["hole"] else 1) * abs(_shoelace(poly))
            for i in range(len(poly)):
                self.edges.append((poly[i], poly[(i + 1) % len(poly)]))
        self.boundary = np.vstack(nodes)             # every fixed node (what the engine sees)
        site = np.array(site)
        self.sites = self.boundary[site]             # w = 1 subset (triangulation / bookkeeping)
        self.ring_of = np.array(ring_of)[site]
        self.B = len(self.sites)
        self.n_holes = sum(1 for r in self.rings if r["hole"])
        self.chi = 1 - self.n_holes
        self.n_free = int(round(self.area - 0.5 * self.B))
        # perimeter (polygon approx for circles)
        self.perimeter = float(sum(np.linalg.norm(q - p) for p, q in self.edges))
        self._e0 = np.array([e[0] for e in self.edges]); self._e1 = np.array([e[1] for e in self.edges])

    def inside(self, pts):
        pts = np.atleast_2d(pts)
        ok = np.ones(len(pts), bool)
        for path, hole in self.membership:
            c = path.contains_points(pts)
            ok &= (~c) if hole else c
        return ok

    def wall_distance(self, pts):
        """Distance of each point to the nearest boundary edge."""
        pts = np.atleast_2d(pts)
        d = np.full(len(pts), np.inf)
        for p, q in zip(self._e0, self._e1):
            v = q - p
            t = np.clip(((pts - p) @ v) / (v @ v), 0, 1)
            proj = p + t[:, None] * v
            d = np.minimum(d, np.linalg.norm(pts - proj, axis=1))
        return d

    def bbox(self):
        allp = np.vstack([np.asarray(p) for e in self.edges for p in e])
        return allp.min(0), allp.max(0)

    def sample(self, n, rng):
        lo, hi = self.bbox()
        out = []
        while len(out) < n:
            p = lo + (hi - lo) * rng.random((4 * n, 2))
            out.extend(p[self.inside(p)].tolist())
        return np.array(out[:n])


def fit_shape(name, n_free_target, lo=3.0, hi=60.0, steps=4000, w=1.0):
    """Scale parameter s whose N_free = round(A - B/2) is closest to the target (ties: smaller s)."""
    best = None
    for s in np.linspace(lo, hi, steps):
        sh = Shape(name, float(s))   # fit always with w = 1: N_free = round(A - B/2) is independent of w
        err = abs(sh.n_free - n_free_target)
        if best is None or err < best[0]:
            best = (err, float(s))
        if sh.n_free > n_free_target + 40:
            break
    return Shape(name, best[1], w)


SHAPES = ["square", "rect1.25", "rect1.5", "rect2", "hexagon", "triangle", "disc", "annulus", "lshape", "maze", "kagomecut"]
