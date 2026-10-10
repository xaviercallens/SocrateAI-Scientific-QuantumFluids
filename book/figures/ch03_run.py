"""Chapter 3: the solver runs.  qf_pgpe (Rust engine of the rusty-SUNDIALS workspace), units hbar = m = g = n0 = 1.

    PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_run.py pair D [T]      # one vortex pair of separation D, horizontal, + on the left
    PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_run.py quad [T]        # two co-moving pairs (leapfrog)

Both write /mnt/data/xdev-cache/ch03/<case>.npz with
    t, pos (nt, nv, 2) tracked sub-grid vortex positions (unwrapped), q, energy, norm, momentum (nt, 2)   -- every 1.0 time unit
    snaps, snap_t                                                                                        -- full fields (projected modes) saved every `snap_every`
and <case>.json with the wall time and the machine load at the start.  Nothing is tuned: the imprint is the programme's
`imprint_v2` (periodic theta-function phase, Bernoulli density), the evolution is the sharp-cutoff projected GP equation
i dpsi/dt = P[-1/2 lap psi + |psi|^2 psi] integrated by IF-RK4 with dt = 0.01.
"""
import json, os, sys, time
sys.path.insert(0, "/mnt/data/xdev-cache/qf_ext")
import numpy as np
import qf_pgpe
from scipy.optimize import linear_sum_assignment

CACHE = "/mnt/data/xdev-cache/ch03"
N, L = 128, 64.0
os.makedirs(CACHE, exist_ok=True)


def per_vec(a, b, Lbox=L):
    d = a - b
    return d - Lbox * np.round(d / Lbox)


def match(prev, q, det_pos, det_q):
    """Assign the new detections to the tracked vortices (same charge, minimum total periodic distance)."""
    out = np.zeros_like(prev)
    for sgn in (+1, -1):
        idx = np.nonzero(q == sgn)[0]
        cand = np.nonzero(det_q == sgn)[0]
        if len(cand) < len(idx):
            raise RuntimeError("lost a vortex of charge %d" % sgn)
        cost = np.array([[np.hypot(*per_vec(det_pos[j], prev[i])) for j in cand] for i in idx])
        r, c = linear_sum_assignment(cost)
        for a, b in zip(r, c):
            out[idx[a]] = prev[idx[a]] + per_vec(det_pos[cand[b]], prev[idx[a]])        # unwrapped step
    return out


def run(case, pos0, q, T, snap_every):
    s = qf_pgpe.Pgpe(N, L)
    pos0 = np.asarray(pos0, float); q = np.asarray(q, np.int64)
    c = s.imprint_v2(s.uniform(), pos0, q)
    t0 = time.time(); load0 = os.getloadavg()[0]
    nt = int(round(T)) + 1
    t = np.arange(nt, dtype=float)
    pos = np.zeros((nt, len(q), 2)); en = np.zeros(nt); nm = np.zeros(nt); mom = np.zeros((nt, 2))
    snaps, snap_t = [], []
    for k in range(nt):
        if k > 0:
            c = s.run(c, 1.0)
        dp, dq = s.detect(c)
        if k == 0:
            # label the detections by the imprinted positions
            pos[0] = pos0.copy()
            pos[0] = match(pos0, q, dp, dq)
        else:
            pos[k] = match(pos[k - 1], q, dp, dq)
        en[k] = s.energy(c); nm[k] = s.norm(c); mom[k] = s.momentum(c)
        if k % snap_every == 0:
            snaps.append(c.copy()); snap_t.append(float(k))
        if len(dq) != len(q):
            print("warning: %d detections at t=%g (expected %d)" % (len(dq), k, len(q)), flush=True)
    wall = time.time() - t0
    np.savez(f"{CACHE}/{case}.npz", t=t, pos=pos, q=q, energy=en, norm=nm, momentum=mom,
             snaps=np.array(snaps), snap_t=np.array(snap_t))
    json.dump(dict(case=case, N=N, L=L, T=T, wall_s=wall, load_at_start=load0, n_modes=s.n_modes, kcut=s.kcut, dx=s.dx,
                   pos0=pos0.tolist(), q=q.tolist(), snap_every=snap_every), open(f"{CACHE}/{case}.json", "w"))
    print(f"{case}: T={T} wall={wall:.1f}s (load at start {load0:.1f}); detections {len(dq)}; E {en[0]:.6f} -> {en[-1]:.6f}; "
          f"N {nm[0]:.9f} -> {nm[-1]:.9f}", flush=True)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "pair":
        d = float(sys.argv[2]); T = float(sys.argv[3]) if len(sys.argv) > 3 else 40.0
        xc, yc = 32.13, 30.71
        run(f"pair_d{d:g}", [[xc - d / 2, yc], [xc + d / 2, yc]], [1, -1], T, snap_every=1 if d == 12 else 10 ** 9)
    elif what == "quad":
        T = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
        run("quad", [[27.10, 27.30], [37.40, 27.30], [27.10, 37.60], [37.40, 37.60]], [1, -1, 1, -1], T, snap_every=2)
