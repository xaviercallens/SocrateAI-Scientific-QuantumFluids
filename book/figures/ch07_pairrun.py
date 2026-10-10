"""Chapter 7: a PGPE run on the Rust engine (rusty-SUNDIALS crate qf-pgpe, Python extension qf_pgpe) of two antiparallel
vortex pairs (+- at x = L/4, -+ at x = 3L/4, separation d0, zero net charge, dipole moment and impulse) imprinted in the stored
thermal base state of the published arm (k_c = pi, N = 128, L = 64, e = 0.60: T = 0.115, rho_n/rho = 0.027).

Instrument = that of exploration/pgpe/vortex_transport.py (imprint_v2 with periodic phase and Bernoulli amplitude; raw phase-winding
detection with sub-grid refinement; tracking by continuity: same sign, nearest detection within r_track = 3 of the previous position;
positions every time unit; stop on track loss or when a vortex and an antivortex come within d_stop = 1.5).

The run is CHUNKED and RESTARTABLE so that the shared machine is never held for long: each call advances `--chunk` time units from the
checkpoint in /mnt/data/xdev-cache/book_ch07/state_<tag>.npz, saves it, and exits; the driver ch07_pairrun_driver.sh calls it again under
`flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice`.  When finished it writes ch07_pairrun_<tag>.npz (t, R, q, n_det, snapshots of the field,
metadata incl. load averages) and the flag file done_<tag>.

    PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch07_pairrun.py --tag e060_d10_s7 --d0 10 --seed 7 --t-max 1500
"""
import sys, json, time, os, argparse
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
import qf_pgpe                                                              # noqa: E402
from transport_estimators import antiparallel, min_opposite_distance        # noqa: E402

OUT = Path("/mnt/data/xdev-cache/book_ch07"); OUT.mkdir(exist_ok=True)
ap = argparse.ArgumentParser()
ap.add_argument("--base", default=str(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy"))
ap.add_argument("--tag", default="e060_d10_s7")
ap.add_argument("--d0", type=float, default=10.0)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--t-max", type=float, default=1500.0)
ap.add_argument("--chunk", type=float, default=100.0)
ap.add_argument("--snap-every", type=float, default=100.0)
ap.add_argument("--r-track", type=float, default=3.0)
ap.add_argument("--d-stop", type=float, default=1.5)
a = ap.parse_args()
L, N = 64.0, 128
state_f = OUT / f"state_{a.tag}.npz"; final_f = OUT / f"ch07_pairrun_{a.tag}.npz"; done_f = OUT / f"done_{a.tag}"
if done_f.exists():                                                        # another queued invocation has already finished the run
    print("already done"); sys.exit(0)
s = qf_pgpe.Pgpe(N, L)
t0 = time.time(); load0 = os.getloadavg()[0]

if state_f.exists():                                                         # resume
    z = np.load(state_f, allow_pickle=True); meta = json.loads(str(z["meta"]))
    c = np.ascontiguousarray(z["c"]); t = float(z["t"]); last = z["last"]; q = z["q"]
    T = list(z["T"]); R = list(z["R"]); ND = list(z["ND"]); SN = list(z["snaps"]); ST = list(z["snap_t"]); E0 = meta["E_imprinted"]
else:                                                                        # fresh start: imprint
    c0 = np.load(a.base); rng = np.random.default_rng(a.seed)
    pos, q = antiparallel(L, a.d0, rng)
    # BOOK-BEGIN imprint
    c = np.ascontiguousarray(s.imprint_v2(np.ascontiguousarray(c0), pos, q)); E0 = s.energy(c); t = 0.0; last = pos.copy()
    # BOOK-END imprint
    T, R, ND, SN, ST = [], [], [], [], []
    meta = dict(base=str(Path(a.base).relative_to(ROOT)), d0=a.d0, seed=a.seed, L=L, N=N, kcut=float(s.kcut), r_track=a.r_track, d_stop=a.d_stop,
                E_imprinted=E0, pos0=pos.tolist(), q=q.tolist(), ended="running", chunks=[])

target = min(t + a.chunk, a.t_max); ended = meta["ended"]; skip_record = state_f.exists()   # on resume the sample at t is already recorded
while ended == "running":
    if not skip_record:
        if abs(t / a.snap_every - round(t / a.snap_every)) < 1e-9 and (not ST or ST[-1] < t - 1e-9):
            SN.append(c.copy()); ST.append(t)
        # BOOK-BEGIN track
        dp, dq = s.detect(c); dp = np.asarray(dp); dq = np.asarray(dq); cur = np.full_like(last, np.nan)
        for i in range(len(q)):
            cand = np.nonzero(dq == q[i])[0]
            if len(cand):
                d = dp[cand] - last[i]; d -= L * np.round(d / L); r = np.hypot(d[:, 0], d[:, 1]); j = int(np.argmin(r))
                if r[j] <= a.r_track:
                    cur[i] = dp[cand[j]]
        # BOOK-END track
        if np.isnan(cur).any():
            ended = "track_lost"; break
        T.append(t); R.append(cur.copy()); ND.append(len(dq)); last = cur
        if min_opposite_distance(cur, q, L) < a.d_stop:
            ended = "annihilated"; break
        if t >= a.t_max - 1e-9:
            ended = "t_max"; break
        if t >= target - 1e-9:
            break                                                           # end of this chunk: checkpoint below
    skip_record = False
    # BOOK-BEGIN step
    c = np.ascontiguousarray(s.run(c, 1.0)); t += 1.0
    # BOOK-END step

meta["ended"] = ended; meta["t_end"] = t
meta["chunks"].append(dict(t_end=t, seconds=round(time.time() - t0, 1), load_start=round(load0, 2), load_end=round(os.getloadavg()[0], 2)))
meta["seconds"] = round(sum(ch["seconds"] for ch in meta["chunks"]), 1)
if ended != "running":
    if not ST or ST[-1] < t - 1e-9:
        SN.append(c.copy()); ST.append(t)                                   # the last field
    meta["drift_E"] = abs(s.energy(c) - E0) / abs(E0)
    np.savez(final_f, t=np.array(T), R=np.array(R), q=q, n_det=np.array(ND), snap_t=np.array(ST), snaps=np.array(SN), meta=json.dumps(meta))
    done_f.write_text(json.dumps(dict(ended=ended, t_end=t))); print("DONE", ended, t, "seconds", meta["seconds"], flush=True)
else:
    np.savez(state_f, c=c, t=t, last=last, q=q, T=np.array(T), R=np.array(R), ND=np.array(ND), snaps=np.array(SN), snap_t=np.array(ST), meta=json.dumps(meta))
    print("chunk to t =", t, "seconds", round(time.time() - t0, 1), "load", round(os.getloadavg()[0], 1), flush=True)
