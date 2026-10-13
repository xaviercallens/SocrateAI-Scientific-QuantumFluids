import sys, time, json, math
sys.path.insert(0, "..")
sys.path.insert(0, "../../H1")
from rig import RigLP
from lp_bound import E_Z_series
d, alpha, K = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
bs = [float(x) for x in sys.argv[4].split(",")]
print("E_Z", E_Z_series(alpha) if d == 1 else None)
for b in bs:
    t0 = time.time()
    lp = RigLP(d, alpha, b, K)
    r = lp.solve(verbose=True, rounds=int(sys.argv[5]) if len(sys.argv) > 5 else 12)
    json.dump(r, open(f"sol_d{d}_a{alpha}_K{K}_b{b}.json", "w"))
    import numpy as np; print("max|c|", np.abs(lp.c).max(), "c", np.round(lp.c[:6], 4))
    print(f"b={b} double bound {r.get('bound_double')}  ({time.time()-t0:.1f}s)", flush=True)
    t1 = time.time()
    try:
        c = lp.certify()
        pass
        print(json.dumps(c), f"({time.time()-t1:.1f}s)", flush=True)
    except Exception as e:
        print("CERT FAIL", repr(e), flush=True)
