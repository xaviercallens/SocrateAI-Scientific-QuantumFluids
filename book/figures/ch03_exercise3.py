"""Chapter 3, exercise 3, worked: the pair of separation 12 in a box of side L = 96 (192 x 192 points, same dx = 0.5 and cut-off), 40 time units.
Predictions: plane law, torus point vortices with zero mean flow, plus the winding-fixed uniform flow (ch03_pv with L = 96).
Writes figures/ch03_exercise3.json (merged into ch03_numbers.json under "exercise3" by ch03_compute.py).   Run (heavy: use the lock):
  flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env OMP_NUM_THREADS=1 PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_exercise3.py"""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, qf_pgpe
import ch03_pv as PV

L2, N2, D = 96.0, 192, 12.0
s = qf_pgpe.Pgpe(N2, L2)
xc, yc = 48.13, 46.07
pos0 = np.array([[xc - D / 2, yc], [xc + D / 2, yc]]); q = np.array([1, -1])
c = s.imprint_v2(s.uniform(), pos0, q)
t0 = time.time(); load0 = os.getloadavg()[0]
T = 40; ts = np.arange(T + 1.0); P = np.zeros((T + 1, 2, 2))
last = pos0.copy()
for k in range(T + 1):
    if k > 0: c = s.run(c, 1.0)
    dp, dq = s.detect(c)
    cur = np.zeros((2, 2))
    for i in range(2):
        cand = dp[dq == q[i]]
        dd = cand - last[i]; dd -= L2 * np.round(dd / L2)
        cur[i] = last[i] + dd[np.argmin(np.hypot(dd[:, 0], dd[:, 1]))]
    P[k] = cur; last = cur
wall = time.time() - t0
win = ts >= 10
cen = P.mean(1)
v = np.array([np.polyfit(ts[win], cen[win, 0], 1)[0], np.polyfit(ts[win], cen[win, 1], 1)[0]])
dd = np.hypot(*(P[:, 0] - P[:, 1]).T)
v0 = np.mean([PV.vortex_velocity(P[k], q, with_sector=False, L=L2).mean(0) for k in np.nonzero(win)[0]], axis=0)
v1 = np.mean([PV.vortex_velocity(P[k], q, with_sector=True, L=L2).mean(0) for k in np.nonzero(win)[0]], axis=0)
res = dict(L=L2, N=N2, d_imprint=D, d_mean=float(dd[win].mean()), v_meas=float(np.hypot(*v)), v_plane=float((1 / dd[win]).mean()),
           v_pv_zero_mean_flow=float(np.hypot(*v0)), v_pv_with_sector_flow=float(np.hypot(*v1)), sector_flow=float(np.hypot(*PV.sector_flow(P[0], q, L2))),
           ratio_to_pv_with_sector=float(np.dot(v, v1) / np.dot(v1, v1)), ratio_to_pv_zero_mean=float(np.dot(v, v0) / np.dot(v0, v0)),
           wall_s=wall, load_at_start=load0, n_modes=s.n_modes)
print(json.dumps(res, indent=1))
(Path(__file__).resolve().parent / "ch03_exercise3.json").write_text(json.dumps(res, indent=1))   # merged into ch03_numbers.json by ch03_compute.py
