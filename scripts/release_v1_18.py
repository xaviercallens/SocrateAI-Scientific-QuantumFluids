#!/usr/bin/env python3
"""Release v1.18.0 (owner: "yes, do it", 2026-10-09): commit + annotated tag + push; Zenodo bundle (new version of the v1.17.0 record);
README DOI/version, LEDGER, GitHub release, Hugging Face refresh. Logs to stdout; aborts before any publication on an error."""
import json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; TAG, PREV = "v1.18.0", "23225129"
NOTES = ("Friction-law paper (own DOI 10.5281/zenodo.23262132): pre-registered test of alpha proportional to rho_n against the cutoff -- FL2 and the Born rival fail (coefficient 0.31, 0.232, 0.102 at k_c = 2.1, 3.1, 6.3), "
         "alpha follows the temperature, alpha/T = 0.054 +- 0.003 (energy) / 0.060 +- 0.002 (regression) over six arms and three cutoffs (chi2 1.3/5), confirmed by the registered window on the last arm; the 'geometric core size' reading of paper 1 withdrawn. "
         "Vortex-transport paper v2.2 (10.5281/zenodo.23262143): the correction. Estimator bias found by a second (Rust) implementation: the energy estimator of alpha is biased low by diffusion (-8, -18, -22 % at eta = 5e-4, 1e-3, 2e-3; registered gate G0 passed on one seed; regression unbiased). "
         "Vortex-phonon scattering instrument and pre-registration (T = 0 Bogoliubov wave on a vortex pair; Born baseline recorded first; first scan read as registered: gates KA1-KA4 mixed, P1 fails, P2 passes, P4 not a valid test; amendment WS-A1 lattice follow-up in progress, not part of this release's claims). "
         "Lean: FrictionKinetic.lean, DissipativeVortexDynamics.stall_of_drive_sign. Autoresearch round 2, counterflow pre-registration (campaign cancelled by the W2 verdict), friction-law pre-registration and results, ledger CLAIM-089 to CLAIM-099. "
         "Companion: rusty-SUNDIALS branch feat/qf-pgpe-reference (Rust vortex instrument, transport estimators, thermal toolkit, scattering, CVODE cross-check).")


def sh(cmd, check=True):
    print("$", " ".join(cmd), flush=True); r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True); print((r.stdout + r.stderr)[-1500:])
    if check and r.returncode:
        sys.exit(f"FAILED rc={r.returncode}: {cmd}")
    return r


tag_exists = bool(subprocess.run(["git", "tag", "-l", TAG], cwd=ROOT, capture_output=True, text=True).stdout.strip())
if not tag_exists:
    mp = ROOT / "paper/zenodo_metadata.json"; meta = json.load(open(mp)); meta["metadata"]["description"] += f"<p><b>New in {TAG}.</b> {NOTES}</p>"
    json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
    dp = ROOT / "scripts/zenodo_deposit.py"; s = dp.read_text()
    if "friction_law.pdf" not in s:
        s = s.replace('ROOT / "paper" / "vortex_transport.pdf"]', 'ROOT / "paper" / "vortex_transport.pdf", ROOT / "paper" / "friction_law.pdf"]'); dp.write_text(s)
    rp = ROOT / "README.md"; r = rp.read_text(); rp.write_text(re.sub(r"release-v1\.\d+\.\d+-orange", f"release-{TAG}-orange", r))
    sh(["git", "add", "paper/zenodo_metadata.json", "scripts/zenodo_deposit.py", "scripts/release_v1_18.py", "README.md"])
    sh(["git", "commit", "-q", "-m", f"{TAG}: friction-law paper (FL2 and Born rival fail; alpha follows T), vortex-transport v2.2 correction, energy-estimator bias, scattering pre-registration and first scan, FrictionKinetic.lean"])
    sh(["git", "tag", "-a", TAG, "-m", f"{TAG}: friction law follows the temperature; energy-estimator bias; scattering instrument"]); sh(["git", "push", "-q", "origin", "master"]); sh(["git", "push", "-q", "origin", TAG])
for attempt in range(4):
    if sh(["python3", "scripts/zenodo_deposit.py", "--tag", TAG, "--new-version-of", PREV, "--publish"], check=False).returncode == 0:
        break
    time.sleep(30)
else:
    sys.exit("Zenodo deposit failed 4 times")
rec = json.load(open(ROOT / "paper/zenodo_record.json")); doi = rec["doi"]; print("bundle", rec)
r = rp.read_text().replace(f"10.5281/zenodo.{PREV}", doi).replace("(`v1.17.0`)", f"(`{TAG}`)"); rp.write_text(r)
lp = ROOT / "LEDGER.md"; L = lp.read_text().split("\n"); i = next(k for k, l in enumerate(L) if l.startswith("| CLAIM-099 |"))
L.insert(i + 1, f"| CLAIM-100 | — → PUBLISHED | {time.strftime('%Y-%m-%d')} | {TAG} published on Zenodo, DOI {doi} (new version of {PREV}, concept 10.5281/zenodo.22855581): archive + 12 PDFs including friction_law.pdf and vortex_transport.pdf v2.2; GitHub release {TAG}; Hugging Face refreshed. Archives the scripts and results of papers 3 and 1 v2.2 (the v1.17.0 bundle predates them). Owner's instruction 2026-10-09 ('yes, do it'). |")
lp.write_text("\n".join(L))
sh(["git", "add", "README.md", "LEDGER.md", "paper/zenodo_record.json"]); sh(["git", "commit", "-q", "-m", f"{TAG} published: Zenodo DOI {doi}, GitHub release, Hugging Face; LEDGER CLAIM-100"]); sh(["git", "push", "-q", "origin", "master"])
sh(["gh", "release", "create", TAG, "--title", TAG, "--notes", NOTES + f"\n\nZenodo: https://doi.org/{doi} (concept 10.5281/zenodo.22855581)."])
sh(["python3", "scripts/hf_publish.py", "--tag", TAG, "--doi", doi], check=False); print("DONE", TAG, doi)
