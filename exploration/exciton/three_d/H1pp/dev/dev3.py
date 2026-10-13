import sys, time, json
sys.path.insert(0, ".."); sys.path.insert(0, "../../H1")
import rig2
d, alpha, K, b, gcut = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4], float(sys.argv[5])
t0 = time.time()
lp = rig2.HPRig(d, alpha, b, K, gcut=gcut)
r = lp.solve(verbose=True, rounds=int(sys.argv[6]) if len(sys.argv) > 6 else 10)
print("hp", r["bound_hp"], time.time() - t0, flush=True)
tag = f"d{d}_a{alpha}_K{K}_b{b.replace('/', '_')}_g{gcut:g}"
json.dump(r, open(f"hp3_{tag}.json", "w"))
c = lp.certify()
c["time_s"] = time.time() - t0
print(json.dumps(c), flush=True)
json.dump(c, open(f"cert3_{tag}.json", "w"))
