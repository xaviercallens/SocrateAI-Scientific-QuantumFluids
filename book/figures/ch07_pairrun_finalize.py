"""Fallback for ch07_pairrun.py: turn the checkpoint state_<tag>.npz (the run so far, whatever time it reached) into the final file ch07_pairrun_<tag>.npz that the figure scripts read,
so that a run that the shared machine could not finish is still usable.  The metadata records that the run was stopped by hand ('ended': 'stopped').
    python ch07_pairrun_finalize.py TAG"""
import sys, json
from pathlib import Path
import numpy as np
import qf_pgpe
OUT = Path("/mnt/data/xdev-cache/book_ch07"); tag = sys.argv[1]
z = np.load(OUT / f"state_{tag}.npz", allow_pickle=True); meta = json.loads(str(z["meta"]))
meta["ended"] = "stopped"; meta["t_end"] = float(z["t"]); meta["note"] = "finalised from the checkpoint by ch07_pairrun_finalize.py"
eng = qf_pgpe.Pgpe(int(meta["N"]), float(meta["L"]))
meta["drift_E"] = abs(eng.energy(np.ascontiguousarray(z["c"])) - meta["E_imprinted"]) / abs(meta["E_imprinted"])   # relative drift of the energy between the imprinted and the last field
snaps, st = list(z["snaps"]), list(z["snap_t"])
if not st or st[-1] < float(z["t"]) - 1e-9:
    snaps.append(z["c"]); st.append(float(z["t"]))
np.savez(OUT / f"ch07_pairrun_{tag}.npz", t=z["T"], R=z["R"], q=z["q"], n_det=z["ND"], snap_t=np.array(st), snaps=np.array(snaps), meta=json.dumps(meta))
print("finalised", tag, "at t =", float(z["t"]), "with", len(z["T"]), "samples")
