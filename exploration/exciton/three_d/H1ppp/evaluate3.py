"""H1''' gate evaluation (PREREG.md).  evaluate.py is an unmodified copy of ../H1pp/evaluate.py and reads K = 40/30
records only; this script applies the same criteria (B_of, V3 window, G thresholds, VOID tests imported/copied
verbatim) to K = 50 (gate) and K = 60, and reports B(K=50) - B(K=40) against ../H1pp/records.  Writes summary.json."""
import json
import os

import mpmath as mp

from evaluate import ALPHA, B_of, HERE, lattice, theta_sum  # noqa: F401  (frozen helpers)

mp.mp.dps = 60
H1PP = os.path.join(HERE, "..", "H1pp", "records")


def load(case, K, base=os.path.join(HERE, "records")):
    p = os.path.join(base, f"{case}_K{K}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def s(x):
    return None if x is None else mp.nstr(x, 15)


def main():
    lat = {a: {n: theta_sum(lattice(n), float(ALPHA[a]))[0] for n in ("FCC", "BCC")} for a in ("pi", "2", "4", "8")}
    rows, gate = [], None
    for case, Ks in [("V3", (50, 60)), ("H2", (50,)), ("H4", (50,)), ("H8", (50,))]:
        r40 = load(case, 40, H1PP)
        B40 = B_of(r40)
        recs = {K: load(case, K) for K in Ks}
        for K in Ks:
            r = recs[K]
            B = B_of(r)
            a = (r or r40 or {}).get("alpha")
            row = {"case": case, "K": K, "B": s(B), "certified": bool(r and r.get("certified")), "B_K40": s(B40),
                   "B_minus_B_K40": None if B is None or B40 is None else mp.nstr(B - B40, 5)}
            if B is None:
                verdict, void = ("not certified (fails gate)" if r else "not run"), False
            elif case == "V3":
                m = min(lat["pi"].values())
                row["min_FCC_BCC"] = repr(m)
                row["B_minus_published"] = mp.nstr(B - mp.mpf("0.22321782"), 5)
                void = B > mp.mpf(m) * (1 + mp.mpf("1e-12"))
                verdict = "pass" if B >= mp.mpf("0.22321782") - mp.mpf("1e-8") else "FAIL"
            else:
                m = min(lat[a].values())
                G = (mp.mpf(m) - B) / mp.mpf(m)
                row.update({"E_FCC": repr(lat[a]["FCC"]), "E_BCC": repr(lat[a]["BCC"]), "G": mp.nstr(G, 6)})
                void = B > mp.mpf(m) * (1 + mp.mpf("1e-12"))
                verdict = "G > 1e-3" if G > mp.mpf("1e-3") else ("G < 1e-6" if G < mp.mpf("1e-6") else "inconclusive")
            row["verdict"] = "VOID (bug)" if void else verdict
            if case == "V3" and K == 50:
                row["role"] = "GATE"
                gate = row["verdict"]
            elif case == "V3":
                row["role"] = "reported (not a registered gate)"
            elif gate != "pass":
                row["note"] = "gated: the K = 50 V3 gate did not pass (reported, not a registered result)"
            rows.append(row)
    v3 = [B_of(load("V3", 40, H1PP))] + [B_of(load("V3", K)) for K in (50, 60)]
    mono = None if None in v3 else bool(v3[0] < v3[1] < v3[2])
    out = {"gate_V3_K50": gate, "V3_monotone_K40_50_60": mono, "rows": rows}
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("gate_V3_K50", "V3_monotone_K40_50_60")}))
    for r in rows:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
