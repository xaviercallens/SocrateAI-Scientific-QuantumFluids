#!/usr/bin/env python3
"""Release of the software bundle: commit + annotated tag + push; Zenodo bundle (new version of the previous record); README DOI/version, LEDGER claim,
GitHub release, Hugging Face refresh. Resumable: re-running after a failure skips what exists (tag present -> no re-commit/tag).

    python3 scripts/release.py --tag v1.19.0 --prev 23262524 --claim CLAIM-104 --after CLAIM-103 --notes-file docs/releases/v1.19.0.md
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--prev", required=True); ap.add_argument("--claim", required=True)
ap.add_argument("--after", required=True, help="ledger claim id after which the new row is inserted"); ap.add_argument("--notes-file", required=True); a = ap.parse_args()
NOTES = Path(a.notes_file).read_text().strip()


def sh(cmd, check=True):
    print("$", " ".join(cmd), flush=True); r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True); print((r.stdout + r.stderr)[-1200:])
    if check and r.returncode:
        sys.exit(f"FAILED rc={r.returncode}: {cmd}")
    return r


rp = ROOT / "README.md"; mp = ROOT / "paper/zenodo_metadata.json"; dp = ROOT / "scripts/zenodo_deposit.py"
if not subprocess.run(["git", "tag", "-l", a.tag], cwd=ROOT, capture_output=True, text=True).stdout.strip():
    meta = json.load(open(mp)); meta["metadata"]["description"] += f"<p><b>New in {a.tag}.</b> {NOTES}</p>"; json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
    s = dp.read_text()
    if "qf_pgpe_software.pdf" not in s:
        dp.write_text(s.replace('ROOT / "paper" / "friction_law.pdf"]', 'ROOT / "paper" / "friction_law.pdf", ROOT / "paper" / "qf_pgpe_software.pdf"]'))
    rp.write_text(re.sub(r"release-v1\.\d+\.\d+-orange", f"release-{a.tag}-orange", rp.read_text()))
    sh(["git", "add", "paper/zenodo_metadata.json", "scripts/zenodo_deposit.py", "scripts/release.py", a.notes_file, "README.md"])
    sh(["git", "commit", "-q", "-m", f"{a.tag}: " + NOTES.split(".")[0][:110]])
    sh(["git", "tag", "-a", a.tag, "-m", f"{a.tag}"]); sh(["git", "push", "-q", "origin", "master"]); sh(["git", "push", "-q", "origin", a.tag])
rec_path = ROOT / "paper/zenodo_record.json"
if json.load(open(rec_path)).get("tag") != a.tag:
    for attempt in range(5):
        if sh(["python3", "scripts/zenodo_deposit.py", "--tag", a.tag, "--new-version-of", a.prev, "--publish"], check=False).returncode == 0:
            break
        time.sleep(30)
    else:
        sys.exit("Zenodo deposit failed 5 times")
rec = json.load(open(rec_path)); doi = rec["doi"]; print("bundle", rec)
r = rp.read_text(); r = r.replace(f"10.5281/zenodo.{a.prev}", doi); r = re.sub(r"\(`v1\.\d+\.\d+`\)", f"(`{a.tag}`)", r, count=1); rp.write_text(r)
lp = ROOT / "LEDGER.md"; L = lp.read_text().split("\n")
if not any(l.startswith(f"| {a.claim} |") for l in L):
    i = next(k for k, l in enumerate(L) if l.startswith(f"| {a.after} |"))
    L.insert(i + 1, f"| {a.claim} | — → PUBLISHED | {time.strftime('%Y-%m-%d')} | {a.tag} published on Zenodo, DOI {doi} (new version of {a.prev}, concept 10.5281/zenodo.22855581): archive + 13 PDFs including qf_pgpe_software.pdf; GitHub release {a.tag}; Hugging Face refreshed. {NOTES} |"); lp.write_text("\n".join(L))
sh(["git", "add", "README.md", "LEDGER.md", "paper/zenodo_record.json"]); sh(["git", "commit", "-q", "-m", f"{a.tag} published: Zenodo DOI {doi}, GitHub release, Hugging Face; LEDGER {a.claim}"], check=False); sh(["git", "push", "-q", "origin", "master"])
if subprocess.run(["gh", "release", "view", a.tag], cwd=ROOT, capture_output=True).returncode:
    sh(["gh", "release", "create", a.tag, "--title", a.tag, "--notes", NOTES + f"\n\nZenodo: https://doi.org/{doi} (concept 10.5281/zenodo.22855581)."])
sh(["python3", "scripts/hf_publish.py", "--tag", a.tag, "--doi", doi], check=False); print("DONE", a.tag, doi)
