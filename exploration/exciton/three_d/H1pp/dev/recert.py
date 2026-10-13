import sys, json, time
sys.path.insert(0, ".."); sys.path.insert(0, "../../H1")
from rig2 import *
fn, d, alpha, b = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
r = json.load(open(fn))
lp = HPRig(d, alpha, b, 29, gcut=1e-12)
c = [fmpq(*map(int, s.split("/"))) if "/" in s else fmpq(int(s)) for s in r["coeffs_exact"]]
t = time.time()
out = lp.certify(c)
out["time_s"] = time.time() - t
print(json.dumps(out, indent=1))
