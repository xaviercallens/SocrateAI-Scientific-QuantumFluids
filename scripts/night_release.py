#!/usr/bin/env python3
"""Release v1.17.0 after the night publication workflow has finished (owner's instruction, 2026-10-07 23:40:
"commit, push, merge and release and let the workflow working during the night for the publication").

Waits for "=== night workflow done" in data/generated/pgpe/transport/night_publish.log (exits without releasing if that
workflow aborted), then follows the v1.16.0 procedure: release commit + annotated tag + push; Zenodo software bundle
as a new version of record 23144587 (--publish); README/LEDGER/record commit; GitHub release; Hugging Face refresh.
Log: data/generated/pgpe/transport/night_release.log. No commit trailers (owner's rule).
"""
import json, os, re, subprocess, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; TR = ROOT / "data/generated/pgpe/transport"
LOG = open(TR / "night_release.log", "a"); TAG, PREV_BUNDLE = "v1.17.0", "23144587"


def log(*a):
    LOG.write(time.strftime("%F %T ") + " ".join(str(x) for x in a) + "\n"); LOG.flush()


def sh(cmd, check=True, **kw):
    log("$", " ".join(cmd)); r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)
    log(r.stdout[-2500:]); log(r.stderr[-1200:]) if r.stderr else None
    if check and r.returncode:
        raise RuntimeError(f"rc={r.returncode}: {cmd}")
    return r


def wait_publication():
    p = TR / "night_publish.log"
    while True:
        s = p.read_text() if p.exists() else ""
        if "=== night workflow done" in s:
            return
        if "!!! ABORTED" in s:
            log("publication workflow aborted; no release"); sys.exit(2)
        time.sleep(120)


def notes(paper_doi, w2):
    v, m, n = w2["verdict"], w2["n_meet"], w2["n"]
    return (f"Vortex-transport paper, **version 2 after peer review 1** (DOI {paper_doi}; concept 10.5281/zenodo.23202454): physics narrative with the "
            f"protocol in an appendix, seven figures, explicit corrected-imprint equations, the frame of the transverse force, code and Lean appendices. "
            f"The L = 96 counterflow control (W2, four runs, rule W2-A fixed before runs 3-4 were read): **{v}** ({m} of {n} runs show no stall); the "
            f"parameter-free wind equation with the measured alpha = 0.0062 is reported against all pairs. New physics content: the Josephson offset is not "
            f"amplitude fluctuations (phase-only correlator, same offset); vortices carry 7-28 % of the normal density in the equilibrated L = 192 states; "
            f"the kinetic reading of the friction law alpha/(rho_n/rho) = (rho/rho_s)<c_g sigma_tr>/kappa, giving a mode-averaged transport cross-section of "
            f"1.4 healing lengths, against Sonin's Born law (valid for < 3 % of the bath's modes; extrapolated, seven times too large). Lean: FrictionKinetic.lean "
            f"(3 theorems) and DissipativeVortexDynamics.stall_of_drive_sign (torus drive). Autoresearch round 2 (ten directions, priors committed before probing; "
            f"R2-03 refuted) selected the counterflow stall map conditional on W2, the friction law against cutoff otherwise; both pre-registered "
            f"(PGPE_COUNTERFLOW_PREREG.md, PGPE_FRICTION_LAW_PREREG.md) with Lean companions. Instrument: --kcut-frac and --nk-every in vortex_transport.py; "
            f"queue runner for the campaign; the night workflow that evaluated, filled and published the paper from templates written before the data. "
            f"LEDGER CLAIM-089 to CLAIM-094.")


def main():
    wait_publication()
    paper = json.load(open(ROOT / "paper/zenodo_record_vortex_transport.json")); w2 = json.load(open(TR / "W2_result.json"))
    body = notes(paper["doi"], w2); log("notes:", body[:200])
    # release content commit
    mp = ROOT / "paper/zenodo_metadata.json"; meta = json.load(open(mp))
    meta["metadata"]["description"] += f"<p><b>New in {TAG}.</b> " + body.replace("**", "") + "</p>"
    json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
    rp = ROOT / "README.md"; s = rp.read_text(); s = re.sub(r"release-v1\.\d+\.\d+-orange", f"release-{TAG}-orange", s); rp.write_text(s)
    sh(["git", "add", "paper/zenodo_metadata.json", "README.md", "scripts/zenodo_deposit.py", "scripts/night_release.py"])
    sh(["git", "commit", "-q", "-m", f"{TAG}: vortex-transport paper v2 published after peer review; W2 verdict {w2['verdict']}; friction-law kinetic reading; FrictionKinetic.lean; round-2 autoresearch selection and two pre-registrations"])
    sh(["git", "tag", "-a", TAG, "-m", f"{TAG}: paper v2 after peer review, W2 verdict {w2['verdict']}, kinetic reading of the friction law"])
    sh(["git", "push", "-q", "origin", "master"]); sh(["git", "push", "-q", "origin", TAG])
    # Zenodo software bundle (new version of the v1.16.0 record)
    sh(["python3", "scripts/zenodo_deposit.py", "--tag", TAG, "--new-version-of", PREV_BUNDLE, "--publish"])
    rec = json.load(open(ROOT / "paper/zenodo_record.json")); doi, rid = rec["doi"], rec["id"]; log("bundle published", rec)
    # README DOI line, LEDGER, record commit
    s = rp.read_text(); s = s.replace(f"10.5281/zenodo.{PREV_BUNDLE}", doi).replace("(`v1.16.0`)", f"(`{TAG}`)"); rp.write_text(s)
    lp = ROOT / "LEDGER.md"; lines = lp.read_text().split("\n")
    i = next((k for k, l in enumerate(lines) if l.startswith("| CLAIM-093 |")), next(k for k, l in enumerate(lines) if l.startswith("| CLAIM-091 |")))
    lines.insert(i + 1, f"| CLAIM-094 | — → PUBLISHED | {time.strftime('%Y-%m-%d')} | {TAG} published on Zenodo, DOI {doi} (new version of {PREV_BUNDLE}, concept 10.5281/zenodo.22855581): archive + 11 PDFs including vortex_transport.pdf v2; GitHub release {TAG}; Hugging Face dataset card refreshed. Contents: {body.replace('**', '')} |")
    lp.write_text("\n".join(lines))
    sh(["git", "add", "README.md", "LEDGER.md", "paper/zenodo_record.json"])
    sh(["git", "commit", "-q", "-m", f"{TAG} published: Zenodo DOI {doi}, GitHub release, Hugging Face dataset updated; LEDGER CLAIM-094"])
    sh(["git", "push", "-q", "origin", "master"])
    sh(["gh", "release", "create", TAG, "--title", TAG, "--notes", body + f"\n\nZenodo: https://doi.org/{doi} (concept 10.5281/zenodo.22855581). Paper v2: https://doi.org/{paper['doi']}"])
    r = sh(["python3", "scripts/hf_publish.py", "--tag", TAG, "--doi", doi], check=False)
    log("hf_publish rc", r.returncode); log("=== release done", TAG, doi)


if __name__ == "__main__":
    try:
        log("=== release workflow start"); main()
    except Exception:
        log("!!! RELEASE ABORTED\n" + traceback.format_exc()); sys.exit(1)
