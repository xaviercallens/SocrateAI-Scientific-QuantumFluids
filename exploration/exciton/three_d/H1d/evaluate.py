"""H1d gate evaluation (PREREG.md).  Reads records/*.json, writes summary.json, prints the table.
Certified statement per case: UB* = min over the ladder of the UPPER end of the certified UB ball."""
import glob
import json
import os
import sys

import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "H1"))
from lp_bound import theta_sum, lattice  # noqa: E402

mp.mp.dps = 50
H1PP = os.path.join(HERE, "..", "H1pp", "records")
H1PPP = os.path.join(HERE, "..", "H1ppp", "records")


def ball_upper(s):
    body = s.strip("[]").split("+/-")
    return mp.mpf(body[0]) + (mp.mpf(body[1]) if len(body) > 1 else 0)


def B_cert(path):
    if not os.path.exists(path):
        return None
    r = json.load(open(path))
    s = r["certificate"]["B_lower"].strip("[]").split("+/-")
    return mp.mpf(s[0]) - (mp.mpf(s[1]) if len(s) > 1 else 0)


def main():
    out = {"cases": []}
    E_Z = 2 * mp.nsum(lambda n: mp.exp(-mp.pi * n * n), [1, mp.inf])
    refs = {
        "V1": {"B": B_cert(os.path.join(H1PP, "V1b_K40.json")), "E_Z": E_Z},
        "V2": {"B": B_cert(os.path.join(H1PP, "V2_K40.json")), "E_A2": mp.mpf(theta_sum(lattice("A2"), float(mp.pi))[0])},
        "D3pi": {"B": B_cert(os.path.join(H1PPP, "V3_K50.json")), "alpha": float(mp.pi)},
        "D3a2": {"B": B_cert(os.path.join(H1PPP, "H2_K50.json")), "alpha": 2.0},
        "D3a4": {"B": B_cert(os.path.join(H1PPP, "H4_K50.json")), "alpha": 4.0},
        "D3a8": {"B": B_cert(os.path.join(H1PPP, "H8_K50.json")), "alpha": 8.0},
    }
    gates_ok = True
    for case, ref in refs.items():
        recs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(HERE, "records", f"{case}_s*_m*.json")))]
        cert = [(ball_upper(r["certificate"]["UB_ball"]), r["s"], r["m"]) for r in recs if r.get("certified")]
        row = {"case": case, "n_records": len(recs), "n_certified": len(cert),
               "not_certified": [(r["s"], r["m"]) for r in recs if not r.get("certified")]}
        if not cert:
            row["verdict"] = "no certified UB"
            out["cases"].append(row); gates_ok = gates_ok and not case.startswith("V"); continue
        UBs = {f"s{s}_m{m}": mp.nstr(u, 15) for u, s, m in cert}
        best = min(cert)
        row.update({"UB_by_grid": UBs, "UB_star": mp.nstr(best[0], 15), "best_grid": f"s{best[1]}_m{best[2]}"})
        B = ref["B"]
        row["B_cert_H1pp_or_H1ppp"] = None if B is None else mp.nstr(B, 15)
        void = B is not None and any(u < B for u, _, _ in cert)          # an upper bound below a certified lower bound
        if case == "V1":
            void = void or any(u < E_Z * (1 - mp.mpf("1e-12")) for u, _, _ in cert)
            row["UB_star_rel_E_Z"] = mp.nstr(best[0] / E_Z - 1, 5)
            verdict = "pass" if best[0] <= E_Z * (1 + mp.mpf("1e-6")) else "FAIL (not tight)"
        elif case == "V2":
            row["UB_star_rel_E_A2"] = mp.nstr(best[0] / ref["E_A2"] - 1, 5)
            verdict = "pass (consistency)"
        else:
            Ef = theta_sum(lattice("FCC"), ref["alpha"])[0]
            Eb = theta_sum(lattice("BCC"), ref["alpha"])[0]
            ml = mp.mpf(min(Ef, Eb))
            row.update({"E_FCC": repr(Ef), "E_BCC": repr(Eb), "UB_star_rel_minlat": mp.nstr(best[0] / ml - 1, 6),
                        "sandwich_width_rel": None if B is None else mp.nstr((best[0] - B) / B, 5)})
            if case == "D3pi":
                row["UB_star_minus_CdCI_record"] = mp.nstr(best[0] - mp.mpf("0.23153532"), 5)
            verdict = "UB < min(FCC,BCC)" if best[0] < ml else "not shown at this resolution"
        row["verdict"] = "VOID (bug)" if void else verdict
        if case.startswith("V") and row["verdict"] not in ("pass", "pass (consistency)"):
            gates_ok = False
        if not case.startswith("V") and not gates_ok:
            row["note"] = "gated: a validation gate failed (reported, not a registered result)"
        if not case.startswith("V") and void:
            gates_ok = False
        out["cases"].append(row)
    out["validation_gates_pass"] = gates_ok
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    for r in out["cases"]:
        print(json.dumps({k: v for k, v in r.items() if k != "UB_by_grid"}))
    print("validation gates pass:", gates_ok)


if __name__ == "__main__":
    main()
