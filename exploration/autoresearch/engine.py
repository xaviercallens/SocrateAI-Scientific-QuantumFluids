#!/usr/bin/env python3
"""autoresearch / engine.py -- the loop. For each hypothesis in hypotheses.json (in file order): run its probe
(`probes.py <id>`) under the fixed budget, read D, compute the fixed score (prepare.score), and decide
keep / discard / crash against a running top-KEEP_TOP leaderboard -- Karpathy's keep-if-better rule applied to
hypotheses instead of training scripts. Appends to results.tsv (never rewritten).

    .venv/bin/python exploration/autoresearch/engine.py            # all hypotheses not yet in results.tsv
    .venv/bin/python exploration/autoresearch/engine.py --only H04 # one (re-run is appended, not overwritten)
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare as P

HERE = Path(__file__).resolve().parent
TSV = HERE / "results.tsv"; HDR = "commit\thyp\tD\tnovelty\treach\tcost_days\tscore\tseconds\tstatus\tdescription\n"


def commit() -> str:
    return subprocess.run(["git", "-C", str(P.ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def rows():
    if not TSV.exists():
        return []
    return [dict(zip(HDR.strip().split("\t"), l.rstrip("\n").split("\t"))) for l in TSV.read_text().splitlines()[1:]]


def run_probe(hid: str):
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    t0 = time.time(); log = HERE / "logs" / f"{hid}.log"; log.parent.mkdir(exist_ok=True)
    try:
        r = subprocess.run([sys.executable, str(HERE / "probes.py"), hid], capture_output=True, text=True, timeout=P.HARD_KILL_S, env=env)
        out = r.stdout + "\n--- stderr\n" + r.stderr
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        out += "\nHARD_KILL"
    dt = time.time() - t0; log.write_text(out)
    res = None
    for line in out.splitlines():
        if line.startswith("PROBE_RESULT "):
            res = json.loads(line[len("PROBE_RESULT "):])
    return res, dt


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); a = ap.parse_args()
    hyps = json.loads((HERE / "hypotheses.json").read_text())["hypotheses"]
    if not TSV.exists():
        TSV.write_text(HDR)
    done = {r["hyp"] for r in rows()}
    for h in hyps:
        if a.only and h["id"] != a.only:
            continue
        if not a.only and h["id"] in done:
            continue
        res, dt = run_probe(h["id"])
        over = dt > P.BUDGET_S * 1.2
        if res is None or over:
            D, sc, status = 0.0, 0.0, "crash"
            note = "over budget" if over and res is not None else "no result"
        else:
            D = float(res["D"]); sc = P.score(D, h["novelty"], h["reach"], h["cost_days"]) if res.get("consistent", True) else 0.0
            kept = sorted((float(r["score"]) for r in rows() if r["status"] == "keep"), reverse=True)
            bar = kept[P.KEEP_TOP - 1] if len(kept) >= P.KEEP_TOP else 0.0
            status = "keep" if sc > bar and sc > 0 else "discard"
            note = ("REFUTED/INVALID BY PROBE: " if not res.get("consistent", True) else "") + res.get("note", "")
        with TSV.open("a") as f:
            f.write(f"{commit()}\t{h['id']}\t{D:.3f}\t{h['novelty']}\t{h['reach']}\t{h['cost_days']}\t{sc:.4f}\t{dt:.0f}\t{status}\t{h['short']} | {note}\n")
        print(f"{h['id']}: D = {D:.2f}, score = {sc:.3f}, {dt:.0f} s -> {status}  ({note})", flush=True)
    latest = {}
    for r in rows():
        latest[r["hyp"]] = r                                    # the last run of a hypothesis is the one that counts
    board = sorted(latest.values(), key=lambda r: -float(r["score"]))
    print("\nleaderboard (latest run per hypothesis):")
    for i, r in enumerate(board):
        print(f"  {i + 1:2d}. {r['hyp']}  score {float(r['score']):.3f}  D {float(r['D']):.2f}  {'SELECTED' if i < P.KEEP_TOP and float(r['score']) > 0 else ''}  {r['description'][:90]}")


if __name__ == "__main__":
    main()
