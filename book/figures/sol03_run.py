"""Solutions, Chapter 3, Exercise 3 ("Run it"): the pair of separation 12 xi in the box of side 64 xi (128^2) and in the box of
side 96 xi (192^2, the same dx = 0.5 xi and the same cut-off k_cut = pi/xi), 40 time units each, with the same imprint, tracking
and speed estimate as the chapter (centre of the two tracked cores, slope over 10 <= t <= 40).  The predictions use the chapter's
periodic point-vortex model (ch03_pv.vortex_velocity: zero-mean-flow field of Weiss-McWilliams, plus the winding-fixed flow).

Heavy (two engine runs, about two minutes on the loaded machine):
  flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env OMP_NUM_THREADS=1 PYTHONPATH=/mnt/data/xdev-cache/qf_ext \
      .venv/bin/python book/figures/sol03_run.py
Writes figures/sol03_runs.json (read by sol03_numbers.py)."""
import json, os, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import qf_pgpe                                                   # noqa: E402
import ch03_pv as PV                                             # noqa: E402

D = 12.0
out = {"script": "book/figures/sol03_run.py", "qf_pgpe": qf_pgpe.__file__, "runs": {}}
for L, N in ((64.0, 128), (96.0, 192)):
    s = qf_pgpe.Pgpe(N, L)
    xc, yc = L / 2 + 0.13, L / 2 - 1.93                          # the chapter's placement relative to the centre (ch03_exercise3.py)
    pos0 = np.array([[xc - D / 2, yc], [xc + D / 2, yc]]); q = np.array([1, -1])
    c = s.imprint_v2(s.uniform(), pos0, q)
    E0, N0, P0 = s.energy(c), s.norm(c), np.asarray(s.momentum(c))
    t0 = time.time(); load0 = os.getloadavg()[0]
    T = 40; ts = np.arange(T + 1.0); P = np.zeros((T + 1, 2, 2)); last = pos0.copy()
    for k in range(T + 1):
        if k > 0:
            c = s.run(c, 1.0)
        dp, dq = s.detect(c)
        cur = np.zeros((2, 2))
        for i in range(2):
            cand = dp[dq == q[i]]
            dd = cand - last[i]; dd -= L * np.round(dd / L)
            cur[i] = last[i] + dd[np.argmin(np.hypot(dd[:, 0], dd[:, 1]))]
        P[k] = cur; last = cur
    wall = time.time() - t0
    win = ts >= 10
    cen = P.mean(1)
    v = np.array([np.polyfit(ts[win], cen[win, 0], 1)[0], np.polyfit(ts[win], cen[win, 1], 1)[0]])
    # the same slope on 10 <= t <= 25 and 25 <= t <= 40: a spread for the estimate
    halves = []
    for a, b in ((10, 25), (25, 40)):
        w = (ts >= a) & (ts <= b)
        halves.append(float(np.polyfit(ts[w], cen[w, 1], 1)[0]))
    dsep = np.hypot(*(P[:, 0] - P[:, 1]).T)
    v0 = np.mean([PV.vortex_velocity(P[k], q, with_sector=False, L=L).mean(0) for k in np.nonzero(win)[0]], axis=0)
    v1 = np.mean([PV.vortex_velocity(P[k], q, with_sector=True, L=L).mean(0) for k in np.nonzero(win)[0]], axis=0)
    sec = np.mean([PV.sector_flow(P[k], q, L) for k in np.nonzero(win)[0]], axis=0)
    out["runs"][f"L{int(L)}"] = dict(L=L, N=N, n_modes=s.n_modes, d_imprint=D, pos0=pos0.tolist(), d_mean=float(dsep[win].mean()),
        d_std=float(dsep[win].std()), v_meas=v.tolist(), v_meas_y_halves=halves, v_plane=float((1 / dsep[win]).mean()),
        v_pv_zero_mean_flow=v0.tolist(), v_pv_with_sector_flow=v1.tolist(), sector_flow=sec.tolist(),
        energy_rel_drift=float(abs(s.energy(c) / E0 - 1)), norm_rel_drift=float(abs(s.norm(c) / N0 - 1)),
        momentum_y_rel_drift=float(abs(np.asarray(s.momentum(c))[1] / P0[1] - 1)),
        track_t=ts.tolist(), track_plus=P[:, 0].tolist(), track_minus=P[:, 1].tolist(), wall_s=wall, load_at_start=load0)
    print(L, json.dumps({k: v for k, v in out["runs"][f"L{int(L)}"].items() if not k.startswith("track")}), flush=True)
(HERE / "sol03_runs.json").write_text(json.dumps(out, indent=1))
