"""H1'' gate evaluation (PREREG.md).  Reads records/*.json, writes summary.json and prints the gate table."""
import json
import math
import os
import sys
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "H1"))
from lp_bound import theta_sum, lattice  # noqa: E402

mp.mp.dps = 60
ALPHA = {"1": mp.mpf(1), "pi": mp.pi, "2": mp.mpf(2), "4": mp.mpf(4), "8": mp.mpf(8)}


def E_Z(a):
    return 2 * mp.nsum(lambda n: mp.exp(-a * n * n), [1, mp.inf])


def B_of(rec):
    if not rec or not rec.get("certified"):
        return None
    s = rec["certificate"]["B_lower"]            # arb string "[mid +/- rad]"
    body = s.strip("[]").split("+/-")
    return mp.mpf(body[0]) - (mp.mpf(body[1]) if len(body) > 1 else 0)


def load(case, K):
    p = os.path.join(HERE, "records", f"{case}_K{K}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    out = {}
    lat = {}
    for a in ("pi", "2", "4", "8"):
        af = float(ALPHA[a])
        lat[a] = {n: theta_sum(lattice(n), af)[0] for n in ("FCC", "BCC")}
    lat_A2 = theta_sum(lattice("A2"), math.pi)[0]
    rows = []
    stop = False
    for case, ref in [("V1a", None), ("V1b", None), ("V2", None), ("V3", None), ("H2", None), ("H4", None), ("H8", None)]:
        r40, r30 = load(case, 40), load(case, 30)
        B, B30 = B_of(r40), B_of(r30)
        d = (r40 or r30 or {}).get("d")
        a = (r40 or r30 or {}).get("alpha")
        row = {"case": case, "d": d, "alpha": a, "B_K40": None if B is None else mp.nstr(B, 15),
               "B_K30": None if B30 is None else mp.nstr(B30, 15), "certified_K40": bool(r40 and r40.get("certified"))}
        verdict, void = None, False
        if B is None:
            verdict = "not certified (fails gate)" if r40 else "not run"
        elif case.startswith("V1"):
            ez = E_Z(ALPHA[a])
            row["E_Z"] = mp.nstr(ez, 15)
            row["E_Z_minus_B_rel"] = mp.nstr((ez - B) / ez, 5)
            void = B > ez
            verdict = "pass" if 0 <= ez - B <= mp.mpf("1e-8") * ez else "FAIL"
        elif case == "V2":
            row["E_A2"] = repr(lat_A2)
            row["E_A2_minus_B"] = mp.nstr(mp.mpf(lat_A2) - B, 5)
            void = B > mp.mpf(lat_A2) * (1 + mp.mpf("1e-12"))
            verdict = "pass" if B >= mp.mpf("0.15959526") - mp.mpf("1e-8") else "FAIL"
        elif case == "V3":
            m = min(lat["pi"].values())
            row["min_FCC_BCC"] = repr(m)
            row["B_minus_published"] = mp.nstr(B - mp.mpf("0.22321782"), 5)
            row["B_minus_CdCI_Thm1.4"] = mp.nstr(B - mp.mpf("0.21736068"), 5)
            void = B > mp.mpf(m) * (1 + mp.mpf("1e-12"))
            verdict = "pass" if B >= mp.mpf("0.22321782") - mp.mpf("1e-8") else "FAIL"
        else:
            m = min(lat[a].values())
            G = (mp.mpf(m) - B) / mp.mpf(m)
            row.update({"E_FCC": repr(lat[a]["FCC"]), "E_BCC": repr(lat[a]["BCC"]), "G": mp.nstr(G, 6)})
            void = B > mp.mpf(m) * (1 + mp.mpf("1e-12"))
            verdict = "G > 1e-3" if G > mp.mpf("1e-3") else ("G < 1e-6" if G < mp.mpf("1e-6") else "inconclusive")
        if stop and case != "V1b":
            row["note"] = "gated: an earlier gate failed (reported, not a registered result)"
        row["verdict"] = "VOID (bug)" if void else verdict
        if case in ("V1a", "V1b", "V2", "V3") and row["verdict"] != "pass":
            stop = True
        rows.append(row)
    out["rows"] = rows
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    for r in rows:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
