#!/usr/bin/env python3
"""Publish the friction-law paper and the correction of the vortex-transport paper (version 2.2), gated.

    python3 scripts/publish_friction_law.py            # DRY RUN: builds both PDFs, checks every gate, prints what would be deposited
    python3 scripts/publish_friction_law.py --publish  # deposits paper 3 (new standalone record), then v2.2 of paper 1 (new version of its latest record)

Gates (all must hold, else exit 1 and nothing is deposited):
  * no \\PENDING marker in paper/friction_law.tex (the fine T = 0.173 arm read and its registered window applied BY HAND);
  * paper/friction_law.tex and paper/vortex_transport.tex compile with no undefined reference;
  * the DOI placeholder in paper/refs_vortex_transport.bib is replaced only after paper 3 is published (dry run keeps it and says so);
  * git tree clean for the two sources (committed).
Owner's authorisation of 2026-10-08: "prepare the publication of the next paper" -- publication itself is run only with --publish.
No commit trailers (owner's rule).
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "paper"
PREV1 = None   # latest record id of paper 1, read from paper/zenodo_record_vortex_transport.json


def sh(cmd, **kw):
    r = subprocess.run(cmd, cwd=kw.pop("cwd", ROOT), capture_output=True, text=True, **kw)
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit(f"FAILED: {' '.join(cmd)}")
    return r.stdout


def build(tex):
    subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", tex], cwd=P, capture_output=True, text=True)
    lg = (P / tex.replace(".tex", ".log")).read_text()
    if "Output written on" not in lg or "undefined" in lg.lower():
        sys.exit(f"gate: {tex} does not compile cleanly")
    return re.search(r"\((\d+ pages?)", lg).group(1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--publish", action="store_true"); a = ap.parse_args()
    t3 = (P / "friction_law.tex").read_text()
    body = t3.split("\\begin{document}", 1)[1]
    if "\\PENDING" in body:
        sys.exit("gate: friction_law.tex still has a \\PENDING marker -- read the fine T = 0.173 arm, apply the registered window, finish the text")
    sh(["git", "diff", "--quiet", "--", "paper/friction_law.tex", "paper/vortex_transport.tex", "paper/refs_vortex_transport.bib"])
    print("paper 3:", build("friction_law.tex"))
    bib = (P / "refs_vortex_transport.bib").read_text()
    if not a.publish:
        print("DRY RUN ok. Would deposit paper/friction_law.pdf (new record), then paper 1 v2.2 (new version of",
              json.loads((P / "zenodo_record_vortex_transport.json").read_text())["id"], ") with the DOI of paper 3 in place of PLACEHOLDER-CALLENS2026B")
        print("placeholder present in bib:", "PLACEHOLDER-CALLENS2026B" in bib); return
    sh(["python3", "scripts/zenodo_deposit_paper.py", "--meta", "paper/zenodo_metadata_friction_law.json", "--pdf", "paper/friction_law.pdf",
        "--record-out", "paper/zenodo_record_friction_law.json", "--publish"])
    rec3 = json.loads((P / "zenodo_record_friction_law.json").read_text()); doi3 = rec3["doi"]; print("paper 3 published:", doi3)
    (P / "refs_vortex_transport.bib").write_text(bib.replace("PLACEHOLDER-CALLENS2026B", doi3.replace("10.5281/", "10.5281/")))
    t1 = (P / "vortex_transport.tex"); s = t1.read_text()
    print("paper 1 v2.2:", build("vortex_transport.tex"))
    m1 = json.loads((P / "zenodo_metadata_vortex_transport.json").read_text()); mm = m1["metadata"]; mm["version"] = "2.2"
    mm["description"] = ("<p><b>Version 2.2</b> (October 2026): correction. The proportionality alpha ~ 0.24 rho_n/rho and its reading as a mode-averaged transport cross-section of 1.4 healing lengths hold at the single cutoff of this paper only; a scan of two further cutoffs (companion paper, doi:" + doi3 + ") shows the friction follows the temperature, alpha ~ 0.054 T, independent of the cutoff, and withdraws the reading. Data, figures and registered verdicts of the other sections are unchanged.</p>") + re.sub(r"^<p><b>Version 2\.1</b>.*?</p>", "", mm["description"], count=1, flags=re.S)
    (P / "zenodo_metadata_vortex_transport.json").write_text(json.dumps(m1, indent=1, ensure_ascii=False))
    prev = json.loads((P / "zenodo_record_vortex_transport.json").read_text())["id"]
    sh(["python3", "scripts/zenodo_deposit_paper.py", "--meta", "paper/zenodo_metadata_vortex_transport.json", "--pdf", "paper/vortex_transport.pdf",
        "--record-out", "paper/zenodo_record_vortex_transport.json", "--new-version-of", str(prev), "--publish"])
    rec1 = json.loads((P / "zenodo_record_vortex_transport.json").read_text()); print("paper 1 v2.2 published:", rec1["doi"])
    print("NEXT BY HAND: README DOI lines, LEDGER claims (publication of paper 3, v2.2 correction), commit and push.")


if __name__ == "__main__":
    main()
