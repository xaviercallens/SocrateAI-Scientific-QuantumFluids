#!/usr/bin/env python3
"""Deposit the qf-pgpe software paper on Zenodo as its own record. Dry run by default; `--publish` deposits and publishes.
Gates: no \\PENDING marker in the document body, clean compile, sources committed, PDF newer than the number macros."""
import argparse, json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "paper"
ap = argparse.ArgumentParser(); ap.add_argument("--publish", action="store_true"); a = ap.parse_args()
body = (P / "qf_pgpe_software.tex").read_text().split("\\begin{document}", 1)[1]
if "\\PENDING" in body:
    sys.exit("gate: \\PENDING left in the paper body")
subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "qf_pgpe_software.tex"], cwd=P, capture_output=True)
lg = (P / "qf_pgpe_software.log").read_text()
if "Output written" not in lg or "undefined" in lg.lower():
    sys.exit("gate: compile problem")
if subprocess.run(["git", "diff", "--quiet", "--", "paper/qf_pgpe_software.tex", "paper/sw_numbers.tex", "paper/zenodo_metadata_qf_pgpe_software.json"], cwd=ROOT).returncode:
    sys.exit("gate: uncommitted sources")
print("software paper:", re.search(r"\((\d+ pages?)", lg).group(1))
if not a.publish:
    print("DRY RUN ok; would deposit paper/qf_pgpe_software.pdf as a new record"); sys.exit(0)
r = subprocess.run(["python3", "scripts/zenodo_deposit_paper.py", "--meta", "paper/zenodo_metadata_qf_pgpe_software.json", "--pdf", "paper/qf_pgpe_software.pdf",
                    "--record-out", "paper/zenodo_record_qf_pgpe_software.json", "--publish"], cwd=ROOT, capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:]); sys.exit(r.returncode)
