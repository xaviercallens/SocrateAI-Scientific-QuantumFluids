import sys, time, json
sys.path.insert(0, "..")
sys.path.insert(0, "../../H1")
from rig2 import HPRig
from lp_bound import E_Z_series
d, alpha, K, b = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4]
rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 8
t0 = time.time()
lp = HPRig(d, alpha, b, K)
r = lp.solve(verbose=True, rounds=rounds)
print(f"hp bound {r['bound_hp']:.15f} ({time.time()-t0:.0f}s)", flush=True)
json.dump(r, open(f"hp_d{d}_a{alpha}_K{K}_b{b.replace('/','_')}.json", "w"))
t1 = time.time()
c = lp.certify()
print(json.dumps(c, indent=None), f"({time.time()-t1:.0f}s)")
if d == 1:
    print("E_Z", repr(E_Z_series(float(eval(alpha)) if alpha != 'pi' else 3.141592653589793)))
