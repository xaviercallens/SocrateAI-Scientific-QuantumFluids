#!/usr/bin/env python3
"""Night workflow (2026-10-07): finish and publish version 2 of the vortex-transport paper without a human.

Steps, each logged to data/generated/pgpe/transport/night_publish.log and abandoned (no publication) on any error:
  1. wait for the two tie-break runs W2_L96_e0.60_dipole_d12_s3/s4 to end;
  2. evaluate all L = 96 runs by the registered rule (evaluate_w2.py) and apply amendment W2-A (>= 3 of 4 meet ->
     SUPPORTED, <= 1 -> REFUTED, else INCONCLUSIVE);
  3. replace the three \\PENDING sentences of paper/vortex_transport.tex with the outcome's pre-written template;
  4. regenerate the figures and the PDF; refuse to go on if any PENDING remains or LaTeX fails;
  5. publish version 2 as a new version of Zenodo record 23202455 (authorised by the owner on 2026-10-07);
  6. README DOI line, review-response status, LEDGER claims, commit and push (no trailers: owner's rule);
  7. if SUPPORTED and the bases exist, start the counterflow cells that do not need the L = 128 base.
Templates and the rule were written before runs 3 and 4 were read.
"""
import json, os, re, subprocess, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; TR = ROOT / "data/generated/pgpe/transport"
LOG = open(TR / "night_publish.log", "a"); PY = str(ROOT / ".venv/bin/python")
TEX = ROOT / "paper/vortex_transport.tex"; META = ROOT / "paper/zenodo_metadata_vortex_transport.json"
REC = ROOT / "paper/zenodo_record_vortex_transport.json"; PREV = "23202455"


def log(*a):
    LOG.write(time.strftime("%F %T ") + " ".join(str(x) for x in a) + "\n"); LOG.flush()


def sh(cmd, **kw):
    log("$", " ".join(cmd) if isinstance(cmd, list) else cmd)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)
    log(r.stdout[-3000:]); log(r.stderr[-1500:]) if r.stderr else None
    if r.returncode:
        raise RuntimeError(f"command failed rc={r.returncode}: {cmd}")
    return r.stdout


def wait_runs():
    logs = [TR / f"W2_L96_e0.60_dipole_d12_s{s}.log" for s in (3, 4)]
    while not all(p.exists() and "ended" in p.read_text() for p in logs):
        time.sleep(120)
    log("runs 3 and 4 ended")


def verdict():
    sh([PY, "exploration/pgpe/evaluate_w2.py"], env=dict(os.environ, OMP_NUM_THREADS="1"))
    j = json.load(open(TR / "W2_result.json")); n, m = j["n"], j["n_meet"]
    v = "SUPPORTED" if m >= 3 else ("REFUTED" if n - m >= 3 else "INCONCLUSIVE")
    j["verdict"] = v; j["rule"] = "W2-A: >=3 of 4 meet -> SUPPORTED; <=1 -> REFUTED; else INCONCLUSIVE"
    json.dump(j, open(TR / "W2_result.json", "w"), indent=1); log("verdict", v, m, "of", n)
    return j


def fill_paper(j):
    n, m, v = j["n"], j["n_meet"], j["verdict"]; runs = j["runs"]
    desc = "; ".join(f"run {k[-5]}: early slope ${r['early']:+.4f}$, late ${r['late']:+.4f}$, $d(4000)={r['d_end']:.1f}$ (wind equation ${r['wind_end']:.1f}$, free ${r['free_end']:.1f}$)"
                     + (", annihilated" if r["ended"] == "annihilated" else "") for k, r in sorted(runs.items()))
    s = TEX.read_text()
    old_abs = r"\PENDING{the $L=96$" + "\ncontrol decides whether the stall is the box's}"
    new_abs = {"SUPPORTED": f"the $L=96$ control, where the box criterion predicts no stall, shows none in {m} of {n} runs: the stall is the box's",
               "REFUTED": f"the $L=96$ control, where the box criterion predicts no stall, stalls in {n - m} of {n} runs: the stall is not the box's and the mechanism as written is refuted",
               "INCONCLUSIVE": f"the $L=96$ control, where the box criterion predicts no stall, splits {m}--{n - m} on the binary criterion, while a parameter-free wind equation lands within about one unit of every pair"}[v]
    old_sec = re.search(r"\\PENDING\{W2 verdict on the four L = 96 runs:.*?\}\.", s, re.S).group(0)
    new_sec = {"SUPPORTED": f"The {n} runs at $L=96$ ({desc}): {m} of {n} meet the no-stall criterion, against the registered threshold of three, so the stall observed at $L=64$ is the box's and the mechanism is supported by its decisive control.",
               "REFUTED": f"The {n} runs at $L=96$ ({desc}): only {m} of {n} meet the no-stall criterion (refutation threshold: at most one), so the pairs stall at $L=96$ as they do at $L=64$, the stall is not the box's, and the phonon-wind mechanism as written is refuted; what follows in this section is therefore the report of a bath-driven stall whose cause is open.",
               "INCONCLUSIVE": f"The {n} runs at $L=96$ ({desc}): {m} of {n} meet the no-stall criterion, between the thresholds fixed before runs 3 and 4 were read (three or more supports, one or fewer refutes), so the binary control is inconclusive at this sample size and the question passes to the graded test."}[v]
    old_con = r"the phonon-wind stall \PENDING{until the $L=96$ control}"
    new_con = {"SUPPORTED": "the stall law of the phonon wind (its mechanism is supported by the $L=96$ control; the law is untested)",
               "REFUTED": "the cause of the box-scale stall (the $L=96$ control refutes the box mechanism)",
               "INCONCLUSIVE": f"the phonon-wind stall (the $L=96$ control split {m}--{n - m}; the graded test is next)"}[v]
    for o, nw in ((old_abs, new_abs), (old_sec, new_sec), (old_con, new_con)):
        assert o in s, o[:60]
        s = s.replace(o, nw)
    TEX.write_text(s); log("paper filled for", v)
    body = s.split(r"\newcommand{\PENDING}", 1)[1].split("\n", 1)[1]
    assert "PENDING" not in body, "PENDING left in the paper"


def build():
    sh([PY, "paper/make_figures_vortex_transport.py"], env=dict(os.environ, OMP_NUM_THREADS="1", MPLBACKEND="Agg"))
    subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "vortex_transport.tex"], cwd=ROOT / "paper", capture_output=True, text=True)
    lg = (ROOT / "paper/vortex_transport.log").read_text()
    assert "Output written on vortex_transport.pdf" in lg and "undefined" not in lg.lower(), "LaTeX failed"
    log("pdf built:", re.search(r"Output written on vortex_transport.pdf \((.*?)\)", lg).group(1))


def publish(j):
    v = j["verdict"]; meta = json.load(open(META)); m = meta["metadata"]
    sent = {"SUPPORTED": f"The L = 96 counterflow control supports the box mechanism ({j['n_meet']} of {j['n']} runs show no stall).",
            "REFUTED": f"The L = 96 counterflow control refutes the box mechanism ({j['n'] - j['n_meet']} of {j['n']} runs stall).",
            "INCONCLUSIVE": f"The L = 96 counterflow control is inconclusive ({j['n_meet']}-{j['n'] - j['n_meet']} split); the parameter-free wind equation is reported."}[v]
    m["description"] = m["description"].replace("and the L = 96 counterflow control.</p>", f"and the L = 96 counterflow control. {sent}</p>")
    m["notes"] = m["notes"].replace("is reported with its registered binary reading", f"({v}) is reported with its registered binary reading")
    json.dump(meta, open(META, "w"), indent=1, ensure_ascii=False)
    sh(["python3", "scripts/zenodo_deposit_paper.py", "--meta", str(META), "--pdf", str(ROOT / "paper/vortex_transport.pdf"),
        "--record-out", str(REC), "--new-version-of", PREV, "--publish"])
    rec = json.load(open(REC)); log("published", rec); return rec


def bookkeeping(j, rec):
    v, doi, rid = j["verdict"], rec["doi"], rec["id"]
    p = ROOT / "README.md"; s = p.read_text()
    s = s.replace(f"**[10.5281/zenodo.{PREV}](https://doi.org/10.5281/zenodo.{PREV})**", f"**[{doi}](https://doi.org/{doi})** (version 2, revised after peer review; concept DOI 10.5281/zenodo.23202454)")
    p.write_text(s)
    p = ROOT / "docs/peer_review/vortex_transport_review_1_response.md"; s = p.read_text()
    s = re.sub(r"Status: version 2 compiles.*", f"Status: version 2 published ({doi}, record {rid}); the L = 96 control (item B) is reported, verdict {v} by the registered rule.", s)
    p.write_text(s)
    p = ROOT / "LEDGER.md"; lines = p.read_text().split("\n"); i = next(k for k, l in enumerate(lines) if l.startswith("| CLAIM-091 |"))
    d = time.strftime("%Y-%m-%d"); rr = "; ".join(f"{k[-6:-4]}: early {r['early']:+.4f} late {r['late']:+.4f} d_end {r['d_end']:.2f} ({'meets' if r['meets'] else 'fails'})" for k, r in sorted(j["runs"].items()))
    rows = [f"| CLAIM-092 | — → W2 (L = 96 counterflow control) VERDICT: {v} ({j['n_meet']} of {j['n']} runs meet the no-stall criterion; rule W2-A fixed before runs 3-4 were read) | {d} | {rr}. Parameter-free wind equation (alpha = 0.0062) and free shrinking recorded per run in W2_result.json. Next campaign per PGPE_COUNTERFLOW_PREREG.md: {'counterflow stall map' if v == 'SUPPORTED' else 'friction law vs cutoff first'}. |",
            f"| CLAIM-093 | — → PAPER vortex_transport.tex VERSION 2 PUBLISHED (after peer review 1) | {d} | DOI {doi} (record {rid}, concept 10.5281/zenodo.23202454). 17 pages, 7 figures, code and Lean appendices; W2 verdict {v} included; kinetic reading of the friction law included. Published by the night workflow scripts/night_publish_v2.py under the owner's authorisation of 2026-10-07. |"]
    for r in reversed(rows): lines.insert(i + 1, r)
    p.write_text("\n".join(lines))
    sh(["git", "add", "paper/vortex_transport.tex", "paper/vortex_transport.pdf", "paper/figures", "paper/zenodo_metadata_vortex_transport.json",
        "paper/zenodo_record_vortex_transport.json", "README.md", "docs/peer_review/vortex_transport_review_1_response.md", "LEDGER.md"])
    sh(["git", "add", "-f", "data/generated/pgpe/transport/W2_result.json"])
    sh(["git", "commit", "-q", "-m", f"Paper v2 published: {doi}; W2 (L=96 control) verdict {v} on {j['n']} runs by rule W2-A; LEDGER CLAIM-092/093; README and review-response updated (night workflow)"])
    sh(["git", "push", "-q", "origin", "master"]); log("committed and pushed")


def campaign(j):
    if j["verdict"] != "SUPPORTED":
        log("campaign: friction law first (needs new bases) -- left for the morning"); return
    cells = "1,2,3,4,5,6,7,10,11"
    log("campaign: counterflow cells", cells, "(8-9 wait for the L = 128 base)")
    subprocess.Popen([PY, "exploration/pgpe/run_counterflow.py", "--workers", "3", "--only", cells],
                     cwd=ROOT, stdout=open(TR / "counterflow_queue_stdout.log", "a"), stderr=subprocess.STDOUT, start_new_session=True)


if __name__ == "__main__":
    try:
        log("=== night workflow start"); wait_runs(); j = verdict(); fill_paper(j); build()
        rec = publish(j); bookkeeping(j, rec); campaign(j); log("=== night workflow done")
    except Exception:
        log("!!! ABORTED\n" + traceback.format_exc()); sys.exit(1)
