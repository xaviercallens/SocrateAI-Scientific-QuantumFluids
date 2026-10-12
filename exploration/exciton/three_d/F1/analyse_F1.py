"""F1 analysis: gates F1a / F1b, gradient-evaluation counts, N = 24 control. Prints a Markdown fragment."""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "C"))
import run_C as R

HERE = os.path.dirname(os.path.abspath(__file__))
TOL_E, TOL_CHORD = 1e-8, 1e-6
CHORD600, CHORD24 = 2 * np.sin(np.pi / 10), 1.0
C6, C24 = R.cell600(), R.cell24()
E600 = {a: R.energy(C6, "g", a) for a in (1.0, 2.0, 4.0)}
E24 = {a: R.energy(C24, "g", a) for a in (1.0, 2.0, 4.0)}
Crec = [json.loads(l) for l in open(os.path.join(HERE, "..", "C", "records.jsonl"))]


def load(name):
    p = os.path.join(HERE, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def hit(E, chord, Eref, chordref):
    return abs(E - Eref) / abs(Eref) <= TOL_E and abs(chord - chordref) <= TOL_CHORD


def report_N120(recs):
    out = ["## N = 120 (gates F1a, F1b)", "",
           "| a | seeds | F1a homotopy hits (E and chord) | E-only hits | F1b plain equal-compute hits | plain E-only | C plain hits (same seeds, from C/records.jsonl, E-only) | homotopy nfev min/mean/max | C plain nit mean (same seeds) |",
           "|---|---|---|---|---|---|---|---|---|"]
    verdict = {}
    for a in (1.0, 2.0, 4.0):
        rs = sorted([r for r in recs if r["a_target"] == a], key=lambda r: r["start"])
        if not rs: continue
        n = len(rs)
        hh = sum(hit(r["homotopy"]["E"], r["homotopy"]["min_chord"], E600[a], CHORD600) for r in rs)
        he = sum(abs(r["homotopy"]["E"] - E600[a]) / E600[a] <= TOL_E for r in rs)
        ph = sum(hit(r["plain_equal_compute"]["E"], r["plain_equal_compute"]["min_chord"], E600[a], CHORD600) for r in rs)
        pe = sum(abs(r["plain_equal_compute"]["E"] - E600[a]) / E600[a] <= TOL_E for r in rs)
        seeds = {r["start"] for r in rs}
        kern = rs[0]["kernel"]
        cr = [c for c in Crec if c["N"] == 120 and c["kernel"] == kern and c["start"] in seeds]
        ch = sum(abs(c["E"] - E600[a]) / E600[a] <= TOL_E for c in cr)
        nf = [r["homotopy"]["nfev_total"] for r in rs]
        out.append(f"| {a:g} | {n} | {hh}/{n} | {he}/{n} | {ph}/{n} | {pe}/{n} | {ch}/{len(cr)} | {min(nf)}/{np.mean(nf):.0f}/{max(nf)} | {np.mean([c['nit'] for c in cr]):.0f} |")
        verdict[a] = dict(n=n, hom=hh, plain=ph, hom_E=he, plain_E=pe, C=ch, nC=len(cr))
    out += ["", "Per-seed detail (N = 120):", "",
            "| a | seed | E_hom - E_600 (rel) | chord_hom | nfev_hom | restarts/plain | E_plain - E_600 (rel) | chord_plain | best plain run nit | E_C - E_600 (rel) | t_hom s | t_plain s |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in (1.0, 2.0, 4.0):
        for r in sorted([r for r in recs if r["a_target"] == a], key=lambda r: r["start"]):
            h, p = r["homotopy"], r["plain_equal_compute"]
            c = [c for c in Crec if c["N"] == 120 and c["kernel"] == r["kernel"] and c["start"] == r["start"]]
            cE = (c[0]["E"] - E600[a]) / E600[a] if c else float("nan")
            out.append(f"| {a:g} | {r['start']} | {(h['E']-E600[a])/E600[a]:.1e} | {h['min_chord']:.6f} | {h['nfev_total']} | {p['restarts']} | {(p['E']-E600[a])/E600[a]:.1e} | {p['min_chord']:.6f} | {len(p['runs'])} runs | {cE:.1e} | {r['t_homotopy']:.0f} | {r['t_plain']:.0f} |")
    # rung trajectories: energies relative to E_600 at a = 1, 2 inside the a = 4 ladders
    out += ["", "Intermediate rungs of the a = 4 ladders (supplementary, gauss4 seeds): relative energy above E_600(a) at a = 1 and a = 2, and rungs hitting the 8000-iteration cap:", ""]
    rs4 = [r for r in recs if r["a_target"] == 4.0]
    if rs4:
        for a in (1.0, 2.0):
            d = [(rg["E"] - E600[a]) / E600[a] for r in rs4 for rg in r["homotopy"]["rungs"] if abs(rg["a"] - a) < 1e-12]
            out.append(f"- a = {a:g}: rel. excess min {min(d):.1e}, median {np.median(d):.1e}, max {max(d):.1e}; within 1e-8: {sum(x <= TOL_E for x in d)}/{len(d)}")
        caps = [sum(rg["nit"] >= 8000 for rg in r["homotopy"]["rungs"]) for r in rs4]
        out.append(f"- rungs at the iteration cap per ladder (17 rungs): min {min(caps)}, mean {np.mean(caps):.1f}, max {max(caps)}")
        capa = {}
        for r in rs4:
            for rg in r["homotopy"]["rungs"]:
                capa.setdefault(round(rg["a"], 4), []).append(rg["nit"])
        out.append("- mean iterations per rung: " + ", ".join(f"a={a:g}: {np.mean(v):.0f}" for a, v in sorted(capa.items())))
    # rung-by-rung energy excess over E_600(a) along every ladder (where does the ladder leave the 600-cell branch?)
    out += ["", "Rung-by-rung: median (max) relative energy excess over E_600(a) across all ladders that contain the rung, and mean iterations (8000 = cap):", "",
            "| a (rung) | ladders | median rel. excess | max rel. excess | min rel. excess | mean nit |", "|---|---|---|---|---|---|"]
    byA = {}
    for r in recs:
        for rg in r["homotopy"]["rungs"]:
            byA.setdefault(rg["a"], []).append(rg)  # exact float key: E_600(a) must be evaluated at the rung's own a
    for a, v in sorted(byA.items()):
        e6 = R.energy(C6, "g", a)
        d = [(rg["E"] - e6) / e6 for rg in v]
        out.append(f"| {a:.4f} | {len(v)} | {np.median(d):.1e} | {max(d):.1e} | {min(d):.1e} | {np.mean([rg['nit'] for rg in v]):.0f} |")
    # plain equal-compute: restart statistics and reproduction of C's record by the first run
    out += ["", "Plain equal-compute control: restarts and per-run outcomes (E-only hits among all restart runs); first run reproduces C's record at the same seed?", "",
            "| a | runs total | runs at E_600 (E-only, 1e-8) | mean nit per completed run | first-run E minus C's E at same seed (max abs over seeds) |", "|---|---|---|---|---|"]
    for a in (1.0, 2.0, 4.0):
        rs = [r for r in recs if r["a_target"] == a]
        if not rs: continue
        runs = [x for r in rs for x in r["plain_equal_compute"]["runs"] if x["E_end"] is not None]
        hits = sum(abs(x["E_end"] - E600[a]) / E600[a] <= TOL_E for x in runs)
        dev = []
        for r in rs:
            c = [c for c in Crec if c["N"] == 120 and c["kernel"] == r["kernel"] and c["start"] == r["start"]]
            x = r["plain_equal_compute"]["runs"][0]
            if c and x["E_end"] is not None: dev.append(abs(x["E_end"] - c[0]["E"]))
        out.append(f"| {a:g} | {len(runs)} | {hits} | {np.mean([x['nit'] for x in runs]):.0f} | {max(dev) if dev else float('nan'):.1e} |")
    return out, verdict


def report_N24(recs):
    out = ["## N = 24 (control 2)", "",
           "| a | seeds | homotopy at E_24cell (E and chord=1) | homotopy below E_24cell by > 1e-8 | lowest homotopy E | E_24cell | plain equal-compute at E_24cell | C plain at E_24cell (same seeds, E-only) | homotopy nfev mean |",
           "|---|---|---|---|---|---|---|---|---|"]
    for a in (1.0, 2.0, 4.0):
        rs = [r for r in recs if r["a_target"] == a]
        if not rs: continue
        n = len(rs)
        hh = sum(hit(r["homotopy"]["E"], r["homotopy"]["min_chord"], E24[a], CHORD24) for r in rs)
        below = sum((r["homotopy"]["E"] - E24[a]) / E24[a] < -TOL_E for r in rs)
        low = min(r["homotopy"]["E"] for r in rs)
        ph = sum(hit(r["plain_equal_compute"]["E"], r["plain_equal_compute"]["min_chord"], E24[a], CHORD24) for r in rs)
        kern = rs[0]["kernel"]; seeds = {r["start"] for r in rs}
        cr = [c for c in Crec if c["N"] == 24 and c["kernel"] == kern and c["start"] in seeds]
        ch = sum(abs(c["E"] - E24[a]) / E24[a] <= TOL_E for c in cr)
        he = sum(abs(r["homotopy"]["E"] - E24[a]) / E24[a] <= TOL_E for r in rs)
        out.append(f"| {a:g} | {n} | {hh}/{n} (E-only {he}/{n}) | {below} | {low:.10g} | {E24[a]:.10g} | {ph}/{n} | {ch}/{len(cr)} | {np.mean([r['homotopy']['nfev_total'] for r in rs]):.0f} |")
        others = sorted({round(r["homotopy"]["E"], 6) for r in rs if not hit(r["homotopy"]["E"], r["homotopy"]["min_chord"], E24[a], CHORD24)})
        if others: out.append(f"  - a = {a:g}: homotopy end energies not at the 24-cell: {others}")
    return out


if __name__ == "__main__":
    r120, r24 = load("records_N120.jsonl"), load("records_N24.jsonl")
    print(f"E_600: " + ", ".join(f"a={a:g}: {E:.10f}" for a, E in E600.items()))
    print(f"E_24cell: " + ", ".join(f"a={a:g}: {E:.10f}" for a, E in E24.items()))
    print(f"min chord 600-cell target {CHORD600:.15f}; thresholds: rel. energy {TOL_E:g}, chord {TOL_CHORD:g}\n")
    if r120:
        o, v = report_N120(r120); print("\n".join(o)); print()
        for a, d in v.items():
            print(f"a={a:g}: F1a homotopy {d['hom']}/{d['n']} ({d['hom']/d['n']:.0%}); F1b plain equal-compute {d['plain']}/{d['n']} ({d['plain']/d['n']:.0%}); C plain {d['C']}/{d['nC']}")
        print()
    if r24:
        print("\n".join(report_N24(r24)))
